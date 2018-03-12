from flask import Flask, render_template, redirect, url_for, session, jsonify, request, g
from flask_mail import Mail, Message
import time
from random import *
import json
import hashlib
import collections
import os
import redis
import logging
import math
import copy
import data_loader as dl
import data_display as dd
import data_model as dm
import user_data as ud
import config
from main_section import main_section
from tutorial import tutorial
from util import state_machine
from global_data import *


app = Flask(__name__)
app.debug = False
app.secret_key = 'a9%z$/`9h8FMnh893;*g783'

app.register_blueprint(tutorial)
app.register_blueprint(main_section)

app.config.from_pyfile('email_config.py')
mail = Mail(app)


if not r.exists('user_id_generator'):
    r.set('user_id_generator', 0)


def get_main_section_data(uid, section):
    data_num = uid%10
    if data_num == 0:
        data_num = 10
    data_num -= 1

    if section == 1:
        return DATA_SECTION1[data_num]
    else:
        return DATA_SECTION2[data_num]


@app.route('/')
@app.route('/index')
def index():
    ustudy_mode = request.args.get('mode')
    ustudy_budget = request.args.get('budget')
    if ustudy_mode is None:
        ustudy_mode = '1'
    if ustudy_budget is None:
        ustudy_budget = '0'
    if ustudy_mode != '4':
        ustudy_budget = '0'
    if int(ustudy_mode) not in [1,2,3,4]:
        return page_not_found('page_not_found')
    if ustudy_budget not in ['moderate', 'minimum']:
        if float(ustudy_budget) < 0 or float(ustudy_budget) > 100:
            return page_not_found('page_not_found')

    session['user_cookie'] = hashlib.sha224("salt12138" + str(time.time()) + '.' + str(randint(1,10000))).hexdigest()
    user_data_key = session['user_cookie'] + '_user_data'
    user_id = 0
    if request.args.get("id") is None:
        user_id = r.incr('user_id_generator')
        r.set("session_"+str(user_id)+"_state", 0)
    else:
       user_id = str(request.args.get("id"))
       # r.set("session_"+user_id+"_state")
    index = r.get("session_"+str(user_id)+"_state")
    session['user_id'] = user_id
    data = 'type: user_id,id: ' + str(user_id) + ';\n'
    data += 'type: session_start,timestamp: ' + str(time.time()) + ';\n'
    r.set(user_data_key, data)
    r.set("session_"+str(user_id), session)

    r.set(session['user_cookie']+'_ustudy_mode', ustudy_mode)
    r.set(session['user_cookie']+'_ustudy_budget', ustudy_budget)


    return redirect(url_for(config.SEQUENCE[int(index)]))


@app.route('/introduction')
@state_machine('show_introduction')
def show_introduction():
    return render_template('introduction.html', uid=str(session['user_id']))


@app.route('/introduction2')
@state_machine('show_introduction2')
def show_introduction2():
    return render_template('introduction2.html', uid=str(session['user_id']))


@app.route('/save_data', methods=['GET', 'POST'])
def save_data():
    user_data = request.form['user_data']
    user_data_key = session['user_cookie'] + '_user_data'
    r.append(user_data_key, user_data+'\n')
    return 'data_saved.'


@app.route('/get_cell', methods=['GET', 'POST'])
def open_cell():
    ret = dict()
    kapr_limit = 0
    
    if session['state'] == 13:
        working_data = DATA_CLICKABLE_DEMO
        full_data = DATASET_TUTORIAL
    elif session['state'] == 24:
        working_data = DATA_DM_DEMO
        full_data = DATASET_TUTORIAL
        # kapr_limit = 100
        # float(r.get(session['user_cookie']+'tutorial_dmdemo_kapr_limit'))
    elif session['state'] == 29:
        working_data = DATA_CLICKABLE_PRACTICE
        full_data = DATASET_TUTORIAL
        kapr_limit = 20
        # float(r.get(session['user_cookie']+'tutorial_practice_kapr_limit'))
    elif session['state'] == 31:
        working_data = get_main_section_data(session['user_id'], 1)
        full_data = DATASET
        kapr_limit = float(r.get(session['user_cookie']+'section1_kapr_limit'))
    else:
        working_data = get_main_section_data(session['user_id'], 2)
        full_data = DATASET2

    id1 = request.args.get('id1')
    id2 = request.args.get('id2')
    mode = request.args.get('mode')
    pair_num = str(id1.split('-')[0])
    attr_num = str(id1.split('-')[2])
    user_key = session['user_cookie']
    ret = dm.open_cell(user_key, full_data, working_data, pair_num, attr_num, mode, r, kapr_limit)
    return jsonify(ret)


