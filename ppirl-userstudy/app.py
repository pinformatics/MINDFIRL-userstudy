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

#app.register_blueprint(tutorial)
#app.register_blueprint(main_section)

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

