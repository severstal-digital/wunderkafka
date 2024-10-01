from wunderkafka import librdkafka

# ToDo (tribunsky.kir): looks like that idea of dynamic import via imp depending on librdkafka
#                       wasn't the worst idea, cause `if`s causes a lot of static checks problems.
# mypy: disable-error-code="no-redef"


if librdkafka.__version__ >= (2, 2, 0):
    from wunderkafka.config.generated.confluent_2_2_0.models import (
        RDKafkaConfig,
        RDConsumerConfig,
        RDProducerConfig
    )

elif librdkafka.__version__ >= (2, 1, 0):
    from wunderkafka.config.generated.confluent_2_1_0.models import (
        RDKafkaConfig,
        RDConsumerConfig,
        RDProducerConfig
    )

elif librdkafka.__version__ >= (2, 0, 0):
    from wunderkafka.config.generated.confluent_2_0_0.models import (
        RDKafkaConfig,
        RDConsumerConfig,
        RDProducerConfig
    )

elif librdkafka.__version__ >= (1, 9, 0):
    from wunderkafka.config.generated.confluent_1_9_0.models import (
        RDKafkaConfig,
        RDConsumerConfig,
        RDProducerConfig
    )

elif librdkafka.__version__ >= (1, 8, 0):
    from wunderkafka.config.generated.confluent_1_8_0.models import *

elif librdkafka.__version__ >= (1, 7, 0):
    from wunderkafka.config.generated.confluent_1_7_0.models import *

elif librdkafka.__version__ >= (1, 6, 0):
    from wunderkafka.config.generated.confluent_1_6_0.models import *

elif librdkafka.__version__ >= (1, 5, 0):
    from wunderkafka.config.generated.confluent_1_5_0.models import *
else:
    from wunderkafka.config.generated.default.models import *
