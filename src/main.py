import os
import sys
import argparse
import time
from utility import print_colored, Colors, get_compression_ratio, create_cefd_banner
from rle_compression_binary import RleCompression
from filesystem_handler import Filesystem_Handler


def compress_to_file(handler, input_paths, output_path, action_type):
    # Record the start time
    start_time = time.time()
    handler.open_output_file(output_file_path=output_path)
    handler.compress(directories=input_paths)
    handler.close_output_file()

    # Calculate the elapsed time
    finish_time = time.time()
    elapsed_time = float(finish_time - start_time)

    compression_info(original_paths=input_paths, output_path=output_path, elapsed_time=elapsed_time, action_type=action_type)

def get_folder_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def display_elapsed_time(action_type: str, elapsed_time: float = 0.0):
    clrs = Colors()
    time_str = f"{elapsed_time} seconds"
    print(f'Time of {action_type}  -->{print_colored(text=time_str,  color=clrs.purple)}')


def compression_info(original_paths, output_path: str = "", elapsed_time: float = 0.0, action_type: str = 'compress'):
    total_size = 0
    for path in original_paths:
        if os.path.isdir(path):
            total_size += get_folder_size(path=path)
        elif os.path.isfile(path):
            total_size += int(os.path.getsize(path))

    clrs = Colors()
    print(
        f"Compressed Size: {print_colored(text=os.path.getsize(output_path),  color=clrs.yellow)} bytes"
    )
    if action_type == 'compress':
        print(f'Delta Size --> {print_colored(int(total_size - os.path.getsize(output_path)), color=clrs.cyan)}')
        ratio = int(total_size/os.path.getsize(output_path))
        ratio_color = print_colored(text=f"{ratio}%",  color=clrs.green)
        print(
            f"Compressed Ratio: {ratio_color}"
        )

    if action_type == 'add-to-archive':
        print(f'Added Files Size --> {print_colored(total_size, color=clrs.cyan)}')

    display_elapsed_time(action_type=action_type, elapsed_time=elapsed_time)


def run(
        input_paths: list, output_path: str, action_type: str = 'compress') -> None:
    """compress a single file.

    Args:
        input_file str: the file to assemble.
        output_file str: writes all output to this file.
    """
    validate_args(output_path=output_path, action_type=action_type)
    # TODO - create ENUM for action types
    rle_algorithem = RleCompression()
    handler = Filesystem_Handler(data_compression_algorithem=rle_algorithem, bytes_size=1)

    if action_type == 'compress':
        if os.path.isfile(output_path):
            os.remove(output_path)

        compress_to_file(handler=handler, input_paths=input_paths, output_path=output_path, action_type=action_type)
         
        
    elif action_type == 'decompress':
        # Record the start time
        start_time = time.time()
        handler.decompress_files(directories=input_paths)

        # Calculate the elapsed time
        finish_time = time.time()
        elapsed_time = float(finish_time - start_time)

        display_elapsed_time(action_type=action_type, elapsed_time=elapsed_time)
        
    elif action_type == 'add-to-archive':
        compress_to_file(handler=handler, input_paths=input_paths, output_path=output_path, action_type=action_type)
        
    elif action_type == 'view-archive':
        handler.decompress_files(directories=input_paths, view_mode=True)


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
        choices=['compress', 'decompress', 'add-to-archive', 'view-archive'], 
        help='Choose one option of action type from the list',
        required=True
    )

    # Parse the command-line arguments
    args = parser.parse_args()
    print(create_cefd_banner(action_type=args.action_type))

    run(
        input_paths=args.input_paths_list, 
        output_path=args.output_path, 
        action_type=args.action_type
    )
    
    # compress_or_extract_file(input_file=argument_input_path, output_file=argument_output_path, action_type=argument_action_type)
