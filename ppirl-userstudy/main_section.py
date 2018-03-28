from flask import Blueprint, render_template, redirect, url_for, session, jsonify, request
from flask_mail import Mail, Message
import os
import time
import math
import redis
import logging
import data_loader as dl
import data_display as dd
import data_model as dm
import user_data as ud
import config
from util import state_machine
from global_data import r, DATASET, DATASET2, DATA_SECTION1, DATA_SECTION2, DATA_SECTION3, DATA_SECTION4, DATA_SECTION5, DATA_SECTION6, DATA_SECTION7, DATA_SECTION8, DATA_SECTION9, DATA_SECTION10


main_section = Blueprint('main_section', __name__, template_folder='templates')


def get_main_section_data(uid, section):
    sample = int(uid)%10
    if sample == 0:
        sample = 10
    sample -= 1

    if section == 1:
        return DATA_SECTION1[sample]
    elif section == 2:
        return DATA_SECTION2[sample]
    elif section == 3:
        return DATA_SECTION3[sample]
    elif section == 4:
        return DATA_SECTION4[sample]    
    elif section == 5:
        return DATA_SECTION5[sample]
    elif section == 6:
        return DATA_SECTION6[sample]
    elif section == 7:
        return DATA_SECTION7[sample]    
    elif section == 8:
        return DATA_SECTION8[sample]
    elif section == 9:
        return DATA_SECTION9[sample]
    elif section == 10:
        return DATA_SECTION10[sample]    




@main_section.route('/section1_guide')
@state_machine('show_section1_guide')
def show_section1_guide():
    return render_template('section1_guide.html', uid=str(session['user_id']))


@main_section.route('/record_linkage')
@state_machine('show_record_linkage_task')
def show_record_linkage_task():
    """
    section 1
    """
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    ustudy_budget = r.get(session['user_id']+'_ustudy_budget')
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(str(session['user_id']), 1)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()

    # if the user is in this section the first time, or coming back
    first_flag = True
    page_size_key = str(session['user_id']) + '_page_size'
    current_page_key = str(session['user_id']) + '_current_page'
    if (not r.get(current_page_key) is None) and (not r.get(current_page_key) == '0'):
        page_size = int(r.get(page_size_key))
        current_page = int(r.get(current_page_key))
        first_flag = False
    else:
        current_page = 0
        page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
        r.set(page_size_key, str(page_size))
        r.set(current_page_key, current_page)

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = str(session['user_id']) + '_KAPR'
    if first_flag:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    else:
        KAPR = round(100*float(r.get(KAPR_key)), 1)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.size())

    '''
    # load KAPR LIMIT from config file
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
    '''
    # load KAPR LIMIT from url parameter
    if ustudy_budget == 'moderate' or ustudy_budget == 'minimum':
        kapr_limit = dm.get_kaprlimit(DATASET, working_data, ustudy_budget)
    else:
        kapr_limit = float(ustudy_budget)
    r.set(str(session['user_id'])+'section1_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Section 1', 
        thisurl='/record_linkage', 
        page_number=str(current_page+1)+"/6", 
        delta=delta, 
        kapr = KAPR,
        kapr_limit = kapr_limit, 
        uid=str(session['user_id']),
        pair_num_base=6*current_page+1,
        ustudy_mode=ustudy_mode
    )


@main_section.route('/record_linkage/next')
def show_record_linkage_next():
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 1)

    page_size = int(r.get(str(session['user_id']) + '_page_size'))
    current_page = int(r.get(str(session['user_id'])+'_current_page'))+1
    if current_page >= page_size:
        ret = {
            'result': 'no more pages'
        }
        return jsonify(ret)
    r.incr(str(session['user_id'])+'_current_page')
    
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = str(session['user_id']) + '-' + id1[i]
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

    page_content = render_template('record_linkage_next.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        pair_num_base=6*current_page+1, 
        ustudy_mode=ustudy_mode
    )

    ret = {
        'result': 'success',
        'ustudy_mode': ustudy_mode,
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1)+'/'+str(page_size),
        'page_content': page_content
    }
    return jsonify(ret)


@main_section.route('/section2_guide')
@state_machine('show_section2_guide')
def show_section2_guide():
    user_data_key = session['user_id'] + '_user_data'
    # grading section 1
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 1))
    # saving user data
    performance1 = {
        'uid': session['user_id'],
        'type': 'performance1',
        'value': str(result[0]) + ' out of ' + str(result[1]),
        'timestamp': int(time.time()),
        'source': 'server'
    }
    r.append(user_data_key, ud.format_user_data(performance1))

    return render_template('section2_guide.html', uid=str(session['user_id']), section=2)

