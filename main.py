import os
import argparse
from func_timeout import func_timeout, FunctionTimedOut
from utility import create_cefd_banner
from filesystem_handler import FilesystemHandler
from display_action_info import DisplayActionInfo
from action_types import ActionTypes
from compression_types import CompressionTypes


def run(
    input_paths: list,
    output_path: str,
    action_type: str,
    compression_type: str = "rle",
    bytes_size: int = 2,
    ignore_files: list = [],
    ignore_folders: list = [],
    ignore_extensions: list = [],
    timeout_seconds: int = 300,
) -> None:
    """Run the specified action with compression and decompression options.

    Args:
        input_paths (list): List of paths to files or folders.
        output_path (str): Path to the output file or directory.
        action_type (str): Type of action to perform.
        compression_type (str, optional): Type of compression algorithm.
        Defaults to 'rle'.
        bytes_size (int, optional): Size of bytes for compression.
        Defaults to 2.
        ignore_files (list, optional): List of files to ignore during
        compression. Defaults to [].
        ignore_folders (list, optional): List of folders to ignore during
        compression. Defaults to [].
        ignore_extensions (list, optional): List of file extensions to
        ignore during compression. Defaults to [].
    """
    validate_args(output_path=output_path, action_type=action_type)

    handler = define_handler(
        compression_type=compression_type, bytes_size=bytes_size)

    display_info = DisplayActionInfo(action_type=action_type,
        input_paths=input_paths, output_path=output_path)
    result = ""
    valid = True

    if action_type == ActionTypes.COMPRESS.value:
        handle_compress_action(handler=handler, input_paths=input_paths, 
        output_path=output_path, ignore_folders=ignore_folders, 
        ignore_files=ignore_files, ignore_extensions=ignore_extensions)

    elif action_type == ActionTypes.DECOMPRESS.value:
        error_msg = handle_decompress_action_with_timeout(
            timeout_seconds=timeout_seconds, handler=handler, 
            input_paths=input_paths, output_path=output_path)

        valid = display_info.alert(error_msg=error_msg)
    elif action_type == ActionTypes.REMOVE_FROM_ARCHIVE.value:
        result = handler.remove_from_archive(
            input_paths=input_paths, archive_path=output_path)

    elif action_type == ActionTypes.UPDATE_ARCHIVE.value:
        handler.open_output_file(output_file_path=output_path)
        result = handler.update_archive(
            input_paths=input_paths, archive_path=output_path)
        handler.close_output_file()

    elif action_type == ActionTypes.VIEW_ARCHIVE.value:
        error_msg = handler.decompress_files(
            directories=input_paths, view_mode=True)
        valid = display_info.alert(error_msg)

    elif action_type == ActionTypes.CHECK_VALIDATION.value:
        result = handler.check_validation(archive_paths=input_paths)
        display_info.alert(result)

    if valid:
        display_info.show(
            result=result,
            compression_algorithem=handler.get_compression_algorithem_name())


def define_handler(compression_type, bytes_size):
    """Define a compression handler based on the specified compression type.

    Args:
        compression_type (str): The type of compression algorithm.
        bytes_size (int): The number of bytes to process at a time.

    Returns:
        FilesystemHandler: The initialized filesystem handler object.
    
    Raises:
        Exception: If the compression_type is not recognized.
    """

    if compression_type == CompressionTypes.RLE.name.lower():
        compression_algorithem = CompressionTypes.RLE.value(
            bytes_size=bytes_size
        )
    elif compression_type == CompressionTypes.HUFFMAN.name.lower():
        compression_algorithem = CompressionTypes.HUFFMAN.value()
    elif compression_type == CompressionTypes.LZ.name.lower():
        compression_algorithem = CompressionTypes.LZ.value()
    else:
        abort_msg = f"Error- {compression_type} must be one of: "
        abort_msg += f"{[member.name.lower() for member in CompressionTypes]}"
        raise Exception(abort_msg)

    handler = FilesystemHandler(
        data_compression_algorithem=compression_algorithem
    )

    return handler


