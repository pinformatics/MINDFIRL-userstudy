from flask import Flask, render_template, redirect, url_for, session, jsonify, request, g
from functools import wraps
import time
from random import *
import json
import hashlib
import collections
import os
import redis
import logging
import data_loader as dl
import data_display as dd
import data_model as dm
from flask_sendgrid import SendGrid
# from flask_mail import Mail, Message
# from config import *


app = Flask(__name__)

app.config['SENDGRID_API_KEY'] = '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'
# app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY')
app.config['SENDGRID_DEFAULT_FROM'] = 'mindfil.ppirl@gmail.com'
mail = SendGrid(app)


"""
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)
"""

# app.config.from_pyfile('config.py')
# app.config.update(dict(
#     MAIL_SUPPRESS_SEND = False,
#     MAIL_DEBUG = True,
#     TESTING = False,
#     MAIL_SERVER = 'smtp.gmail.com',
#     MAIL_PORT = 587,
#     MAIL_USE_TLS = False,
#     MAIL_USE_SSL = False,
#     MAIL_USERNAME = 'mindfil.ppirl@gmail.com',
#     MAIL_PASSWORD = 'Abcd1234$',
#     MAIL_DEFAULT_SENDER = 'mindfil.ppirl@gmail.com'
# ))


MAIL_SENDER = 'mindfil.ppirl@gmail.com'
MAIL_RECEIVER = 'mindfil.ppirl@gmail.com'

# mail = Mail(app)

if 'DYNO' in os.environ:
    r = redis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)
else:
    r = redis.Redis(host='localhost', port=6379, db=0, charset="utf-8", decode_responses=True)

DATASET = dl.load_data_from_csv('data/section2.csv')
DATA_PAIR_LIST = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/ppirl.csv'))

@app.route('/')
@app.route('/survey_link')
def show_survey_link():
    mail.send_email(
    from_email=MAIL_SENDER,
    to_email=MAIL_RECEIVER,
    subject='Aim 3 start',
    text='Start',
    )
    
    pairs_formatted = DATA_PAIR_LIST.get_data_display('masked')[0:12]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = DATA_PAIR_LIST.get_icons()[0:6]
    ids_list = DATA_PAIR_LIST.get_ids()[0:12]
    ids = list(zip(ids_list[0::2], ids_list[1::2]))
    session['user_cookie'] = hashlib.sha224((str(time.time()) + str(randint(1,100))).encode('utf-8')).hexdigest()

    total_characters = DATA_PAIR_LIST.get_total_characters()
    mindfil_total_characters_key = session['user_cookie'] + '_mindfil_total_characters'
    r.set(mindfil_total_characters_key, total_characters)
    mindfil_disclosed_characters_key = session['user_cookie'] + '_mindfil_disclosed_characters'
    r.set(mindfil_disclosed_characters_key, 0)


    # KAPR - K-Anonymity privacy risk
    KAPR_key = session['user_cookie'] + '_KAPR'
    r.set(KAPR_key, 0)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = session['user_cookie'] + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    delta = list()
    delta_cdp = list()
    for i in range(6):
        data_pair = DATA_PAIR_LIST.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'])
        delta_cdp += dm.cdp_delta(data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 0, total_characters)
    return render_template('survey_link.html', data=data, icons=icons, ids=ids, title='Privacy Perserving Interactive Record Linkage (PPIRL)', thisurl='/record_linkage', page_number=16, delta=delta, delta_cdp=delta_cdp)

@app.route("/save_survey", methods=['POST'])
def save_survey():
    f = request.form
    resps = ""
    for key in f.keys():
        variable = key.encode('utf8')
        value = f.get(variable).encode('utf8')
        resps += variable + ','.encode('utf8') + '"'.encode('utf8') + value + '"'.encode('utf8') + ";".encode('utf8') 
    
    mail.send_email(from_email=MAIL_SENDER,to_email=MAIL_RECEIVER,subject='Aim 3 survey',text=resps)
    
    # sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    # data = {
    #   "personalizations": [
    #     {
    #       "to": [
    #         {
    #           "email": MAIL_RECEIVER
    #         }
    #       ],
    #       "subject": "Sending with SendGrid is Fun"
    #     }
    #   ],
    #   "from": {
    #     "email": MAIL_RECEIVER
    #   },
    #   "content": [
    #     {
    #       "type": "text/plain",
    #       "value": "and easy to do anywhere, even with Python"
    #     }
    #   ]
    # }
    # response = sg.client.mail.send.post(request_body=data)
    # msg = Message(subject='Aim 3 Survey', body=resps, recipients=[MAIL_RECEIVER])
    # mail.send(msg)

    return "Thank you!"