@app.route('/get_big_cell', methods=['GET', 'POST'])
def open_big_cell():
    ret = dict()

    kapr_limit = 0
    if session['state'] == 13:
        working_data = DATA_CLICKABLE_DEMO
        full_data = DATASET_TUTORIAL
    elif session['state'] == 24:
        working_data = DATA_DM_DEMO
        full_data = DATASET_TUTORIAL
        # kapr_limit = float(r.get(session['user_cookie']+'tutorial_dmdemo_kapr_limit'))
    elif session['state'] == 29:
        working_data = DATA_CLICKABLE_PRACTICE
        full_data = DATASET_TUTORIAL
        kapr_limit = 20
        # float(r.get(session['user_cookie']+'tutorial_practice_kapr_limit'))
    elif session['state'] == 31:
        working_data = get_main_section_data(session['user_id'], 1)
        full_data = DATASET
        kapr_limit = float(r.get(session['user_cookie']+'section1_kapr_limit'))
    else:
        working_data = get_main_section_data(session['user_id'], 2)
        full_data = DATASET2

    id1 = request.args.get('id1')
    id2 = request.args.get('id2')
    id3 = request.args.get('id3')
    id4 = request.args.get('id4')
    mode = request.args.get('mode')
    user_key = session['user_cookie']

    pair_num1 = str(id1.split('-')[0])
    attr_num1 = str(id1.split('-')[2])
    ret1 = dm.open_cell(user_key, full_data, working_data, pair_num1, attr_num1, mode, r, kapr_limit)
    pair_num2 = str(id3.split('-')[0])
    attr_num2 = str(id3.split('-')[2])
    ret2 = dm.open_cell(user_key, full_data, working_data, pair_num2, attr_num2, mode, r, kapr_limit)

    if ret2['result'] == 'fail':
        return jsonify(ret2)

    ret = {
        'value1': ret1['value1'],
        'value2': ret1['value2'],
        'value3': ret2['value1'],
        'value4': ret2['value2'],
        'mode': ret2['mode'],
        'KAPR': ret2['KAPR'],
        'result': ret2['result'],
        'new_delta': ret2['new_delta']
    }

    return jsonify(ret)


@app.route('/next', methods=['GET', 'POST'])
def next():
    sequence = config.SEQUENCE
    state = session['state'] + 1
    session['state'] += 1
    user_id = session["user_id"]
    r.set("session_"+str(user_id)+"_state", str(session['state']))
    #timing info on next click 
    # timing_info = sequence[session['state']-1] + ": " + time.strftime("%a, %d %b %Y %H:%M:%S")
    # msg = Message(subject='user click: ' + session['user_cookie'], body=timing_info, recipients=['ppirl.mindfil@gmail.com'])
    # mail.send(msg)
 
    return redirect(url_for(sequence[state]))


@app.route('/pull_data')
def pull_data():
    user_data_key = session['user_cookie'] + '_user_data'
    user_data = r.get(user_data_key)
    if not user_data:
        return render_template('show_data.html', data='No data is collected for this user.', uid=str(session['user_id']))

    data = ud.parse_user_data(user_data)

    ret = ''
    for d in data:
        if 'type' in d and d['type'] == 'performance1':
            ret += ('section 1: ' + d['content'] + ';\n')
    for d in data:
        if 'type' in d and d['type'] == 'performance2':
            ret += ('section 2: ' + d['content'] + ';\n')
    for d in data:
        if 'type' in d and d['type'] == 'final_KAPR_section1':
            ret += ('Final privacy budget used in section 1: ' + str(round(100*float(d['value']), 2)) + '% out of ' + d['total'] + '%;\n')
    
    ret = ret + '\n' + user_data
    ret = ret.replace('\n', '<br />')

    return render_template('show_data.html', data=ret, uid=str(session['user_id']))


