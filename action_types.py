from enum import Enum


class ActionTypes(Enum):
    """An enumeration defining various actions for managing archives.

    This enum maps action names to their corresponding functionality.

    Attributes:
        COMPRESS (str): Represents the action to compress data.
        DECOMPRESS (str): Represents the action to decompress data.
        UPDATE_ARCHIVE (str): Represents the action to update data in an archive.
        REMOVE_FROM_ARCHIVE (str): Represents the action to remove data from an archive.
        VIEW_ARCHIVE (str): Represents the action to view data in an archive.
        CHECK_VALIDATION (str): Represents the action to check the validity of an archive.
    """

    COMPRESS = "compress"
    DECOMPRESS = "decompress"
    UPDATE_ARCHIVE = "update-archive"
    REMOVE_FROM_ARCHIVE = "remove-from-archive"
    VIEW_ARCHIVE = "view-archive"
    CHECK_VALIDATION = "is-valid-archive"
