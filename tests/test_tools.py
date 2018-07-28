#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from device_manager import tools


def test_jwt():
    payload = {'test': 'hello'}
    generated = tools.generate_token(payload)
    assert payload == tools.verify_token(generated)

