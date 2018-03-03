# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import os


CONSUMER_KEY = os.environ.get("ENNO_CONSUMER_KEY", "")
"""The Evernote OAuth application key, used for making oauth requests"""

CONSUMER_SECRET = os.environ.get("ENNO_CONSUMER_SECRET", "")
"""The Evernote OAuth application secret, used for making oauth requests"""

ACCESS_TOKEN = os.environ.get("ENNO_ACCESS_TOKEN", "")
"""This is the what is used to make actual requests to Evernote, you can use the 
CONSUMER_KEY and CONSUMER_SECRET to request a TOKEN. You cannot make any requests
to Evernote without a TOKEN"""

SANDBOX = os.environ.get("ENNO_SANDBOX", "0").lower()
"""True if evernote is in sandbox environment (dev.evernote.com), if this is True
then internally SANDBOX_ACCESS_TOKEN will be used, if False then ACCESS_TOKEN will
be used"""
if SANDBOX.isdigit():
    SANDBOX = bool(int(SANDBOX))
else:
    if SANDBOX == "true":
        SANDBOX = True
    elif SANDBOX == "false":
        SANDBOX = False
    else:
        raise ValueError("Cannot decipher SANDBOX value {}".format(SANDBOX))

SANDBOX_ACCESS_TOKEN = os.environ.get("ENNO_SANDBOX_ACCESS_TOKEN", "")
"""This is a valid access token for the sandbox, this is more to make it easier for
testing while also making it easy to seemlessly switch to production"""

