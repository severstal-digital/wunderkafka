import sys

if sys.version_info > (3, 8):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec
