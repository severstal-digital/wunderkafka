from dataclasses import dataclass


class Mask(object):
    def __init__(self, value: str):
        self._value = value
        self.__unpack = '>{0}'.format(self._value)
        self.__pack = '>b{0}'.format(self._value)

    @property
    def unpack(self) -> str:
        return self.__unpack

    @property
    def pack(self) -> str:
        return self.__pack


@dataclass(frozen=True)
class Protocol(object):
    header_size: int
    mask: Mask
