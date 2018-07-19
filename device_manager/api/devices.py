#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging

from flask import Blueprint

from device_manager.config import config
from device_manager.tools import ok, err

# We are adding the prefix to the blueprint itself, then will add
# BasicAuth via Nginx to project all these endpoints

blueprint = Blueprint('api', __name__,
                      url_prefix="/api")

log = logging.getLogger('device_manager')


@blueprint.route('/')
def index():
    return ok()
