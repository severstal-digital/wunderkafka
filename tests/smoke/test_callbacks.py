from typing import Optional

import pytest
from confluent_kafka import KafkaError

from wunderkafka.callbacks import info_callback, error_callback


class Message(object):

    def topic(self) -> str:
        return 'test'

    def partition(self) -> Optional[int]:
        return 1


@pytest.mark.parametrize("callback", [error_callback, info_callback])
@pytest.mark.parametrize("callback_args", [(None, Message()), (KafkaError(10), Message())])
def test_just_print(callback, callback_args) -> None:
    callback(*callback_args)
