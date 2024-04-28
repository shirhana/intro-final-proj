import shutil
from main import *
from action_types import ActionTypes
from compression_types import CompressionTypes
import os
import pytest

FOLDER_NAME = 'test-folder'
FILE_NAME = 'file'

def make_dirs(folders_num=2, files_num=4, size=10):
    folders_lst = []
    for j in range(folders_num):
        folder_name = f'{FOLDER_NAME}-{j}'
        folders_lst.append(folder_name)
        data = b"1"*size

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        for i in range(files_num):
            file_name = f"{FILE_NAME}{i}"
            with open(os.path.join(folder_name, file_name), 'wb') as f:
                f.write(data)

    return folders_lst


def clean(paths):
    for path in paths:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)


def test_compression_decompression():
    input_paths = make_dirs()
    paths = []
    for member in CompressionTypes:
        compression_type = member.name.lower()
        output_path = f"output-{member.name}.bin"
        paths.append(output_path)

        # COMPRESS
        assert not os.path.isfile(output_path)
        run(input_paths=input_paths, output_path=output_path, action_type=ActionTypes.COMPRESS.value, compression_type=compression_type)
        assert os.path.isfile(output_path)

    # DECOMPRESS
    run(input_paths=paths, output_path='', action_type=ActionTypes.DECOMPRESS.value)

    # VIEW-ARCHIVE
    run(input_paths=paths, output_path='', action_type=ActionTypes.VIEW_ARCHIVE.value)

    paths.extend(input_paths)

    clean(paths=paths)

def test_remove_from_archive():
    files_num = 5
    folders_num = 1
    folder_name = f"{FOLDER_NAME}-{folders_num-1}"
    file_name = f"{FILE_NAME}1"
    
    paths = []
    for member in CompressionTypes:
        input_paths = make_dirs(folders_num=folders_num, files_num=files_num)
        compression_type = member.name.lower()
        output_path = f"output-{member.name}.bin"
        paths.append(output_path)

        assert len(os.listdir(folder_name)) == files_num
        assert file_name in os.listdir(folder_name)

        # COMPRESS
        run(input_paths=input_paths, output_path=output_path, action_type=ActionTypes.COMPRESS.value, compression_type=compression_type)

        clean(input_paths)

        # REMOVE NON EXIST FILE FROM ARCHIVE
        run(input_paths=['stam'], output_path=output_path, action_type=ActionTypes.REMOVE_FROM_ARCHIVE.value, compression_type=compression_type)

        # DECOMPRESS
        run(input_paths=[output_path], output_path='', action_type=ActionTypes.DECOMPRESS.value, compression_type=compression_type)
        assert len(os.listdir(folder_name)) == files_num
        assert file_name in os.listdir(folder_name)

        clean(input_paths)

        # REMOVE_FROM_ARCHIVE
        run(input_paths=[os.path.join(folder_name, file_name)], output_path=output_path, action_type=ActionTypes.REMOVE_FROM_ARCHIVE.value, compression_type=compression_type)
        # DECOMPRESS
        run(input_paths=[output_path], output_path='', action_type=ActionTypes.DECOMPRESS.value, compression_type=compression_type)
        

        assert len(os.listdir(folder_name)) == files_num - 1
        assert file_name not in os.listdir(folder_name)

        paths.extend(input_paths)

        clean(paths)


def test_add_to_archive():
    files_num = 5
    folders_num = 1
    folder_name = f"{FOLDER_NAME}-{folders_num-1}"
    new_file_name = f"new_file_name"

    
    
    paths = []
    for member in CompressionTypes:
        input_paths = make_dirs(folders_num=folders_num, files_num=files_num)
        compression_type = member.name.lower()
        output_path = f"output-{member.name}.bin"
        paths.append(output_path)

        # COMPRESS
        run(input_paths=input_paths, output_path=output_path, action_type=ActionTypes.COMPRESS.value, compression_type=compression_type)

        with open(os.path.join(folder_name, new_file_name), 'wt') as f:
            f.write('stamstam')

        # ADD TO ARCHIVE
        run(input_paths=[os.path.join(folder_name, new_file_name)], output_path=output_path, action_type=ActionTypes.ADD_TO_ARCHIVE.value, compression_type=compression_type)


        clean([os.path.join(folder_name, new_file_name)])

        assert len(os.listdir(folder_name)) == files_num
        assert new_file_name not in os.listdir(folder_name)

        clean(input_paths)
        # DECOMPRESS
        run(input_paths=[output_path], output_path='', action_type=ActionTypes.DECOMPRESS.value, compression_type=compression_type)
        assert len(os.listdir(folder_name)) == files_num + 1
        assert new_file_name in os.listdir(folder_name)


        paths.extend(input_paths)

        clean(paths)


def test_compression_file_doesnot_exist():
    non_exist_file = 'non-exist'
    with pytest.raises(expected_exception=Exception, match=f"Error - {non_exist_file} does not exist."):
        # COMPRESS
        run(input_paths=[non_exist_file], output_path='stam.bin', action_type=ActionTypes.COMPRESS.value)

def test_compress_empty_folder():
    folder_name = 'stam'
    output_path = 'stam.bin'
    os.makedirs(folder_name)
    # COMPRESS
    run(input_paths=[folder_name], output_path=output_path, action_type=ActionTypes.COMPRESS.value)

    shutil.rmtree(folder_name)
    assert not os.path.isdir(folder_name)
    # DECOMPRESS
    run(input_paths=[output_path], output_path='', action_type=ActionTypes.DECOMPRESS.value)
    assert os.path.isdir(folder_name)

    clean(paths=[folder_name, output_path])


def test_decompress_to_specific_location():
    input_paths = make_dirs(folders_num=1)
    output_path = f"output.bin"
    new_folder = "newfolder"

    # COMPRESS
    run(input_paths=input_paths, output_path=output_path, action_type=ActionTypes.COMPRESS.value, compression_type=CompressionTypes.HUFFMAN.name.lower())

    os.makedirs(new_folder)

    assert len(os.listdir(new_folder)) == 0
    # DECOMPRESS TO SPECIFIC PATH
    run(input_paths=[output_path], output_path=new_folder, action_type=ActionTypes.DECOMPRESS.value)
    assert not len(os.listdir(new_folder)) == 0
    assert input_paths[0] in os.listdir(new_folder)
    for file in os.listdir(input_paths[0]):
        assert file in os.listdir(os.path.join(new_folder, input_paths[0]))
    input_paths.extend([output_path, new_folder])
    clean(input_paths)


def test_compress_and_decompress_big_files():
    test_folder = 'assets'
    playground_folder = 'playground'
    paths = [playground_folder]
    os.makedirs(playground_folder)
    for member in CompressionTypes:
        compression_type = member.name.lower()
        output_path = f"output-{member.name}.bin"
        paths.append(output_path)

        # COMPRESS
        assert not os.path.isfile(output_path)
        run(input_paths=[test_folder], output_path=output_path, action_type=ActionTypes.COMPRESS.value, compression_type=compression_type)
        assert os.path.isfile(output_path)

    # DECOMPRESS
    run(input_paths=paths, output_path=playground_folder, action_type=ActionTypes.DECOMPRESS.value)

    files = os.listdir(test_folder)

    for file in files:

        with open(os.path.join(test_folder, file), 'rb') as f:
            original_data = f.read()

        with open(os.path.join(playground_folder, test_folder, file), 'rb') as f:
            compare_data = f.read()


        assert original_data == compare_data

    clean(paths=paths)