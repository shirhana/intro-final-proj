import shutil
from display_action_info import DisplayActionInfo
import pytest
import os
from action_types import ActionTypes

runner = DisplayActionInfo(action_type='stam', input_paths="", output_path="")


@pytest.mark.parametrize("size, files_num", [
    (0, 1),
    (5, 1), 
    (215, 2),
    (0, 7),
    (5, 6), 
    (500, 4)
])
def test_get_folder_size(size, files_num):
    folder_name = 'test-folder'
    data = b"1"*size
    print(data)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    for i in range(files_num):
        file_name = f"file{i}"
        with open(os.path.join(folder_name, file_name), 'wb') as f:
            f.write(data)
    assert size*files_num == runner.get_folder_size(path=folder_name)

    shutil.rmtree(folder_name)


@pytest.mark.parametrize("size, folders_num, files_num", [
    (0, 1, 8),
    (5, 1, 3), 
    (215, 2, 1),
    (0, 7, 2),
    (5, 6, 3), 
    (500, 4, 5)
])
def test_get_total_size_of_directories(size, folders_num, files_num):
    folders_lst = []
    for j in range(folders_num):
        folder_name = f'test-folder-{j}'
        folders_lst.append(folder_name)
        data = b"1"*size
        print(data)

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        for i in range(files_num):
            file_name = f"file{i}"
            with open(os.path.join(folder_name, file_name), 'wb') as f:
                f.write(data)

    assert size*files_num*folders_num == runner.get_total_size_of_directories(directories=folders_lst)

    for folder in folders_lst:
        shutil.rmtree(folder)


def test_show():
    for member in ActionTypes:
        runner = DisplayActionInfo(action_type=member.value, input_paths="", output_path="")
        runner.show(result='', compression_algorithem="")


@pytest.mark.parametrize("error_msg, return_value", [
    ({}, True),
    ({'error': '!!!!'}, False),
    ({'error1': '!!!!', 'error2': '!!!!'}, False),
    ("", True)
])
def test_alert(error_msg, return_value):
    assert return_value == runner.alert(error_msg=error_msg)
    