# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from unittest import TestCase
import time

import testdata

from enno.model import Notebook, Note
from enno.utils import HTML


class NoteTest(TestCase):
    def test_notebook(self):
        n = None
        for nb in Notebook.query.get():
            n = Note.query.is_notebook(nb).get_one()
            if n is not None:
                break
        self.assertIsNotNone(n)

#         nb = testdata.random.choice(list(Notebook.query.get()))
#         n = Note.query.is_notebook(nb).get_one()

        nb2 = n.notebook
        self.assertEqual(nb.guid, nb2.guid)

    def test_notebook_set(self):
        n = Note()
        nb = testdata.random.choice(list(Notebook.query.get()))

        self.assertIsNone(n.notebook_guid)
        n.notebook_guid = nb.guid
        self.assertEqual(n.notebook_guid, nb.guid)

        nb_guid = n.notebook_guid
        n.notebook = nb
        self.assertEqual(n.notebook_guid, nb.guid)

    def test_content(self):
        n = Note()

        plain = testdata.get_words()
        n.plain = plain
        self.assertTrue(plain in n.content)

        html = "<p>{}</p>".format(testdata.get_words())
        n.html = html
        self.assertFalse(plain in n.content)
        self.assertTrue(HTML(html).plain() in n.content)

        # TODO -- test & in note

    def test_html(self):
        n = Note()
        nb = testdata.random.choice(list(Notebook.query.get()))
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

        n2 = Note.query.is_guid(n.guid).one()

    def test_crud(self):
        n = Note()
        title = testdata.get_ascii()
        plain = testdata.get_words()
        n.title = title
        n.plain = plain
        n.save()

        guid = n.guid

        n.title = testdata.get_ascii()
        n.plain = testdata.get_words()
        n.save()
        self.assertEqual(guid, n.guid)
        self.assertNotEqual(title, n.title)
        self.assertNotEqual(plain, n.plain)


class NotebookTest(TestCase):
    def get_query(self):
        return Notebook.query

    def test_crud(self):
        nb = Notebook()
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
        time.sleep(1)
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


