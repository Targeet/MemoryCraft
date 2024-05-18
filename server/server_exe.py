# https://cx-freeze.readthedocs.io/en/latest/distutils.html

import sys
from cx_Freeze import setup, Executable

includes = []

# Include your files and folders
includefiles = ['settings.json']

# Exclude unnecessary packages
excludes = ["cx_Freeze","pydoc_data","setuptools","distutils","tkinter", "numpy"]

# Dependencies are automatically detected, but some modules need help.
packages = ["pygame"]    

base = None
shortcutName = None
shortcutDir = None
if sys.platform == "win32":
    base = "Console"
    shortcutName="My App"
    shortcutDir="DesktopFolder"

setup(
    name = "MemoryCraft - Server",
    version = "1.0",
    description = "MemoryCraft - Server",
    author = "Massimiliano Esposito",
    author_email = "",
    options = {"build_exe": {
        "includes": includes,
        "excludes": excludes,
        "packages": packages,
        "include_files": includefiles}
        }, 
    executables = [Executable("main.py", 
    base = base,
    icon = "../client/assets/images/icon.ico", 
    shortcut_name = shortcutName, 
    shortcut_dir = shortcutDir)]
)