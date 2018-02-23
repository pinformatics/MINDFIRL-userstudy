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
import math
import data_loader as dl
import data_display as dd
import data_model as dm
import config


app = Flask(__name__)


if config.ENV == 'production':
    r = redis.from_url(os.environ.get("REDIS_URL"))
elif config.ENV == 'development':
    r = redis.Redis(host='localhost', port=6379, db=0)


# global data, this should be common across all users, not affected by multiple process
DATASET = dl.load_data_from_csv('data/section2.csv')
DATA_PAIR_LIST = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/ppirl.csv'))
DATA_TUTORIAL1 = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/tutorial1.csv'))
DATA_inc3 = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/tutorial_sec3_incremental3_data.csv'))
DATA_tut3 = dm.DataPairList(data_pairs = dl.load_data_from_csv('data/tutorial3.csv'))
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
    print(session['user_cookie'])
    user_data_key = session['user_cookie'] + '_user_data'
    r.set(user_data_key, 'Session start time: ' + str(time.time()) + ';\n')

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

# def set_session_state(function_name):
#     sequence = config.SEQUENCE
#     for i in range(len(sequence)):
#         if sequence[i] == function_name:
#             session['state'] = i
#             break

# @app.route('/tutorial/')
# @app.route('/tutorial/rl/')
# @app.route('/tutorial/<tutorial_section>/<page>')
# # @state_machine('show_tutorial_'+page)
# def show_tutorial_id_1(tutorial_section = "rl", page = "id_1"):
#     pairs = dl.load_data_from_csv('data/tutorial/rl/id_1.csv')
#     pairs_formatted = dd.format_data(pairs, 'full')
#     data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
#     icons = dd.generate_icon(pairs)
#     return render_template('tutorial/rl/id_1.html', data=data, icons=icons, title='Section 1: practice', thisurl='/tutorial/rl/id_1', page_number=5)


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

# @app.route('/practice/full_mode')
# @state_machine('show_pratice_full_mode')
# def show_pratice_full_mode():
#     pairs = dl.load_data_from_csv('data/practice_full_mode.csv')
#     pairs_formatted = dd.format_data(pairs, 'full')
#     data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
#     icons = dd.generate_icon(pairs)
#     return render_template('record_linkage_d.html', data=data, icons=icons, title='Practice 1', thisurl='/practice/full_mode', page_number=7)


# @app.route('/practice/masked_mode')
# @state_machine('show_pratice_masked_mode')
# def show_pratice_masked_mode():
#     pairs = dl.load_data_from_csv('data/practice_masked_mode.csv')
#     pairs_formatted = dd.format_data(pairs, 'masked')
#     data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
#     icons = dd.generate_icon(pairs)
#     return render_template('record_linkage_d.html', data=data, icons=icons, title='Section 1: practice', thisurl='/practice/masked_mode', page_number=10)


# @app.route('/practice/minimum_mode')
# @state_machine('show_pratice_minimum_mode')
# def show_pratice_minimum_mode():
#     pairs = dl.load_data_from_csv('data/practice_minimum_mode.csv')
#     pairs_formatted = dd.format_data(pairs, 'minimum')
#     data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
#     icons = dd.generate_icon(pairs)
#     return render_template('record_linkage_d.html', data=data, icons=icons, title='Section 1: practice', thisurl='/practice/minimum_mode', page_number=12)


# @app.route('/practice/moderate_mode')
# @state_machine('show_pratice_moderate_mode')
# def show_pratice_moderate_mode():
#     pairs = dl.load_data_from_csv('data/practice_moderate_mode.csv')
#     pairs_formatted = dd.format_data(pairs, 'moderate')
#     data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
#     icons = dd.generate_icon(pairs)
#     return render_template('record_linkage_d.html', data=data, icons=icons, title='Section 1: practice', thisurl='/practice/moderate_mode', page_number=14)


@app.route('/tutorial/<tutorial_section>/<page>/grading')
def grade_pratice_full_mode(tutorial_section, page):
    # data_file = 'practice_' + str(table_mode) + '.csv'
    print "HIIIIIIIIIIIIIIIIIIII",tutorial_section

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

    return render_template('record_linkage_ppirl.html', data=data, icons=icons, ids=ids, title='Section 1', thisurl='/record_linkage', page_number="1/6", delta=delta)


