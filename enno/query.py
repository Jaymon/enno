# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import re
import datetime
import copy

import evernote.edam.notestore.ttypes as NoteStore 

from .compat import *
from .utils import Plain


class Iterator(list):
    def __init__(self, items, response, model_class, query):
        self.response = response
        self.model_class = model_class
        self.query = query
        self.all_items = False
        self.item_count = len(items)
        super(Iterator, self).__init__(items)

    def __len__(self):
        return self.response.totalNotes if self.all_items else super(Iterator, self).__len__()

    def __getslice__(self, i, j): # py2
        return self.__getitem__(slice(i, j))

    def _getitem(self, index):
        if isinstance(index, slice):
            # https://docs.python.org/2/library/functions.html?highlight=slice%20object#slice
            # https://stackoverflow.com/a/16033058/5006
            instance = type(self)(
                items=super(Iterator, self).__getitem__(index),
                response=self.response,
                model_class=self.model_class,
                query=self.query
            )

        else:
            note = super(Iterator, self).__getitem__(index)
            instance = self.model_class(note)

        return instance

    def _allitem(self, index):
        if isinstance(index, slice):
            offset = index.start + self.query.bounds["offset"]
            limit = index.stop - index.start
            instance = self.query.copy().offset(offset).limit(limit).get()
            if index.step:
                instance = instance[0::index.step]

        else:
            if index > len(self):
                raise IndexError("list index out of range")

            if index < 0:
                index = len(self) + index

            if index < self.item_count:
                instance = self._getitem(index)

            else:
                offset = index + self.query.bounds["offset"]
                note = self.query.copy().offset(offset).get_one()
                instance = self.model_class(note)

        return instance

    def __getitem__(self, index):
        if self.all_items:
            instance = self._allitem(index)

        else:
            instance = self._getitem(index)

        return instance

    def __iter__(self):
        limit = self.query.bounds["limit"]
        offset = self.query.bounds["offset"]
        total = len(self) + offset
        itr = self
        while offset < total:
            item_count = itr.item_count
            for index in range(item_count):
                yield itr[index]

            offset += limit
            if self.all_items and offset < total:
                itr = self.query.copy().offset(offset).get()


