class NotValidCompressionAlgorithem(Exception):
    """Exception raised when an invalid compression algorithm is encountered.

    This exception is raised when attempting to use a compression 
    algorithm that is not supported or recognized.
    """
    pass


class MissingInputPath(Exception):
    """Exception raised when a required input path is missing.

    This exception is raised when an operation expects a path 
    as input but receives None or an empty path.
    """
    pass