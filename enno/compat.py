# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import sys

_ver = sys.version_info
is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)

if is_py2:
    basestring = basestring
    unicode = unicode
    range = xrange # range is now always an iterator

    # shamelously ripped from six https://bitbucket.org/gutworth/six
    exec("""def reraise(tp, value, tb=None):
        try:
            raise tp, value, tb
        finally:
            tb = None
    """)

    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from BaseHTTPServer import HTTPServer
    import urlparse


elif is_py3:
    basestring = (str, bytes)
    unicode = str

    from http.server import HTTPServer, SimpleHTTPRequestHandler
    from urllib import parse as urlparse


    # ripped from six https://bitbucket.org/gutworth/six
    def reraise(tp, value, tb=None):
        try:
            if value is None:
                value = tp()
            if value.__traceback__ is not tb:
                raise value.with_traceback(tb)
            raise value
        finally:
            value = None
            tb = None

