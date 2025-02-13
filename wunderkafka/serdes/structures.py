from dataclasses import dataclass


class Mask:
    def __init__(self, value: str):
        self._value = value
        self.__unpack = f'>{self._value}'
        self.__pack = f'>b{self._value}'

    @property
    def unpack(self) -> str:
        return self.__unpack

    @property
    def pack(self) -> str:
        return self.__pack


@dataclass(frozen=True)
class Protocol:
    header_size: int
    mask: Mask
