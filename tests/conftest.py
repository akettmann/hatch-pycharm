# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT

import shutil

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

ROOT = Path(__file__).parent.parent


@pytest.fixture(name="plugin_dir")
def _plugin_dir():
    """
    Install the plugin into a temporary directory with a random path to
    prevent pip from caching it.

    Copy only the src directory, pyproject.toml, and whatever is needed
    to build ourselves.
    """
    with TemporaryDirectory() as d:
        directory = Path(d, "plugin")
        shutil.copytree(ROOT / "hatch_pycharm", directory / "hatch_pycharm")
        for fn in [
            "pyproject.toml",
            "README.md",
        ]:
            shutil.copy(ROOT / fn, directory / fn)

        yield directory.resolve()


@pytest.fixture(name="new_project")
def _new_project(plugin_dir, tmp_path, monkeypatch):
    """
    Create, and cd into, a blank new project that is configured to use our
    temporary plugin installation.
    """
    project_dir = tmp_path / "my-app"
    project_dir.mkdir()

    project_file = project_dir / "pyproject.toml"
    project_file.write_text(
        f"""\
[build-system]
requires = ["hatchling", "hatch-pycharm @ {plugin_dir.as_uri()}"]
build-backend = "hatchling.build"

[project]
name = "my-app"
version = "1.0"
dynamic = ["readme"]
[tool.hatch.envs.default]
type = "pycharm"
""",
        encoding="utf-8",
    )

    package_dir = project_dir / "src" / "my_app"
    package_dir.mkdir(parents=True)

    package_root = package_dir / "__init__.py"
    package_root.write_text("")

    monkeypatch.chdir(project_dir)

    return project_dir
