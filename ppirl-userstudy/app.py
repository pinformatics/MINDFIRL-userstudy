from flask import Flask, render_template, redirect, url_for, session, jsonify, request, g
from flask_mail import Mail, Message
from functools import wraps
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
from global_data import *



app = Flask(__name__)
app.debug = False
app.secret_key = 'a9%z$/`9h8FMnh893;*g783'

app.config.from_pyfile('email_config.py')
mail = Mail(app)


if not r.exists('user_id_generator'):
    r.set('user_id_generator', 0)


def state_machine(function_name):
    def wrapper(f):
        @wraps(f)
        def inner_wrapper(*args, **kwargs):
            sequence = config.SEQUENCE
            for i in range(len(sequence)):
                if sequence[i] == function_name:
                    session['state'] = i
                    break
            return f(*args, **kwargs)
        return inner_wrapper
    return wrapper


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
def show_record_linkages():
    session['user_cookie'] = hashlib.sha224("salt12138" + str(time.time()) + '.' + str(randint(1,10000))).hexdigest()
    user_data_key = session['user_cookie'] + '_user_data'
    user_id = r.incr('user_id_generator')
    session['user_id'] = user_id
    data = 'type: user_id,id: ' + str(user_id) + ';\n'
    data += 'type: session_start,timestamp: ' + str(time.time()) + ';\n'
    r.set(user_data_key, data)

    return redirect(url_for('show_introduction'))


@app.route('/introduction')
@state_machine('show_introduction')
def show_introduction():
    return render_template('introduction.html', uid=str(session['user_id']))


@app.route('/introduction2')
@state_machine('show_introduction2')
def show_introduction2():
    return render_template('introduction2.html', uid=str(session['user_id']))

@app.route('/tutorial/')
@app.route('/tutorial/rl/')
@state_machine('show_tutorial_rl_pdf')
def show_tutorial_rl_pdf():
    return render_template('tutorial/rl/tutorial_pdf.html')


@app.route('/tutorial/privacy')
@state_machine('show_tutorial_privacy_pdf')
def show_tutorial_privacy_pdf():
    return render_template('tutorial/privacy/tutorial_pdf.html')


@app.route('/instructions/ppirl')
@state_machine('show_instruction_ppirl')
def show_instruction_ppirl():
    return render_template('instruction_ppirl.html')


@app.route('/tutorial/rl/id')
@app.route('/tutorial/rl/id_1')
@state_machine('show_tutorial_rl_id_1')
def show_tutorial_rl_id_1():
    pairs = dl.load_data_from_csv('data/tutorial/rl/id_1.csv')
    pairs_formatted = dd.format_data(pairs, 'full')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('tutorial/rl/id_1.html', data=data, icons=icons, title='Section 1: practice', thisurl='/tutorial/rl/id_1', page_number=5)

@app.route('/tutorial/rl/id_2')
@state_machine('show_tutorial_rl_id_2')
def show_tutorial_rl_id_2():
    return render_template('tutorial/rl/id_2.html')

@app.route('/tutorial/rl/id_3')
@state_machine('show_tutorial_rl_id_3')
def show_tutorial_rl_id_3():
    pairs = dl.load_data_from_csv('data/tutorial/rl/id_3.csv')
    pairs_formatted = dd.format_data(pairs, 'full')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('tutorial/rl/id_3.html', data=data, icons=icons, title='Section 1: practice', thisurl='/tutorial/rl/id_3',  page_number=5)

@app.route('/tutorial/rl/twin')
@state_machine('show_tutorial_rl_twin')
def show_tutorial_rl_twin():
    pairs = dl.load_data_from_csv('data/tutorial/rl/twin.csv')
    pairs_formatted = dd.format_data(pairs, 'full')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('tutorial/rl/twin.html', data=data, icons=icons, title='Section 1: practice', thisurl='/tutorial/rl/twin',  page_number=5)

@app.route('/tutorial/rl/dup')
@state_machine('show_tutorial_rl_dup')
def show_tutorial_rl_dup():
    pairs = dl.load_data_from_csv('data/tutorial/rl/dup.csv')
    pairs_formatted = dd.format_data(pairs, 'full')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('tutorial/rl/dup.html', data=data, icons=icons, title='Section 1: practice', thisurl='/tutorial/rl/dup',  page_number=5)

@app.route('/tutorial/rl/missing')
@state_machine('show_tutorial_rl_missing')
def show_tutorial_rl_missing():
    pairs = dl.load_data_from_csv('data/tutorial/rl/missing.csv')
    pairs_formatted = dd.format_data(pairs, 'full')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('tutorial/rl/missing.html', data=data, icons=icons, title='Section 1: practice', thisurl='/tutorial/rl/missing',  page_number=5)

@app.route('/tutorial/rl/freq')
@state_machine('show_tutorial_rl_freq')
def show_tutorial_rl_freq():
    pairs = dl.load_data_from_csv('data/tutorial/rl/freq.csv')
    pairs_formatted = dd.format_data(pairs, 'full')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('tutorial/rl/freq.html', data=data, icons=icons, title='Section 1: practice', thisurl='/tutorial/rl/freq',  page_number=5)

@app.route('/tutorial/privacy/practice')
@state_machine('show_tutorial_privacy_practice')
def show_tutorial_privacy_practice():
    pairs = dl.load_data_from_csv('data/tutorial/privacy/practice.csv')
    pairs_formatted = dd.format_data(pairs, 'masked')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('tutorial/privacy/practice.html', data=data, icons=icons, title='Section 2: practice', thisurl='/tutorial/privacy/practice',  page_number=5)

@app.route('/tutorial/<tutorial_section>/<page>/grading')
def grade_pratice_full_mode(tutorial_section, page):
    # print 'hi'
    # data_file = 'practice_' + str(table_mode) + '.csv'
    data_file = 'data/tutorial/' + str(tutorial_section) + "/" + str(page) + '.csv'
    pairs = dl.load_data_from_csv(data_file)
    # print pairs
    ret = list()
    responses = request.args.get('response').split(',')
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
            ret.append('<h5>' + ", ".join(pairs[i][18:]) + '</h5>')
            all_correct = False
    if all_correct:
        ret.append('<h5>Good job!</h5>')
    # print ret
    return jsonify(result=ret)


@app.route('/ppirl_tutorial1')
@state_machine('show_ppirl_tutorial1')
def show_ppirl_tutorial1():
    pairs_formatted = DATA_TUTORIAL1.get_data_display('masked')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = DATA_TUTORIAL1.get_icons()
    ids_list = DATA_TUTORIAL1.get_ids()
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = session['user_cookie'] + '_KAPR'
    r.set(KAPR_key, 0)

    # set the user-display-status as masked for all cell
    attribute_size = 6
    for id1 in ids_list:
        for i in range(attribute_size):
            key = session['user_cookie'] + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    delta = list()
    for i in range(len(icons)):
        data_pair = DATA_TUTORIAL1.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_TUTORIAL1.size())

    return render_template('tutorial1.html', data=data, icons=icons, ids=ids, title='Practice 2', thisurl='/ppirl_tutorial1', page_number=" ", delta=delta)


@app.route('/record_linkage')
@state_machine('show_record_linkage_task')
def show_record_linkage_task():
    working_data = get_main_section_data(session['user_id'], 1)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()
    page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
    page_size_key = session['user_cookie'] + '_page_size'
    r.set(page_size_key, str(page_size))
    current_page_key = session['user_cookie'] + '_current_page'
    r.set(current_page_key, '0')

    pairs_formatted = working_data.get_data_display('masked')[0:2*dp_size]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[0:dp_size]
    ids_list = working_data.get_ids()[0:2*dp_size]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = session['user_cookie'] + '_KAPR'
    r.set(KAPR_key, 0)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = session['user_cookie'] + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    delta = list()
    for i in range(dp_size):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.size())

    if config.KAPR_LIMIT == 'moderate':
        kapr_limit = dm.get_kaprlimit(DATASET, working_data, 'moderate')
    elif type(config.KAPR_LIMIT) is int or type(config.KAPR_LIMIT) is float:
        if config.KAPR_LIMIT > 0 and config.KAPR_LIMIT <= 100:
            kapr_limit = config.KAPR_LIMIT
        else:
            kapr_limit = 0
    else:
        kapr_limit = 0

    kapr_limit = config.KAPR_LIMIT_FACTOR * kapr_limit

    r.set(session['user_cookie']+'section1_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', data=data, icons=icons, ids=ids, title='Section 1', thisurl='/record_linkage', page_number="1/6", delta=delta, kapr_limit = kapr_limit, uid=str(session['user_id']))


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


@app.route('/record_linkage/next')
def show_record_linkage_next():
    working_data = get_main_section_data(session['user_id'], 1)

    current_page = int(r.get(session['user_cookie']+'_current_page'))+1
    r.incr(session['user_cookie']+'_current_page')
    page_size = int(r.get(session['user_cookie'] + '_page_size'))
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display('masked')[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = session['user_cookie'] + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    #delta = dm.get_delta_for_dataset(DATASET, working_data.get_raw_data()[12:])
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.size())
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', data=data, icons=icons, ids=ids, pair_num_base=6*current_page+1)
    ret = {
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1)+'/'+str(page_size),
        'page_content': page_content
    }
    return jsonify(ret)


@app.route('/section2')
@state_machine('show_section2')
def show_section2():
    """
    section 2 contains 300 questions. The students don't need to finish them all, it just for those who 
    finish section 1 very fast.
    """
    working_data = get_main_section_data(session['user_id'], 2)

    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()
    page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
    page_size_key = session['user_cookie'] + '_section2_page_size'
    r.set(page_size_key, str(page_size))
    current_page_key = session['user_cookie'] + '_section2_current_page'
    r.set(current_page_key, '0')

    pairs_formatted = working_data.get_data_display('masked')[0:2*dp_size]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[0:dp_size]
    ids_list = working_data.get_ids()[0:2*dp_size]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # percentage of character disclosure
    """
    mindfil_total_characters_key = session['user_cookie'] + '_mindfil_total_characters'
    r.set(mindfil_total_characters_key, total_characters)
    mindfil_disclosed_characters_key = session['user_cookie'] + '_mindfil_disclosed_characters'
    r.set(mindfil_disclosed_characters_key, 0)
    """

    # KAPR - K-Anonymity privacy risk
    KAPR_key = session['user_cookie'] + '_KAPR'
    r.set(KAPR_key, 0)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = session['user_cookie'] + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    delta = list()
    for i in range(dp_size):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET2, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*dp_list_size)

    return render_template('record_linkage_ppirl.html', data=data, icons=icons, ids=ids, title='Section 2', thisurl='/section2', page_number="1", delta=delta, kapr_limit=0, uid=str(session['user_id']))


@app.route('/section2/next')
def show_section2_next():
    working_data = get_main_section_data(session['user_id'], 2)

    dp_list_size = working_data.get_size()
    current_page = int(r.get(session['user_cookie']+'_section2_current_page'))+1
    r.incr(session['user_cookie']+'_section2_current_page')
    page_size = int(r.get(session['user_cookie'] + '_section2_page_size'))
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display('masked')[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = session['user_cookie'] + '-' + id1[i]
            r.set(key, 'M')

    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET2, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*dp_list_size)
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', data=data, icons=icons, ids=ids, pair_num_base=6*current_page+1)
    ret = {
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1),
        'page_content': page_content
    }
    return jsonify(ret)


@app.route('/next', methods=['GET', 'POST'])
def next():
    sequence = config.SEQUENCE
    state = session['state'] + 1
    session['state'] += 1

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


@app.route('/section1_guide')
@state_machine('show_section1_guide')
def show_section1_guide():
    return render_template('section1_guide.html', uid=str(session['user_id']))


@app.route('/section2_guide')
@state_machine('show_section2_guide')
def show_section2_guide():
    # grading section 1
    user_data_key = session['user_cookie'] + '_user_data'
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 1))
    performance1 = 'type:performance1,content:' + str(result[0]) + ' out of ' + str(result[1]) + ';\n'
    r.append(user_data_key, performance1)

    return render_template('section2_guide.html', uid=str(session['user_id']))


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


@app.route('/tutorial/clickable')
@state_machine('show_tutorial_clickable_start')
def show_tutorial_clickable_start():
    return render_template('tutorial/clickable/start.html')


@app.route('/tutorial/clickable/demo')
@state_machine('show_tutorial_clickable_demo')
def show_tutorial_clickable_demo():
    pairs_formatted = DATA_CLICKABLE_DEMO.get_data_display('masked')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = DATA_CLICKABLE_DEMO.get_icons()
    ids_list = DATA_CLICKABLE_DEMO.get_ids()
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = session['user_cookie'] + '_KAPR'
    r.set(KAPR_key, 0)

    # set the user-display-status as masked for all cell
    attribute_size = 6
    for id1 in ids_list:
        for i in range(attribute_size):
            key = session['user_cookie'] + '-' + id1[i]
            r.set(key, 'M')
    
    delta = list()
    for i in range(1):
        data_pair = DATA_CLICKABLE_DEMO.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET_TUTORIAL, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_CLICKABLE_DEMO.size())

    return render_template('tutorial/clickable/demo.html', data=data, icons=icons, ids=ids, title='Tutorial 3', thisurl='/tutorial/clickable/demo', page_number=" ", delta=delta, kapr_limit = 100)


@app.route('/tutorial/clickable/incremental1')
@state_machine('show_tutorial_clickable_incremental1')
def show_tutorial_clickable_incremental1():
    return render_template('tutorial/clickable/incremental1.html')


@app.route('/tutorial/clickable/incremental2')
@state_machine('show_tutorial_clickable_incremental2')
def show_tutorial_clickable_incremental2():
    return render_template('tutorial/clickable/incremental2.html')

@app.route('/tutorial/clickable/whatopen')
@state_machine('show_tutorial_clickable_whatopen')
def show_tutorial_clickable_whatopen():
    return render_template('/tutorial/clickable/whatopen.html')

@app.route('/tutorial/clickable/whenidentical')
@state_machine('show_tutorial_clickable_whenidentical')
def show_tutorial_clickable_whenidentical():
    return render_template('/tutorial/clickable/whenidentical.html')

@app.route('/tutorial/clickable/whatnotopen')
@state_machine('show_tutorial_clickable_whatnotopen')
def show_tutorial_clickable_whatnotopen():
    return render_template('/tutorial/clickable/whatnotopen.html')

@app.route('/tutorial/clickable/decision_making_1')
@state_machine('show_tutorial_clickable_decision_making_1')
def show_tutorial_clickable_decision_making_1():
    return render_template('tutorial/clickable/decision_making_1.html')

@app.route('/tutorial/clickable/decision_making_2')
@state_machine('show_tutorial_clickable_decision_making_2')
def show_tutorial_clickable_decision_making_2():
    return render_template('tutorial/clickable/decision_making_2.html')

@app.route('/tutorial/clickable/decision_making_3')
@state_machine('show_tutorial_clickable_decision_making_3')
def show_tutorial_clickable_decision_making_3():
    return render_template('tutorial/clickable/decision_making_3.html')

@app.route('/tutorial/clickable/decision_making_4')
@state_machine('show_tutorial_clickable_decision_making_4')
def show_tutorial_clickable_decision_making_4():
    return render_template('tutorial/clickable/decision_making_4.html')

@app.route('/tutorial/clickable/decision_making_5')
@state_machine('show_tutorial_clickable_decision_making_5')
def show_tutorial_clickable_decision_making_5():
    return render_template('tutorial/clickable/decision_making_5.html')

@app.route('/tutorial/clickable/decision_making_demo')
@state_machine('show_tutorial_clickable_decision_making_demo')
def show_tutorial_clickable_decision_making_demo():
    pairs_formatted =  DATA_DM_DEMO.get_data_display('masked')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = DATA_DM_DEMO.get_icons()
    ids_list = DATA_DM_DEMO.get_ids()
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = session['user_cookie'] + '_KAPR'
    r.set(KAPR_key, 0)

    # set the user-display-status as masked for all cell
    attribute_size = 6
    for id1 in ids_list:
        for i in range(attribute_size):
            key = session['user_cookie'] + '-' + id1[i]
            r.set(key, 'M')

    # DATASET_T = dl.load_data_from_csv('data/tutorial1.csv')
    # print DATASET_T
    # get the delta information
    delta = list()
    for i in range(DATA_DM_DEMO.size()):
        data_pair = DATA_DM_DEMO.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET_TUTORIAL, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_DM_DEMO.size())

    # kapr_limit = dm.get_kaprlimit(DATASET_TUTORIAL, DATA_DM_DEMO, 'moderate')
    # r.set(session['user_cookie']+'tutorial_dmdemo_kapr_limit', kapr_limit)

    return render_template('tutorial/clickable/decision_making_demo.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Tutorial 3', 
        thisurl='/tutorial/clickable/decision_making_demo', 
        page_number=" ", 
        delta=delta,
        kapr_limit=100)



@app.route('/tutorial/clickable/budgetmeter')
@state_machine('show_tutorial_clickable_budgetmeter')
def show_tutorial_clickable_budgetmeter():
    return render_template('tutorial/clickable/budgetmeter.html')

@app.route('/tutorial/clickable/budgetlimit')
@state_machine('show_tutorial_clickable_budgetlimit')
def show_tutorial_clickable_budgetlimit():
    return render_template('tutorial/clickable/budgetlimit.html')

@app.route('/tutorial/clickable/budgeting')
@state_machine('show_tutorial_clickable_budgeting')
def show_tutorial_clickable_budgeting():
    return render_template('tutorial/clickable/budgeting.html')


@app.route('/tutorial/clickable/budgetmeter_vid')
@state_machine('show_tutorial_clickable_budgetmeter_vid')
def show_tutorial_clickable_budgetmeter_vid():
    return render_template('tutorial/clickable/budgetmeter_vid.html')


@app.route('/tutorial/clickable/prepractice')
@state_machine('show_tutorial_clickable_prepractice')
def show_tutorial_clickable_prepractice():
    return render_template('tutorial/clickable/prepractice.html')

    

@app.route('/tutorial/clickable/practice')
@state_machine('show_tutorial_clickable_practice')
def show_tutorial_clickable_practice():
    pairs_formatted = DATA_CLICKABLE_PRACTICE.get_data_display('masked')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = DATA_CLICKABLE_PRACTICE.get_icons()
    ids_list = DATA_CLICKABLE_PRACTICE.get_ids()
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = session['user_cookie'] + '_KAPR'
    r.set(KAPR_key, 0)

    # set the user-display-status as masked for all cell
    attribute_size = 6
    for id1 in ids_list:
        for i in range(attribute_size):
            key = session['user_cookie'] + '-' + id1[i]
            r.set(key, 'M')

    # DATASET_T = dl.load_data_from_csv('data/tutorial1.csv')
    # print DATASET_T
    # get the delta information
    delta = list()
    for i in range(DATA_CLICKABLE_PRACTICE.size()):
        data_pair = DATA_CLICKABLE_PRACTICE.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET_TUTORIAL, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_CLICKABLE_PRACTICE.size())

    # kapr_limit = dm.get_kaprlimit(DATASET_TUTORIAL, DATA_CLICKABLE_PRACTICE, 'moderate')
    # r.set(session['user_cookie']+'tutorial_practice_kapr_limit', kapr_limit)

    return render_template('tutorial/clickable/practice.html', 
        data=data, icons=icons, ids=ids, title='Practice 3 ', 
        thisurl='/tutorial/clickable/practice', page_number=" ", delta=delta, kapr_limit = 20)


@app.route('/section1_start')
@state_machine('show_section1_startpage')
def show_section1_startpage():
    return render_template('section1_start.html')


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
        
