import logging
import subprocess
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
import re
from xml.etree.ElementTree import Element, SubElement, tostring

log = logging.getLogger(__name__)


@dataclass()
class PyCharmVenv:
    name: str
    exe_loc: Path
    type: str = "Python SDK"
    flavor_id: str = "VirtualEnvSdkFlavor"

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

    def _build_roots(self):
        """Assemble the paths to add to the Virtual Environment's system path"""
        pass

    def build_jdk_xml(self):
        """Goes to  $PycharmConfig/options/jdk.table.xml"""
        pass

    def _build_jdk_element(self) -> Element:
        """Returns the ElementTree object for the jdk xml"""
        pass

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
