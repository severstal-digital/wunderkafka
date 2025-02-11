import inspect
from typing import Any, get_origin

# We check it via import to avoid using nested imports in implementation in `is_union_type() function`
HAS_UNION_TYPE = True
try:
    from types import UnionType  # type: ignore[attr-defined]
except ImportError:
    HAS_UNION_TYPE = False

from typing import Annotated


def create_annotation(generic: Any, types_list: list[type[object]]) -> type[object]:
    # return generic[Union[types_list]]
    return generic[tuple(types_list)]


# Same as `sys.version_info <= (3, 10)`
if HAS_UNION_TYPE is False:
    def is_union_type(generic: Any) -> bool:
        return False
else:
    def is_union_type(generic: Any) -> bool:
        return inspect.isclass(generic) and issubclass(generic, UnionType)

def get_generic(annotation: Any) -> Any:
    return get_origin(annotation)

def is_annotated_type(annotation: Any) -> bool:
    return get_origin(annotation) is Annotated
