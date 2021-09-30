"""Some compatibility dirt to not fail while importing incompatible functionality."""

import warnings

from wunderkafka.compat.constants import PY36

if PY36 is False:
    # package is for python3.7 and higher.
    from dataclasses_avroschema import AvroModel  # noqa: WPS433
else:
    message = ' '.join([
        'Python 3.6 reaches end of lifespan approximately 2021-12.',
        'Please, consider upgrading to python 3.7 or above to use AvroModel.',
    ])
    warnings.warn(message)

    # I "love" mypy. https://github.com/python/mypy/issues/1153
    class AvroModel(object):  # type: ignore  # noqa: WPS440
        """Stub for 3.6."""

        def __init__(self) -> None:
            """
            Stop execution while trying to use it.

            :raises NotImplementedError:        Python 3.6 reaches end of life soon.
            """
            raise NotImplementedError(message)
