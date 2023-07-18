from confluent_kafka import libversion

_triplet, _ = libversion()

__version__ = tuple(int(digit) for digit in _triplet.split('.'))
