import os
import sys
from rle_compression import RleCompression
from filesystem_handler import Filesystem_Handler


def compress_or_extract_file(
        input_file: str, output_file: str, action_type: str = 'compress') -> None:
    """compress a single file.

    Args:
        input_file str: the file to assemble.
        output_file str: writes all output to this file.
    """
    rle_algorithem = RleCompression()
    handler = Filesystem_Handler(data_compression_algorithem=rle_algorithem, bytes_size=1)

    if action_type == 'compress':
        handler.open_output_file(output_file_path=output_file)
        handler.compress(directories=[input_file])
        handler.close_output_file()
    elif action_type == 'decompress':
        handler.decompress(compressed_file_path=input_file)


if "__main__" == __name__:
    argument_input_path = os.path.abspath(sys.argv[1])
    argument_output_path = os.path.abspath(sys.argv[2])
    argument_action_type = sys.argv[3]
    # multiple_compression = False
    # if os.path.isdir(argument_path):
    #     multiple_compression = True
    #     # files_to_compress = [
    #     #     os.path.join(argument_path, filename)
    #     #     for filename in os.listdir(argument_path)]
    # # else:
    # #     files_to_compress = [argument_path]
    # # for input_path in files_to_compress:
    # filename, extension = os.path.splitext(argument_path)
    # if extension.lower() == ".bin":
    #     output_path = filename + ".txt"
    #     action_type = 'extract'
    # else:
    #     if multiple_compression:
    #         output_path = os.path.basename(argument_path) + ".bin"

    #     else:
    #         output_path = filename + ".bin"
    #     action_type = 'compress'
    compress_or_extract_file(input_file=argument_input_path, output_file=argument_output_path, action_type=argument_action_type)
