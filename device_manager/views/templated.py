#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging

from flask import render_template, Blueprint

from device_manager.config import config

blueprint = Blueprint('templated', __name__, template_folder='templates')

log = logging.getLogger('device_manager')


@blueprint.route('/')
@blueprint.route('/index')
def index():
    return render_template('index.html',
                           page_name='Main',
                           device_manager="device_manager")
