import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": [], "excludes": []}

# GUI applications require a different base on Windows (the default is for
# a console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "netsis-image-uploader",
        version = "1.1",
        description = "euu netsis resim yükleyici",
        options = {"build_exe": build_exe_options},
        executables = [Executable("netsis-image-uploader.py", base=base)])
