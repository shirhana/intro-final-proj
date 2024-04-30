import pytest
import sys
import os
import shutil

# Get the current directory (where conftest.py is located)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project root)
project_root = os.path.dirname(current_dir)

# Add the 'src' directory to the Python path
# sys.path.insert(0, os.path.join(project_root, ''))


def clean():
    prefix = 'test-'
    current_directory = os.getcwd()
    files = os.listdir(current_directory)
    for file in files:
        if file.startswith(prefix):
            os.remove(os.path.join(current_directory, file))
            print(f"Removed file: {file}")


@pytest.fixture
def setup_before_tests():
    # Code to run before all tests
    print("Setting up before running tests")
    # You can add any setup logic here
    clean()
    yield  # This is where the tests will run

    # Code to run after all tests
    print("Tearing down after running tests")
    clean()
    # You can add any teardown logic here