@main_section.route('/section3_guide')
@state_machine('show_section3_guide')
def show_section3_guide():
    user_data_key = session['user_id'] + '_user_data'
    # grading section 1
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 2))
    # saving user data
    performance2 = {
        'uid': session['user_id'],
        'type': 'performance2',
        'value': str(result[0]) + ' out of ' + str(result[1]),
        'timestamp': int(time.time()),
        'source': 'server'
    }
    r.append(user_data_key, ud.format_user_data(performance2))

    return render_template('section2_guide.html', uid=str(session['user_id']), section=3)

@main_section.route('/section4_guide')
@state_machine('show_section4_guide')
def show_section4_guide():
    user_data_key = session['user_id'] + '_user_data'
    # grading section 1
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 3))
    # saving user data
    performance3 = {
        'uid': session['user_id'],
        'type': 'performance3',
        'value': str(result[0]) + ' out of ' + str(result[1]),
        'timestamp': int(time.time()),
        'source': 'server'
    }
    r.append(user_data_key, ud.format_user_data(performance3))

    return render_template('section2_guide.html', uid=str(session['user_id']), section=4)


@main_section.route('/section5_guide')
@state_machine('show_section5_guide')
def show_section5_guide():
    user_data_key = session['user_id'] + '_user_data'
    # grading section 1
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 4))
    # saving user data
    performance4 = {
        'uid': session['user_id'],
        'type': 'performance4',
        'value': str(result[0]) + ' out of ' + str(result[1]),
        'timestamp': int(time.time()),
        'source': 'server'
    }
    r.append(user_data_key, ud.format_user_data(performance4))

    return render_template('section2_guide.html', uid=str(session['user_id']), section=5)

@main_section.route('/section6_guide')
@state_machine('show_section6_guide')
def show_section6_guide():
    user_data_key = session['user_id'] + '_user_data'
    # grading section 1
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 5))
    # saving user data
    performance5 = {
        'uid': session['user_id'],
        'type': 'performance5',
        'value': str(result[0]) + ' out of ' + str(result[1]),
        'timestamp': int(time.time()),
        'source': 'server'
    }
    r.append(user_data_key, ud.format_user_data(performance5))

    return render_template('section2_guide.html', uid=str(session['user_id']), section=6)

@main_section.route('/section7_guide')
@state_machine('show_section7_guide')
def show_section7_guide():
    user_data_key = session['user_id'] + '_user_data'
    # grading section 1
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 6))
    # saving user data
    performance6 = {
        'uid': session['user_id'],
        'type': 'performance6',
        'value': str(result[0]) + ' out of ' + str(result[1]),
        'timestamp': int(time.time()),
        'source': 'server'
    }
    r.append(user_data_key, ud.format_user_data(performance6))

    return render_template('section2_guide.html', uid=str(session['user_id']), section=7)

@main_section.route('/section8_guide')
@state_machine('show_section8_guide')
def show_section8_guide():
    user_data_key = session['user_id'] + '_user_data'
    # grading section 1
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 7))
    # saving user data
    performance7 = {
        'uid': session['user_id'],
        'type': 'performance7',
        'value': str(result[0]) + ' out of ' + str(result[1]),
        'timestamp': int(time.time()),
        'source': 'server'
    }
    r.append(user_data_key, ud.format_user_data(performance7))

    return render_template('section2_guide.html', uid=str(session['user_id']), section=8)

@main_section.route('/section9_guide')
@state_machine('show_section9_guide')
def show_section9_guide():
    user_data_key = session['user_id'] + '_user_data'
    # grading section 1
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 8))
    # saving user data
    performance8 = {
        'uid': session['user_id'],
        'type': 'performance8',
        'value': str(result[0]) + ' out of ' + str(result[1]),
        'timestamp': int(time.time()),
        'source': 'server'
    }
    r.append(user_data_key, ud.format_user_data(performance8))

    return render_template('section2_guide.html', uid=str(session['user_id']), section=9)

@main_section.route('/section10_guide')
@state_machine('show_section10_guide')
def show_section10_guide():
    user_data_key = session['user_id'] + '_user_data'
    # grading section 1
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 9))
    # saving user data
    performance9 = {
        'uid': session['user_id'],
        'type': 'performance9',
        'value': str(result[0]) + ' out of ' + str(result[1]),
        'timestamp': int(time.time()),
        'source': 'server'
    }
    r.append(user_data_key, ud.format_user_data(performance9))

    return render_template('section2_guide.html', uid=str(session['user_id']), section=10)



