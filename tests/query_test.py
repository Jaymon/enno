# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
from unittest import TestCase
import random

import testdata

from enno.query import NoteQuery, NotebookQuery
from enno.model import Note, Notebook


class NotebookQueryTest(TestCase):
    def get_query(self):
        return Notebook.query

    def test_is_name(self):
        nb = random.choice(list(self.get_query().get()))

        nb1 = self.get_query().is_name(nb.name).one()
        self.assertEqual(nb.name, nb1.name)

    def test_all_names(self):
        raise self.skipTest("This uses a lot of api requests")
        nbs = list(self.get_query().get())
        for nb in nbs:
            nb1 = self.get_query().is_name(nb.name).one()
            self.assertEqual(nb.name, nb1.name)


class NoteQueryTest(TestCase):
    def get_query(self):
        return Note.query

    def test_is_guid(self):
        r1 = self.get_query().one()
        r2 = self.get_query().is_guid(r1.guid).one()
        self.assertEqual(r1.guid, r2.guid)

    def test_sort_order_1(self):
        q = self.get_query()
        r1 = q.limit(1).desc().get()
        r2 = q.limit(1).asc().get()
        self.assertNotEqual(r1[0].guid, r2[0].guid)

    def test_sort_order_2(self):
        rs = self.get_query().limit(10).desc().get()
        ts = rs[0].updated
        guid = rs[0].guid
        for r in rs[1:]:
            self.assertGreaterEqual(ts, r.updated)
            self.assertNotEqual(guid, r.guid)
            ts = r.updated
            guid = r.guid

        rs = self.get_query().limit(10).asc().get()
        ts = rs[0].updated
        guid = rs[0].guid
        for r in rs[1:]:
            self.assertLessEqual(ts, r.updated)
            self.assertNotEqual(guid, r.guid)
            ts = r.updated
            guid = r.guid

    def test_is_notebook(self):
        nb = random.choice(list(Notebook.query.get()))

        ns1 = self.get_query().is_notebook(nb.name).get()
        ns2 = self.get_query().is_notebook(nb.guid).get()
        ns3 = self.get_query().is_notebook(nb).get()
        self.assertTrue(len(ns1) == len(ns2) == len(ns3))

        for ns in [ns1, ns2, ns3]:
            for n in ns:
                self.assertEqual(nb.guid, n.notebook_guid)

        with self.assertRaises(ValueError):
            self.get_query().is_notebook(testdata.get_words())

    def test_in_nin_note(self):
        q = self.get_query().in_note("foo bar")
        self.assertEqual('"foo bar"', q.note_filter.words)

        q = self.get_query().in_note("foo bar", "che")
        self.assertEqual('"foo bar" che', q.note_filter.words)

        q = self.get_query().nin_note("foo bar")
        self.assertEqual('-"foo bar"', q.note_filter.words)

        q = self.get_query().nin_note("foo bar", "che")
        self.assertEqual('-"foo bar" -che', q.note_filter.words)

        q = self.get_query().nin_note("foo bar").in_note("che")
        self.assertEqual('-"foo bar" che', q.note_filter.words)

    def test_in_nin_title(self):
        q = self.get_query().in_title("foo bar")
        self.assertEqual('intitle:"foo bar"', q.note_filter.words)

        q = self.get_query().in_title("foo bar", "che")
        self.assertEqual('intitle:"foo bar" intitle:che', q.note_filter.words)

        q = self.get_query().nin_title("foo bar")
        self.assertEqual('-intitle:"foo bar"', q.note_filter.words)

        q = self.get_query().nin_title("foo bar", "che")
        self.assertEqual('-intitle:"foo bar" -intitle:che', q.note_filter.words)

        q = self.get_query().nin_title("foo bar").in_title("che")
        self.assertEqual('-intitle:"foo bar" intitle:che', q.note_filter.words)

    def test_count(self):
        count = self.get_query().in_note("foo").count()
        self.assertTrue(isinstance(count, int))

        count = self.get_query().count()
        self.assertLess(0, count)

    def test_all___iter__(self):
        ns = self.get_query().all()
        all_count = 0
        for n in ns:
            all_count += 1

        count = self.get_query().count()
        self.assertEqual(count, all_count)

        count -= 10
        ns = self.get_query().offset(10).all()
        all_count = 0
        for n in ns:
            all_count += 1
        self.assertEqual(count, all_count)

    def test_all___getitem__(self):
        ns = self.get_query().all()
        count = self.get_query().count()
        index = count - 10

        # regular index
        n = ns[index]
        n2 = self.get_query().offset(index).get_one()
        self.assertEqual(n.guid, n2.guid)

        # negative index
        index = -1
        n = ns[index]
        n2 = self.get_query().offset(count + index).get_one()
        self.assertEqual(n.guid, n2.guid)

        # negative slice
        ns3 = ns[count-10:-1]
        ns4 = self.get_query().offset(count - 10).limit(9).get()
        self.assertEqual(len(ns3), len(ns4))
        for i in range(len(ns4)):
            self.assertEqual(ns3[i].guid, ns4[i].guid)

        # regular slice
        ns3 = ns[count-10:count-5]
        ns4 = self.get_query().offset(count - 10).limit(5).get()
        self.assertEqual(len(ns3), len(ns4))
        for i in range(len(ns4)):
            self.assertEqual(ns3[i].guid, ns4[i].guid)

        # test indexing with an initial offset
        ns = self.get_query().offset(10).all()
        count = self.get_query().count()
        index = count - 15

        n = ns[index]
        n2 = self.get_query().offset(index).get_one()
        self.assertNotEqual(n.guid, n2.guid)

        n2 = self.get_query().offset(index + 10).get_one()
        self.assertEqual(n.guid, n2.guid)


