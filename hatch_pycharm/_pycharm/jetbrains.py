"""This file contains the logic for apps directly in the `JetBrains` named folder"""
import logging
import re
from pathlib import Path
from typing import Any

from hatch_pycharm._pycharm.types import Build_EXE

log = logging.getLogger(__name__)


def folder_key(s: Path) -> tuple[str | Any, ...]:
    """This is for folders in the path `JetBrains/PyCharm2022.1`"""
    m = re.match(r"^PyCharm(?P<year>\d+)\.(?P<rest>.*)$", s.name)
    if m:
        return m.groups()
    return ("",)


def newest_folder(jb_folder: Path) -> Path | None:
    log.warning("Looking in `%s` for folders named PyCharm", jb_folder)
    pycharm_folders = list(jb_folder.glob("PyCharm*"))
    if pycharm_folders:
        log.warning(f"Found `%s`", pycharm_folders)
        pycharm_folders.sort(key=folder_key)
        log.warning(f"Returning newest installed version, `%s`", pycharm_folders[0])
        return pycharm_folders[0]


def find_executable(fp: Path) -> Build_EXE | None:
    jb_folder = fp / "JetBrains"
    if not jb_folder.is_dir():
        log.debug(f"`%s` is not a directory, returning zero results", jb_folder)
        return
