import os
import shutil
import pytest
from rle_compression import RleCompression
from filesystem_handler import Filesystem_Handler


def create_file(file_path, data):
    with open(file_path, 'wt') as f:
        f.write(data)


def pre_compress(output_file, file_path, file_data):
    if os.path.isfile(output_file):
        clean(files=[output_file])
    create_file(file_path, file_data)


def assert_file_and_folders_exist(files=[], folders=[], suppose_exist=True):
    for file in files:
        assert os.path.isfile(file) == suppose_exist

    for folder in folders:
        assert os.path.isdir(folder) == suppose_exist


def clean(files=[], folders=[]):
    # TODO - write fixtures?
    for file in files:
        os.remove(file)

    for folder in folders:
        shutil.rmtree(folder)


def test_basic_compression_and_decompression():
    file_path = 'test.txt'
    file_data = 'stam-data'
    output_file = 'test.bin'
    pre_compress(output_file, file_path, file_data)

    rle_algorithem = RleCompression(bytes_size=1)
    handler = Filesystem_Handler(data_compression_algorithem=rle_algorithem)

    handler.open_output_file(output_file_path=output_file)
    handler.compress(directories=[file_path])
    handler.close_output_file()

    assert_file_and_folders_exist(files=[file_path])
    clean(files=[file_path])
    assert_file_and_folders_exist(files=[file_path],suppose_exist=False)

    handler.decompress(compressed_file_path=output_file)
    assert_file_and_folders_exist(files=[file_path])
    clean(files=[output_file, file_path])


def test_recursive_compression_and_decompression():
    folder = 'stam'
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, 'test.txt')
    file_data = 'stam-data'
    output_file = 'test.bin'
    if os.path.isfile(output_file):
        clean(files=[output_file])
    create_file(file_path, file_data)

    rle_algorithem = RleCompression(bytes_size=1)
    handler = Filesystem_Handler(data_compression_algorithem=rle_algorithem)

    handler.open_output_file(output_file_path=output_file)
    handler.compress(directories=[folder])
    handler.close_output_file()

    assert_file_and_folders_exist(files=[file_path], folders=[folder])
    clean(folders=[folder])
    assert_file_and_folders_exist(files=[file_path], folders=[folder], suppose_exist=False)

    handler.decompress(compressed_file_path=output_file)
    assert_file_and_folders_exist(files=[file_path], folders=[folder])
    clean(files=[file_path, output_file], folders=[folder])


def test_some_files_compression_and_decompression():
    files_path = ['fileone', 'filetwo','filethree']
    output_file = 'test.bin'
    if os.path.isfile(output_file):
        clean(files=[output_file])

    for file_path in files_path:
        create_file(file_path, f'{file_path}-data')

    rle_algorithem = RleCompression(bytes_size=1)
    handler = Filesystem_Handler(data_compression_algorithem=rle_algorithem)

    handler.open_output_file(output_file_path=output_file)
    handler.compress(directories=files_path)
    handler.close_output_file()

    assert_file_and_folders_exist(files=files_path)
    clean(files=files_path)
    assert_file_and_folders_exist(files=files_path, suppose_exist=False)

    handler.decompress(compressed_file_path=output_file)
    assert_file_and_folders_exist(files=files_path)

    files_path.extend([output_file])
    clean(files=files_path)
