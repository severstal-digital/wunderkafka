import datetime

from my_module import MyConsumer


if __name__ == '__main__':
    consumer = MyConsumer()
    consumer.subscribe(['my_topic'], with_timedelta=datetime.timedelta(minutes=2))
    while True:
        msgs = consumer.consume()
        ...
