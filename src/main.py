import os
import argparse
from utility import create_cefd_banner
from huffman_compression import HuffmanCompression
from rle_compression import RleCompression
from lempel_ziv_compression import LempelZivCompression
from filesystem_handler import Filesystem_Handler
from display_action_info import DisplayActionInfo
from action_types import ActionTypes
from compression_types import CompressionTypes


def run(
        input_paths: list, output_path: str, action_type: str, compression_type: str = 'rle', bytes_size: int = 2, ignore_files: list = [],
        ignore_folders: list = [], ignore_extensions: list = []) -> None:
    """compress a single file.

    Args:
        input_file str: the file to assemble.
        output_file str: writes all output to this file.
    """
    validate_args(output_path=output_path, action_type=action_type)
    
    if compression_type == CompressionTypes.RLE.name.lower():
        compression_algorithem = CompressionTypes.RLE.value(bytes_size=bytes_size)
    elif compression_type == CompressionTypes.HUFFMAN.name.lower():
        compression_algorithem = CompressionTypes.HUFFMAN.value()
    elif compression_type == CompressionTypes.LZ.name.lower():
        compression_algorithem = CompressionTypes.LZ.value()
    else:
        raise Exception(f"Error- {compression_type} must be one of: {[member.name.lower() for member in CompressionTypes]}")
    
    handler = Filesystem_Handler(data_compression_algorithem=compression_algorithem)

    display_info = DisplayActionInfo(action_type=action_type, input_paths=input_paths, output_path=output_path)
    result = ''
    valid = True

    if action_type == ActionTypes.COMPRESS.value:
        if os.path.isfile(output_path):
            os.remove(output_path)

        handler.open_output_file(output_file_path=output_path)
        handler.compress(directories=input_paths, ignore_folders=ignore_folders, ignore_extensions=ignore_extensions, ignore_files=ignore_files, init_compression=True)
        handler.close_output_file()
         
    elif action_type == ActionTypes.DECOMPRESS.value:
        error_msg = handler.check_validation(archive_paths=input_paths)
        valid = display_info.alert(error_msg)
        if valid:
            handler.decompress_files(directories=input_paths, output_path=output_path)
        
    elif action_type == ActionTypes.REMOVE_FROM_ARCHIVE.value:
        error_msg = handler.check_validation(archive_paths=[output_path])
        valid = display_info.alert(error_msg)
        if valid:
            result = handler.remove_from_archive(input_paths=input_paths, archive_path=output_path)
                
    elif action_type == ActionTypes.UPDATE_ARCHIVE.value or action_type == ActionTypes.ADD_TO_ARCHIVE.value:
        handler.open_output_file(output_file_path=output_path)
        handler.update_archive(input_paths=input_paths, archive_path=output_path)
        handler.close_output_file()

    elif action_type == ActionTypes.VIEW_ARCHIVE.value:
        error_msg = handler.check_validation(archive_paths=input_paths)
        valid = display_info.alert(error_msg)
        if valid:
            handler.decompress_files(directories=input_paths, view_mode=True)

    elif action_type == ActionTypes.CHECK_VALIDATION.value:
        result = handler.check_validation(archive_paths=input_paths)
        display_info.alert(result)

    if valid:
        display_info.show(result=result, compression_algorithem=handler.get_compression_algorithem_name())


def validate_args(output_path: str, action_type: str):
    if action_type in [ActionTypes.COMPRESS.value, ActionTypes.ADD_TO_ARCHIVE.value] and not output_path:
        raise Exception(f'Error - missing output path parameter.')
    elif action_type == ActionTypes.DECOMPRESS.value:
        if output_path and not os.path.isdir(output_path):
            raise Exception(f'Error - output_path: {output_path} is invalid.')


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
        '--compression_type', 
        metavar='compression_type',
        choices=[member.name.lower() for member in CompressionTypes], 
        help='Choose your wanted algorithem for compression',
        required=False,
        default="rle"
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
        compression_type=args.compression_type,
        bytes_size=args.bytes_size,
        ignore_files=args.ignore_files,
        ignore_folders=args.ignore_folders,
        ignore_extensions=args.ignore_extensions,
    )
    