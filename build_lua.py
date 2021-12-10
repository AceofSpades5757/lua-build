""" Build Lua from source.

Steps
-----
1. Download dependencies.
    * Compiler (TDM-GCC)
    * Lua
"""
import subprocess
import urllib.request
from pathlib import Path
from typing import Final


GCC: Final[str] = 'gcc'


# Check dependencies
try:
    subprocess.check_call(
        [GCC],
        shell=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
except FileNotFoundError:
    raise SystemExit(
        'Please install TDM-GCC, or add bin directory, with gcc.exe, to PATH.'
    )  # noqa: E501
except subprocess.CalledProcessError:
    # Installed
    pass

# Download Lua
download_url: Final[str] = 'http://www.lua.org/ftp/lua-5.4.3.tar.gz'
download_path: Final[str] = 'lua-5.4.3.tar.gz'

if not Path(download_path).exists():
    urllib.request.urlretrieve(download_url, download_path)