@app.route('/thankyou')
@state_machine('show_thankyou')
def show_thankyou():
    user_data_key = session['user_cookie'] + '_user_data'
    r.append(user_data_key, 'Session end time: '+str(time.time())+';\n')
    user_data = r.get(user_data_key)
    dl.save_data_to_json('data/saved/'+str(session['user_cookie'])+'.json', user_data)

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
    if session['state'] == 5:
        working_data = DATA_TUTORIAL1
    else:
        working_data = DATA_PAIR_LIST

    id1 = request.args.get('id1')
    id2 = request.args.get('id2')
    mode = request.args.get('mode')

    pair_num = str(id1.split('-')[0])
    attr_num = str(id1.split('-')[2])

    pair_id = int(pair_num)
    attr_id = int(attr_num)

    pair = working_data.get_data_pair(pair_id)
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

    # TODO: assert the mode is consistent with the display_mode in redis

    """ no character disclosed percentage now
    for character disclosure percentage, see branch ELSI
    """

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
        logging.error('Error: invalid display status.')

    display_status1 = list()
    display_status2 = list()
    key1_prefix = session['user_cookie'] + '-' + pair_num + '-1-'
    key2_prefix = session['user_cookie'] + '-' + pair_num + '-2-'
    for attr_i in range(6):
        display_status1.append(r.get(key1_prefix + str(attr_i)))
        display_status2.append(r.get(key2_prefix + str(attr_i)))

    old_KAPR = dm.get_KAPR_for_dp(DATASET, pair, old_display_status1, 2*working_data.size())
    KAPR = dm.get_KAPR_for_dp(DATASET, pair, display_status1, 2*working_data.size())
    KAPRINC = KAPR - old_KAPR
    KAPR_key = session['user_cookie'] + '_KAPR'
    overall_KAPR = float(r.get(KAPR_key))
    overall_KAPR += KAPRINC
    r.incrbyfloat(KAPR_key, KAPRINC)
    ret['KAPR'] = round(100*overall_KAPR, 1)

    # refresh the delta of KAPR
    new_delta_list = dm.KAPR_delta(DATASET, pair, display_status1, 2*working_data.size())
    ret['new_delta'] = new_delta_list

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


@app.route('/select')
def select_panel():
    return render_template('select_panel2.html')


@app.route('/test')
def test():
    return render_template('bootstrap_test.html')


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

@app.route('/tutorial_sec3_start')
@state_machine('show_tutorial_sec3_start')
def show_tutorial_sec3_start():
    return render_template('tutorial_sec3_start.html')



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



@app.route('/tutorial_sec3_clickable')
@state_machine('show_tutorial_sec3_clickable')
def show_tutorial_sec3_clickable():
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

    DATASET_T = dl.load_data_from_csv('data/tutorial1.csv')
    # print DATASET_T
    # get the delta information
    delta = list()
    for i in range(1):
        data_pair = DATA_TUTORIAL1.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET_T, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_TUTORIAL1.size())

    return render_template('tutorial_sec3_clickable.html', data=data, icons=icons, ids=ids, title='Tutorial 3', thisurl='/tutorial_sec3_clickable', page_number=" ", delta=delta)

@app.route('/tutorial_sec3_incremental3')
@state_machine('show_tutorial_sec3_incremental3')
def show_tutorial_sec3_incremental3():
    pairs_formatted =  DATA_inc3.get_data_display('masked')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = DATA_inc3.get_icons()
    ids_list = DATA_inc3.get_ids()
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
        data_pair = DATA_inc3.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_inc3.size())

    return render_template('tutorial_sec3_incremental3.html', data=data, icons=icons, ids=ids, title='Tutorial 3', thisurl='/tutorial_sec3_clickable', page_number=" ", delta=delta)


@app.route('/tutorial_sec3_incremental1')
@state_machine('show_tutorial_sec3_incremental1')
def show_tutorial_sec3_incremental1():
    return render_template('tutorial_sec3_incremental1.html')


@app.route('/tutorial_sec3_incremental2')
@state_machine('show_tutorial_sec3_incremental2')
def show_tutorial_sec3_incremental2():
    return render_template('tutorial_sec3_incremental2.html')

@app.route('/tutorial_sec3_howto')
@state_machine('show_tutorial_sec3_howto')
def show_tutorial_sec3_howto():
    return render_template('tutorial_sec3_howto.html')

@app.route('/tutorial_sec3_howto2')
@state_machine('show_tutorial_sec3_howto2')
def show_tutorial_sec3_howto2():
    return render_template('tutorial_sec3_howto2.html')

@app.route('/tutorial_sec3_prepractice')
@state_machine('show_tutorial_sec3_prepractice')
def show_tutorial_sec3_prepractice():
    return render_template('tutorial_sec3_prepractice.html')

    

@app.route('/tutorial_sec3_decision_making')
@state_machine('show_tutorial_sec3_decision_making')
def show_tutorial_sec3_decision_making():
    return render_template('tutorial_sec3_decision_making.html')


@app.route('/tutorial_sec3_privacy_budget_vid')
@state_machine('show_tutorial_sec3_privacy_budget_vid')
def show_tutorial_sec3_privacy_budget_vid():
    return render_template('tutorial_sec3_privacy_budget_vid.html')


@app.route('/tutorial_sec3_practice')
@state_machine('show_tutorial_sec3_practice')
def show_tutorial_sec3_practice():
    pairs_formatted = DATA_tut3.get_data_display('masked')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = DATA_tut3.get_icons()
    ids_list = DATA_tut3.get_ids()
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
        data_pair = DATA_tut3.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*DATA_tut3.size())

    return render_template('tutorial_sec3_practice.html', data=data, icons=icons, ids=ids, title='Practice 3 ', thisurl='/tutorial_sec3_practice', page_number=" ", delta=delta)

