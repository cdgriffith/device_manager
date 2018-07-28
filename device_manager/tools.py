#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import json
from functools import wraps
import inspect

from box import Box
from flask import make_response, request
import jwt

from device_manager.config import config


def ok(data=None, code=200, **kwargs):
    response = {'version': config.version, 'status': code, 'error': False}
    if isinstance(data, Box):
        data = data.to_dict()
    if data is not None:
        response['data'] = data
    elif kwargs:
        response['data'] = kwargs
    return make_response(json.dumps(response), code,
                         {'mimetype': 'application/json'})


def err(msg=None, code=500):
    response = {'version': config.version, 'status': code, 'error': True}
    if isinstance(msg, Box):
        msg = msg.to_dict()
    if msg is not None:
        response['msg'] = msg
    return make_response(json.dumps(response), code,
                         {'mimetype': 'application/json'})


def api(auth=True):
    def inner(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            arg_spec = inspect.getfullargspec(f)
            arg_list = arg_spec.args + arg_spec.kwonlyargs
            if 'payload' in arg_list:
                try:
                    payload = request.get_json()
                    if not payload and request.data:
                        payload = request.get_json(force=True)
                except Exception as error:
                    print(str(error))
                    return err(msg=f"Bad JSON - {str(error)}", code=400)
                kwargs['payload'] = Box(payload)
            if auth:
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith("Bearer "):
                    return err(msg=f"Unauthorized: This endpoint requires "
                                   f"an Authorization header", code=401)
                try:
                    jwt_payload = verify_token(auth_header.split(" ")[1])
                except jwt.exceptions.PyJWTError:
                    return err(msg=f"Unauthorized: Bad JWT token", code=401)
                if 'jwt' in arg_list:
                    kwargs['jwt'] = Box(jwt_payload)
            return f(*args, **kwargs)
        return wrapper
    return inner


def generate_token(payload):
    return jwt.encode(payload, config.jwt_key,
                      algorithm='HS256').decode('utf-8')


def verify_token(payload):
    if isinstance(payload, str):
        payload = payload.encode('utf-8')
    return jwt.decode(payload, config.jwt_key, algorithms=['HS256'])

