"""This is where we find PyCharms versions that are available and pick the winner"""

import logging
import shutil
from collections.abc import Iterable
from itertools import chain
from pathlib import Path
from typing import NamedTuple

from hatch_pycharm._pycharm.jetbrains import find_executable as jb_find
from hatch_pycharm._pycharm.paths import platform_search_paths, platform_exe_name
from hatch_pycharm._pycharm.toolbox import find_executable as tb_find

log = logging.getLogger(__name__)


def locate_pycharm():
    # Easy first try:
    pycharm = shutil.which(platform_exe_name())
    if not pycharm:
        log.info(f"We didn't find an exe on system path, looking elsewhere")

        tb_exes = [tb_find(fp) for fp in platform_search_paths()]
        jb_exes = [jb_find(fp) for fp in platform_search_paths()]
        exes_found = list(filter(lambda x: x is not None, tb_exes + jb_exes))
        exes_found.sort(key=lambda x: x[0], reverse=True)
        pycharm = exes_found[0][1]
    return pycharm


_PYCHARM = str(locate_pycharm())


class FileRef(NamedTuple):
    path: Path
    line: int = None
    column: int = None

    def command_args(self) -> Iterable[str]:
        yield str(self.path)
        if self.line:
            yield "--line"
            yield str(self.line)
        if self.column:
            yield "--column"
            yield str(self.column)


def make_open_file_command(*files: Iterable[FileRef | Path]) -> Iterable[str]:
    # Making it a list of FileRef instead of FileRef or paths
    files: list[FileRef] = [p if isinstance(p, FileRef) else FileRef(p) for p in files]
    cmd = [_PYCHARM]
    cmd.extend(chain(map(FileRef.command_args, files)))
    return cmd


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(name)s [%(levelname)s]:%(message)s")
    locate_pycharm()