@app.route('/pull_data_all')
def pull_data_all():
    ret = ''
    for key in r.scan_iter("*_user_data"):
        user_data = r.get(key)
        ret = ret + user_data + '<br/><br/>'
    return ret


@app.route('/thankyou')
@state_machine('show_thankyou')
def show_thankyou():
    # grading section 1
    user_data_key = session['user_cookie'] + '_user_data'
    r.append(user_data_key, 'type: session_end,timestamp: '+str(time.time())+';\n')
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 1))
    performance1 = 'type:performance1,content:' + str(result[0]) + ' out of ' + str(result[1]) + ';\n'
    r.append(user_data_key, performance1)

    # grading section 2
    user_data_key = session['user_cookie'] + '_user_data'
    #r.append(user_data_key, 'type: session_end,timestamp: '+str(time.time())+';\n')
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    # TODO! TODO! TODO! TODO! TODO! TODO! TODO! TODO! TODO! TODO! 
    # SECTION 2 pair num must be different from section 1! section 2 num be a factor of 6
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 2))
    performance2 = 'type:performance2,content:' + str(result[0]) + ' out of ' + str(result[1]) + ';\n'
    r.append(user_data_key, performance2)

    # get final KAPR
    KAPR_key = session['user_cookie'] + '_KAPR'
    final_KAPR = r.get(KAPR_key)
    kapr_limit = r.get(session['user_cookie']+'section1_kapr_limit')
    if final_KAPR is not None:
        kapr_info = 'type:final_KAPR_section1, value:' + str(final_KAPR) + ',total:' + kapr_limit + ';\n'
        r.append(user_data_key, kapr_info)

    data = ud.parse_user_data(r.get(user_data_key))
    # dl.save_data_to_json('data/saved/'+str(session['user_cookie'])+'.json', user_data)
    extend_data = ''
    for d in data:
        if 'type' in d and d['type'] == 'performance1':
            extend_data += ('section 1: ' + d['content'] + ';\n')
    for d in data:
        if 'type' in d and d['type'] == 'performance2':
            extend_data += ('section 2: ' + d['content'] + ';\n')
    for d in data:
        if 'type' in d and d['type'] == 'final_KAPR_section1':
            extend_data += ('Final privacy budget used in section 1: ' + str(round(100*float(d['value']), 2)) + '% out of ' + d['total'] + '%;\n')
    extend_data = extend_data + r.get(user_data_key)

    if r.get("data_choice_" + session['user_cookie']) != "collect":
        # print "discareded"
        r.delete(user_data_key)
        # print r.get(user_data_key)
        user_data = 'type:user_id,id:'+str(session['user_id'])+';\n'
        user_data = user_data + 'type:consent,value:NoDataCollection;\n'
        r.set(user_data_key, user_data)

    # send the data to email.
    msg = Message(subject='user data: ' + session['user_cookie'], body=extend_data, recipients=['mindfil.ppirl@gmail.com'])
    mail.send(msg)

    # clear user data in redis
    #for key in r.scan_iter("prefix:"+session['user_cookie']):
    #    r.delete(key)

    return render_template('thankyou.html', uid=str(session['user_id']))


'''
@app.route('/section1_start')
@state_machine('show_section1_startpage')
def show_section1_startpage():
    return render_template('section1_start.html')
'''

@app.route('/id')
def get_id():
    if session['user_id']:
        return str(session['user_id'])
    return 'Null'


@app.route('/flushdb_522006058')
def flush_redis():
    r.flushdb()
    return 'redis flushed.'


@app.route('/save_data_choice', methods=['POST'])
def save_data_choice():
    data_choice = request.form.get('data_choice')
    r.set("data_choice_" + session['user_cookie'], data_choice)
    print r.get("data_choice_" + session['user_cookie'])
    return redirect(url_for('next'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

