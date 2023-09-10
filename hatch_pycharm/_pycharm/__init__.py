"""This is where we find PyCharms versions that are available and pick the winner"""

import logging
from collections.abc import Iterable
from functools import wraps
from itertools import chain
from pathlib import Path
from typing import NamedTuple

from hatch_pycharm._pycharm.types import FMT

log = logging.getLogger(__name__)


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
def make_open_file_command(pycharm: Path, *files: FileRef | Path) -> Iterable[str]:
    # Making it a list of FileRef instead of FileRef or paths
    files: list[FileRef] = [p if isinstance(p, FileRef) else FileRef(p) for p in files]
    cmd = [str(pycharm)]
    cmd.extend(chain.from_iterable(map(FileRef.command_args, files)))
    return cmd


@log_command
def make_compare_file_command(pycharm: Path, path1: Path, path2: Path, path3: Path = None) -> Iterable[str]:
    """
    Runs Pycharm, asking for a diff between two or three files.
    ref: https://www.jetbrains.com/help/pycharm/command-line-differences-viewer.html
    """
    cmd = [pycharm, "diff", str(path1.absolute()), str(path2.absolute())]
    if path3:
        cmd.append(str(path3))
    return cmd


@log_command
def make_merge_file_command(pycharm: Path, path1: Path, path2: Path, output: Path, base: Path = None) -> Iterable[str]:
    """
    Runs PyCharm, asking for a merge between two or three files.
    ref: https://www.jetbrains.com/help/pycharm/command-line-merge-tool.html
    Additional footnote from the reference:

    Don't specify the optional base revision if you want to treat the current
    contents of the output file as the common origin. In this case, if the
    output is an empty file, this essentially becomes a two-way merge.
    """
    cmd = [pycharm, "merge", str(path1), str(path2)]
    if base:
        # Base is optional, output is the base if it has content
        cmd.append(str(base))
    cmd.append(str(output))
    return cmd


@log_command
def make_format_files_command(
    pycharm: Path,
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
        pycharm,
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
    pycharm: Path,
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
    cmd = [pycharm, "inspect", str(project), str(inspection_profile), str(output)]
    if changes:
        cmd.append("-changes")
    if subdirectory:
        cmd.extend(("-d", str(subdirectory)))
    cmd.extend(("-format", format_))
    if verbosity:
        cmd.append(f"-v{verbosity}")
    return cmd


@log_command
def make_install_plugins_command(pycharm: Path, *plugins: str) -> Iterable[str]:
    """
    Runs PyCharm, asking installation of plugins either by plugin-id or repository-url
    ref: https://www.jetbrains.com/help/pycharm/install-plugins-from-the-command-line.html
    So much potential for a hatch hook into PyCharm and managing the environment smoothly
    Combined with potentially reading state out of the IDE's directories
    ref: https://www.jetbrains.com/help/pycharm/directories-used-by-the-ide-to-store-settings-caches-plugins-and-logs.html
    ref: https://www.jetbrains.com/help/pycharm/file-idea-properties.html

    :return:
    """
    cmd = [pycharm, "installPlugins"]
    cmd.extend(map(str, plugins))
    return cmd
