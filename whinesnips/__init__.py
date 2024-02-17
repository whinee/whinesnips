import platform
import warnings
from os import path
from os.path import dirname, realpath
from shutil import get_terminal_size
from sys import platform as PLATFORM
from typing import Final

import msgpack

warnings.filterwarnings("ignore")

DEF_STR = "c0VjUmVUX2NPZEUgYnkgd2hpX25l"

PROJ_ABS_PATH: Final[str] = dirname(realpath(__file__))

try:
    TW = get_terminal_size().columns
    """Stands for terminal width.
    """
except OSError:
    TW = 0

with open(path.join(PROJ_ABS_PATH, "constants", "const.mp"), "rb") as f:
    CONST = msgpack.unpackb(f.read(), raw=False, use_list=True)

PROJECT_NAME = CONST["project"]["name"]
"""Project's name"""

__version__ = CONST["ver"]
"""The current version of the project.

This project uses a modified semver. For more information, visit [this link](../../../../../notes-to-self.md#versioning-system).
"""

CHOLDER = CONST["cholder"]
"""HTML text of copyright holders of this project"""

SVER = CONST["sver"]
"""The current version of the project, compliant with the semver.

This project uses a modified semver. For more information, visit [this link](../../../../../notes-to-self.md#versioning-system).
"""

VLS = CONST["vls"]
"""The current version of the project as a list.

The list consists of 6 integers, which represent the following:
    - User
    - Dev
    - Minor
    - Patch
    - Prerelease Identifier
        The prerelease identifier number corresponds to the following values:
            0: alpha
            1: beta
            2: release candidate or rc
            3: none
    - Prerelease Version
"""

MACHINE = platform.machine()

match PLATFORM:
    case "win32":
        PSH = "win"
        """Platform Short Hand"""
    case "darwin":
        PSH = "mac"
    case _:
        PSH = PLATFORM
