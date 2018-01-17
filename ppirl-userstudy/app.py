from flask import Flask, render_template, redirect, url_for, session, jsonify, request, g
#from flask.ext.session import Session
from functools import wraps
import time
from random import *
import data_loader as dl
import data_display as dd
import json
import hashlib
import collections
import os
import redis


app = Flask(__name__)
"""
SESSION_TYPE = 'redis'
app.config.from_object(__name__)
Session(app)
"""

#ENV = 'development'
ENV = 'production'


CONFIG = {
    'sequence': [
        'show_introduction',
        'show_introduction2',
        'show_RL_tutorial',
        'show_instruction_base_mode',
        'show_pratice_base_mode',
        'show_instruction_full_mode',
        'show_pratice_full_mode',
        'show_privacy_in_RL',
        'show_instruction_masked_mode',
        'show_pratice_masked_mode',
        'show_instruction_minimum_mode',
        'show_pratice_minimum_mode',
        'show_instruction_moderate_mode',
        'show_pratice_moderate_mode',
        'show_instruction_ppirl',
        'show_record_linkage_task',
        'show_thankyou'
    ]
}


if ENV == 'production':
    r = redis.from_url(os.environ.get("REDIS_URL"))
elif ENV == 'development':
    r = redis.Redis(host='localhost', port=6379, db=0)


def state_machine(function_name):
    def wrapper(f):
        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            sequence = CONFIG['sequence']
            for i in range(len(sequence)):
                if sequence[i] == function_name:
                    session['state'] = i
                    break
            return f(*args, **kwargs)
        return inner_wrapper
    return wrapper


@app.route('/')
def show_record_linkages():
    #debug
    r.set('foo', 'bar')
    print(r.get('foo'))
    print('redis success.')

    session['user_cookie'] = hashlib.sha224("salt12138" + str(time.time()) + '.' + str(randint(1,10000))).hexdigest()
    session['data'] = dict()
    session['data']['practice'] = ''
    session['data']['start_time'] = time.time()

    return redirect(url_for('show_introduction'))
    #return render_template('record_linkage.html')


@app.route('/introduction')
@state_machine('show_introduction')
def show_introduction():
    return render_template('introduction.html')


@app.route('/introduction2')
@state_machine('show_introduction2')
def show_introduction2():
    return render_template('introduction2.html')


@app.route('/RL_tutorial')
@state_machine('show_RL_tutorial')
def show_RL_tutorial():
    return render_template('RL_tutorial.html')


@app.route('/privacy_in_RL')
@state_machine('show_privacy_in_RL')
def show_privacy_in_RL():
    return render_template('privacy.html')


@app.route('/instructions/base_mode')
@state_machine('show_instruction_base_mode')
def show_instruction_base_mode():
    return render_template('instruction_base_mode.html')


@app.route('/instructions/full_mode')
@state_machine('show_instruction_full_mode')
def show_instruction_full_mode():
    return render_template('instruction_full_mode.html')


@app.route('/instructions/masked_mode')
@state_machine('show_instruction_masked_mode')
def show_instruction_masked_mode():
    return render_template('instruction_masked_mode.html')


@app.route('/instructions/minimum_mode')
@state_machine('show_instruction_minimum_mode')
def show_instruction_minimum_mode():
    return render_template('instruction_minimum_mode.html')


@app.route('/instructions/moderate_mode')
@state_machine('show_instruction_moderate_mode')
def show_instruction_moderate_mode():
    return render_template('instruction_moderate_mode.html')


@app.route('/instructions/encrypted_mode')
@state_machine('show_instruction_encrypted_mode')
def show_instruction_encrypted_mode():
    return render_template('instruction_encrypted_mode.html')


@app.route('/instructions/ppirl')
@state_machine('show_instruction_ppirl')
def show_instruction_ppirl():
    return render_template('instruction_ppirl.html')