@main_section.route('/section2_budget')
@state_machine('show_section2_budget')
def show_section2_budget():
    return render_template('section2_budget.html', uid=str(session['user_id']))


@main_section.route('/section2')
@state_machine('show_section2')
def show_section2():
    """
    section 2 contains 300 questions. The students don't need to finish them all, it just for those who 
    finish section 1 very fast.
    """
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    ustudy_budget = r.get(session['user_id']+'_ustudy_budget')

    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(str(session['user_id']), 2)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()

    # if the user is in this section the first time, or coming back
    first_flag = True
    page_size_key = str(session['user_id']) + '_section2_page_size'
    current_page_key = str(session['user_id']) + '_section2_current_page'
    if (not r.get(current_page_key) is None) and (not r.get(current_page_key) == '0'):
        page_size = int(r.get(page_size_key))
        current_page = int(r.get(current_page_key))
        if current_page >= page_size or (current_page+1)*6 > working_data.size():
            return redirect(url_for('next'))
        first_flag = False
    else:
        current_page = 0
        page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
        r.set(page_size_key, str(page_size))
        r.set(current_page_key, current_page)

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = str(session['user_id']) + '_KAPR'
    if first_flag:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    else:
        KAPR = round(100*float(r.get(KAPR_key)), 1)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    working_data.set_kapr_size(6*6)
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())

    # load KAPR LIMIT from url parameter
    if ustudy_budget == 'moderate' or ustudy_budget == 'minimum':
        kapr_limit = dm.get_kaprlimit(DATASET, working_data, ustudy_budget)
    else:
        kapr_limit = float(ustudy_budget)
    r.set(str(session['user_id'])+'section2_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Section <span id="end_session">2</span>', 
        thisurl='/section2', 
        page_number=str(current_page+1), 
        delta=delta, 
        kapr = KAPR,
        kapr_limit = kapr_limit, 
        uid=str(session['user_id']),
        pair_num_base=6*current_page+1,
        ustudy_mode=ustudy_mode
    )


@main_section.route('/section2/next')
def show_section2_next():
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 2)

    page_size = int(r.get(str(session['user_id']) + '_section2_page_size'))
    current_page = int(r.get(str(session['user_id'])+'_section2_current_page'))+1
    if current_page >= page_size or (current_page+1)*6 > working_data.size():
        ret = {
            'result': 'no more pages'
        }
        return jsonify(ret)
    r.incr(str(session['user_id'])+'_section2_current_page')
    
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    KAPR_key = str(session['user_id']) + '_KAPR'
    if current_page%6 == 0:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    KAPR = 100*float(r.get(KAPR_key))

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    #delta = dm.get_delta_for_dataset(DATASET, working_data.get_raw_data()[12:])
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        pair_num_base=6*current_page+1, 
        ustudy_mode=ustudy_mode
    )

    ret = {
        'result': 'success',
        'ustudy_mode': ustudy_mode,
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1),
        'page_content': page_content,
        'kapr': KAPR
    }
    return jsonify(ret)




@main_section.route('/section3')
@state_machine('show_section3')
def show_section3():
    """
    section 2 contains 300 questions. The students don't need to finish them all, it just for those who 
    finish section 1 very fast.
    """
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    ustudy_budget = r.get(session['user_id']+'_ustudy_budget')

    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(str(session['user_id']), 3)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()

    # if the user is in this section the first time, or coming back
    first_flag = True
    page_size_key = str(session['user_id']) + '_section3_page_size'
    current_page_key = str(session['user_id']) + '_section3_current_page'
    if (not r.get(current_page_key) is None) and (not r.get(current_page_key) == '0'):
        page_size = int(r.get(page_size_key))
        current_page = int(r.get(current_page_key))
        if current_page >= page_size or (current_page+1)*6 > working_data.size():
            return redirect(url_for('next'))
        first_flag = False
    else:
        current_page = 0
        page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
        r.set(page_size_key, str(page_size))
        r.set(current_page_key, current_page)

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = str(session['user_id']) + '_KAPR'
    if first_flag:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    else:
        KAPR = round(100*float(r.get(KAPR_key)), 1)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    working_data.set_kapr_size(6*6)
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())

    # load KAPR LIMIT from url parameter
    if ustudy_budget == 'moderate' or ustudy_budget == 'minimum':
        kapr_limit = dm.get_kaprlimit(DATASET, working_data, ustudy_budget)
    else:
        kapr_limit = float(ustudy_budget)
    r.set(str(session['user_id'])+'section3_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Section <span id="end_session">3</span>', 
        thisurl='/section3', 
        page_number=str(current_page+1), 
        delta=delta, 
        kapr = KAPR,
        kapr_limit = kapr_limit, 
        uid=str(session['user_id']),
        pair_num_base=6*current_page+1,
        ustudy_mode=ustudy_mode
    )


