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
    """
    Return absolute path to the data directory.
    Priority:
    1. OS Environment Variable 'EPIC_DATA_DIR'
    2. User Documents/EpicGamesCollectorData (Persistent)
    3. Fallback to local 'data' folder
    """
    # 1. Env Var
    env_path = os.environ.get("EPIC_DATA_DIR")
    if env_path:
        os.makedirs(env_path, exist_ok=True)
        return env_path
        
    # 2. Config File (Custom Path)
    # Manual read to avoid full ConfigManager import loop if not needed
    try:
        config_path = os.path.join(get_app_base_path(), "config.json")
        if os.path.exists(config_path):
             import json
             with open(config_path, 'r') as f:
                 data = json.load(f)
                 custom_path = data.get("custom_data_path", "")
                 if custom_path and os.path.isdir(os.path.dirname(custom_path)): # Basic validity check
                      if not os.path.exists(custom_path):
                           os.makedirs(custom_path, exist_ok=True)
                      return custom_path
    except Exception: pass
    
    # 3. Documents (Windows/Linux/Mac)
        
    # 2. Documents (Windows/Linux/Mac)
    try:
        user_docs = os.path.expanduser("~/Documents")
        persistent_path = os.path.join(user_docs, "EpicGamesCollectorData")
        os.makedirs(persistent_path, exist_ok=True)
        return persistent_path
    except Exception as e:
        print(f"⚠️ Could not create persistent path: {e}")
        pass

    # 3. Fallback to local
    local_path = os.path.join(get_app_base_path(), "data")
    os.makedirs(local_path, exist_ok=True)
    return local_path
