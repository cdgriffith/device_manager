#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import uuid

from flask import Blueprint
from box import Box
from schema import Schema, And, Use, Optional, SchemaError

from device_manager.config import config
from device_manager.local_storage import StorageBox
from device_manager.tools import ok, err, api, generate_token

# We are adding the prefix to the blueprint itself, then will add
# BasicAuth via Nginx to project all these endpoints

blueprint = Blueprint('auth', __name__,
                      url_prefix="/api/v1/auth/")

log = logging.getLogger('device_manager')


@blueprint.route('/')
def index():
    return ok()


@blueprint.route('/token_request', methods=['POST'])
def access():
    return ok(token=generate_token({'uuid': uuid.uuid4().hex, 'user': 'test'}))



