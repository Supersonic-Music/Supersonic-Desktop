import os

LINUX_CONFIG_PATHS = [
    "~/.config/supersonic-desktop/config.py", 
    "/etc/supersonic-desktop/config.py", 
    ".local/share/supersonic-desktop/config.py", 
    "/usr/local/share/supersonic-desktop/config.py", 
    "/usr/share/supersonic-desktop/config.py"
]

WINDOWS_CONFIG_PATHS = [
    "%APPDATA%\\supersonic-desktop\\config.py",
    "%LOCALAPPDATA%\\supersonic-desktop\\config.py",
    "%PROGRAMDATA%\\supersonic-desktop\\config.py"
]

GENERIC_CONFIG_PATHS = [
    "~/Library/Application Support/supersonic-desktop/config.py",
    "/Library/Application Support/supersonic-desktop/config.py",
    "config.py", 
    "/usr/local/share/supersonic-desktop/config.py"
]

def loop_paths(paths, os_name):
    for path in paths:
        if os.path.isdir(path):
            return path
    for path in GENERIC_CONFIG_PATHS:
        if os.path.isdir(path):
            return path
    if os_name not in ["posix", "nt"]:
        return "400" # Unsupported OS
    else:
        return "401" # No config found

def find_config():
    os_name = os.name
    if os_name == "posix":
        return loop_paths(LINUX_CONFIG_PATHS, os_name)
    elif os_name == "nt":
        return loop_paths(WINDOWS_CONFIG_PATHS, os_name)
    else:
        return loop_paths(GENERIC_CONFIG_PATHS, os_name)