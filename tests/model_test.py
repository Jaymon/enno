# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from unittest import TestCase

import testdata

from enno.model import Ennotebook, Ennote


class EnnoteTest(TestCase):
    def test_notebook(self):
        n = None
        for nb in Ennotebook.query.get():
            n = Ennote.query.is_notebook(nb).get_one()
            if n is not None:
                break
        self.assertIsNotNone(n)

#         nb = testdata.random.choice(list(Ennotebook.query.get()))
#         n = Ennote.query.is_notebook(nb).get_one()

        nb2 = n.notebook
        self.assertEqual(nb.guid, nb2.guid)

    def test_notebook_set(self):
        n = Ennote()
        nb = testdata.random.choice(list(Ennotebook.query.get()))

        self.assertIsNone(n.notebook_guid)
        n.notebook_guid = nb.guid
        self.assertEqual(n.notebook_guid, nb.guid)

        nb_guid = n.notebook_guid
        n.notebook = nb
        self.assertEqual(n.notebook_guid, nb.guid)

    def test_content_1(self):
        n = Ennote()

        n = Ennote.query.one()
        pout.v(n.content)


        r = n.html
        pout.v(r)

        r = n.plain
        pout.v(r)





        # TODO -- test & in note

    def test_html(self):
        n = Ennote()
        nb = testdata.random.choice(list(Ennotebook.query.get()))
        html_doc = """
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
"""

        self.assertIsNone(n.guid)

        n.title = testdata.get_words()
        n.html = html_doc
        n.notebook = nb
        n.save()
        self.assertIsNotNone(n.guid)
        pout.v(n.content)

        n2 = Ennote.query.is_guid(n.guid).one()
        pout.v(n2.plain)



class EnnotebookTest(TestCase):
    def get_query(self):
        return Ennotebook.query

    def test_crud(self):
        nb = Ennotebook()
        self.assertIsNone(nb.guid)
        self.assertIsNone(nb.name)
        self.assertIsNone(nb.created)
        self.assertIsNone(nb.updated)

        name = testdata.get_unicode_words()
        nb.name = name
        self.assertEqual(name, nb.name)

        nb.save()
        self.assertIsNotNone(nb.guid)
        self.assertEqual(name, nb.name)
        self.assertIsNotNone(nb.created)
        self.assertIsNotNone(nb.updated)

        updated = nb.updated
        name2 = testdata.get_words()
        nb.name = name2
        self.assertNotEqual(name, nb.name)
        nb.save()
        self.assertEqual(name2, nb.name)
        self.assertNotEqual(updated, nb.updated)

    def test_query(self):
        names = [nb.name for nb in self.get_query().get()]

        r = [nb.name for nb in self.get_query().is_name(names[0]).get()]
        self.assertEqual(1, len(r))

        r = [nb.name for nb in self.get_query().limit(2).get()]
        self.assertEqual(2, len(r))

        nb = self.get_query().get_one()
        r = [nb.name for nb in self.get_query().is_guid(nb.guid).get()]
        self.assertEqual(1, len(r))

        r = [nb.name for nb in self.get_query().in_guid(nb.guid).get()]
        self.assertEqual(1, len(r))


