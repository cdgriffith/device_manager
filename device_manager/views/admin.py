#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging

from flask import render_template, Blueprint

from device_manager.config import config

# We are adding the prefix to the blueprint itself, then will add
# BasicAuth via Nginx to project all these endpoints

blueprint = Blueprint('admin', __name__,
                      url_prefix="/admin",
                      template_folder='templates')

log = logging.getLogger('device_manager')


@blueprint.route('/')
def index():
    return render_template('admin.html',
                           page_name='Admin Area',
                           device_manager="device_manager")
