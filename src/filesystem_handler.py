import os
from data_compression import DataCompression
from compression_types import CompressionTypes
from typing import Union
from exceptions import *


BYTES_LENGTH = 16

class Filesystem_Handler:

    def __init__(self, data_compression_algorithem: DataCompression) -> None:
        self._compression_algorithem = None
        self._output_file = None
        self._folder_suffix = '/'

        self.set_compression_algorithem(compression_algorithem=data_compression_algorithem)

    def get_compression_algorithem_name(self) -> str:
        return self._compression_algorithem.__class__.__name__

    def set_compression_algorithem(self, compression_algorithem: DataCompression):
        self._compression_algorithem = compression_algorithem

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
        if data:
            with open(file, 'wb') as f:
                f.write(data)

    def compress_data_to_file(self, data: str):
        compressed_data = self._compression_algorithem.compress_data(data=data)
        self._output_file.write(len(compressed_data).to_bytes(BYTES_LENGTH, byteorder='big'))
        # self._output_file.write(compressed_data.encode('utf-8'))
        self._output_file.write(compressed_data)

    def get_decompressed_data(self, compressed_data: bytes, index:int = 0):
        compressed_len = int.from_bytes(compressed_data[index:index+BYTES_LENGTH][::-1], byteorder='little')
        next_index = BYTES_LENGTH + index + compressed_len
        compressed = compressed_data[index+BYTES_LENGTH:next_index]
        decompress_data = self._compression_algorithem.decompress_data(compressed_data=compressed)

        return decompress_data, next_index
    
    def define_compression_algorithem(self, algorithem_type: bytes):
        # RLE algorithem
        if algorithem_type.startswith(CompressionTypes.RLE.value.__name__.encode()):
            bytes_size = int.from_bytes(algorithem_type[3:][::-1], byteorder='little')
            self.set_compression_algorithem(compression_algorithem=CompressionTypes.RLE.value(bytes_size=bytes_size))

        elif algorithem_type.startswith(CompressionTypes.HUFFMAN.value.__name__.encode()):
            self.set_compression_algorithem(compression_algorithem=CompressionTypes.HUFFMAN.value())

        elif algorithem_type.startswith(CompressionTypes.LZ.value.__name__.encode()):
            self.set_compression_algorithem(compression_algorithem=CompressionTypes.LZ.value())
        
        else:
            raise NotValidCompressionAlgorithem(f'Invalid compression format!')
        
    def write_metadata(self):
        compress_algorithem_metadata = self._compression_algorithem.get_metadata()
        self._output_file.write(len(compress_algorithem_metadata).to_bytes(BYTES_LENGTH, byteorder='big'))
        # self._output_file.write(compressed_data.encode('utf-8'))
        self._output_file.write(compress_algorithem_metadata)

    def read_metadata(self, compressed_data: str, index: int = 0):
        metadata_len = int.from_bytes(compressed_data[index:index+BYTES_LENGTH][::-1], byteorder='little')
        next_index = BYTES_LENGTH + index + metadata_len
        metadata = compressed_data[index+BYTES_LENGTH:next_index]

        return metadata, next_index

    def compress(self, directories: list, subfolder: str = '', ignore_folders: list = [], ignore_files: list = [], ignore_extensions: list = [], init_compression: bool = False):
        if init_compression:
            self.write_metadata()

        ignore_folders = [os.path.normpath(path) for path in ignore_folders]
        # pass on each given directory
        for dir in directories:
            full_dir_path = os.path.join(subfolder, dir)
            # if it is directory to folder
            if os.path.isdir(full_dir_path):
                
                if os.path.normpath(full_dir_path) not in ignore_folders:
                    
                    files_in_folder = os.listdir(full_dir_path)
                    # if it is an empty folder -> compress full folder path name
                    if len(files_in_folder) == 0:
                        full_dir_path += self._folder_suffix
                        self.compress_data_to_file(data=full_dir_path.encode())

                    # compress recursive the files which inside the directory to current folder
                    self.compress(directories=files_in_folder, subfolder=full_dir_path, ignore_files=ignore_files, ignore_extensions=ignore_extensions, ignore_folders=ignore_folders) 
            
            # if it is directory to file
            elif os.path.isfile(full_dir_path):
            
                if full_dir_path not in ignore_files and not full_dir_path.endswith(tuple(ignore_extensions)):
                    # compress full file path name
                    self.compress_data_to_file(data=full_dir_path.encode())

                    # read data from current file
                    full_file_data = self.read_file(file=full_dir_path)
                    
                    # compress file data
                    self.compress_data_to_file(data=full_file_data)

            else:
                #TODO: what should happen?
                self.close_output_file()
                os.remove(self._output_file.name)
                raise MissingInputPath(f"Error - {full_dir_path} does not exist.")

    def should_stop(self, compressed_file_path: str = '', compressed_data: bytes = b''):
        # if compressed_data is empty and compressed file path was not inserted
        if compressed_data == b'' and not compressed_file_path:
            return True
        return False
    
    def should_read_compressed_file(self, compressed_file_path: str = '', compressed_data: bytes = b''):
        # if compressed_data is empty and compressed file path was inserted
        if compressed_data == b'' and compressed_file_path:
            return True
        return False
    
    def handle_init_decompression(self, compressed_data, view_mode=False, debug_mode=False, compressed_file_path: str = ''):
        # get full file path from compressed data
        algorithem_type, next_index = self.read_metadata(compressed_data=compressed_data)
        self.define_compression_algorithem(algorithem_type=algorithem_type)
        if view_mode and not debug_mode:
            print(f"{compressed_file_path} - [{self.get_compression_algorithem_name()}] compressed file contains:")

        return next_index
    
    def get_next_path_from_archive(self, compressed_data, view_mode=False, debug_mode=True, index=0, get_file_path=False, output_path: str = ""):
        # get full file path from compressed data
        path, next_index = self.get_decompressed_data(
            compressed_data=compressed_data,
            index=index
        )

        # if path presents a folder
        if path.decode().endswith(self._folder_suffix):
            file_data = None
        
         # if path presents a file
        else:
            # get original file data from compressed data
            file_data, next_index = self.get_decompressed_data(
                compressed_data=compressed_data, 
                index=next_index
            )

        if view_mode and not debug_mode:
            print(f'{path.decode()} - size [{len(file_data)}]')
        elif not debug_mode:
            self.write_file(file=os.path.join(output_path, path.decode()), data=file_data)

        if get_file_path:
            return next_index, path
        else:
            return next_index

    def decompress(self, compressed_file_path: str = '', compressed_data: bytes = b'', subfolder: str = '', view_mode: bool = False, debug_mode: bool = False, init_decompression: bool = False, output_path: str = ""):
        if self.should_stop(compressed_file_path=compressed_file_path, compressed_data=compressed_data):
            return
        
        if self.should_read_compressed_file(
            compressed_file_path=compressed_file_path, compressed_data=compressed_data
        ):
            compressed_data = self.read_file(file=compressed_file_path)
            
        if init_decompression:
            next_index = self.handle_init_decompression(compressed_data=compressed_data, view_mode=view_mode, debug_mode=debug_mode, compressed_file_path=compressed_file_path)
        else:
            next_index = 0

        next_index = self.get_next_path_from_archive(compressed_data=compressed_data, view_mode=view_mode, debug_mode=debug_mode, index=next_index, output_path=output_path)

        # decompress the original data recursivlly from the 
        # rest of the compressed data
        self.decompress(
            compressed_data=compressed_data[next_index:], 
            subfolder=subfolder,
            view_mode=view_mode,
            debug_mode=debug_mode,
            output_path=output_path
        )

    def decompress_files(self, directories: list, output_path: str = '', view_mode: bool = False):
        for compressed_file in directories:
            self.decompress(compressed_file_path=compressed_file, view_mode=view_mode, init_decompression=True, output_path=output_path)

    def remove_from_archive(self, input_paths: list, archive_path:str):
        count_files_removes = 0
        update_compressed_data = bytearray()
        compressed_data = self.read_file(
            file=archive_path
        )

        next_index = self.handle_init_decompression(compressed_data=compressed_data)
        update_compressed_data.extend(compressed_data[0:next_index])

        i = next_index
        while i < len(compressed_data):
            
            next_index, file_path = self.get_next_path_from_archive(compressed_data=compressed_data, get_file_path=True, index=next_index)
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

    def check_validation(self, archive_paths: str):
        non_valid_archive_paths = {}
        for archive_path in archive_paths:
            try:
                self.decompress(compressed_file_path=archive_path, debug_mode=True, init_decompression=True)
            
            except Exception as e:
                non_valid_archive_paths[archive_path] = f'raise {type(e).__name__}({e})'
            
        return non_valid_archive_paths
            

        
        