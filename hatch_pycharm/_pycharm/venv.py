import subprocess
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from xml.etree.ElementTree import Element

from hatch_pycharm._pycharm.paths import platform_exe_name


@dataclass
class PyCharmVenv:
    name: Path
    type: str = "Python SDK"
    flavor_id: str = "VirtualEnvSdkFlavor"

    @cached_property
    def version(self):
        return subprocess.run([str(self.name), "-V"], capture_output=True, check=True).stdout

    def _build_roots(self):
        """Assemble the paths to add to the Virtual Environment's system path"""

    def build_jdk_xml(self):
        """Goes to  $PycharmConfig/options/jdk.table.xml"""

    def _build_jdk_element(self) -> Element:
        """Returns the ElementTree object for the jdk xml"""

    def build_misc_xml(self):
        """Goes to the .idea/misc.xml file"""

    def _build_misc_element(self) -> Element:
        """Returns the ElementTree object for the tree xml"""
