import os
import argparse
from utility import create_cefd_banner, timer
from rle_compression import RleCompression
from filesystem_handler import Filesystem_Handler
from display_action_info import DisplayActionInfo
from action_types import ActionTypes


def run(
        input_paths: list, output_path: str, action_type: str, bytes_size: int = 2, ignore_files: list = [],
        ignore_folders: list = [], ignore_extensions: list = []) -> None:
    """compress a single file.

    Args:
        input_file str: the file to assemble.
        output_file str: writes all output to this file.
    """
    validate_args(output_path=output_path, action_type=action_type)
    rle_algorithem = RleCompression(bytes_size=bytes_size)
    handler = Filesystem_Handler(data_compression_algorithem=rle_algorithem)

    display_info = DisplayActionInfo(action_type=action_type, input_paths=input_paths, output_path=output_path)

    if action_type == ActionTypes.COMPRESS.value:
        if os.path.isfile(output_path):
            os.remove(output_path)

        handler.open_output_file(output_file_path=output_path)
        handler.compress(directories=input_paths, ignore_folders=ignore_folders, ignore_extensions=ignore_extensions, ignore_files=ignore_files)
        handler.close_output_file()
         
    elif action_type == ActionTypes.DECOMPRESS.value:
        handler.decompress_files(directories=input_paths)
        
    elif action_type == ActionTypes.REMOVE_FROM_ARCHIVE.value:
         # Record the start time
        files_removed = handler.remove_from_archive(input_paths=input_paths, archive_path=output_path)
        print(f'{files_removed} files were removed from {output_path} archive file.')
        # Calculate the elapsed time
        
    elif action_type == ActionTypes.UPDATE_ARCHIVE.value or action_type == ActionTypes.ADD_TO_ARCHIVE.value:
        handler.open_output_file(output_file_path=output_path)
        handler.update_archive(input_paths=input_paths, archive_path=output_path)
        handler.close_output_file()

    elif action_type == ActionTypes.VIEW_ARCHIVE.value:
        handler.decompress_files(directories=input_paths, view_mode=True)

    display_info.show()


def validate_args(output_path: str, action_type: str):
    if action_type in ['compress', 'add-to-archive'] and not output_path:
        raise Exception(f'Missing output path parameter')


if "__main__" == __name__:

    parser = argparse.ArgumentParser(description='Compression parameters')

    # Add optional parameters
    parser.add_argument(
        '--input_paths_list',
        metavar='input_paths_list', 
        type=str, 
        nargs='+',
        help='list of paths to files or folders',
        required=True
    )
    parser.add_argument(
        '--output_path', 
        metavar='output_path',
        default='',
        type=str, 
        help='path to output file'
    )

    parser.add_argument(
        '--action_type', 
        metavar='action_type',
        choices=[member.value.lower() for member in ActionTypes], 
        help='Choose one option of action type from the list',
        required=True
    )

    parser.add_argument(
        '--bytes_size', 
        metavar='bytes_size',
        type=int,
        default=2,
        help='Choose bytes size of your compression',
    )

    parser.add_argument(
        '--ignore_files', 
        metavar='ignore_files', 
        type=str, 
        nargs='+',
        help='list of files that will be ignored while compression',
        required=False,
        default=[]
    )

    parser.add_argument(
        '--ignore_folders', 
        metavar='ignore_folders', 
        type=str, 
        nargs='+',
        help='list of folders that will be ignored while compression',
        required=False,
        default=[]
    )

    parser.add_argument(
        '--ignore_extensions', 
        metavar='ignore_extensions', 
        type=str, 
        nargs='+',
        help='list of files extensions that will be ignored while compression',
        required=False,
        default=[]
    )

    # Parse the command-line arguments
    args = parser.parse_args()
    print(create_cefd_banner(action_type=args.action_type))
    run(
        input_paths=args.input_paths_list, 
        output_path=args.output_path, 
        action_type=args.action_type,
        bytes_size=args.bytes_size,
        ignore_files=args.ignore_files,
        ignore_folders=args.ignore_folders,
        ignore_extensions=args.ignore_extensions
    )
    