@main_section.route('/section3/next')
def show_section3_next():
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 3)

    page_size = int(r.get(str(session['user_id']) + '_section3_page_size'))
    current_page = int(r.get(str(session['user_id'])+'_section3_current_page'))+1
    if current_page >= page_size or (current_page+1)*6 > working_data.size():
        ret = {
            'result': 'no more pages'
        }
        return jsonify(ret)
    r.incr(str(session['user_id'])+'_section3_current_page')
    
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    KAPR_key = str(session['user_id']) + '_KAPR'
    if current_page%6 == 0:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    KAPR = 100*float(r.get(KAPR_key))

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    #delta = dm.get_delta_for_dataset(DATASET, working_data.get_raw_data()[12:])
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        pair_num_base=6*current_page+1, 
        ustudy_mode=ustudy_mode
    )

    ret = {
        'result': 'success',
        'ustudy_mode': ustudy_mode,
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1),
        'page_content': page_content,
        'kapr': KAPR
    }
    return jsonify(ret)


@main_section.route('/section4')
@state_machine('show_section4')
def show_section4():
    """
    section 2 contains 300 questions. The students don't need to finish them all, it just for those who 
    finish section 1 very fast.
    """
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    ustudy_budget = r.get(session['user_id']+'_ustudy_budget')

    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(str(session['user_id']), 4)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()

    # if the user is in this section the first time, or coming back
    first_flag = True
    page_size_key = str(session['user_id']) + '_section4_page_size'
    current_page_key = str(session['user_id']) + '_section4_current_page'
    if (not r.get(current_page_key) is None) and (not r.get(current_page_key) == '0'):
        page_size = int(r.get(page_size_key))
        current_page = int(r.get(current_page_key))
        if current_page >= page_size or (current_page+1)*6 > working_data.size():
            return redirect(url_for('next'))
        first_flag = False
    else:
        current_page = 0
        page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
        r.set(page_size_key, str(page_size))
        r.set(current_page_key, current_page)

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = str(session['user_id']) + '_KAPR'
    if first_flag:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    else:
        KAPR = round(100*float(r.get(KAPR_key)), 1)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    working_data.set_kapr_size(6*6)
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())

    # load KAPR LIMIT from url parameter
    if ustudy_budget == 'moderate' or ustudy_budget == 'minimum':
        kapr_limit = dm.get_kaprlimit(DATASET, working_data, ustudy_budget)
    else:
        kapr_limit = float(ustudy_budget)
    r.set(str(session['user_id'])+'section4_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Section <span id="end_session">4</span>', 
        thisurl='/section4', 
        page_number=str(current_page+1), 
        delta=delta, 
        kapr = KAPR,
        kapr_limit = kapr_limit, 
        uid=str(session['user_id']),
        pair_num_base=6*current_page+1,
        ustudy_mode=ustudy_mode
    )


@main_section.route('/section4/next')
def show_section4_next():
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 4)

    page_size = int(r.get(str(session['user_id']) + '_section4_page_size'))
    current_page = int(r.get(str(session['user_id'])+'_section4_current_page'))+1
    if current_page >= page_size or (current_page+1)*6 > working_data.size():
        ret = {
            'result': 'no more pages'
        }
        return jsonify(ret)
    r.incr(str(session['user_id'])+'_section4_current_page')
    
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    KAPR_key = str(session['user_id']) + '_KAPR'
    if current_page%6 == 0:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    KAPR = 100*float(r.get(KAPR_key))

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    #delta = dm.get_delta_for_dataset(DATASET, working_data.get_raw_data()[12:])
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        pair_num_base=6*current_page+1, 
        ustudy_mode=ustudy_mode
    )

    ret = {
        'result': 'success',
        'ustudy_mode': ustudy_mode,
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1),
        'page_content': page_content,
        'kapr': KAPR
    }
    return jsonify(ret)


