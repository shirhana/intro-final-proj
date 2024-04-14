import os
from data_compression import DataCompression
from typing import Union


BYTES_LENGTH = 16

class Filesystem_Handler:

    def __init__(self, data_compression_algorithem: DataCompression) -> None:
        self._compress_func = data_compression_algorithem.compress_data
        self._decompress_func = data_compression_algorithem.decompress_data
        self._output_file = None

    def open_output_file(self, output_file_path: str) -> None:
        self._output_file = open(output_file_path, 'ab')

    def close_output_file(self) -> None:
        self._output_file.close()

    def read_file(self, file: str) ->  Union[str, bytes]:
        with open(file, 'rb') as f:
            return f.read()
        
    def write_file(self, file: str, data: str) -> None:
        sub_directories = os.path.dirname(file)
        if sub_directories:
            os.makedirs(sub_directories, exist_ok=True)
        with open(file, 'wb') as f:
            f.write(data)

    def compress_data_to_file(self, data: str):
        compressed_data = self._compress_func(data=data)
        self._output_file.write(len(compressed_data).to_bytes(BYTES_LENGTH, byteorder='big'))
        # self._output_file.write(compressed_data.encode('utf-8'))
        self._output_file.write(compressed_data)

    def get_decompressed_data(self, compressed_data: bytes, index:int = 0):
        compressed_len = int.from_bytes(compressed_data[index:index+BYTES_LENGTH][::-1], byteorder='little')
        next_index = BYTES_LENGTH + index + compressed_len
        compressed = compressed_data[index+BYTES_LENGTH:next_index]
        decompress_data = self._decompress_func(compressed_data=compressed)

        return decompress_data, next_index

    def compress(self, directories: list, subfolder: str = '', ignore_folders: list = [], ignore_files: list = [], ignore_extensions: list = []):
        ignore_folders = [os.path.normpath(path) for path in ignore_folders]
        # pass on each given directory
        for dir in directories:
            full_dir_path = os.path.join(subfolder, dir)
            # if it is directory to folder
            if os.path.isdir(full_dir_path):
                
                if os.path.normpath(full_dir_path) not in ignore_folders:
                    files_in_folder = os.listdir(full_dir_path)

                    # compress recursive the files which inside the directory to current folder
                    self.compress(directories=files_in_folder, subfolder=full_dir_path, ignore_files=ignore_files, ignore_extensions=ignore_extensions, ignore_folders=ignore_folders) 

            
            # if it is directory to file
            elif os.path.isfile(full_dir_path):
            
                if full_dir_path not in ignore_files and not full_dir_path.endswith(tuple(ignore_extensions)):
                    # compress full file path name
                    self.compress_data_to_file(data=full_dir_path.encode())

                    # read data from current file
                    full_file_data = self.read_file(file=full_dir_path)
                    # print(f'full_file_data: {full_file_data}')
                    
                    # compress file data
                    self.compress_data_to_file(data=full_file_data)

            else:
                pass #TODO: what should happen?


    def decompress(self, compressed_file_path: str = '', compressed_data: bytes = b'', subfolder: str = '', view_mode: bool = False):
        # TODO - check differenes between strings and bytes

        # if compressed_data is empty
        if compressed_data == b'':
            # if compressed file path was inserted ->
            #  read compressed_data from file path
            if compressed_file_path:
                compressed_data = self.read_file(
                    file=compressed_file_path
                )

                if view_mode:
                    print(f"{compressed_file_path} compressed file contains:")
                
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
        if view_mode:
            print(f'{file_path.decode()} - size [{len(file_data)}]')
        else:
            self.write_file(file=file_path, data=file_data)
        # decompress the original data recursivlly from the 
        # rest of the compressed data
        self.decompress(
            compressed_data=compressed_data[next_index:], 
            subfolder=subfolder,
            view_mode=view_mode
        )

    def decompress_files(self, directories: list, view_mode: bool = False):
        for compressed_file in directories:
            self.decompress(compressed_file_path=compressed_file, view_mode=view_mode)

    def remove_from_archive(self, input_paths: list, archive_path:str):
        count_files_removes = 0
        update_compressed_data = bytearray()
        compressed_data = self.read_file(
            file=archive_path
        )

        i = 0
        while i < len(compressed_data):
            
            # get full file path from compressed data
            file_path, next_index = self.get_decompressed_data(
                compressed_data=compressed_data,
                index=i
            )
            
            # get original file data from compressed data
            file_data, next_index = self.get_decompressed_data(
                compressed_data=compressed_data, 
                index=next_index
            )
            
            if file_path.decode().startswith(tuple(input_paths)):
                count_files_removes += 1
            else:
                update_compressed_data.extend(compressed_data[i:next_index])
            
            i = next_index
        
        self.write_file(file=archive_path, data=bytes(update_compressed_data))
        return count_files_removes
    

    def update_archive(self, input_paths: list, archive_path:str):
        self.remove_from_archive(input_paths=input_paths, archive_path=archive_path)
        self.compress(directories=input_paths)
        
        