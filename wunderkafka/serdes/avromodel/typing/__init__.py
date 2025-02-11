from typing import Optional, Type, get_origin, get_args


def is_generic_type(annotation: Optional[type[object]]) -> bool:
    return get_origin(annotation) is not None and len(get_args(annotation)) > 0
