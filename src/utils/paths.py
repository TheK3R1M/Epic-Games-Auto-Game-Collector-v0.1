import sys
import os

def get_app_base_path() -> str:
    """
    Return the base path of the application.
    If frozen (bundled via PyInstaller), returns the directory containing the executable.
    If running from source, returns the project root directory (assumes src/utils/paths.py location).
    """
    if getattr(sys, 'frozen', False):
        # Running as compiled EXE
        return os.path.dirname(sys.executable)
    else:
        # Running from source: Go up from src/utils/paths.py to root
        # .../src/utils/paths.py -> .../src/utils -> .../src -> .../ (root)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

def get_data_dir() -> str:
    """Return absolute path to the data directory."""
    return os.path.join(get_app_base_path(), "data")
