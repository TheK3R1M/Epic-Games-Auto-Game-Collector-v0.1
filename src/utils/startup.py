"""Windows Task Scheduler integration for auto-start."""

import subprocess
import subprocess
import sys
import os
from typing import Tuple


def _run(cmd: str) -> Tuple[bool, str]:
    try:
        completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if completed.returncode == 0:
            return True, completed.stdout.strip() or "Success"
        return False, completed.stderr.strip() or completed.stdout.strip() or "Unknown error"
    except Exception as exc:
        return False, str(exc)


def register_startup_task(task_name: str, exe_path: str, args: str = "") -> Tuple[bool, str]:
    """Create a shortcut in the Windows Startup folder."""
    try:
        # Get Startup Folder Path
        startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_dir, f"{task_name}.lnk")
        
        # Ensure exe_path is absolute and clean
        exe_path = os.path.abspath(exe_path.strip('"'))
        working_dir = os.path.dirname(exe_path)

        ps_script = f"""
        $WshShell = New-Object -comObject WScript.Shell
        $Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
        $Shortcut.TargetPath = "{exe_path}"
        $Shortcut.Arguments = "{args}"
        $Shortcut.WorkingDirectory = "{working_dir}"
        $Shortcut.Save()
        """
        
        cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script]
        
        subprocess.run(cmd, check=True, capture_output=True)
        return True, "Startup shortcut created successfully."
        
    except Exception as e:
        return False, str(e)


def unregister_startup_task(task_name: str) -> Tuple[bool, str]:
    """Remove the shortcut from the Startup folder."""
    try:
        startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        shortcut_path = os.path.join(startup_dir, f"{task_name}.lnk")
        
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            return True, "Startup shortcut removed."
        else:
            return True, "Shortcut did not exist."
            
    except Exception as e:
        return False, str(e)
