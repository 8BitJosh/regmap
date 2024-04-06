from typing import Protocol


class Interface(Protocol):
    def read(self, address: int) -> int:
        ...

    def write(self, address: int, value: int):
        ...
