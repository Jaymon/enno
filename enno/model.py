# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import datetime
import re
from collections import Sequence

#import evernote.edam.notestore.ttypes as Notebook
from evernote.edam.type.ttypes import \
    Notebook as EvernoteNotebook, \
    Note as EvernoteNote, \
    Tag as EvernoteTag
from evernote.edam.error.ttypes import EDAMUserException

from .query import NoteQuery, NotebookQuery, TagQuery
from .interface import get_interface
from .decorators import classproperty
from .compat import *
from .utils import Plain, HTML, ENML, TypeList


class Enbase(object):
    query_class = None
    """Query class that will be used to query the different child class things like
    notes or notebooks, this is set in the child classes"""

    note_class = None
    """set at the very bottom of this module"""

    notebook_class = None
    """set at the very bottom of this module"""

    tag_class = None
    """set at the very bottom of this module"""

    struct_class = None
    """This is the Evernote equivalent that each model wraps"""

    @classproperty
    def interface(cls):
        """returns the interface singleton"""
        return get_interface()

    @classproperty
    def query(cls):
        """Provide fluid interface to query things

        :returns: query.Query instance
        """
        return cls.query_class(cls)

    @property
    def note_store(self):
        ret = self.interface.get_note_store()
        self.__dict__["note_store"] = ret
        return ret

    @classmethod
    def convert_timestamp(self, ts):
        """I'm not sure what thrift is doing here, the type is I64 but it
        returns an integer that is right padded with zeroes, this method takes 
        that integer, strips off the 3 zeros and converts it to a datetime

        :param ts: int, most likely a zero right padded unix timestamp
        :returns: datetime instance
        """
        ret = None
        if ts:
            if str(ts).endswith("000"):
                ts = int(str(ts)[0:-3])
            ret = datetime.datetime.utcfromtimestamp(ts)
        return ret

    def convert_key(self, k):
        """Evernote uses camelcase for variable names, which is very unpythonic,
        so this will convert foo_bar to fooBar to match evernote so fooBar and
        foo_bar will both work

        :param k: string, the key
        :returns: string, k converted to camel case
        """
        bits = k.split("_")
        camel_bits = list(map(lambda s: s.capitalize(), bits[1:]))
        ret = "".join([bits[0]] + camel_bits)
        return ret


class Struct(Enbase):

    @property
    def notes(self):
        """Returns all the notes in this notebook"""
        #return self.note_class.query.is_notebook(self).all()
        raise NotImplementedError()

    @property
    def created(self):
        return self.convert_timestamp(self.struct.serviceCreated)

    @property
    def updated(self):
        return self.convert_timestamp(self.struct.serviceUpdated)

    @property
    def guid(self):
        return self.struct.guid

    @property
    def name(self):
        return self.struct.name

    @name.setter
    def name(self, v):
        self.struct.name = v

    def __init__(self, struct=None, **kwargs):
        self.struct = self.struct_class() if struct is None else struct
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def assure_instance(cls, mixed):
        """This just makes sure any input is a class instance we can use

        :param mixed: Struct|string, already an instance or a guid or a name
        :returns: Struct, an instance of this class
        """
        ret = mixed
        if not isinstance(mixed, cls):
            mixed = Plain(mixed)
            if len(mixed) == 36 and re.match("^[a-f0-9\-]{36}$", mixed):
                ret = cls.query.is_guid(mixed).one()

            else:
                ret = cls(name=mixed)

        return ret

    def save(self):
        orig_name = self.struct.name

        # handle unicode problems
        if is_py2:
            if isinstance(orig_name, unicode):
                self.struct.name = orig_name.encode("utf-8")

        if self.guid:
            self.update()

        else:
            try:
                self.insert()

            except EDAMUserException as e:
                if e.errorCode == 10:
                    # data conflict, this probably already exists
                    struct = self.query.is_name(self.name).one()
                    if struct is None:
                        raise

                    else:
                        self.struct = struct

        self.struct.name = orig_name

    def insert(self):
        raise NotImplementedError()

    def update(self):
        raise NotImplementedError()

    def count(self):
        """Return how many notes are in this notebook"""
        # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_findNoteCounts (use this one)
        # http://dev.evernote.com/doc/reference/NoteStore.html#Struct_NoteCollectionCounts
        #return self.note_class.query.is_notebook(self).count()
        raise NotImplementedError()

    __len__ = count