@main_section.route('/section5')
@state_machine('show_section5')
def show_section5():
    """
    section 2 contains 500 questions. The students don't need to finish them all, it just for those who 
    finish section 1 very fast.
    """
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    ustudy_budget = r.get(session['user_id']+'_ustudy_budget')

    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(str(session['user_id']), 5)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()

    # if the user is in this section the first time, or coming back
    first_flag = True
    page_size_key = str(session['user_id']) + '_section5_page_size'
    current_page_key = str(session['user_id']) + '_section5_current_page'
    if (not r.get(current_page_key) is None) and (not r.get(current_page_key) == '0'):
        page_size = int(r.get(page_size_key))
        current_page = int(r.get(current_page_key))
        if current_page >= page_size or (current_page+1)*6 > working_data.size():
            return redirect(url_for('next'))
        first_flag = False
    else:
        current_page = 0
        page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
        r.set(page_size_key, str(page_size))
        r.set(current_page_key, current_page)

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = str(session['user_id']) + '_KAPR'
    if first_flag:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    else:
        KAPR = round(100*float(r.get(KAPR_key)), 1)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    working_data.set_kapr_size(6*6)
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())

    # load KAPR LIMIT from url parameter
    if ustudy_budget == 'moderate' or ustudy_budget == 'minimum':
        kapr_limit = dm.get_kaprlimit(DATASET, working_data, ustudy_budget)
    else:
        kapr_limit = float(ustudy_budget)
    r.set(str(session['user_id'])+'section5_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Section <span id="end_session">5</span>', 
        thisurl='/section5', 
        page_number=str(current_page+1), 
        delta=delta, 
        kapr = KAPR,
        kapr_limit = kapr_limit, 
        uid=str(session['user_id']),
        pair_num_base=6*current_page+1,
        ustudy_mode=ustudy_mode
    )


@main_section.route('/section5/next')
def show_section5_next():
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 5)

    page_size = int(r.get(str(session['user_id']) + '_section5_page_size'))
    current_page = int(r.get(str(session['user_id'])+'_section5_current_page'))+1
    if current_page >= page_size or (current_page+1)*6 > working_data.size():
        ret = {
            'result': 'no more pages'
        }
        return jsonify(ret)
    r.incr(str(session['user_id'])+'_section5_current_page')
    
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    KAPR_key = str(session['user_id']) + '_KAPR'
    if current_page%6 == 0:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    KAPR = 100*float(r.get(KAPR_key))

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    #delta = dm.get_delta_for_dataset(DATASET, working_data.get_raw_data()[12:])
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        pair_num_base=6*current_page+1, 
        ustudy_mode=ustudy_mode
    )

    ret = {
        'result': 'success',
        'ustudy_mode': ustudy_mode,
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1),
        'page_content': page_content,
        'kapr': KAPR
    }
    return jsonify(ret)







@main_section.route('/section6')
@state_machine('show_section6')
def show_section6():
    """
    section 2 contains 600 questions. The students don't need to finish them all, it just for those who 
    finish section 1 very fast.
    """
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    ustudy_budget = r.get(session['user_id']+'_ustudy_budget')

    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(str(session['user_id']), 6)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()

    # if the user is in this section the first time, or coming back
    first_flag = True
    page_size_key = str(session['user_id']) + '_section6_page_size'
    current_page_key = str(session['user_id']) + '_section6_current_page'
    if (not r.get(current_page_key) is None) and (not r.get(current_page_key) == '0'):
        page_size = int(r.get(page_size_key))
        current_page = int(r.get(current_page_key))
        if current_page >= page_size or (current_page+1)*6 > working_data.size():
            return redirect(url_for('next'))
        first_flag = False
    else:
        current_page = 0
        page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
        r.set(page_size_key, str(page_size))
        r.set(current_page_key, current_page)

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = str(session['user_id']) + '_KAPR'
    if first_flag:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    else:
        KAPR = round(100*float(r.get(KAPR_key)), 1)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    working_data.set_kapr_size(6*6)
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())

    # load KAPR LIMIT from url parameter
    if ustudy_budget == 'moderate' or ustudy_budget == 'minimum':
        kapr_limit = dm.get_kaprlimit(DATASET, working_data, ustudy_budget)
    else:
        kapr_limit = float(ustudy_budget)
    r.set(str(session['user_id'])+'section6_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Section <span id="end_session">6</span>', 
        thisurl='/section6', 
        page_number=str(current_page+1), 
        delta=delta, 
        kapr = KAPR,
        kapr_limit = kapr_limit, 
        uid=str(session['user_id']),
        pair_num_base=6*current_page+1,
        ustudy_mode=ustudy_mode
    )


