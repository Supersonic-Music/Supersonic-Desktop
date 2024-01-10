import os

LINUX_CONFIG_PATHS = [
    "~/.config/supersonic-desktop/config.py", 
    "/etc/supersonic-desktop/config.py", 
    ".local/share/supersonic-desktop/config.py", 
    "/usr/local/share/supersonic-desktop/config.py", 
    "/usr/share/supersonic-desktop/config.py"
]

WINDOWS_CONFIG_PATHS = [
    "%APPDATA%/supersonic-desktop/config.py",
    "%LOCALAPPDATA%/supersonic-desktop/config.py",
    "%PROGRAMDATA%/supersonic-desktop/config.py"
]

GENERIC_CONFIG_PATHS = [
    "config.py", 
    "~/Library/Application Support/supersonic-desktop/config.py",
    "/Library/Application Support/supersonic-desktop/config.py",
    "/usr/local/share/supersonic-desktop/config.py"
]

def loop_paths(paths, os_name):
    for path in paths:
        if os.path.exists(path):
            return path
    for path in GENERIC_CONFIG_PATHS:
        if os.path.exists(path):
            return path
    if os_name not in ["posix", "nt"]:
        raise OSError("OS not supported")
    else:
        raise FileNotFoundError("Config file could not found")

def find_config():
    os_name = os.name()
    if os_name == "posix":
        loop_paths(LINUX_CONFIG_PATHS)
    elif os_name == "nt":
        loop_paths(WINDOWS_CONFIG_PATHS)
    else:
        loop_paths(GENERIC_CONFIG_PATHS)
