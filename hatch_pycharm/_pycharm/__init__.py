"""This is where we find PyCharms versions that are available and pick the winner"""

import logging
import shutil
from collections.abc import Iterable
from functools import wraps
from itertools import chain
from pathlib import Path
from typing import NamedTuple

from hatch_pycharm._pycharm.jetbrains import find_executable as jb_find
from hatch_pycharm._pycharm.paths import platform_search_paths, platform_exe_name
from hatch_pycharm._pycharm.toolbox import find_executable as tb_find
from hatch_pycharm._pycharm.types import FMT

log = logging.getLogger(__name__)


def locate_pycharm():
    # Easy first try:
    pycharm = shutil.which(platform_exe_name())
    if not pycharm:
        log.info(f"We didn't find an exe on system path, looking elsewhere")
        tb_exes = [tb_find(fp) for fp in platform_search_paths()]
        jb_exes = [jb_find(fp) for fp in platform_search_paths()]
        exes_found = list(filter(None, tb_exes + jb_exes))
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


def log_command(f):
    @wraps(f)
    def inner(*args, **kwargs):
        log.debug("Function %s received the args `%s` and the kwargs `%s`", args, kwargs)
        res = f(*args, **kwargs)
        log.debug("Function %s created the command %s", f.__name__, res)
        return res

    return inner


@log_command
def make_open_file_command(*files: FileRef | Path) -> Iterable[str]:
    # Making it a list of FileRef instead of FileRef or paths
    files: list[FileRef] = [p if isinstance(p, FileRef) else FileRef(p) for p in files]
    cmd = [_PYCHARM]
    cmd.extend(chain.from_iterable(map(FileRef.command_args, files)))
    return cmd


@log_command
def make_compare_file_command(path1: Path, path2: Path, path3: Path = None) -> Iterable[str]:
    """
    Runs Pycharm, asking for a diff between two or three files.
    ref: https://www.jetbrains.com/help/pycharm/command-line-differences-viewer.html
    """
    cmd = [_PYCHARM, "diff", str(path1.absolute()), str(path2.absolute())]
    if path3:
        cmd.append(str(path3))
    return cmd


@log_command
def make_merge_file_command(path1: Path, path2: Path, output: Path, base: Path = None) -> Iterable[str]:
    """
    Runs PyCharm, asking for a merge between two or three files.
    ref: https://www.jetbrains.com/help/pycharm/command-line-merge-tool.html
    Additional footnote from the reference:

    Don't specify the optional base revision if you want to treat the current
    contents of the output file as the common origin. In this case, if the
    output is an empty file, this essentially becomes a two-way merge.
    """
    cmd = [_PYCHARM, "merge", str(path1), str(path2)]
    if base:
        # Base is optional, output is the base if it has content
        cmd.append(str(base))
    cmd.append(str(output))
    return cmd


@log_command
def make_format_files_command(
    *files: Path,
    masks: Iterable[str] = (),
    recursive: bool = False,
    settings: Path = None,
    allow_defaults: bool = False,
    charset: str = None,
    dry: bool = False,
) -> Iterable[str]:
    """
    Runs PyCharm, asking for formatting of N number of paths
    ref: https://www.jetbrains.com/help/pycharm/command-line-formatter.html
    There are options to change behavior, consult the reference linked

    :return:
    """
    cmd = [
        _PYCHARM,
        "format",
    ]
    # Using extend to keep each command on one line where possible
    if masks:
        # Orig docs:
        ## Specify a comma-separated list of file masks that define
        ## the files to be processed. You can use the * (any string)
        ## and ? (any single character) wildcards.
        cmd.extend(("-mask", ",".join(masks)))
    if recursive:
        cmd.append("-R")
    if settings:
        cmd.extend(("-settings", str(settings)))
    if allow_defaults:
        cmd.append("-allowDefaults")
    if charset:
        cmd.extend(("-charset", charset))
    if dry:
        cmd.append("-dry")
    cmd.extend(map(str, files))
    return cmd


@log_command
def make_code_inspections_command(
    project: Path,
    inspection_profile: Path,
    output: Path,
    changes: bool = False,
    subdirectory: Path = None,
    format_: FMT = "xml",
    verbosity: int = None,
) -> Iterable[str]:
    """
    Runs PyCharm, asking for code inspections of a project
    ref: https://www.jetbrains.com/help/pycharm/command-line-formatter.html
    There are options to change behavior, consult the reference linked

    :return:
    """
    cmd = [_PYCHARM, "inspect", str(project), str(inspection_profile), str(output)]
    if changes:
        cmd.append("-changes")
    if subdirectory:
        cmd.extend(("-d", str(subdirectory)))
    cmd.extend(("-format", format_))
    if verbosity:
        cmd.append(f"-v{verbosity}")
    return cmd


@log_command
def make_install_plugins_command(*plugins: str) -> Iterable[str]:
    """
    Runs PyCharm, asking installation of plugins either by plugin-id or repository-url
    ref: https://www.jetbrains.com/help/pycharm/install-plugins-from-the-command-line.html
    So much potential for a hatch hook into PyCharm and managing the environment smoothly
    Combined with potentially reading state out of the IDE's directories
    ref: https://www.jetbrains.com/help/pycharm/directories-used-by-the-ide-to-store-settings-caches-plugins-and-logs.html
    ref: https://www.jetbrains.com/help/pycharm/file-idea-properties.html

    :return:
    """
    cmd = [_PYCHARM, "installPlugins"]
    cmd.extend(map(str, plugins))
    return cmd


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(name)s [%(levelname)s]:%(message)s")
    locate_pycharm()
