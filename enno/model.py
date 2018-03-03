# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import datetime

#import evernote.edam.notestore.ttypes as Notebook
from evernote.edam.type.ttypes import Notebook, Note

from .query import Query, NotebookQuery
from .interface import get_interface
from .decorators import classproperty
from .compat import *
from .utils import Plain, HTML, ENML


class Enbase(object):
    @classproperty
    def interface(cls):
        return get_interface()

    @classproperty
    def query(cls):
        raise NotImplementedError()

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


class Ennote(Enbase):

    query_cls = Query

    notebook_cls = None
    """set at the very bottom of this module"""

    @classproperty
    def query(cls):
        return cls.query_cls(cls)

    @property
    def created(self):
        return self.convert_timestamp(self.__getattr__("created"))

    @property
    def updated(self):
        return self.convert_timestamp(self.__getattr__("updated"))

    @property
    def notebook(self):
        """Returns the notebook this note belongs to"""
        return self.notebook_cls.query.is_guid(self.notebookGuid).get_one()

    @notebook.setter
    def notebook(self, nb):
        self.notebookGuid = nb.guid

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

        # set the title if the html has a <title> tag and we don't have a title
#         if not self.title:
#             title = p.title
#             if title:
#                 self.title = title

#     @property
#     def note(self):
#         ret = self.note_store.getNote(self.guid, True, False, False, False)
#         self.__dict__["note"] = ret
#         return ret

    def __init__(self, note=None, **kwargs):
        if note:
            self.note = note
            self._hydrated = False
        else:
            self.note = Note()
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
                self.note = self.note_store.getNote(guid, True, False, False, False)

        return self.note

    def __getattr__(self, k):
        if k.startswith("_"):
            ret = super(Ennote, self).__getattr__(k)

        else:
            k = self.convert_key(k)
            note = self.note
            ret = getattr(self.note, k, None)

            if ret is None and not self._hydrated:
                self._hydrate()
                ret = getattr(self.note, k)

        return ret

    def __setattr__(self, k, v):
        if k.startswith("_"):
            super(Ennote, self).__setattr__(k, v)

        elif k == "note":
            super(Ennote, self).__setattr__(k, v)

        elif k in self.__dict__:
            super(Ennote, self).__setattr__(k, v)

        else:
            k = self.convert_key(k)
            if hasattr(self.note, k):
                setattr(self.note, k, v)

            else:
                super(Ennote, self).__setattr__(k, v)

    def save(self):
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

        if self.guid:
            # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_updateNotebook
            n = note_store.updateNote(self.note)

        else:
            # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_createNotebook
            n = note_store.createNote(self.note)

        self.note = n

        for k, v in orig_vals.items():
            setattr(self, k, v)

#         if k in ["title", "guid"]:
#             ret = getattr(self._note, k)
# 
#         elif not k.startswith("__"):
#             note = self.note
#             ret = getattr(self.note, k)
# 
#         else:
#             raise AttributeError(k)
# 
#         return ret


class Ennotebook(Enbase):
    """
    https://dev.evernote.com/doc/reference/Types.html#Struct_Notebook
    """
    query_cls = NotebookQuery

    @classproperty
    def query(cls):
        return cls.query_cls(cls)

    @property
    def notes(self):
        """Returns all the notes in this notebook"""

    @property
    def created(self):
        ret = None
        ts = self.notebook.serviceCreated
        if ts:
            ts = int(str(ts)[0:-3])
            ret = datetime.datetime.utcfromtimestamp(ts)
        return ret

    @property
    def updated(self):
        ret = None
        ts = self.notebook.serviceUpdated
        if ts:
            ts = int(str(ts)[0:-3])
            ret = datetime.datetime.utcfromtimestamp(ts)
        return ret

    @property
    def guid(self):
        return self.notebook.guid

    @property
    def name(self):
        return self.notebook.name

    @name.setter
    def name(self, v):
        self.notebook.name = v

    @property
    def default(self):
        return self.notebook.defaultNotebook

    @default.setter
    def default(self, v):
        self.notebook.default = bool(v)

    def __init__(self, notebook=None, **kwargs):
        self.notebook = Notebook() if notebook is None else notebook
        for k, v in kwargs.items():
            setattr(self, k, v)

#     def is_default(self):
#         return self.default

    def save(self):

        orig_name = self.notebook.name
        note_store = self.note_store

        # handle unicode problems
        if is_py2:
            if isinstance(orig_name, unicode):
                self.notebook.name = orig_name.encode("utf-8")

        if self.guid:
            # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_updateNotebook
            note_store.updateNotebook(self.notebook)
            # ugh, why would they not return the updated notebook? Sigh
            nb = note_store.getNotebook(self.guid)
            self.notebook = nb

        else:
            # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_createNotebook
            nb = note_store.createNotebook(self.notebook)
            self.notebook = nb

        self.notebook.name = orig_name

    def count(self):
        """Return how many notes are in this notebook"""
        # TODO -- this can be done by running a note query with just the
        # notebook and then call noteCounts or something like that

        # http://dev.evernote.com/doc/reference/NoteStore.html#Fn_NoteStore_findNoteCounts (use this one)
        # http://dev.evernote.com/doc/reference/NoteStore.html#Struct_NoteCollectionCounts



Ennote.notebook_cls = Ennotebook
Ennotebook.note_cls = Ennote

