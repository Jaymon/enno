# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import

from evernote.api.client import EvernoteClient
import evernote.edam.notestore.ttypes as NoteStore
import evernote.edam.userstore.constants as UserStoreConstants

from . import environ
from .query import Query, NotebookQuery


__version__ = "0.0.1"



class Ennotes(list):
    def __init__(self, response, note_store):
        self.response = response
        self.note_store = note_store
        super(Ennotes, self).__init__(response.notes)

    def __getitem__(self, index):
        note = super(Ennotes, self).__getitem__(index)
        return Ennote(note, self.note_store)

        #guid = note.guid
        #return self.note_store.getNote(guid, True, False, False, False)

        #note_guid = notes_metadata_list.notes[0].guid
        #note = note_store.getNote(note_guid, True, False, False, False)



class Enno(object):
    """
    Wraps Evernote's python module: https://github.com/evernote/evernote-sdk-python/
    """
    def __init__(self, access_token, sandbox=False):
        self.client = EvernoteClient(token=access_token, sandbox=sandbox)

    def recent(self, limit):
        note_store = self.client.get_note_store()
        note_filter = NoteStore.NoteFilter()
        note_filter.ascending = False

        spec = NoteStore.NotesMetadataResultSpec()
        spec.includeTitle = True
        response = note_store.findNotesMetadata(note_filter, 0, limit, spec)
        return Ennotes(response, note_store)

    def is_latest(self):
        """Return true if using the latest Evernote API version"""
        user_store = client.get_user_store()

        ret = user_store.checkVersion(
            "{} {}".format(self.__class__.__name__, __version__),
            UserStoreConstants.EDAM_VERSION_MAJOR,
            UserStoreConstants.EDAM_VERSION_MINOR
        )
        return ret


