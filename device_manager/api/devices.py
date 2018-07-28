#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import logging
import uuid

from flask import Blueprint
from box import Box
from schema import Schema, And, Optional, SchemaError

from device_manager.config import config
from device_manager.local_storage import StorageBox
from device_manager.tools import ok, err, api

# We are adding the prefix to the blueprint itself, then will add
# BasicAuth via Nginx to project all these endpoints

blueprint = Blueprint('devices', __name__,
                      url_prefix="/api/v1/devices")

log = logging.getLogger('device_manager')

device_schema = Schema({
    'id': str,
    'name': str,
    Optional('state'): And(str, lambda x: x in ['on', 'off']),
    Optional('addresses'): {
        'status': str,
        'start': str,
        'stop': str
    },
    'auth_token': And(str, lambda x: len(x) > 16),
    'user': str
})

devices = StorageBox('devices', schema=device_schema)


def get_next_dev_id():
    existing = sorted([int(x) for x in devices.keys()])
    if not existing:
        return 1
    else:
        return str(existing[-1] + 1)


def scrub_device(device, keys=('auth_token', 'user')):
    for key in keys:
        try:
            del device[key]
        except KeyError:
            pass
    return device


@blueprint.route('', methods=['GET'])
@api()
def get_devices(jwt):
    return ok([scrub_device(x) for x in devices.search('user', jwt)])


@blueprint.route('', methods=['POST'])
@api()
def new_device(payload, jwt):
    new_id = get_next_dev_id()
    if 'state' not in payload:
        payload['state'] = 'off'
    payload['id'] = new_id
    payload['auth_token'] = f"{uuid.uuid4().hex}"
    payload['user'] = jwt.user
    try:
        devices.set(new_id, payload)
    except SchemaError as error:
        return err(str(error), 400)

    return ok(id=new_id, access_token=payload['auth_token'])


@blueprint.route('', methods=['DELETE'])
@api()
def delete_devices(jwt):
    for device in devices.search('user', jwt):
        devices.delete(device.id)
    return ok()


@blueprint.route('/<device_id>', methods=['GET'])
@api()
def get_device(device_id, jwt):
    data = devices.get(device_id)
    if not data:
        return err('Device not found', 404)

    if data['user'] != jwt.user:
        return err('You do not have permission to view this device', 401)

    return ok(scrub_device(data))


@blueprint.route('/<device_id>', methods=['POST'])
@api()
def modify_device(device_id, payload):
    safer = scrub_device(payload)
    if 'id' in safer:
        del safer['id']

    data = devices.get(device_id)

    if data['auth_token'] != payload['access_token']:
        return err('Incorrect access token', 401)

    data.update(payload)

    try:
        devices.set(device_id, data)
    except SchemaError as error:
        return err(str(error), 400)

    return ok(scrub_device(data))


@blueprint.route('/<device_id>', methods=['DELETE'])
@api()
def delete_device(device_id, jwt):
    data = devices.get(device_id)

    if data['user'] != jwt.user:
        return err('You do not have permission to delete this device', 401)

    devices.delete(device_id)
    return ok()

