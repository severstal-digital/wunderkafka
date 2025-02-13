from typing import Optional, get_args, get_origin


def is_generic_type(annotation: Optional[type[object]]) -> bool:
    return get_origin(annotation) is not None and len(get_args(annotation)) > 0