@main_section.route('/section6/next')
def show_section6_next():
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 6)

    page_size = int(r.get(str(session['user_id']) + '_section6_page_size'))
    current_page = int(r.get(str(session['user_id'])+'_section6_current_page'))+1
    if current_page >= page_size or (current_page+1)*6 > working_data.size():
        ret = {
            'result': 'no more pages'
        }
        return jsonify(ret)
    r.incr(str(session['user_id'])+'_section6_current_page')
    
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    KAPR_key = str(session['user_id']) + '_KAPR'
    if current_page%6 == 0:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    KAPR = 100*float(r.get(KAPR_key))

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    #delta = dm.get_delta_for_dataset(DATASET, working_data.get_raw_data()[12:])
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        pair_num_base=6*current_page+1, 
        ustudy_mode=ustudy_mode
    )

    ret = {
        'result': 'success',
        'ustudy_mode': ustudy_mode,
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1),
        'page_content': page_content,
        'kapr': KAPR
    }
    return jsonify(ret)




@main_section.route('/section7')
@state_machine('show_section7')
def show_section7():
    """
    section 2 contains 700 questions. The students don't need to finish them all, it just for those who 
    finish section 1 very fast.
    """
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    ustudy_budget = r.get(session['user_id']+'_ustudy_budget')

    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(str(session['user_id']), 7)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()

    # if the user is in this section the first time, or coming back
    first_flag = True
    page_size_key = str(session['user_id']) + '_section7_page_size'
    current_page_key = str(session['user_id']) + '_section7_current_page'
    if (not r.get(current_page_key) is None) and (not r.get(current_page_key) == '0'):
        page_size = int(r.get(page_size_key))
        current_page = int(r.get(current_page_key))
        if current_page >= page_size or (current_page+1)*6 > working_data.size():
            return redirect(url_for('next'))
        first_flag = False
    else:
        current_page = 0
        page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
        r.set(page_size_key, str(page_size))
        r.set(current_page_key, current_page)

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = str(session['user_id']) + '_KAPR'
    if first_flag:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    else:
        KAPR = round(100*float(r.get(KAPR_key)), 1)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    working_data.set_kapr_size(6*6)
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())

    # load KAPR LIMIT from url parameter
    if ustudy_budget == 'moderate' or ustudy_budget == 'minimum':
        kapr_limit = dm.get_kaprlimit(DATASET, working_data, ustudy_budget)
    else:
        kapr_limit = float(ustudy_budget)
    r.set(str(session['user_id'])+'section7_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Section <span id="end_session">7</span>', 
        thisurl='/section7', 
        page_number=str(current_page+1), 
        delta=delta, 
        kapr = KAPR,
        kapr_limit = kapr_limit, 
        uid=str(session['user_id']),
        pair_num_base=6*current_page+1,
        ustudy_mode=ustudy_mode
    )


@main_section.route('/section7/next')
def show_section7_next():
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 7)

    page_size = int(r.get(str(session['user_id']) + '_section7_page_size'))
    current_page = int(r.get(str(session['user_id'])+'_section7_current_page'))+1
    if current_page >= page_size or (current_page+1)*6 > working_data.size():
        ret = {
            'result': 'no more pages'
        }
        return jsonify(ret)
    r.incr(str(session['user_id'])+'_section7_current_page')
    
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    KAPR_key = str(session['user_id']) + '_KAPR'
    if current_page%6 == 0:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    KAPR = 100*float(r.get(KAPR_key))

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    #delta = dm.get_delta_for_dataset(DATASET, working_data.get_raw_data()[12:])
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        pair_num_base=6*current_page+1, 
        ustudy_mode=ustudy_mode
    )

    ret = {
        'result': 'success',
        'ustudy_mode': ustudy_mode,
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1),
        'page_content': page_content,
        'kapr': KAPR
    }
    return jsonify(ret)




@main_section.route('/section8')
@state_machine('show_section8')
def show_section8():
    """
    section 2 contains 800 questions. The students don't need to finish them all, it just for those who 
    finish section 1 very fast.
    """
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    ustudy_budget = r.get(session['user_id']+'_ustudy_budget')

    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(str(session['user_id']), 8)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()

    # if the user is in this section the first time, or coming back
    first_flag = True
    page_size_key = str(session['user_id']) + '_section8_page_size'
    current_page_key = str(session['user_id']) + '_section8_current_page'
    if (not r.get(current_page_key) is None) and (not r.get(current_page_key) == '0'):
        page_size = int(r.get(page_size_key))
        current_page = int(r.get(current_page_key))
        if current_page >= page_size or (current_page+1)*6 > working_data.size():
            return redirect(url_for('next'))
        first_flag = False
    else:
        current_page = 0
        page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
        r.set(page_size_key, str(page_size))
        r.set(current_page_key, current_page)

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = str(session['user_id']) + '_KAPR'
    if first_flag:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    else:
        KAPR = round(100*float(r.get(KAPR_key)), 1)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    working_data.set_kapr_size(6*6)
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())

    # load KAPR LIMIT from url parameter
    if ustudy_budget == 'moderate' or ustudy_budget == 'minimum':
        kapr_limit = dm.get_kaprlimit(DATASET, working_data, ustudy_budget)
    else:
        kapr_limit = float(ustudy_budget)
    r.set(str(session['user_id'])+'section8_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Section <span id="end_session">8</span>', 
        thisurl='/section8', 
        page_number=str(current_page+1), 
        delta=delta, 
        kapr = KAPR,
        kapr_limit = kapr_limit, 
        uid=str(session['user_id']),
        pair_num_base=6*current_page+1,
        ustudy_mode=ustudy_mode
    )


