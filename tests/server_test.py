# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from unittest import TestCase

import requests

from enno.server import AuthServer


class AuthServerTest(TestCase):
    def test_callback(self):
        ret = {}
        def callback(res):
            ret.update(res.query)

        with AuthServer(callback) as s:
            res = requests.get("{}?foo=bar&baz=che".format(s.netloc))
            self.assertEqual(204, res.status_code)
            self.assertEqual({"foo": "bar", "baz": "che"}, ret)


