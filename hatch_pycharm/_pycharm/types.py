from pathlib import Path
from typing import Literal

BuildNumber = tuple[int, int, int]
Build_EXE = tuple[BuildNumber, Path]
FMT = Literal["xml", "json", "plain"]