@app.route('/practice/base_mode')
@state_machine('show_pratice_base_mode')
def show_pratice_base_mode():
    pairs = dl.load_data_from_csv('data/practice_base_mode.csv')
    pairs_formatted = dd.format_data(pairs, 'base')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = (len(pairs)/2)*[7*['']]
    return render_template('record_linkage_d.html', data=data, icons=icons, title='Base mode', thisurl='/practice/base_mode')


@app.route('/practice/full_mode')
@state_machine('show_pratice_full_mode')
def show_pratice_full_mode():
    pairs = dl.load_data_from_csv('data/practice_full_mode.csv')
    pairs_formatted = dd.format_data(pairs, 'full')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('record_linkage_d.html', data=data, icons=icons, title='Full mode', thisurl='/practice/full_mode')


@app.route('/practice/masked_mode')
@state_machine('show_pratice_masked_mode')
def show_pratice_masked_mode():
    pairs = dl.load_data_from_csv('data/practice_masked_mode.csv')
    pairs_formatted = dd.format_data(pairs, 'masked')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('record_linkage_d.html', data=data, icons=icons, title='Masked mode', thisurl='/practice/masked_mode')


@app.route('/practice/minimum_mode')
@state_machine('show_pratice_minimum_mode')
def show_pratice_minimum_mode():
    pairs = dl.load_data_from_csv('data/practice_minimum_mode.csv')
    pairs_formatted = dd.format_data(pairs, 'minimum')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('record_linkage_d.html', data=data, icons=icons, title='Minimum mode', thisurl='/practice/minimum_mode')


@app.route('/practice/moderate_mode')
@state_machine('show_pratice_moderate_mode')
def show_pratice_moderate_mode():
    pairs = dl.load_data_from_csv('data/practice_moderate_mode.csv')
    pairs_formatted = dd.format_data(pairs, 'moderate')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('record_linkage_d.html', data=data, icons=icons, title='Moderate mode', thisurl='/practice/moderate_mode')


@app.route('/practice/<table_mode>/grading')
def grade_pratice_full_mode(table_mode):
    data_file = 'practice_' + str(table_mode) + '.csv'
    ret = list()
    responses = request.args.get('response').split(',')
    pairs = dl.load_data_from_csv('data/' + data_file)
    j = 0
    all_correct = True
    for i in range(0, len(pairs), 2):
        result = False
        j += 1
        q = 'q' + str(j)
        answer = pairs[i][17]
        if answer == '1' and (q+'a4' in responses or q+'a5' in responses or q+'a6' in responses):
            result = True
        if answer == '0' and (q+'a1' in responses or q+'a2' in responses or q+'a3' in responses):
            result = True
        if not result:
            ret.append('<div>' + pairs[i][18] + '</div>')
            all_correct = False
    if all_correct:
        ret.append('<div>Good job!</div>')
    return jsonify(result=ret)


@app.route('/record_linkage')
@state_machine('show_record_linkage_task')
def show_record_linkage_task():
    pairs = dl.load_data_from_csv('data/ppirl.csv')
    pairs_formatted = dd.format_data(pairs, 'masked')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    ids = dd.get_attribute_id(pairs)
    ids = zip(ids[0::2], ids[1::2])

    total_characters = dd.get_total_characters(pairs)

    mindfil_total_characters_key = session['user_cookie'] + '_mindfil_total_characters'
    r.set(mindfil_total_characters_key, total_characters)
    mindfil_disclosed_characters_key = session['user_cookie'] + '_mindfil_disclosed_characters'
    r.set(mindfil_disclosed_characters_key, 0)

    return render_template('record_linkage_ppirl.html', data=data, icons=icons, ids=ids, title='MINDFIL', thisurl='/record_linkage')


@app.route('/thankyou')
@state_machine('show_thankyou')
def show_thankyou():
    session['data']['end_time'] = time.time()
    dl.save_data_to_json('data/saved/'+str(session['user_cookie'])+'.json', session['data'])
    return render_template('thankyou.html')


@app.route('/save_data', methods=['GET', 'POST'])
def save_data():
    #print(request.form['user_data'])
    session['data']['practice'] = session['data']['practice'] + request.form['user_data']
    return ''


