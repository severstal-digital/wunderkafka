from wunderkafka import librdkafka

# ToDo (tribunsky.kir): looks like that idea of dynamic import via imp depending on librdkafka
#                       wasn't the worst idea, cause `if`s causes a lot of static checks problems.
# mypy: disable-error-code="no-redef"


if librdkafka.__version__ >= (2, 2, 0):
    from wunderkafka.config.generated.models_versions.models_2_2_0 import *  # type:ignore[assignment]

elif librdkafka.__version__ >= (2, 1, 0):
    from wunderkafka.config.generated.models_versions.models_2_1_0 import *  # type:ignore[assignment]

elif librdkafka.__version__ >= (2, 0, 0):
    from wunderkafka.config.generated.models_versions.models_2_0_0 import *  # type:ignore[assignment]

elif librdkafka.__version__ >= (1, 9, 0):
    from wunderkafka.config.generated.models_versions.models_1_9_0 import *  # type:ignore[assignment]

elif librdkafka.__version__ >= (1, 8, 0):
    from wunderkafka.config.generated.models_versions.models_1_8_0 import *  # type:ignore[assignment]

elif librdkafka.__version__ >= (1, 7, 0):
    from wunderkafka.config.generated.models_versions.models_1_7_0 import *  # type:ignore[assignment]

elif librdkafka.__version__ >= (1, 6, 0):
    from wunderkafka.config.generated.models_versions.models_1_6_0 import *  # type:ignore[assignment]

elif librdkafka.__version__ >= (1, 5, 0):
    from wunderkafka.config.generated.models_versions.models_1_5_0 import *  # type:ignore[assignment]
else:
    from wunderkafka.config.generated.models_versions.models_default import *          # type:ignore[assignment]
