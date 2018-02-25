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
import config



app = Flask(__name__)

app.config.from_pyfile('email_config.py')
mail = Mail(app)


if config.ENV == 'production':
    r = redis.from_url(os.environ.get("REDIS_URL"))
elif config.ENV == 'development':
    r = redis.Redis(host='localhost', port=6379, db=0)


# global data, this should be common across all users, not affected by multiple process
# this is the full database for section 1
DATASET = dl.load_data_from_csv('data/section1_full.csv')
# this is the full database for section 2
DATASET2 = dl.load_data_from_csv('data/section2.csv')
DATA_PAIR_LIST = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/ppirl.csv'))

DATA_CLICKABLE_DEMO = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/tutorial/clickable/demo.csv'))

DATA_SECTION2 = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/section2.csv'))
DATA_TUTORIAL1 = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/tutorial1.csv'))

DATA_DM_DEMO = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/tutorial/clickable/decision_making_demo.csv'))
# DATA_TUTORIAL1 = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/tutorial1.csv'))

DATA_CLICKABLE_PRACTICE = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/tutorial/clickable/practice.csv'))
# DATA_inc3 = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/video_decisonmaking.csv'))
# DATA_PAIR_LIST = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/tutorial_sec3_incremental3_data.csv'))

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


@app.route('/')
def show_record_linkages():
    session['user_cookie'] = hashlib.sha224("salt12138" + str(time.time()) + '.' + str(randint(1,10000))).hexdigest()
    user_data_key = session['user_cookie'] + '_user_data'
    r.set(user_data_key, 'type: session_start,timestamp: ' + str(time.time()) + ';\n')

    return redirect(url_for('show_introduction'))


@app.route('/introduction')
@state_machine('show_introduction')
def show_introduction():
    return render_template('introduction.html')


@app.route('/introduction2')
@state_machine('show_introduction2')
def show_introduction2():
    return render_template('introduction2.html')

@app.route('/tutorial/')
@app.route('/tutorial/rl/')
@state_machine('show_tutorial_rl_pdf')
def show_tutorial_rl_pdf():
    return render_template('tutorial/rl/tutorial_pdf.html')


@app.route('/tutorial/privacy')
@state_machine('show_tutorial_privacy_pdf')
def show_tutorial_privacy_pdf():
    return render_template('tutorial/privacy/tutorial_pdf.html')


# @app.route('/instructions/base_mode')
# @state_machine('show_instruction_base_mode')
# def show_instruction_base_mode():
#     return render_template('instruction_base_mode.html')


# @app.route('/instructions/full_mode')
# @state_machine('show_instruction_full_mode')
# def show_instruction_full_mode():
#     return render_template('instruction_full_mode.html')


# @app.route('/instructions/masked_mode')
# @state_machine('show_instruction_masked_mode')
# def show_instruction_masked_mode():
#     return render_template('instruction_masked_mode.html')


# @app.route('/instructions/minimum_mode')
# @state_machine('show_instruction_minimum_mode')
# def show_instruction_minimum_mode():
#     return render_template('instruction_minimum_mode.html')


# @app.route('/instructions/moderate_mode')
# @state_machine('show_instruction_moderate_mode')
# def show_instruction_moderate_mode():
#     return render_template('instruction_moderate_mode.html')


# @app.route('/instructions/encrypted_mode')
# @state_machine('show_instruction_encrypted_mode')
# def show_instruction_encrypted_mode():
#     return render_template('instruction_encrypted_mode.html')


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
    # data_file = 'practice_' + str(table_mode) + '.csv'
    data_file = 'data/tutorial/' + str(tutorial_section) + "/" + str(page) + '.csv'
    pairs = dl.load_data_from_csv(data_file)
    print pairs
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
            ret.append('<div>' + pairs[i][18] + '</div>')
            all_correct = False
    if all_correct:
        ret.append('<div>Good job!</div>')
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
    #pairs = dl.load_data_from_csv('data/ppirl.csv')
    #total_characters = dd.get_total_characters(pairs)
    #pairs = pairs[0:12]

    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = DATA_PAIR_LIST.get_size()
    page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
    page_size_key = session['user_cookie'] + '_page_size'
    r.set(page_size_key, str(page_size))
    current_page_key = session['user_cookie'] + '_current_page'
    r.set(current_page_key, '0')

    pairs_formatted = DATA_PAIR_LIST.get_data_display('masked')[0:2*dp_size]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = DATA_PAIR_LIST.get_icons()[0:dp_size]
    ids_list = DATA_PAIR_LIST.get_ids()[0:2*dp_size]
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
        data_pair = DATA_PAIR_LIST.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_PAIR_LIST.size())

    return render_template('record_linkage_ppirl.html', data=data, icons=icons, ids=ids, title='Section 1', thisurl='/record_linkage', page_number="1/6", delta=delta, kapr_limit = config.KAPR_LIMIT)


@app.route('/thankyou')
@state_machine('show_thankyou')
def show_thankyou():
    user_data_key = session['user_cookie'] + '_user_data'
    r.append(user_data_key, 'type: session_end,timestamp: '+str(time.time())+';\n')
    user_data = r.get(user_data_key)
    dl.save_data_to_json('data/saved/'+str(session['user_cookie'])+'.json', user_data)

    # send the data to email.
    msg = Message(subject='user data: ' + session['user_cookie'], body=user_data, recipients=['mindfil.ppirl@gmail.com'])
    mail.send(msg)

    # clear user data in redis
    for key in r.scan_iter("prefix:"+session['user_cookie']):
        r.delete(key)

    return render_template('thankyou.html')


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
    if session['state'] == 5:
        working_data = DATA_TUTORIAL1
        full_data = DATASET
    elif session['state'] == 7:
        working_data = DATA_PAIR_LIST
        full_data = DATASET
        kapr_limit = config.KAPR_LIMIT
    else:
        working_data = DATA_SECTION2
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
    if session['state'] == 5:
        working_data = DATA_TUTORIAL1
        full_data = DATASET
    elif session['state'] == 7:
        working_data = DATA_PAIR_LIST
        full_data = DATASET
        kapr_limit = config.KAPR_LIMIT
    else:
        working_data = DATA_SECTION2
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
    current_page = int(r.get(session['user_cookie']+'_current_page'))+1
    r.incr(session['user_cookie']+'_current_page')
    page_size = int(r.get(session['user_cookie'] + '_page_size'))
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = DATA_PAIR_LIST.get_data_display('masked')[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = DATA_PAIR_LIST.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = DATA_PAIR_LIST.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = session['user_cookie'] + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    #delta = dm.get_delta_for_dataset(DATASET, DATA_PAIR_LIST.get_raw_data()[12:])
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = DATA_PAIR_LIST.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_PAIR_LIST.size())
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', data=data, icons=icons, ids=ids)
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

    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = DATA_SECTION2.get_size()
    page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
    page_size_key = session['user_cookie'] + '_section2_page_size'
    r.set(page_size_key, str(page_size))
    current_page_key = session['user_cookie'] + '_section2_current_page'
    r.set(current_page_key, '0')

    pairs_formatted = DATA_SECTION2.get_data_display('masked')[0:2*dp_size]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = DATA_SECTION2.get_icons()[0:dp_size]
    ids_list = DATA_SECTION2.get_ids()[0:2*dp_size]
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
        data_pair = DATA_SECTION2.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET2, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*dp_list_size)

    return render_template('record_linkage_ppirl.html', data=data, icons=icons, ids=ids, title='Section 2', thisurl='/section2', page_number="1/55", delta=delta, kapr_limit=0)


@app.route('/section2/next')
def show_section2_next():
    dp_list_size = DATA_SECTION2.get_size()
    current_page = int(r.get(session['user_cookie']+'_section2_current_page'))+1
    r.incr(session['user_cookie']+'_section2_current_page')
    page_size = int(r.get(session['user_cookie'] + '_section2_page_size'))
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = DATA_SECTION2.get_data_display('masked')[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = DATA_SECTION2.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = DATA_SECTION2.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = session['user_cookie'] + '-' + id1[i]
            r.set(key, 'M')

    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = DATA_SECTION2.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET2, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*dp_list_size)
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', data=data, icons=icons, ids=ids)
    ret = {
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1)+'/'+str(page_size),
        'page_content': page_content
    }
    return jsonify(ret)


@app.route('/next', methods=['GET', 'POST'])
def next():
    sequence = config.SEQUENCE
    state = session['state'] + 1
    session['state'] += 1

    return redirect(url_for(sequence[state]))


@app.route('/pull_data')
def pull_data():
    user_data_key = session['user_cookie'] + '_user_data'
    user_data = r.get(user_data_key)
    return user_data


app.secret_key = 'a9%z$/`9h8FMnh893;*g783'



# @app.route('/ppirl_tutorial1')
# @state_machine('show_ppirl_tutorial1')
# def show_ppirl_tutorial1():
#     pairs_formatted = DATA_TUTORIAL1.get_data_display('masked')
#     data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
#     icons = DATA_TUTORIAL1.get_icons()
#     ids_list = DATA_TUTORIAL1.get_ids()
#     ids = zip(ids_list[0::2], ids_list[1::2])

#     # KAPR - K-Anonymity privacy risk
#     KAPR_key = session['user_cookie'] + '_KAPR'
#     r.set(KAPR_key, 0)

#     # set the user-display-status as masked for all cell
#     attribute_size = 6
#     for id1 in ids_list:
#         for i in range(attribute_size):
#             key = session['user_cookie'] + '-' + id1[i]
#             r.set(key, 'M')

#     # get the delta information
#     delta = list()
#     for i in range(len(icons)):
#         data_pair = DATA_TUTORIAL1.get_data_pair_by_index(i)
#         delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_TUTORIAL1.size())

#     return render_template('tutorial1.html', data=data, icons=icons, ids=ids, title='Practice 2', thisurl='/ppirl_tutorial1', page_number=" ", delta=delta)

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
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_CLICKABLE_DEMO.size())

    return render_template('tutorial/clickable/demo.html', data=data, icons=icons, ids=ids, title='Tutorial 3', thisurl='/tutorial/clickable/demo', page_number=" ", delta=delta)


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
    for i in range(1):
        data_pair = DATA_DM_DEMO.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_DM_DEMO.size())

    return render_template('tutorial/clickable/decision_making_demo.html', data=data, icons=icons, ids=ids, title='Tutorial 3', thisurl='/tutorial/clickable/clickable/decision_making_demo', page_number=" ", delta=delta)



@app.route('/tutorial/clickable/budgetmeter')
@state_machine('show_tutorial_clickable_budgetmeter')
def show_tutorial_clickable_budgetmeter():
    return render_template('tutorial/clickable/budgetmeter.html')

@app.route('/tutorial/clickable/budgetlimit')
@state_machine('show_tutorial_clickable_budgetlimit')
def show_tutorial_clickable_budgetlimit():
    return render_template('tutorial/clickable/budgetlimit.html')


@app.route('/tutorial/clickable/budgetmeter_vid')
@state_machine('show_tutorial_clickable_budgetmeter_vid')
def show_tutorial_clickable_budgetmeter_vid():
    return render_template('tutorial/clickable/budgetmeter_vid.html')


@app.route('/tutorial/clickable/prepractice')
@state_machine('show_tutorial_clickable_prepractice')
def show_tutorial_clickable_prepractice():
    return render_template('tutorial/clickable/prepractice.html')

    

# @app.route('/tutorial_clickable_decision_making')
# @state_machine('show_tutorial_clickable_decision_making')
# def show_tutorial_clickable_decision_making():
#     return render_template('tutorial_clickable_decision_making.html')



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
    for i in range(1):
        data_pair = DATA_CLICKABLE_PRACTICE.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_CLICKABLE_PRACTICE.size())

    return render_template('tutorial/clickable/practice.html', data=data, icons=icons, ids=ids, title='Practice 3 ', thisurl='/tutorial_clickable_practice', page_number=" ", delta=delta)

