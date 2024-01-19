import inspect
import sys
import typing
from types import MappingProxyType
from typing import Any, List, Type, Union, get_origin

# We check it via import to avoid using nested imports in implementation in `is_union_type() function`
HAS_UNION_TYPE = True
try:
    from types import UnionType  # type: ignore[attr-defined]
except ImportError:
    HAS_UNION_TYPE = False

if sys.version_info >= (3, 9):
    from typing import Annotated
else:
    from typing_extensions import Annotated


def create_annotation(generic: Any, types_list: List[Type[object]]) -> Type[object]:
    # return generic[Union[types_list]]
    return generic[tuple(types_list)]


# Same as `sys.version_info <= (3, 10)`
if HAS_UNION_TYPE is False:
    def is_union_type(generic: Any) -> bool:
        return False
else:
    def is_union_type(generic: Any) -> bool:
        return inspect.isclass(generic) and issubclass(generic, UnionType)

if sys.version_info >= (3, 9):
    def get_generic(annotation: Any) -> Any:
        return get_origin(annotation)

    def is_annotated_type(annotation: Any) -> bool:
        return get_origin(annotation) is Annotated
else:
    _TYPE_MAPPING = MappingProxyType({
        getattr(t, '__origin__', None): t for t in typing.__dict__.values() if hasattr(t, '__origin__')
    })

    def get_generic(annotation: Any) -> Any:
        origin = get_origin(annotation)
        if origin is Union:
            return Union
        return _TYPE_MAPPING.get(origin)

    def is_annotated_type(annotation: Any) -> bool:
        return hasattr(annotation, '__metadata__') and hasattr(annotation, '__origin__')
