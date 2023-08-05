import os
from functools import wraps
from pathlib import Path
from typing import Iterable

from hatch.utils.platform import get_platform_name

search_paths = {
    "windows": (
        # Is there an "intended order" for these?
        "APPDATA",  # Roaming
        "LOCALAPPDATA",  # Local
        "PROGRAMFILES",  # Program Files
        "PROGRAMFILES(X86)",  # X86 edition
    ),
    # "linux": (),
    # "macos": (),
}


exe_names = {"windows": "pycharm64.exe", "linux": "pycharm.sh", "macos": "pycharm"}


def resolve_paths(paths: Iterable[str]) -> Iterable[Path]:
    env_values = filter(bool, (os.getenv(ev) for ev in paths))
    yield from map(Path, env_values)


def not_supported_logger(f):
    @wraps(f)
    def inner():
        try:
            return f()
        except KeyError:
            msg = f"Platform `{get_platform_name()}` is not supported!"
            raise RuntimeError(msg)

    return inner


@not_supported_logger
def platform_search_paths() -> Iterable[Path]:
    """Returns Path objects that are interpreted from defined environment variables"""
    return resolve_paths(search_paths[get_platform_name()])


@not_supported_logger
def platform_exe_name() -> str:
    return exe_names[get_platform_name()]


if __name__ == "__main__":
    import rich.pretty as pretty

    pretty.pprint(list(platform_search_paths()))
    pretty.pprint(platform_exe_name())
