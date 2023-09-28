from confluent_kafka import libversion

_triplet, _ = libversion()

if '-' in _triplet:
    _triplet = _triplet.split('-')[0]
__version__ = tuple(int(digit) for digit in _triplet.split('.'))
