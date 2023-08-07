import os
from functools import wraps
from pathlib import Path
from typing import Iterable, NamedTuple

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
config_dirs = {
    "windows": r"%APPDATA%\JetBrains\{product}{version}",
    "linux": "~/.config/JetBrains/{product}{version}",
    "macos": "~/Library/Application Support/JetBrains/{product}{version}",
}
system_dirs = {
    "windows": r"%LOCALAPPDATA%\JetBrains\{product}{version}",
    "linux": "~/.cache/JetBrains/{product}{version}",
    "macos": "~/Library/Caches/JetBrains/{product}{version}",
}
# From PyCharm docs
# If you installed PyCharm via the Toolbox App, the plugins directory will be located in the installation directory.
# To find the installation directory, open the settings of the IDE instance in the Toolbox App, expand Configuration
# and look for the Install location field. There should be a directory that ends with .plugins.
plugins_dirs = {
    "windows": r"%APPDATA%\JetBrains\{product}{version}\plugins",
    "linux": "~/.local/share/JetBrains/{product}{version}",
    "macos": "~/Library/Application Support/JetBrains/{product}{version}/plugins",
}
logs_dirs = {
    "windows": r"%LOCALAPPDATA%\JetBrains\{product}{version}\log",
    "linux": "~/.cache/JetBrains/{product}{version}/log",
    "macos": "~/Library/Logs/JetBrains/{product}{version}",
}


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


@not_supported_logger
def platform_config_dir() -> str:
    return config_dirs[get_platform_name()]


@not_supported_logger
def platform_system_dir() -> str:
    return system_dirs[get_platform_name()]


@not_supported_logger
def platform_plugin_dir() -> str:
    return plugins_dirs[get_platform_name()]


@not_supported_logger
def platform_log_dir() -> str:
    return logs_dirs[get_platform_name()]


if __name__ == "__main__":
    import rich.pretty as pretty

    pretty.pprint(list(platform_search_paths()))
    pretty.pprint(platform_exe_name())
