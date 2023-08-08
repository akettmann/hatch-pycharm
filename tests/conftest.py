# SPDX-FileCopyrightText: 2022 Hynek Schlawack <hs@ox.cx>
#
# SPDX-License-Identifier: MIT
import shutil
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from xml.etree.ElementTree import fromstring, Element

import pytest

from hatch_pycharm._pycharm import settings
from hatch_pycharm._pycharm.venv_xml import PyCharmVenv, PythonConfigVars

ROOT = Path(__file__).parent.parent
assc_project_path = "ASSOCIATED_PROJECT_PATH"


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


@pytest.fixture
def current_project_venv(current_project_misc_file) -> "PyCharmVenv":
    from hatch_pycharm._pycharm.venv_xml import PyCharmVenv

    yield PyCharmVenv("Python 3.11 (hatch-pycharm)", Path(sys.executable), ROOT)


@pytest.fixture
def config_vars() -> "PythonConfigVars":
    import sysconfig

    return PythonConfigVars(**sysconfig.get_config_vars())


@pytest.fixture
def jdk_element() -> Element:
    return fromstring(
        r"""<jdk version="2">
    <name value="Python 3.11 (hatch-pycharm)"/>
    <type value="Python SDK"/>
    <version value="Python 3.11.3"/>
    <homePath value="C:\Users\veigar\PycharmProjects\hatch-pycharm\.hatch\hatch-pycharm\Scripts\python.exe"/>
    <roots>
        <classPath>
            <root type="composite">
                <root url="file://$USER_HOME$/AppData/Local/Programs/Python/Python311/DLLs" type="simple"/>
                <root url="file://$USER_HOME$/AppData/Local/Programs/Python/Python311/Lib" type="simple"/>
                <root url="file://$USER_HOME$/AppData/Local/Programs/Python/Python311" type="simple"/>
                <root url="file://$USER_HOME$/PycharmProjects/hatch-pycharm/.hatch/hatch-pycharm" type="simple"/>
                <root url="file://$USER_HOME$/PycharmProjects/hatch-pycharm/.hatch/hatch-pycharm/Lib/site-packages"
                      type="simple"/>
                <root url="file://$USER_HOME$/AppData/Local/JetBrains/PyCharm2023.2/python_stubs/374006827"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/python-skeletons" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stdlib" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/gdb" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/six" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/boto" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/cffi" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/mock" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pytz" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/toml" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/tqdm" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/annoy" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/babel" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/emoji" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/first" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/fpdf2" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/ldap3" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/polib" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/redis" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/regex" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/retry" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/ujson" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/bleach" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/caldav" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/docopt" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/hdbcli" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/invoke" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/passpy" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/Pillow" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/psutil" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pycurl" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pynput" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pysftp" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/PyYAML" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/stripe" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/xxhash" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/zxcvbn" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/appdirs" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/certifi" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/chardet" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/chevron" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/D3DShot" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/passlib" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pyaudio" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/PyMySQL" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pyvmomi" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/slumber" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/tzlocal" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/urllib3" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/vobject" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/aiofiles" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/colorama" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/croniter" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/docutils" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/html5lib" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/httplib2" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/jmespath" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/keyboard" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/Markdown" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/oauthlib" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/openpyxl" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/paramiko" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/psycopg2" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pyflakes" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/Pygments" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/requests" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/tabulate" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/toposort" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/waitress" type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/braintree"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/decorator"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/freezegun"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/playsound"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/PyAutoGUI"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pyOpenSSL"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pyRFC3339"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/termcolor"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/ttkthemes"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/typed-ast"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/xmltodict"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/cachetools"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/commonmark"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/dateparser"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/Deprecated"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/Flask-Cors"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/jsonschema"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pyfarmhash"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/Send2Trash"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/setuptools"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/simplejson"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/SQLAlchemy"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/contextvars"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/entrypoints"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/flake8-2020"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/JACK-Client"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/mysqlclient"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/opentracing"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pep8-naming"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/prettytable"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pyinstaller"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/python-jose"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/python-nmap"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/stdlib-list"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/tree-sitter"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/atomicwrites"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/aws-xray-sdk"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/cryptography"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/editdistance"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/parsimonious"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/whatthepatch"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/click-spinner"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/DateTimeRange"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/humanfriendly"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/python-gflags"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/beautifulsoup4"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/flake8-bugbear"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/python-slugify"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/singledispatch"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/dj-database-url"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/flake8-builtins"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/flake8-simplify"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/mypy-extensions"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/python-dateutil"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/Flask-SQLAlchemy"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/flake8-docstrings"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/flake8-plugin-utils"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/pytest-lazy-fixture"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/flake8-rst-docstrings"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/flake8-typing-imports"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/tree-sitter-languages"
                      type="simple"/>
                <root url="file://$APPLICATION_HOME_DIR$/plugins/python/helpers/typeshed/stubs/backports.ssl_match_hostname"
                      type="simple"/>
            </root>
        </classPath>
        <sourcePath>
            <root type="composite"/>
        </sourcePath>
    </roots>
    <additional ASSOCIATED_PROJECT_PATH="$USER_HOME$/PycharmProjects/hatch-pycharm"
                SDK_UUID="6493cba4-b306-4764-8c17-e2efff5259b2">
        <setting name="FLAVOR_ID" value="VirtualEnvSdkFlavor"/>
        <setting name="FLAVOR_DATA" value="{}"/>
    </additional>
</jdk>
"""
    )


@pytest.fixture
def misc_element_static() -> Element:
    return fromstring(
        r"""<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" project-jdk-name="Python 3.11 (hatch-pycharm)" project-jdk-type="Python SDK" />
</project>"""
    )


@pytest.fixture()
def current_project_misc_file() -> Element:
    misc_file = ROOT / ".idea" / "misc.xml"
    yield fromstring(misc_file.read_text())


@pytest.fixture()
def current_tools_jdk_file() -> Element:
    yield fromstring(settings.jdk_tools_xml.read_text())


def jetbrains_path_render(jb_path: str) -> Path:
    user_home = str(Path.home())
    app_home = str(settings.config_dir)
    jb_path = jb_path.replace("$APPLICATION_HOME_DIR$", app_home)
    jb_path = jb_path.replace("$USER_HOME$", user_home)
    return Path(jb_path).resolve()


@pytest.fixture()
def current_jdk_element(current_tools_jdk_file, current_project_venv) -> Element:
    current_project_venv.sdk_uuid
    for jdk_elem in current_tools_jdk_file.iterfind(f".//jdk"):
        addl = jdk_elem.find("./additional")
        project_path = addl.attrib.get(assc_project_path)
        project_path = jetbrains_path_render(project_path)
        hp = jdk_elem.find("./homePath")
        home_path = hp.attrib.get("value")
        home_path = jetbrains_path_render(home_path)
        if project_path == current_project_venv.associated_project_path and home_path == current_project_venv.exe_loc:
            yield jdk_elem
            # Don't keep trying to find stuff after we have returned something
            break
