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
from global_data import r, DATASET, DATASET2, DATA_SECTION1, DATA_SECTION2


main_section = Blueprint('main_section', __name__, template_folder='templates')


def get_main_section_data(uid, section):
    data_num = uid%10
    if data_num == 0:
        data_num = 10
    data_num -= 1

    if section == 1:
        return DATA_SECTION1[data_num]
    else:
        return DATA_SECTION2[data_num]


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
    ustudy_mode = int(r.get(session['user_cookie']+'_ustudy_mode'))
    ustudy_budget = r.get(session['user_cookie']+'_ustudy_budget')
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 1)
    dp_size = config.DATA_PAIR_PER_PAGE
    attribute_size = 6
    dp_list_size = working_data.get_size()
    page_size = int(math.ceil(1.0*dp_list_size/config.DATA_PAIR_PER_PAGE))
    page_size_key = session['user_cookie'] + '_page_size'
    r.set(page_size_key, str(page_size))
    current_page_key = session['user_cookie'] + '_current_page'
    r.set(current_page_key, '0')

    pairs_formatted = working_data.get_data_display(data_mode)[0:2*dp_size]
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
    r.set(session['user_cookie']+'section1_kapr_limit', kapr_limit)

    return render_template('record_linkage_ppirl.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        title='Section 1', 
        thisurl='/record_linkage', 
        page_number="1/6", 
        delta=delta, 
        kapr_limit = kapr_limit, 
        uid=str(session['user_id']),
        ustudy_mode=ustudy_mode
    )


@main_section.route('/record_linkage/next')
def show_record_linkage_next():
    ustudy_mode = int(r.get(session['user_cookie']+'_ustudy_mode'))
    ustudy_budget = float(r.get(session['user_cookie']+'_ustudy_budget'))
    data_mode = 'masked'
    if ustudy_mode == 1:
        data_mode = 'full'

    working_data = get_main_section_data(session['user_id'], 1)

    current_page = int(r.get(session['user_cookie']+'_current_page'))+1
    r.incr(session['user_cookie']+'_current_page')
    page_size = int(r.get(session['user_cookie'] + '_page_size'))
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

    page_content = render_template('record_linkage_next.html', 
        data=data, 
        icons=icons, 
        ids=ids, 
        pair_num_base=6*current_page+1, 
        ustudy_mode=ustudy_mode
    )

    ret = {
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
    # grading section 1
    user_data_key = session['user_cookie'] + '_user_data'
    user_data = r.get(user_data_key)
    data = ud.parse_user_data(user_data)
    result = ud.grade_final_answer(data, get_main_section_data(session['user_id'], 1))
    performance1 = 'type:performance1,content:' + str(result[0]) + ' out of ' + str(result[1]) + ';\n'
    r.append(user_data_key, performance1)

    return render_template('section2_guide.html', uid=str(session['user_id']))


@main_section.route('/section2')
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


@main_section.route('/section2/next')
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
