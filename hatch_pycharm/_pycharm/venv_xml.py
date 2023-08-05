import json
import logging
import re
import subprocess
import sysconfig
import uuid
from dataclasses import dataclass, field
from functools import cached_property
from itertools import chain
from pathlib import Path
from typing import Iterable, ClassVar
from uuid import UUID
from xml.etree.ElementTree import Element, SubElement, tostring

from hatch_pycharm._pycharm import pycharm_exe, app_root, plugins_folder

log = logging.getLogger(__name__)


@dataclass()
class PythonConfigVars:
    """
    Represents configuration variables for a Python project.

    :param prefix: The path to the project's prefix directory.
    :param exec_prefix: The path to the project's exec_prefix directory.
    :param py_version: The Python version string.
    :param py_version_short: The short form of the Python version string.
    :param py_version_nodot: The Python version string without dots.
    :param installed_base: The path to the installed base directory.
    :param base: The path to the project's base directory.
    :param installed_platbase: The path to the installed platbase directory.
    :param platbase: The path to the project's platbase directory.
    :param projectbase: The path to the project's projectbase directory.
    :param platlibdir: The platlib directory name.
    :param abiflags: ABI flags string.
    :param py_version_nodot_plat: The Python version string without dots for platbase.
    :param LIBDEST: The path to the LIBDEST directory.
    :param BINLIBDEST: The path to the BINLIBDEST directory.
    :param INCLUDEPY: The path to the INCLUDEPY directory.
    :param EXT_SUFFIX: The extension suffix string.
    :param EXE: The executable file extension string.
    :param VERSION: The version string.
    :param BINDIR: The path to the BINDIR directory.
    :param TZPATH: The TZPATH string.
    :param VPATH: The path to the VPATH directory.
    :param userbase: The path to the userbase directory.
    :param srcdir: The path to the srcdir directory.
    """

    path_json_script: ClassVar[
        str
    ] = """\
    import json
    import sysconfig
    import sys
    json.dump(sysconfig.get_config_vars({keys}), sys.stdout)"""
    prefix: Path = r"C:\Users\veigar\PycharmProjects\hatch-pycharm\.hatch\hatch-pycharm"
    exec_prefix: Path = r"C:\Users\veigar\PycharmProjects\hatch-pycharm\.hatch\hatch-pycharm"
    py_version: str = "3.11.3"
    py_version_short: str = "3.11"
    py_version_nodot: str = "311"
    installed_base: Path = r"C:\Users\veigar\AppData\Local\Programs\Python\Python311"
    base: Path = r"C:\Users\veigar\PycharmProjects\hatch-pycharm\.hatch\hatch-pycharm"
    installed_platbase: Path = r"C:\Users\veigar\AppData\Local\Programs\Python\Python311"
    platbase: Path = r"C:\Users\veigar\PycharmProjects\hatch-pycharm\.hatch\hatch-pycharm"
    projectbase: Path = r"C:\Users\veigar\AppData\Local\Programs\Python\Python311"
    platlibdir: str = "DLLs"
    abiflags: str = ""
    py_version_nodot_plat: str = "311"
    LIBDEST: Path = r"C:\Users\veigar\AppData\Local\Programs\Python\Python311\Lib"
    BINLIBDEST: Path = r"C:\Users\veigar\PycharmProjects\hatch-pycharm\.hatch\hatch-pycharm\Lib"
    INCLUDEPY: Path = r"C:\Users\veigar\AppData\Local\Programs\Python\Python311\Include"
    EXT_SUFFIX: str = ".cp311-win_amd64.pyd"
    EXE: str = ".exe"
    VERSION: str = "311"
    BINDIR: Path = r"C:\Users\veigar\PycharmProjects\hatch-pycharm\.hatch\hatch-pycharm\Scripts"
    TZPATH: str = ""
    VPATH: Path = r"..\.."
    userbase: Path = r"C:\Users\veigar\AppData\Roaming\Python"
    srcdir: Path = r"C:\Users\veigar\AppData\Local\Programs\Python\Python311"

    @classmethod
    def from_json_str(cls, config_vars: str | bytes):
        import json

        return cls(**json.loads(config_vars))

    @classmethod
    def from_current_interpreter(cls):
        return cls(**sysconfig.get_config_vars())