class NoteQuery(object):
    """
    searching notes:
        https://dev.evernote.com/doc/articles/searching_notes.php
        https://dev.evernote.com/doc/articles/search.php (python examples)
        https://dev.evernote.com/doc/articles/search_grammar.php

    all Thrift functions:
        http://dev.evernote.com/doc/reference/
    """
    def __init__(self, note_class):
        self.model_class = note_class
        self.interface = note_class.interface
        self.note_store = self.interface.get_note_store()
        self.note_filter = NoteStore.NoteFilter()
        self.guids = set()

        self.spec = NoteStore.NotesMetadataResultSpec()
        # These are the spec instance properties you can set:
        # includeUpdateSequenceNum
        # includeDeleted
        # includeContentLength
        # includeTitle
        # includeNotebookGuid
        # includeTagGuids
        # includeLargestResourceSize
        # includeAttributes
        # includeLargestResourceMime
        # includeCreated
        # includeUpdated
        self.spec.includeTitle = True
        self.spec.includeCreated = True
        self.spec.includeUpdated = True
        self.spec.includeNotebookGuid = True
        self.spec.includeTagGuids = True

        self.bounds = {
            "limit": 50,
            "offset": 0
        }

    def desc(self):
        self.note_filter.ascending = False
        return self

    def asc(self):
        self.note_filter.ascending = True
        return self

    def limit(self, limit):
        self.bounds["limit"] = int(limit)
        return self

    def offset(self, offset):
        self.bounds["offset"] = int(offset)
        return self

    def is_guid(self, guid):
        self.guids.clear()
        self.guids.add(guid)
        return self

    def in_guid(self, *guids):
        self.guids.update(guids)
        return self

    def is_notebook(self, nb):
        if hasattr(nb, "guid"):
            self.note_filter.notebookGuid = nb.guid

        elif len(nb) == 36 and re.match("^[a-f0-9\-]{36}$", nb):
            self.note_filter.notebookGuid = nb

        else:
            name = nb
            nb = self.model_class.notebook_class.query.is_name(name).one()

            if nb is None:
                raise ValueError("Notebook {} was not found".format(Plain(name)))

            else:
                self.note_filter.notebookGuid = nb.guid

        return self

    def any_note(self, *words):
        ws = self._format_words(words, prefix="any:")
        return self._append_words(ws)

    def nany_note(self, *words):
        ws = self._format_words(words, prefix="-any:")
        return self._append_words(ws)

    def contains(self, *words): return self.in_words(*words)
    def in_note(self, *words):
        ws = self._format_words(words)
        return self._append_words(ws)

    def excludes(self, *words): return self.nin_words(*words) # omits?
    def nin_note(self, *words):
        ws = self._format_words(words, prefix="-")
        return self._append_words(ws)

    def in_title(self, *words):
        ws = self._format_words(words, prefix="intitle:")
        return self._append_words(ws)

    def nin_title(self, *words):
        ws = self._format_words(words, prefix="-intitle:")
        return self._append_words(ws)

    def gt_created(self, dt):
        return self._format_time(dt, prefix="created:")

    def lt_created(self, dt):
        return self._format_time(dt, prefix="-created:")

    def after(self, dt): return self.gt_updated(dt)
    def gt_updated(self, dt):
        return self._format_time(dt, prefix="updated:")

    def before(self, dt): return self.lt_updated(dt)
    def lt_updated(self, dt):
        return self._format_time(dt, prefix="-updated:")

    def today(self): return self.days(0)
    def days(self, count=0):
        return self._format_relative("day", count)

    def weeks(self, count=0):
        return self._format_relative("week", count)

    def months(self, count=0):
        return self._format_relative("month", count)

    def years(self, count=0):
        return self._format_relative("year", count)

    def get(self, limit=0, offset=0):
        if self.guids:
            items = []
            #pout.i(self.note_store._client)
            for guid in self.guids:
                # python evernote doesn't seem to have this method:
                # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_getNoteWithResultSpec
                #items.append(self.note_store.getNoteWithResultSpec(guid, self.spec))
                # so we will use the deprecated method:
                # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_getNote
                items.append(self.note_store.getNote(
                    guid,
                    False,
                    False,
                    False,
                    False,
                ))

            # TODO -- should this take into account asc and desc?

            # ducktype the response for the iterator
            class Response(object): pass
            response = Response()
            response.totalNotes = len(self.guids)

        else:
            if limit: self.limit(limit)
            if offset: self.offset(offset)

            # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_findNotesMetadata
            response = self.note_store.findNotesMetadata(
                self.note_filter,
                self.bounds["offset"],
                self.bounds["limit"],
                self.spec
            )
            items = response.notes

        return Iterator(
            items=items,
            response=response,
            model_class=self.model_class,
            query=self
        )

    def all(self):
        itr = self.get(limit=250)
        itr.all_items = True
        return itr

    def get_one(self): return self.one()
    def one(self):
        for n in self.get(limit=1):
            return n

    def search(self, q):
        return self._append_words(q)

    def count(self):
        """Count all the notes for the given query"""
        # https://discussion.evernote.com/topic/62382-count-notes-matching-a-filter/?do=findComment&comment=286689
        # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_findNoteCounts (use this one)
        ret = 0
        response = self.note_store.findNoteCounts(self.note_filter, False)
        for count in response.notebookCounts.values():
            ret += count
        return ret

    def copy(self):
        """nice handy wrapper around the deepcopy"""
        return copy.deepcopy(self)

    def __deepcopy__(self, memodict={}):
        instance = type(self)(self.model_class)
        ignore_keys = set(["interface", "note_store"])
        for key, val in self.__dict__.items():
            if key not in ignore_keys:
                setattr(instance, key, copy.deepcopy(val, memodict))
        return instance

    def _format_relative(self, relative, count):
        v = "{}-{}".format(relative, count) if count else relative
        return self._format_time(v, prefix="updated:")

    def _format_time(self, dt, prefix):
        ws = ""
        if isinstance(dt, basestring):
            ws = self._format_words([dt], prefix=prefix)

        elif isinstance(dt, datetime.date):
            ws = self._format_words([datetime.strftime("%Y%m%d")], prefix=prefix)

        elif isinstance(dt, datetime.datetime):
            ws = self._format_words([datetime.strftime("%Y%m%dT%H%M%S")], prefix=prefix)

        else:
            raise ValueError("Not sure how to handle date value")

        return self._append_words(ws)

    def _format_words(self, words, prefix=""):
        ret = []
        for w in words:
            w = w.strip()
            if " " in w:
                w = '"{}"'.format(w)
            ret.append(w)
        return prefix + " {}".format(prefix).join(ret)

    def _append_words(self, words):
        if not words: return self

        fwords = self.note_filter.words
        if not fwords:
            fwords = ""

        if fwords:
            fwords += " "

        fwords += words
        self.note_filter.words = fwords
        return self


