# Config Manager
import json
import os
import sys

# We need to import paths carefully to avoid circular imports.
# Actually, paths.py depends on config.py (conceptually), or vice versa.
# To avoid circularity:
# paths.py will read config.json directly or we pass config to it.
# Better: ConfigManager uses a fixed location for config.json (App Base),
# and paths.py reads it.

def get_app_base_path_safe() -> str:
    """Duplicate of paths.get_app_base_path to avoid circular import."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))

class ConfigManager:
    """Manage application configuration."""
    
    DEFAULT_CONFIG = {
        "minimize_to_tray": True,
        "notifications": True,
        "auto_update": False,
        "run_on_startup": False, # Synced with Task Scheduler state where possible
        "custom_data_path": ""
    }
    
    def __init__(self):
        self.config_file = os.path.join(get_app_base_path_safe(), "config.json")
        self.config = self.load_config()
        
    def load_config(self) -> dict:
        if not os.path.exists(self.config_file):
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged = self.DEFAULT_CONFIG.copy()
                merged.update(data)
                return merged
        except Exception as e:
            print(f"⚠️ Config load error: {e}")
            return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"💾 Config saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Config save error: {e}")
            
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
        self.save_config()
        
    def reset(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
