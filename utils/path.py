import os

from math import log2
from time import ctime


def is_valid_subpath(relative_directory: str, base_directory: str) -> bool:
    """
    Check if a relative directory is a valid subpath of the base directory.

    Args:
        relative_directory (str): The relative directory path.
        base_directory (str): The base directory path.

    Returns:
        bool: True if the relative directory is a valid subpath of the 
        base directory, False otherwise.
    """
    in_question = os.path.abspath(
        os.path.join(base_directory, relative_directory)
    )
    return (
        os.path.commonprefix([base_directory, in_question]) == base_directory
    )


def is_valid_upload_path(path: str, base_directory: str) -> bool:
    """
    Check if a path is a valid upload path within the base directory.

    Args:
        path (str): The path to check.
        base_directory (str): The base directory path.

    Returns:
        bool: True if the path is a valid upload path within 
        the base directory, False otherwise.
    """
    if path == "":
        return False
    in_question = os.path.abspath(path)
    return (
        os.path.commonprefix([base_directory, in_question]) == base_directory
    )


def get_relative_path(file_path: str, base_directory: str) -> str:
    """
    Get the relative path of a file or directory with respect to 
    the base directory.

    Args:
        file_path (str): The file or directory path.
        base_directory (str): The base directory path.

    Returns:
        str: The relative path of the file or directory.
    """
    return file_path.split(os.path.commonprefix([base_directory, file_path]))[
        1
    ][1:]


def human_readable_file_size(size: int):
    """
    Convert a file size to a human-readable format.

    Args:
        size (int): The size in bytes.

    Returns:
        str: The human-readable file size string.
    """
    _suffixes = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]
    order = int(log2(size) / 10) if size else 0
    return "{:.4g} {}".format(size / (1 << (order * 10)), _suffixes[order])


def process_files(directory_files: list, base_directory: str) -> list:
    """
    Process a list of directory files into a structured format.

    Args:
        directory_files (list): List of directory files.
        base_directory (str): The base directory path.

    Returns:
        list: Processed list of files with metadata.
    """
    files = []
    for file in directory_files:
        if file.is_dir():
            size = "--"
            size_sort = -1
        else:
            size = human_readable_file_size(file.stat().st_size)
            size_sort = file.stat().st_size
        files.append(
            {
                "name": file.name,
                "is_dir": file.is_dir(),
                "rel_path": get_relative_path(file.path, base_directory),
                "size": size,
                "size_sort": size_sort,
                "last_modified": ctime(file.stat().st_mtime),
                "last_modified_sort": file.stat().st_mtime,
            }
        )
    return files


def get_parent_directory(path: str, base_directory: str) -> str:
    """
    Get the parent directory of a path with respect to the base directory.

    Args:
        path (str): The path to get the parent directory for.
        base_directory (str): The base directory path.

    Returns:
        str: The parent directory path.
    """
    difference = get_relative_path(path, base_directory)
    difference_fields = difference.split("/")
    if len(difference_fields) == 1:
        return ""
    else:
        return "/".join(difference_fields[:-1])
