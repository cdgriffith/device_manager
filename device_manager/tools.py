#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
from functools import wraps

from box import Box
from flask import make_response, request
import jwt

from device_manager.config import config


def ok(data=None, code=200):
    response = {'version': config.version, 'status': code, 'error': False}
    if isinstance(data, Box):
        data = data.to_dict()
    if data is not None:
        response['data'] = data
    return make_response(json.dumps(response), code, {'mimetype': 'application/json'})


def err(msg=None, code=500):
    response = {'version': config.version, 'status': code, 'error': True}
    if isinstance(msg, Box):
        msg = msg.to_dict()
    if msg is not None:
        response['msg'] = msg
    return make_response(json.dumps(response), code, {'mimetype': 'application/json'})


def json_in(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            payload = request.get_json()
            if not payload and request.data:
                payload = request.get_json(force=True)
        except Exception as error:
            print(str(error))
            return err(msg=f"Bad JSON - {str(error)}", code=400)
        else:
            return f(*args, payload, **kwargs)
    return wrapper


def generate_token(payload):
    return jwt.encode(payload, config.jwt_key, algorithm='HS256').decode('utf-8')


def verify_token(payload):
    if isinstance(payload, str):
        payload = payload.encode('utf-8')
    return jwt.decode(payload, config.jwt_key, algorithms=['HS256'])