def handle_decompress_action_with_timeout(
        timeout_seconds: int, handler: FilesystemHandler, 
        input_paths: list, output_path: str) -> bool:
    """Handle decompression action with a timeout.

    Args:
        timeout_seconds (int): The timeout duration in seconds.
        handler (FilesystemHandler): The filesystem handler object.
        input_paths (list): List of input file paths to decompress.
        output_path (str): Output path for the decompressed files.

    Returns:
        bool: True if decompression succeeds, False otherwise.
    """
    try:
        error_msg = func_timeout(
            timeout_seconds, handler.decompress_files, 
            args=(input_paths, output_path))
    except FunctionTimedOut:
        error_msg = f"Decompress execution timed out "
        error_msg += f"[{timeout_seconds} seconds]."
    return error_msg 


def handle_compress_action(
        handler, input_paths, output_path, ignore_folders, 
        ignore_files, ignore_extensions) -> None:
    """Handle compression action.

    Args:
        handler (FilesystemHandler): The filesystem handler object.
        input_paths (list): List of input paths to compress.
        output_path (str): Output path for the compressed file.
        ignore_folders (list): List of folder names to ignore during compression.
        ignore_files (list): List of file names to ignore during compression.
        ignore_extensions (list): List of file extensions to ignore during compression.
    """
    if os.path.isfile(output_path):
        os.remove(output_path)

    handler.open_output_file(output_file_path=output_path)
    handler.compress(
        directories=input_paths,ignore_folders=ignore_folders,
        ignore_extensions=ignore_extensions,ignore_files=ignore_files,
        init_compression=True,)
    handler.close_output_file()


def validate_args(output_path: str, action_type: str) -> None:
    """Validate the command-line arguments.

    Args:
        output_path (str): Path to the output file or directory.
        action_type (str): Type of action to perform.
    Raises:
        Exception: If validation fails.
    """
    error_msg = ""

    if action_type in [ActionTypes.COMPRESS.value] and not output_path:
        error_msg = f"Error - missing output path parameter."

    elif action_type in [
        ActionTypes.REMOVE_FROM_ARCHIVE.value,
        ActionTypes.UPDATE_ARCHIVE.value,
    ] and not os.path.isfile(output_path):
        error_msg = f"Error - output path: [{output_path}] "
        error_msg += "does not exist as file path."

    elif action_type == ActionTypes.DECOMPRESS.value:
        if output_path and not os.path.isdir(output_path):
            error_msg = f"Error - output_path: {output_path} is invalid."

    if error_msg:
        raise Exception(error_msg)


if "__main__" == __name__:
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Compression parameters")

    # Add optional parameters
    parser.add_argument(
        "--input_paths_list",
        metavar="input_paths_list",
        type=str,
        nargs="+",
        help="list of paths to files or folders",
        required=True,
    )
    parser.add_argument(
        "--output_path",
        metavar="output_path",
        default="",
        type=str,
        help="path to output file",
    )

    parser.add_argument(
        "--compression_type",
        metavar="compression_type",
        choices=[member.name.lower() for member in CompressionTypes],
        help="Choose your wanted algorithem for compression",
        required=False,
        default="rle",
    )

    parser.add_argument(
        "--action_type",
        metavar="action_type",
        choices=[member.value.lower() for member in ActionTypes],
        help="Choose one option of action type from the list",
        required=True,
    )

    parser.add_argument(
        "--bytes_size",
        metavar="bytes_size",
        type=int,
        default=2,
        help="Choose bytes size of your compression",
    )

    parser.add_argument(
        "--ignore_files",
        metavar="ignore_files",
        type=str,
        nargs="+",
        help="list of files that will be ignored while compression",
        required=False,
        default=[],
    )

    parser.add_argument(
        "--ignore_folders",
        metavar="ignore_folders",
        type=str,
        nargs="+",
        help="list of folders that will be ignored while compression",
        required=False,
        default=[],
    )

    parser.add_argument(
        "--ignore_extensions",
        metavar="ignore_extensions",
        type=str,
        nargs="+",
        help="list of extensions that will be ignored while compression",
        required=False,
        default=[],
    )

    parser.add_argument(
        "--timeout",
        metavar="timeout",
        type=int,
        help="timeout in seconds to execute decompress function",
        default=300,
        required=False
    )

    # Parse the command-line arguments
    args = parser.parse_args()
    print(create_cefd_banner())
    run(
        input_paths=args.input_paths_list,
        output_path=args.output_path,
        action_type=args.action_type,
        compression_type=args.compression_type,
        bytes_size=args.bytes_size,
        ignore_files=args.ignore_files,
        ignore_folders=args.ignore_folders,
        ignore_extensions=args.ignore_extensions,
        timeout_seconds=args.timeout
    )
