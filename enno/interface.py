# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

from evernote.api.client import EvernoteClient

from . import environ


_interface = None


# def create_interface(access_token=None, sandbox=None):
# 
#     if sandbox is None:
#         sandbox = environ.SANDBOX
# 
#     if access_token is None:
#         if sandbox:
#             access_token = environ.SANDBOX_ACCESS_TOKEN
#         else:
#             access_token = environ.ACCESS_TOKEN
# 
#     interface = EvernoteClient(token=access_token, sandbox=sandbox)
#     return interface

def get_interface():
    global _interface
    if _interface is None:
        sandbox = environ.SANDBOX
        if sandbox:
            access_token = environ.SANDBOX_ACCESS_TOKEN
        else:
            access_token = environ.ACCESS_TOKEN

        interface = EvernoteClient(token=access_token, sandbox=sandbox)
        set_interface(interface)

    return _interface


def set_interface(interface):
    global _interface
    _interface = interface