@app.route('/get_cell', methods=['GET', 'POST'])
def open_cell():
    id1 = request.args.get('id1')
    id2 = request.args.get('id2')
    mode = request.args.get('mode')

    pair_num = str(id1.split('-')[0])
    attr_num = str(id1.split('-')[2])

    pair_id = int(pair_num)
    attr_id = int(attr_num)

    pair = DATA_PAIR_LIST.get_data_pair(pair_id)
    attr = pair.get_attributes(attr_id)
    attr1 = attr[0]
    attr2 = attr[1]
    helper = pair.get_helpers(attr_id)
    helper1 = helper[0]
    helper2 = helper[1]

    if mode == 'full':
        return jsonify({"value1": attr1, "value2": attr2, "mode": "full"})

    attr_display_next = pair.get_next_display(attr_id = attr_id, attr_mode = mode)
    ret = {"value1": attr_display_next[1][0], "value2": attr_display_next[1][1], "mode": attr_display_next[0]}

    cdp_previous = pair.get_character_disclosed_num(1, attr_id, mode) + pair.get_character_disclosed_num(2, attr_id, mode)
    cdp_post = pair.get_character_disclosed_num(1, attr_id, ret['mode']) + pair.get_character_disclosed_num(2, attr_id, ret['mode'])
    cdp_increment = cdp_post - cdp_previous

    # atom operation! updating character disclosed percentage
    mindfil_disclosed_characters_key = session['user_cookie'] + '_mindfil_disclosed_characters'
    r.incrby(mindfil_disclosed_characters_key, cdp_increment)
    mindfil_total_characters_key = session['user_cookie'] + '_mindfil_total_characters'
    cdp = 100.0*int(r.get(mindfil_disclosed_characters_key))/int(r.get(mindfil_total_characters_key))
    ret['cdp'] = round(cdp, 1)

    # get K-Anonymity based Privacy Risk
    old_display_status1 = list()
    old_display_status2 = list()
    key1_prefix = session['user_cookie'] + '-' + pair_num + '-1-'
    key2_prefix = session['user_cookie'] + '-' + pair_num + '-2-'
    for attr_i in range(6):
        old_display_status1.append(r.get(key1_prefix + str(attr_i)))
        old_display_status2.append(r.get(key2_prefix + str(attr_i)))

    # update the display status in redis
    key1 = session['user_cookie'] + '-' + pair_num + '-1-' + attr_num
    key2 = session['user_cookie'] + '-' + pair_num + '-2-' + attr_num
    if ret['mode'] == 'full':
        r.set(key1, 'F')
        r.set(key2, 'F')
    elif ret['mode'] == 'partial':
        r.set(key1, 'P')
        r.set(key2, 'P')
    else:
        print("Error: invalid display status.")
        # logging.error('Error: invalid display status.')

    display_status1 = list()
    display_status2 = list()
    key1_prefix = session['user_cookie'] + '-' + pair_num + '-1-'
    key2_prefix = session['user_cookie'] + '-' + pair_num + '-2-'
    for attr_i in range(6):
        display_status1.append(r.get(key1_prefix + str(attr_i)))
        display_status2.append(r.get(key2_prefix + str(attr_i)))

    old_KAPR = dm.get_KAPR_for_dp(DATASET, pair, old_display_status1)
    KAPR = dm.get_KAPR_for_dp(DATASET, pair, display_status1)
    KAPRINC = KAPR - old_KAPR
    KAPR_key = session['user_cookie'] + '_KAPR'
    overall_KAPR = float(r.get(KAPR_key))
    overall_KAPR += KAPRINC
    r.incrbyfloat(KAPR_key, KAPRINC)
    ret['KAPR'] = round(100*overall_KAPR, 1)

    # refresh the delta of KAPR
    new_delta_list = dm.KAPR_delta(DATASET, pair, display_status1)
    ret['new_delta'] = new_delta_list
    new_delta_cdp_list = dm.cdp_delta(pair, display_status1, int(r.get(mindfil_disclosed_characters_key)), int(r.get(mindfil_total_characters_key)))
    ret['new_delta_cdp'] = new_delta_cdp_list

    return jsonify(ret)

app.secret_key = 'a9%z$/`9h8FMnh893;*g783'