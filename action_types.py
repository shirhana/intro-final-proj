from enum import Enum


class ActionTypes(Enum):
    COMPRESS = 'compress'
    DECOMPRESS = 'decompress'
    ADD_TO_ARCHIVE = 'add-to-archive'
    UPDATE_ARCHIVE = 'update-archive'
    REMOVE_FROM_ARCHIVE = 'remove-from-archive'
    VIEW_ARCHIVE = 'view-archive'
    CHECK_VALIDATION = 'is-valid-archive'
