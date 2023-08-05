import logging
import re
import subprocess
from dataclasses import dataclass
from functools import cached_property
from itertools import chain
from pathlib import Path
from typing import Iterable
from xml.etree.ElementTree import Element, SubElement, tostring
from hatch_pycharm._pycharm import _PYCHARM

log = logging.getLogger(__name__)


@dataclass()
class PyCharmVenv:
    name: str
    exe_loc: Path
    type: str = "Python SDK"
    flavor_id: str = "VirtualEnvSdkFlavor"
    root_type: str = "composite"

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

    def _make_path_relative_to_pycharm_vars(self, path: Path):
        """
        :param path: The path that needs to be made relative to PyCharm variables. :return: The path made relative to
        PyCharm variables. If the given path is already relative to any of the PyCharm variables, it returns the path
        with the variable name as a prefix. Otherwise, it returns the original path.

        """
        path = path.expanduser().resolve()
        for var_name, var_path in self._java_vars():
            if path.absolute().is_relative_to(var_path):
                return f"${var_name.upper()}${path.relative_to(var_path)}"
        return f"{path}"

    def _java_vars(self) -> Iterable[tuple[str, Path]]:
        """
        Returns an iterable of tuples containing Java environment variables and their corresponding values.

        Each tuple in the iterable consists of a string representing the name of the Java environment variable and a
        `Path` object representing its value.

        :param self: The `PyCharmVenv` object.
        :return: An iterable of tuples containing Java environment variables and their corresponding values.
        """
        yield "APPLICATION_HOME_DIR", self.app_home_dir()
        yield "USER_HOME", Path("~").expanduser()

    def _build_roots(self) -> Iterable[dict[str, str]]:
        """Assemble the paths to add to the Virtual Environment's system path"""
        for root in chain((self._python_roots(), self._helpers_dir_roots())):
            yield {"url": f"file:///{root}", "type": "simple"}

    def _helpers_dir_roots(self) -> Iterable[Path]:
        """Walks the $APP_HOME_DIR/plugins/python/helpers dir to build part of the `root` objects"""
        helpers = self.app_home_dir() / "plugins/python/helpers"
        assert helpers.is_dir()
        type_shed = helpers / "typeshed"
        yield helpers / "python-skeletons"
        yield type_shed / "stdlib"
        stubs_dir = type_shed / "stubs"
        assert stubs_dir.is_dir()
        yield from filter(lambda x: x.is_dir(), stubs_dir.iterdir())

    def app_home_dir(self) -> Path:
        base = Path(_PYCHARM)
        app_home_dir = base.parent.parent
        assert app_home_dir.is_dir()
        return app_home_dir

    def build_jdk_xml(self) -> str:
        """Goes to  $PycharmConfig/options/jdk.table.xml"""
        return tostring(self._build_jdk_element(), "utf-8").decode("UTF-8")

    def _build_jdk_element(self) -> Element:
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
        return jdk

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
        pass
