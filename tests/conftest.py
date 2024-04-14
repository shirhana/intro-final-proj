import sys
import os

# Get the current directory (where conftest.py is located)
current_dir = os.path.dirname(os.path.abspath(__file__))

# Get the parent directory (project root)
project_root = os.path.dirname(current_dir)

# Add the 'src' directory to the Python path
sys.path.insert(0, os.path.join(project_root, 'src'))