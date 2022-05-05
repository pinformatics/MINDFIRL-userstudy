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
    #return render_template('instruction_ppirl.html')
    return redirect("https://vidal.tamu.edu/mindfirl-userstudy")


@app.route('/practice/base_mode')
@state_machine('show_pratice_base_mode')
def show_pratice_base_mode():
    pairs = dl.load_data_from_csv('data/practice_base_mode.csv')
    pairs_formatted = dd.format_data(pairs, 'base')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = (len(pairs)/2)*[7*['']]
    return render_template('record_linkage_d.html', data=data, icons=icons, title='Section 1: practice', thisurl='/practice/base_mode', page_number=5)


@app.route('/practice/full_mode')
@state_machine('show_pratice_full_mode')
def show_pratice_full_mode():
    pairs = dl.load_data_from_csv('data/practice_full_mode.csv')
    pairs_formatted = dd.format_data(pairs, 'full')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('record_linkage_d.html', data=data, icons=icons, title='Section 1: practice', thisurl='/practice/full_mode', page_number=7)


@app.route('/practice/masked_mode')
@state_machine('show_pratice_masked_mode')
def show_pratice_masked_mode():
    pairs = dl.load_data_from_csv('data/practice_masked_mode.csv')
    pairs_formatted = dd.format_data(pairs, 'masked')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('record_linkage_d.html', data=data, icons=icons, title='Section 1: practice', thisurl='/practice/masked_mode', page_number=10)


@app.route('/practice/minimum_mode')
@state_machine('show_pratice_minimum_mode')
def show_pratice_minimum_mode():
    pairs = dl.load_data_from_csv('data/practice_minimum_mode.csv')
    pairs_formatted = dd.format_data(pairs, 'minimum')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('record_linkage_d.html', data=data, icons=icons, title='Section 1: practice', thisurl='/practice/minimum_mode', page_number=12)


@app.route('/practice/moderate_mode')
@state_machine('show_pratice_moderate_mode')
def show_pratice_moderate_mode():
    pairs = dl.load_data_from_csv('data/practice_moderate_mode.csv')
    pairs_formatted = dd.format_data(pairs, 'moderate')
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = dd.generate_icon(pairs)
    return render_template('record_linkage_d.html', data=data, icons=icons, title='Section 1: practice', thisurl='/practice/moderate_mode', page_number=14)


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
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'])

    return render_template('record_linkage_ppirl.html', data=data, icons=icons, ids=ids, title='Section 2: Minimum Necessary Disclosure For Interactive record Linkage', thisurl='/record_linkage', page_number=16, delta=delta)


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

    return jsonify(ret)


@app.route('/record_linkage/next')
def show_record_linkage_next():
    current_page = int(r.get(session['user_cookie']+'_current_page'))+1
    r.incr(session['user_cookie']+'_current_page')
    is_last_page = 0
    if current_page == int(r.get(session['user_cookie'] + '_page_size'))-1:
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
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'])
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', data=data, icons=icons, ids=ids)
    ret = {
        'delta': delta_dict,
        'is_last_page': is_last_page,
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