class Note(Enbase):
    """Encapsulates Evernote's raw note information in order to make it more fluid
    so you don't have to worry about things like loading the full note and unicode
    problems

    also gives you fast access to note querying using .query
    """

    query_class = NoteQuery
    """Query class that will be used to query notes"""

    struct_class = EvernoteNote

    @property
    def created(self):
        return self.convert_timestamp(self.__getattr__("created"))

    @property
    def updated(self):
        return self.convert_timestamp(self.__getattr__("updated"))

    @property
    def notebook(self):
        """Returns the notebook this note belongs to"""
        if self._notebook is None:
            guid = self.notebookGuid
            if guid:
                self._notebook = self.notebook_class.query.is_guid(guid).one()
        return self._notebook

    @notebook.setter
    def notebook(self, nb):
        if nb is None:
            self._notebook = None
            self.notebookGuid = None

        else:
            nb = self.notebook_class.assure_instance(nb)
            guid = nb.guid
            if guid:
                self.notebookGuid = guid
            self._notebook = nb

    @property
    def tags(self):
        if self._tags is None:
            self._tags = TypeList(self.tag_class.assure_instance)
            guids = self.tagGuids
            if guids:
                self._tags.extend(self.tag_class.query.in_guid(*guids).get())
        return self._tags

    @tags.setter
    def tags(self, tags):
        if tags is None:
            self.tagGuids = None
            self._tags = None

        else:
            if not isinstance(tags, Sequence):
                tags = [tags]

            self._tags = TypeList(self.tag_class.assure_instance, tags)
            guids = filter(None, (t.guid for t in self._tags))
            if guids:
                self.tagGuids = guids

    @property
    def plain(self):
        return self.content.plain()

    @plain.setter
    def plain(self, v):
        p = Plain(v)
        self.content = p.enml()

    @property
    def html(self):
        return self.content.html()

    @html.setter
    def html(self, v):
        p = HTML(v)
        self.content = p.enml()

    @property
    def content(self):
        s = self.note.content
        return ENML(s) if s else None

    @content.setter
    def content(self, v):
        self.content = ENML(v)

    def __init__(self, struct=None, **kwargs):
        self._notebook = None
        self._tags = None
        if struct:
            self.struct = struct
            self._hydrated = False
        else:
            self.struct = self.struct_class()
            self._hydrated = True

        for k, v in kwargs.items():
            setattr(self, k, v)

    def _hydrate(self):
        # avoid infinite recurrsion because self.guid will trigger __getattr__
        # again
        hydrated = self._hydrated
        self._hydrated = True
        guid = self.guid
        if self.guid:
            if not hydrated:
                self.struct = self.note_store.getNote(guid, True, False, False, False)

        return self.struct

    def __getattr__(self, k):
        if k.startswith("_"):
            ret = super(Note, self).__getattr__(k)

        else:
            k = self.convert_key(k)
            ret = getattr(self.struct, k, None)

            if ret is None and not self._hydrated:
                self._hydrate()
                ret = getattr(self.struct, k)

        return ret

    def __setattr__(self, k, v):
        if k.startswith("_"):
            super(Note, self).__setattr__(k, v)

        elif k == "struct":
            super(Note, self).__setattr__(k, v)

        elif k in self.__dict__:
            super(Note, self).__setattr__(k, v)

        else:
            k = self.convert_key(k)
            if hasattr(self.struct, k):
                setattr(self.struct, k, v)

            else:
                super(Note, self).__setattr__(k, v)

    def save(self):
        """create/update the note

        https://dev.evernote.com/doc/articles/creating_notes.php
        """
        note_store = self.note_store

        orig_keys = ["title", "content"]
        orig_vals = {}

        # handle unicode problems
        if is_py2:
            for k in orig_keys:
                ov = getattr(self, k)
                if isinstance(ov, unicode):
                    setattr(self, k, ov.encode("utf-8"))
                    orig_vals[k] = ov

        nb = self._notebook
        if nb is not None:
            if not nb.guid:
                nb.save()
                self.notebookGuid = nb.guid

        tags = self._tags
        if tags is not None:
            tag_guids = []
            for t in tags:
                if not t.guid:
                    t.save()
                tag_guids.append(t.guid)
            self.tagGuids = tag_guids

        if self.guid:
            # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_updateNotebook
            n = note_store.updateNote(self.struct)

        else:
            # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_createNotebook
            n = note_store.createNote(self.struct)

        self.struct = n

        for k, v in orig_vals.items():
            setattr(self, k, v)


class Notebook(Struct):
    """
    https://dev.evernote.com/doc/reference/Types.html#Struct_Notebook
    """
    query_class = NotebookQuery

    struct_class = EvernoteNotebook

    @property
    def notes(self):
        """Returns all the notes in this notebook"""
        return self.note_class.query.is_notebook(self).all()

    @property
    def default(self):
        return self.struct.defaultNotebook

    @default.setter
    def default(self, v):
        self.struct.default = bool(v)

    def is_default(self):
        return self.default

    def update(self):
        note_store = self.note_store

        # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_updateNotebook
        note_store.updateNotebook(self.struct)
        # ugh, why would they not return the updated notebook? Sigh
        nb = note_store.getNotebook(self.guid)
        self.struct = nb

    def insert(self):
        note_store = self.note_store
        # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_createNotebook
        nb = note_store.createNotebook(self.struct)
        self.struct = nb

    def count(self):
        """Return how many notes are in this notebook"""
        # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_findNoteCounts (use this one)
        # http://dev.evernote.com/doc/reference/NoteStore.html#Struct_NoteCollectionCounts
        return self.note_class.query.is_notebook(self).count()


class Tag(Struct):
    """
    http://dev.evernote.com/doc/reference/Types.html#Struct_Tag
    """
    query_class = TagQuery

    struct_class = EvernoteTag

    def update(self):
        note_store = self.note_store
        # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_updateTag
        note_store.updateTag(self.struct)
        tag = note_store.getTag(self.guid)
        self.struct = tag

    def insert(self):
        note_store = self.note_store
        # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_createTag
        tag = note_store.createTag(self.struct)
        self.struct = tag


Enbase.note_class = Note
Enbase.notebook_class = Notebook
Enbase.tag_class = Tag