@main_section.route('/section8/next')
def show_section8_next():
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 8)

    page_size = int(r.get(str(session['user_id']) + '_section8_page_size'))
    current_page = int(r.get(str(session['user_id'])+'_section8_current_page'))+1
    if current_page >= page_size or (current_page+1)*6 > working_data.size():
        ret = {
            'result': 'no more pages'
        }
        return jsonify(ret)
    r.incr(str(session['user_id'])+'_section8_current_page')
    
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    KAPR_key = str(session['user_id']) + '_KAPR'
    if current_page%6 == 0:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    KAPR = 100*float(r.get(KAPR_key))

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    #delta = dm.get_delta_for_dataset(DATASET, working_data.get_raw_data()[12:])
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        pair_num_base=6*current_page+1, 
        ustudy_mode=ustudy_mode
    )

    ret = {
        'result': 'success',
        'ustudy_mode': ustudy_mode,
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1),
        'page_content': page_content,
        'kapr': KAPR
    }
    return jsonify(ret)




@main_section.route('/section9')
@state_machine('show_section9')
def show_section9():
    """
    section 2 contains 900 questions. The students don't need to finish them all, it just for those who 
    finish section 1 very fast.
    """
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    ustudy_budget = r.get(session['user_id']+'_ustudy_budget')

    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(str(session['user_id']), 9)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()

    # if the user is in this section the first time, or coming back
    first_flag = True
    page_size_key = str(session['user_id']) + '_section9_page_size'
    current_page_key = str(session['user_id']) + '_section9_current_page'
    if (not r.get(current_page_key) is None) and (not r.get(current_page_key) == '0'):
        page_size = int(r.get(page_size_key))
        current_page = int(r.get(current_page_key))
        if current_page >= page_size or (current_page+1)*6 > working_data.size():
            return redirect(url_for('next'))
        first_flag = False
    else:
        current_page = 0
        page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
        r.set(page_size_key, str(page_size))
        r.set(current_page_key, current_page)

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = str(session['user_id']) + '_KAPR'
    if first_flag:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    else:
        KAPR = round(100*float(r.get(KAPR_key)), 1)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    working_data.set_kapr_size(6*6)
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())

    # load KAPR LIMIT from url parameter
    if ustudy_budget == 'moderate' or ustudy_budget == 'minimum':
        kapr_limit = dm.get_kaprlimit(DATASET, working_data, ustudy_budget)
    else:
        kapr_limit = float(ustudy_budget)
    r.set(str(session['user_id'])+'section9_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Section <span id="end_session">9</span>', 
        thisurl='/section9', 
        page_number=str(current_page+1), 
        delta=delta, 
        kapr = KAPR,
        kapr_limit = kapr_limit, 
        uid=str(session['user_id']),
        pair_num_base=6*current_page+1,
        ustudy_mode=ustudy_mode
    )


@main_section.route('/section9/next')
def show_section9_next():
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 9)

    page_size = int(r.get(str(session['user_id']) + '_section9_page_size'))
    current_page = int(r.get(str(session['user_id'])+'_section9_current_page'))+1
    if current_page >= page_size or (current_page+1)*6 > working_data.size():
        ret = {
            'result': 'no more pages'
        }
        return jsonify(ret)
    r.incr(str(session['user_id'])+'_section9_current_page')
    
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    KAPR_key = str(session['user_id']) + '_KAPR'
    if current_page%6 == 0:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    KAPR = 100*float(r.get(KAPR_key))

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    #delta = dm.get_delta_for_dataset(DATASET, working_data.get_raw_data()[12:])
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        pair_num_base=6*current_page+1, 
        ustudy_mode=ustudy_mode
    )

    ret = {
        'result': 'success',
        'ustudy_mode': ustudy_mode,
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1),
        'page_content': page_content,
        'kapr': KAPR
    }
    return jsonify(ret)




