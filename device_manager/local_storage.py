#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
from threading import Lock

from box import Box
from appdirs import user_data_dir

from device_manager.config import config

__all__ = ['StorageBox', 'StorageBoxError']

LOCK = Lock()
SAVE_LOCK = Lock()


class StorageBoxError(Exception):
    pass


class StorageBox:

    def __init__(self, storage_type, project_name='device_manager', storage_directory=None, schema=None):
        if not re.match('^\w+$', project_name):
            raise StorageBoxError('Must only include letter, numbers and underscores in project_name')
        if not re.match('^\w+$', storage_type):
            raise StorageBoxError('Must only include letter, numbers and underscores in storage_type')

        storage_directory = user_data_dir(project_name) if not storage_directory else storage_directory
        os.makedirs(storage_directory, mode=0o644, exist_ok=True)
        self.storage_location = os.path.join(storage_directory, f"{storage_type}.json")
        print(f'Using storage location {self.storage_location}')
        with SAVE_LOCK:
            self.data = Box.from_json(filename=self.storage_location) if os.path.exists(self.storage_location) else Box()
        self.schema = schema
        self.save()

    def keys(self):
        with LOCK:
            return self.data.keys()

    def values(self):
        with LOCK:
            return self.data.values()

    def items(self):
        with LOCK:
            return list(self.data.items())

    def get(self, key, default=None):
        with LOCK:
            return self.data.get(key, default)

    def set(self, key, value):
        if self.schema:
            self.schema.validate(value)
        with LOCK:
            self.data[key] = value
            self.save()

    def delete(self, key):
        with LOCK:
            del self.data[key]
            self.save()

    def save(self):
        with SAVE_LOCK:
            self.data.to_json(filename=self.storage_location)

    def load(self):
        with SAVE_LOCK:
            data = Box.from_json(filename=self.storage_location)
        with LOCK:
            self.data = data

    def purge(self):
        with LOCK:
            self.data = Box()
            self.save()