@dataclass()
class PyCharmVenv:
    name: str
    exe_loc: Path
    associated_project_path: Path
    sdk_uuid: UUID = field(default_factory=uuid.uuid4)
    type: str = "Python SDK"
    root_type: str = "composite"
    flavor_id: str = "VirtualEnvSdkFlavor"
    flavor_data: dict = field(default_factory=dict)

    @cached_property
    def _exe_version(self):
        """
        Returns the version of the executable file used by PyCharmVenv.

        :return: The version of the executable file.
        """
        return subprocess.run([str(self.exe_loc), "-V"], capture_output=True, text=True, check=True).stdout.strip()

    @property
    def exe_version(self) -> tuple[int, int, int]:
        m = re.match(r"Python (?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<else>.*)$", self._exe_version)
        if m and (else_ := m.group("else")):
            log.warning("Something was matched by else and I haven't tested that `%s`", else_)
        elif m:
            major, minor, patch = map(int, m.groups()[:3])
            return major, minor, patch
        msg = f"parsing version string from `{self._exe_version}` failed!"
        raise RuntimeError(msg)

    def _make_path_relative_to_pycharm_vars(self, path: Path) -> str:
        """
        :param path: The path that needs to be made relative to PyCharm variables. :return: The path made relative to
        PyCharm variables. If the given path is already relative to any of the PyCharm variables, it returns the path
        with the variable name as a prefix. Otherwise, it returns the original path.

        """
        path = path.expanduser().resolve()
        for var_name, var_path in self._java_vars():
            if path.absolute().is_relative_to(var_path):
                return f"${var_name.upper()}$/{path.relative_to(var_path).as_posix()}"
        return f"{path}"

    def _java_vars(self) -> Iterable[tuple[str, Path]]:
        """
        Returns an iterable of tuples containing Java environment variables and their corresponding values.

        Each tuple in the iterable consists of a string representing the name of the Java environment variable and a
        `Path` object representing its value.

        :param self: The `PyCharmVenv` object.
        :return: An iterable of tuples containing Java environment variables and their corresponding values.
        """
        yield "APPLICATION_HOME_DIR", app_root
        yield "USER_HOME", Path("~").expanduser()

    def _build_roots(self) -> Iterable[dict[str, str]]:
        """Assemble the paths to add to the Virtual Environment's system path"""
        for root in chain(self._python_roots(), self._helpers_dir_roots()):
            yield {"url": f"file://{self._make_path_relative_to_pycharm_vars(root)}", "type": "simple"}

    def _helpers_dir_roots(self) -> Iterable[Path]:
        """Walks the $APP_HOME_DIR/plugins/python/helpers dir to build part of the `root` objects"""
        helpers = plugins_folder / "python/helpers"
        assert helpers.is_dir()
        type_shed = helpers / "typeshed"
        yield helpers / "python-skeletons"
        yield type_shed / "stdlib"
        stubs_dir = type_shed / "stubs"
        assert stubs_dir.is_dir()
        yield from filter(lambda x: x.is_dir(), stubs_dir.iterdir())

    def build_jdk_xml(self) -> str:
        """Goes to  $PycharmConfig/options/jdk.table.xml"""
        return tostring(self._build_jdk_element(), "utf-8").decode("UTF-8")

    def _build_jdk_element(self) -> Element:
        """
        Builds an XML element representing a JDK in the PyCharm project configuration.

        :return: The XML element representing the JDK
        """
        jdk = Element("jdk", version="2")

        SubElement(jdk, "name", value=self.name)
        SubElement(jdk, "type", value=self.type)
        SubElement(jdk, "version", value=self._exe_version)
        SubElement(jdk, "homePath", value=str(self.exe_loc))

        roots = SubElement(jdk, "roots")
        classPath = SubElement(roots, "classPath")
        root_composite = SubElement(classPath, "root", type=self.root_type)

        for elem in self._build_roots():
            SubElement(root_composite, "root", type=elem["type"], url=f"file://{elem['url']}")

        sourcePath = SubElement(roots, "sourcePath")
        SubElement(sourcePath, "root", type="composite")
        # the `additional` element, contains the project path and UUID
        jdk.append(self._build_additional_element())
        return jdk

    def _build_additional_element(self) -> Element:
        element = Element(
            "additional",
            attrib={
                "ASSOCIATED_PROJECT_PATH": self._make_path_relative_to_pycharm_vars(self.associated_project_path),
                "SDK_UUID": str(self.sdk_uuid),
            },
        )
        SubElement(element, "setting", attrib={"name": "FLAVOR_ID", "VALUE": self.flavor_id})
        SubElement(element, "setting", attrib={"name": "FLAVOR_DATA", "VALUE": json.dumps(self.flavor_data)})
        return element

    def build_misc_xml(self) -> str:
        """Goes to the .idea/misc.xml file"""
        return tostring(self._build_misc_element(), "utf-8").decode("UTF-8")

    def _build_misc_element(self) -> Element:
        """Returns the ElementTree object for the tree xml"""
        project = Element("project", version="4")
        SubElement(
            project,
            "component",
            {
                "name": "ProjectRootManager",
                "version": "2",
                "project-jdk-name": str(self.name),
                "project-jdk-type": self.type,
            },
        )

        return project

    def _python_roots(self):
        """We are asking the Python for its paths"""
        return
        # noinspection PyUnreachableCode
        yield
