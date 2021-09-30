"""This module contains helpers to avoid using try/except ImportError pattern."""

import sys

from typing_extensions import Final

PY36: Final = (sys.version_info.major, sys.version_info.minor) == (3, 6)
