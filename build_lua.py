""" Build and install Lua from source, give a version and install location.

* Currently only supports tested on Lua 5.4.3
* Only allows user install (no admin elevation)

Steps
-----
1. Download dependencies.
    * Compiler (TDM-GCC)
    * Lua
"""
import glob
import logging.config
import os
import platform
import shutil
import subprocess
import urllib.request
from pathlib import Path
from typing import Final

from log_config import LOGGING_CONFIG


# Config
GCC: Final[str] = 'gcc'
version: Final[str] = '5.4.3'
if platform.system() == 'Windows':
    install_directory: Final[Path] = Path(os.environ['APPDATA']) / 'Lua'
elif platform.system() == 'Linux':
    raise NotImplementedError('Unsupported platform: Linux.')
else:
    raise NotImplementedError('Unsupported platform: not Windows or Linux.')

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)


def is_executable(executable: str) -> bool:
    """Check if a command is executable."""
    logger.info(f'Checking if {executable} is executable.')
    try:
        subprocess.check_call(
            [executable],
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        return False
    except subprocess.CalledProcessError:
        # Installed but requires an argument(s).
        return True

    return True


def check_dependencies() -> None:
    """Check if dependencies are installed."""
    logger.info('Checking dependencies.')
    gcc_installed: bool = is_executable(GCC)
    if not gcc_installed:
        raise SystemExit(
            'Please install TDM-GCC, or add bin directory, with gcc.exe, to PATH.'  # noqa: E501
        )


def download_lua(version: str) -> Path:
    """Download Lua source code."""
    logger.info(f'Downloading Lua {version}')
    download_url: Final[str] = f'http://www.lua.org/ftp/lua-{version}.tar.gz'
    download_path: Final[Path] = Path(f'lua-{version}.tar.gz')

    if not Path(download_path).exists():
        urllib.request.urlretrieve(download_url, download_path)

    return download_path


def extract_lua(archive: Path) -> None:
    """Extract Lua source code."""
    logger.info(f'Extracting {archive!s}')
    shutil.unpack_archive(archive)


def clean_lua_source() -> None:
    """Clean Lua source code."""
    logger.info('Cleaning Lua source code.')
    for path in glob.glob('lua-*'):
        if Path(path).is_dir():
            logger.info(f'Removing {path} directory.')
            shutil.rmtree(path)


def build_lua(build_directory: Path) -> None:
    """Build Lua."""
    logger.info(f'Building Lua in {build_directory!s}')
    process = subprocess.Popen(
        ['mingw32-make', 'PLAT=mingw'],
        cwd=build_directory,
    )

    return_code: int = process.wait()
    if return_code != 0:
        raise SystemExit(f'Failed to build Lua with {return_code=}.')


def check_lua(lua_executable: str) -> None:
    """Check if Lua was built."""

    # Check Build
    logger.info(f'Checking {lua_executable}')
    if not is_executable(lua_executable):
        raise SystemExit(f'Lua is not executable: {lua_executable}.')


def clean_distribution(dist_directory: Path) -> None:
    """Clean binary distribution."""
    logger.info(f'Cleaning dist directory: {dist_directory}')
    if dist_directory.exists():
        shutil.rmtree(dist_directory)


def create_distribution(build_directory: Path, dist_directory: Path) -> None:
    """Create binary distribution for successful build."""

    doc_directory: Final[Path] = dist_directory / 'doc'
    bin_directory: Final[Path] = dist_directory / 'bin'
    include_directory: Final[Path] = dist_directory / 'include'

    # Move to clean "binary" installation
    logger.info(f'Creating dist directory: {dist_directory!s}')
    for subdirectory in (doc_directory, bin_directory, include_directory):
        logger.info(f'Creating dist directory: {subdirectory!s}')
        subdirectory.mkdir(parents=True, exist_ok=False)

    # Copy files to build directory for "binary" installation
    logger.info(
        f'Copying files to dist directory: {build_directory!s} -> {dist_directory!s}'  # noqa: E501
    )
    for file in (build_directory / 'doc').glob('*.*'):
        logger.info(f'Copying file: {file!s} -> {doc_directory!s}')
        shutil.copy2(file, doc_directory)
    for glob_ in ('*.exe', '*.dll'):
        for file in (build_directory / 'src').glob(glob_):
            logger.info(f'Copying file: {file!s} -> {bin_directory!s}')
            shutil.copy2(file, bin_directory)
    for header_file in (
        'luaconf.h',
        'lua.h',
        'lualib.h',
        'lauxlib.h',
        'lua.hpp',
    ):
        logger.info(f'Copying file: {header_file!s} -> {include_directory!s}')
        shutil.copy2(build_directory / 'src' / header_file, include_directory)


def install_lua(dist_directory: Path, install_directory: Path) -> None:
    """Install Lua."""
    logger.info(
        f'Installing Lua to {install_directory!s} from {dist_directory!s}'
    )
    if install_directory.exists():
        shutil.rmtree(install_directory)
    shutil.copytree(dist_directory, install_directory)


def main() -> int:

    build_directory: Final[Path] = Path(f'lua-{version}')
    distribution_directory: Final[Path] = Path('dist') / f'lua-{version}'

    check_dependencies()

    clean_lua_source()

    archive: Final[Path] = download_lua(version)
    extract_lua(archive)

    build_lua(build_directory)
    lua_build_executable: Final[str] = str(build_directory / 'src' / 'lua')
    check_lua(lua_build_executable)

    clean_distribution(distribution_directory)
    create_distribution(build_directory, distribution_directory)
    lua_dist_executable: Final[str] = str(
        distribution_directory / 'bin' / 'lua'
    )
    check_lua(lua_dist_executable)

    install_lua(distribution_directory, install_directory)

    logger.info(f'Lua {version} has been successfully built and installed.')

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
