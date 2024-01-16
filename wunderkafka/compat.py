import sys

if sys.version_info >= (3, 9):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec
