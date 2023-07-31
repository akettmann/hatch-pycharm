"""This file is for looking under the `Jetbrains/Toolbox` flavored directories"""
import logging
from pathlib import Path
from typing import Any, Iterable
import re

from hatch_pycharm._pycharm.paths import platform_exe_name
from hatch_pycharm._pycharm.types import Build_EXE

log = logging.getLogger(__name__)

# Example
# JetBrains\Toolbox\apps\PyCharm-P\ch-0\232.8660.197\bin\pycharm64.exe
# Looking for groups of digits separated by periods, without ending with a period
folder_check = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def folder_key(s: Path) -> tuple[str | Any, ...]:
    """This is for folders in the path `JetBrains/Toolbox/apps/PyCharm/232.8660.197`"""
    m = re.match(r"^((\d+) )+$", s.name)
    if m:
        return m.groups()
    return ("",)


def discover_executables(tb_folder: Path) -> Iterable[Build_EXE]:
    """Looks under the Toolbox folder for channel folders, then finds the executable"""
    # I assume the `ch-` prefix is for channels, as I had `ch-0` and installed another and it came in as `ch-1`
    channel_folders = tb_folder.rglob("apps/PyCharm*/ch-*")

    for cf in channel_folders:
        log.debug(f"Scanning channel folder `%s`", cf)
        for fp in cf.iterdir():
            if fp.is_dir() and (fc := folder_check.fullmatch(fp.name)):
                log.debug(f"Found a version named folder named `%s`", fp.name)
                exe = fp / "bin" / platform_exe_name()
                if exe.is_file():
                    log.debug(f"Binary found, `%s`", exe)
                    yield fc.groups(), exe


def newest_executable(tb_folder: Path) -> Build_EXE | None:
    """Sort the list of discovered executables, return the newest"""
    log.debug("Looking in `%s` for PyCharm folders", tb_folder)
    executables = list(discover_executables(tb_folder))
    if len(executables) == 0:
        return
    executables.sort(key=lambda x: x[0], reverse=True)
    return executables[0]


def find_executable(fp: Path) -> Build_EXE | None:
    tb_folder = fp / "JetBrains" / "ToolBox"
    if not tb_folder.is_dir():
        log.debug(f"`%s` is not a directory, returning zero results", tb_folder)
        return
    ne = newest_executable(tb_folder)
    if ne is not None:
        log.debug("Returning executable `%s`", ne)
        return ne


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(name)s [%(levelname)s]:%(message)s")
    test_path = Path(r"C:\Users\veigar\AppData\Local\JetBrains\Toolbox")
    print(newest_executable(test_path))
    print(find_executable(test_path.parent))
