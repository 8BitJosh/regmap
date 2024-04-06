from dataclasses import dataclass


@dataclass(frozen=True)
class BitField:
    msb: int
    lsb: int = None  # type:ignore
    name: str = None  # type:ignore

    def __post_init__(self) -> None:
        # If only one is provided lsb = msb
        if self.lsb is None:
            object.__setattr__(self, "lsb", self.msb)

    @property
    def num_bits(self) -> int:
        return (self.msb - self.lsb) + 1

    @property
    def mask(self) -> int:
        # Bit mask for this bitfield
        return ((2 ** self.num_bits) - 1) << self.lsb

    def _check_size(self, value) -> None:
        # Value setter, checks the size of the value fits in this bitfield
        max_value = 2 ** self.num_bits

        if (value < 0) or (value > max_value):
            raise ValueError(f"Value provided ({value}) is too large to fit in {self.num_bits} bit")

    def __str__(self) -> str:
        if self.lsb == self.msb:
            return f"{self.name}[{self.msb}]"
        else:
            return f"{self.name}[{self.msb}:{self.lsb}]"