@main_section.route('/section10')
@state_machine('show_section10')
def show_section10():
    """
    section 2 contains 1000 questions. The students don't need to finish them all, it just for those who 
    finish section 1 very fast.
    """
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    ustudy_budget = r.get(session['user_id']+'_ustudy_budget')

    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(str(session['user_id']), 10)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()

    # if the user is in this section the first time, or coming back
    first_flag = True
    page_size_key = str(session['user_id']) + '_section10_page_size'
    current_page_key = str(session['user_id']) + '_section10_current_page'
    if (not r.get(current_page_key) is None) and (not r.get(current_page_key) == '0'):
        page_size = int(r.get(page_size_key))
        current_page = int(r.get(current_page_key))
        if current_page >= page_size or (current_page+1)*6 > working_data.size():
            return redirect(url_for('next'))
        first_flag = False
    else:
        current_page = 0
        page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
        r.set(page_size_key, str(page_size))
        r.set(current_page_key, current_page)

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    # KAPR - K-Anonymity privacy risk
    KAPR_key = str(session['user_id']) + '_KAPR'
    if first_flag:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    else:
        KAPR = round(100*float(r.get(KAPR_key)), 1)

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(attribute_size):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    working_data.set_kapr_size(6*6)
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())

    # load KAPR LIMIT from url parameter
    if ustudy_budget == 'moderate' or ustudy_budget == 'minimum':
        kapr_limit = dm.get_kaprlimit(DATASET, working_data, ustudy_budget)
    else:
        kapr_limit = float(ustudy_budget)
    r.set(str(session['user_id'])+'section10_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Section <span id="end_session">10</span>', 
        thisurl='/section10', 
        page_number=str(current_page+1), 
        delta=delta, 
        kapr = KAPR,
        kapr_limit = kapr_limit, 
        uid=str(session['user_id']),
        pair_num_base=6*current_page+1,
        ustudy_mode=ustudy_mode
    )


@main_section.route('/section10/next')
def show_section10_next():
    ustudy_mode = int(r.get(session['user_id']+'_ustudy_mode'))
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 10)

    page_size = int(r.get(str(session['user_id']) + '_section10_page_size'))
    current_page = int(r.get(str(session['user_id'])+'_section10_current_page'))+1
    if current_page >= page_size or (current_page+1)*6 > working_data.size():
        ret = {
            'result': 'no more pages'
        }
        return jsonify(ret)
    r.incr(str(session['user_id'])+'_section10_current_page')
    
    is_last_page = 0
    if current_page == page_size - 1:
        is_last_page = 1

    pairs_formatted = working_data.get_data_display(data_mode)[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    data = zip(pairs_formatted[0::2], pairs_formatted[1::2])
    icons = working_data.get_icons()[config.DATA_PAIR_PER_PAGE*current_page:config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids_list = working_data.get_ids()[2*config.DATA_PAIR_PER_PAGE*current_page:2*config.DATA_PAIR_PER_PAGE*(current_page+1)]
    ids = zip(ids_list[0::2], ids_list[1::2])

    KAPR_key = str(session['user_id']) + '_KAPR'
    if current_page%6 == 0:
        KAPR = 0
        r.set(KAPR_key, KAPR)
    KAPR = 100*float(r.get(KAPR_key))

    # set the user-display-status as masked for all cell
    for id1 in ids_list:
        for i in range(6):
            key = str(session['user_id']) + '-' + id1[i]
            r.set(key, 'M')

    # get the delta information
    #delta = dm.get_delta_for_dataset(DATASET, working_data.get_raw_data()[12:])
    delta = list()
    for i in range(config.DATA_PAIR_PER_PAGE*current_page, config.DATA_PAIR_PER_PAGE*(current_page+1)):
        data_pair = working_data.get_data_pair_by_index(i)
        delta += dm.KAPR_delta(DATASET, data_pair, ['M', 'M', 'M', 'M', 'M', 'M'], 2*working_data.get_kapr_size())
    # make delta to be a dict
    delta_dict = dict()
    for d in delta:
        delta_dict[d[0]] = d[1]

    page_content = render_template('record_linkage_next.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        pair_num_base=6*current_page+1, 
        ustudy_mode=ustudy_mode
    )

    ret = {
        'result': 'success',
        'ustudy_mode': ustudy_mode,
        'delta': delta_dict,
        'is_last_page': is_last_page,
        'page_number': 'page: ' + str(current_page+1),
        'page_content': page_content,
        'kapr': KAPR
    }
    return jsonify(ret)




