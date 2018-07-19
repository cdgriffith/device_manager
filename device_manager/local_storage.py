#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os

from appdirs import user_data_dir

from device_manager.config import config

DEFAULT_DIR = user_data_dir(config.app_name)


class LocalStorageError(Exception):
    pass


class PermissionError(LocalStorageError):
    pass


class LocalStorage:

    def __init__(self, project_name, storage_directory=DEFAULT_DIR):
        self.project_name = project_name
        self.storage_directory = storage_directory
        self.structure = {}
        self.permissions_check()

    def permissions_check(self):
        test_dir = os.path.join(self.storage_directory, 'test_directory_plz_ignore')
        if os.path.exists(test_dir):
            try:
                os.unlink(test_dir)
            except OSError:
                raise LocalStorageError(f'Test directory exists already, please remove {test_dir}')
        try:
            os.makedirs(test_dir)
        except OSError:
            raise PermissionError(f'Do not have permission to create folders at {self.storage_directory}')

    def get(self, path):
        pass



