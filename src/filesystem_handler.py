import os
from data_compression import DataCompression
from typing import Union


BYTES_LENGTH = 4

class Filesystem_Handler:

    def __init__(self, data_compression_algorithem: DataCompression, bytes_size) -> None:
        self._compress_func = data_compression_algorithem.compress_data
        self._decompress_func = data_compression_algorithem.decompress_data
        self._bytes_size = bytes_size
        self._output_file = None

    def open_output_file(self, output_file_path: str) -> None:
        self._output_file = open(output_file_path, 'ab')

    def close_output_file(self) -> None:
        self._output_file.close()

    def read_file(self, file: str, mode: str = 'rb') ->  Union[str, bytes]:
        with open(file, mode) as f:
            return f.read()
        
    def write_file(self, file: str, data: str) -> None:
        sub_directories = os.path.dirname(file)
        if sub_directories:
            os.makedirs(sub_directories, exist_ok=True)
        with open(file, 'wt') as f:
            f.write(data)

    def compress_data_to_file(self, data: str):
        compressed_data = self._compress_func(data=data, bytes_size=self._bytes_size)
        self._output_file.write(len(compressed_data).to_bytes(BYTES_LENGTH, byteorder='big'))
        self._output_file.write(compressed_data.encode('utf-8'))

    def get_decompressed_data(self, compressed_data: bytes, index:int = 0):
        index += BYTES_LENGTH - 1
        compressed_len = compressed_data[index]
        next_index = 1 + index + compressed_len
        compressed = compressed_data[index+1:next_index]
        decompress_data = self._decompress_func(compressed_data=compressed, bytes_size=self._bytes_size)

        return decompress_data, next_index

    def compress(self, directories: list, subfolder: str = ''):
            # pass on each given directory
            for dir in directories:
                full_dir_path = os.path.join(subfolder, dir)

                # if it is directory to folder
                if os.path.isdir(full_dir_path):
                    files_in_folder = os.listdir(full_dir_path)

                    # compress recursive the files which inside the directory to current folder
                    current_folder = os.path.join(subfolder, full_dir_path)
                    self.compress(directories=files_in_folder, subfolder=current_folder) 

                # if it is directory to file
                elif os.path.isfile(full_dir_path):

                    # compress full file path name
                    self.compress_data_to_file(data=full_dir_path)

                    # read data from current file
                    full_file_data = self.read_file(file=full_dir_path)
                    
                    # compress file data
                    self.compress_data_to_file(data=full_file_data)

                else:
                    pass #TODO: what should happen?


    def decompress(self, compressed_file_path: str = '', compressed_data: bytes = b'', subfolder: str = ''):
        # TODO - check differenes between strings and bytes

        # if compressed_data is empty
        if compressed_data == b'':
            # if compressed file path was inserted ->
            #  read compressed_data from file path
            if compressed_file_path:
                compressed_data = self.read_file(
                    file=compressed_file_path, 
                    mode='rb'
                )
                
            else: 
                return # TODO - think of another way

        # get full file path from compressed data
        file_path, next_index = self.get_decompressed_data(
            compressed_data=compressed_data
        )
        
        # get original file data from compressed data
        file_data, next_index = self.get_decompressed_data(
            compressed_data=compressed_data, 
            index=next_index
        )

        # TODO - check if supposed to be written inside of a folder
        print(f'will write data: [{file_data}] into file: {file_path}')
        self.write_file(file=file_path, data=file_data)
        # decompress the original data recursivlly from the 
        # rest of the compressed data
        self.decompress(
            compressed_data=compressed_data[next_index:], 
            subfolder=subfolder
        )