class NotebookQuery(object):
    def __init__(self, model_class):
        self.model_class = model_class
        self.interface = model_class.interface
        self.note_store = self.interface.get_note_store()
        self.filter_cbs = []
        self.sort_kwargs = {}
        self.guids = set()
        self.bounds = {"limit": 0}

    def _filter(self, v):
        ret = True
        for filter_cb in self.filter_cbs:
            if not filter_cb(v):
                ret = False
                break
        return ret

    def asc(self):
        # https://docs.python.org/3/howto/sorting.html#sortinghowto
        self.sort_kwargs = {"key": lambda x: x.updated, "reverse": False}
        return self

    def desc(self):
        self.asc()
        self.sort_kwargs["reverse"] = True
        return self

    def startswith_name(self, name):
        name = Plain(name).lower()
        self.filter_cbs.append(lambda x: Plain(x.name).lower().startswith(name))
        return self

    def endswith_name(self, name):
        name = Plain(name).lower()
        self.filter_cbs.append(lambda x: Plain(x.name).lower().endswith(name))
        return self

    def contains_name(self, name):
        name = Plain(name).lower()
        self.filter_cbs.append(lambda x: name in Plain(x.name).lower())
        return self

    def is_name(self, name):
        name = Plain(name).lower()
        self.filter_cbs.append(lambda x: name == Plain(x.name).lower())
        return self

    def is_guid(self, guid):
        self.guids.clear()
        self.guids.add(guid)
        #self.filter_cbs.append(lambda x: guid == x.guid)
        return self

    def in_guid(self, *guids):
        self.guids.update(guids)
        return self

    def filter(self, callback):
        self.filter_cbs.append(callback)
        return self

    def limit(self, limit):
        self.bounds["limit"] = int(limit)
        return self

    def get_guid(self, guid):
        model = self.note_store.getNotebook(guid)
        return self._create_model(model) if model else None

    def _get_list(self):
        return self.note_store.listNotebooks()

    def _create_model(self, model):
        return self.model_class(model)

    def get(self):
        limit = self.bounds["limit"]
        count = 0

        if len(self.guids) == 1:
            model = self.get_guid(list(self.guids)[0])
            if model is not None:
                yield model

        else:
            ret = []
            for enb in self._get_list():
                nb = self._create_model(enb)

                if self.guids:
                    if nb.guid in self.guids and self._filter(nb):
                        if self.sort_kwargs:
                            ret.append(nb)
                        else:
                            yield nb

                else:
                    if self._filter(nb):
                        if self.sort_kwargs:
                            ret.append(nb)
                        else:
                            yield nb

                count += 1
                if limit and count == limit:
                    break

            if ret:
                if self.sort_kwargs:
                    ret.sort(**self.sort_kwargs)
                    for nb in ret:
                        yield nb

    def get_one(self): return self.one()
    def one(self):
        for instance in self.get():
            return instance

    def __iter__(self):
        return self.get()

    def count(self):
        count = 0
        for _ in self.get():
            count += 1
        return count


class TagQuery(NotebookQuery):
    def get_guid(self, guid):
        # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_getTag
        model = self.note_store.getTag(guid)
        return self._create_model(model) if model else None

    def _get_list(self):
        # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_listTags
        return self.note_store.listTags()