@app.route('/get_cell', methods=['GET', 'POST'])
def open_cell():
    id1 = request.args.get('id1')
    id2 = request.args.get('id2')
    mode = request.args.get('mode')


    pair_num = str(id1.split('-')[0])
    attr_num = str(id1.split('-')[2])

    pair = dl.get_pair('data/ppirl.csv', pair_num)
    record1 = pair[0]
    record2 = pair[1]
 
    attr1 = record1[int(attr_num)]
    attr2 = record2[int(attr_num)]

    if mode == 'full':
        return jsonify({"value1": attr1, "value2": attr2, "mode": "full"})

    if attr_num == '1':
        # id
        helper1 = record1[9]
        helper2 = record2[9]
        get_display = dd.get_string_display
    elif attr_num == '3':
        # first name
        helper1 = record1[10]
        helper2 = record2[10]
        get_display = dd.get_string_display
    elif attr_num == '4':
        # last name
        helper1 = record1[11]
        helper2 = record2[11]
        get_display = dd.get_string_display
    elif attr_num == '6':
        # DoB
        helper1 = record1[12]
        helper2 = record2[12]
        get_display = dd.get_date_display
    elif attr_num == '7':
        # sex
        helper1 = record1[13]
        helper2 = record2[13]
        get_display = dd.get_character_display
    elif attr_num == '8':
        # race
        helper1 = record1[14]
        helper2 = record2[14]
        get_display = dd.get_character_display

    attr_full = get_display(attr1=attr1, attr2=attr2, helper1=helper1, helper2=helper2, attribute_mode='full')
    attr_partial = get_display(attr1=attr1, attr2=attr2, helper1=helper1, helper2=helper2, attribute_mode='partial')
    attr_masked = get_display(attr1=attr1, attr2=attr2, helper1=helper1, helper2=helper2, attribute_mode='masked')

    ret = dict()
    if mode == 'masked':
        if(attr_partial[0] == attr_masked[0] and attr_partial[1] == attr_masked[1]):
            ret = {"value1": attr_full[0], "value2": attr_full[1], "mode": "full"}
        else:
            ret = {"value1": attr_partial[0], "value2": attr_partial[1], "mode": "partial"}
    elif mode == 'partial':
        ret = {"value1": attr_full[0], "value2": attr_full[1], "mode": "full"}

    # get character disclosed percentage
    cdp_previous_attr1 = 0
    cdp_previous_attr2 = 0
    if mode == 'partial':
        cdp_previous_attr1 = dd.get_character_disclosed_num(helper1)
        cdp_previous_attr2 = dd.get_character_disclosed_num(helper2)

    cdp_post_attr1 = len(attr1)
    cdp_post_attr2 = len(attr2)
    if ret['mode'] == 'partial':
        cdp_post_attr1 = dd.get_character_disclosed_num(helper1)
        cdp_post_attr2 = dd.get_character_disclosed_num(helper2)
    cdp_increment = (cdp_post_attr1 - cdp_previous_attr1) + (cdp_post_attr2 - cdp_previous_attr2)

    # atom operation!
    mindfil_disclosed_characters_key = session['user_cookie'] + '_mindfil_disclosed_characters'
    r.incrby(mindfil_disclosed_characters_key, cdp_increment)
    mindfil_total_characters_key = session['user_cookie'] + '_mindfil_total_characters'
    cdp = 100.0*int(r.get(mindfil_disclosed_characters_key))/int(r.get(mindfil_total_characters_key))
    ret['cdp'] = round(cdp, 1)

    return jsonify(ret)


@app.route('/select')
def select_panel():
    return render_template('select_panel2.html')


@app.route('/test')
def test():
    return render_template('bootstrap_test.html')


@app.route('/next', methods=['GET', 'POST'])
def next():
    sequence = CONFIG['sequence']
    state = session['state'] + 1
    session['state'] += 1

    return redirect(url_for(sequence[state]))


app.secret_key = 'a9%z$/`9h8FMnh893;*g783'