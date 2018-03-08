# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

import evernote.edam.userstore.constants as UserStoreConstants

from . import environ
from .interface import get_interface
from .model import Note, Notebook


__version__ = "0.0.1"


def check_api():
    """Return true if using the latest Evernote API version"""
    interface = get_interface()
    user_store = interface.get_user_store()

    ret = user_store.checkVersion(
        "{} {}".format(__name__, __version__),
        UserStoreConstants.EDAM_VERSION_MAJOR,
        UserStoreConstants.EDAM_VERSION_MINOR
    )
    return ret


