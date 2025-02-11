"""This module contains some predefined callbacks to interact with librdkafka."""

from typing import List, Optional

from confluent_kafka import Message, KafkaError, TopicPartition

from wunderkafka.logger import logger
from wunderkafka.structures import Timestamp
from wunderkafka.consumers.abc import AbstractConsumer


# FixMe (tribunsky.kir): do not mutate consumer from here, try to closure it in consumer itself.
def reset_partitions(consumer: AbstractConsumer, partitions: list[TopicPartition]) -> None:
    """
    Set specific offset for assignment after subscription.

    Depending on type of subscription, will set offset or timestamp.

    :param consumer:            Consumer, which is subscribes to topics.
    :param partitions:          List of TopicPartitions, which is returned from the underlying library.
    """
    new_offsets = consumer.subscription_offsets
    if new_offsets is None:
        logger.warning(
            f'{consumer}: re-assigned (using auto.offset.reset={consumer.config.auto_offset_reset})',
        )
        return
    by_offset = []
    by_ts = []
    for partition in partitions:
        new_offset = new_offsets[partition.topic]
        if new_offset is None:
            by_offset.append(partition)
        else:
            partition.offset = new_offset.value
            if isinstance(new_offset, Timestamp):
                logger.info(f'Setting {new_offset}...')
                by_ts.append(partition)
            else:
                by_offset.append(partition)
    if by_ts:
        by_ts = consumer.offsets_for_times(by_ts)
    new_ptns = by_ts + by_offset
    consumer.assign(new_ptns)
    logger.info(f'{consumer} assigned to {new_ptns}')
    consumer.subscription_offsets = None


def info_callback(err: Optional[KafkaError], msg: Message) -> None:
    """
    Log every message delivery.

    :param err:             Error, if any, thrown from confluent-kafka cimpl.
    :param msg:             Message to be delivered.
    """
    if err is None:
        logger.info(f'Message delivered to {msg.topic()} partition: {msg.partition()}')
    else:
        logger.error(f'Message failed delivery: {err}')


def error_callback(err: Optional[KafkaError], _: Message) -> None:
    """
    Log only failed message delivery.

    :param err:             Error, if any, thrown from confluent-kafka cimpl.
    :param _:               Message to be delivered (unused, but needed to not break callback signature).
    """
    if err:
        logger.error(f'Message failed delivery: {err}')
