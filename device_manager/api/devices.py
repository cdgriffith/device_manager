#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging

from flask import Blueprint
from box import Box
from schema import Schema, And, Use, Optional, SchemaError

from device_manager.config import config
from device_manager.local_storage import StorageBox
from device_manager.tools import ok, err, json_in

# We are adding the prefix to the blueprint itself, then will add
# BasicAuth via Nginx to project all these endpoints

blueprint = Blueprint('api', __name__,
                      url_prefix="/api/v1/")

log = logging.getLogger('device_manager')

device_schema = Schema({
    'name': str,
    'state': And(str, lambda x: x in ['on', 'off']),
    Optional('addresses'): {
        'status': str,
        'start': str,
        'stop': str
    }


})

devices = StorageBox('devices', schema=device_schema)


def get_next_dev_id():
    existing = sorted([int(x) for x in devices.keys()])
    if not existing:
        return 1
    else:
        return str(existing[-1] + 1)


@blueprint.route('/')
def index():
    return ok()


@blueprint.route('/device', methods=['GET'])
def get_devices():
    return ok(devices.data)


@blueprint.route('/device', methods=['POST'])
@json_in
def new_device(payload):
    new_id = get_next_dev_id()
    try:
        devices.set(new_id, payload)
    except SchemaError as error:
        return err(str(error), 400)
    return ok(new_id)


@blueprint.route('/device', methods=['DELETE'])
def delete_devices():
    devices.purge()
    return ok()


@blueprint.route('/device/<device_id>', methods=['GET'])
def get_device(device_id):
    device_id = int(device_id)
    return ok(devices.get(device_id))


@blueprint.route('/device/<device_id>', methods=['POST'])
@json_in
def modify_device(device_id, payload):
    device_id = int(device_id)

    data = devices.get(device_id)
    data.update(payload)
    try:
        devices.set(device_id, data)
    except SchemaError as error:
        return err(str(error))
    return ok(data)


@blueprint.route('/device/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    device_id = int(device_id)
    devices.delete(device_id)
    return ok()

