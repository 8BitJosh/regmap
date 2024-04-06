from __future__ import annotations

import warnings
from dataclasses import dataclass
from enum import Enum
from threading import Lock
from typing import Any

from .bitfield import BitField
from .interface import Interface


class Mode(Enum):
    RO = "RO"
    WO = "WO"
    RMW = "RMW"


@dataclass
class State:
    from_call: bool = False
    mode: Mode = Mode.RMW
    modified: bool = False


class Register:
    _name: str
    _address: int

    def __init__(self, interface: Interface) -> None:
        self._interface = interface
        self._value = 0
        self._state = State()
        self._lock = Lock()

        # Grab the bitfield objects and modify them slightly
        for name, item in self.__class__.__dict__.items():
            if isinstance(item, BitField):
                super().__setattr__(name, BitField(item.msb, item.lsb, name))

    @property
    def _bitfields(self) -> list[BitField]:
        # Get a list of the bitfield objects in the register object
        bitfields = []
        for name, item in self.__dict__.items():
            if isinstance(item, BitField):
                bitfields.append(item)

        bitfields.sort(key=lambda b: b.msb, reverse=True)
        return bitfields

    def __getattribute__(self, name: str) -> Any:
        attr = super().__getattribute__(name)
        if isinstance(attr, BitField):
            return (self._value & attr.mask) >> attr.lsb

        return attr

    def __setattr__(self, name: str, value: Any) -> None:
        if name in ("_value", "_interface", "_state", "_lock"):
            return super().__setattr__(name, value)

        attr = super().__getattribute__(name)
        if isinstance(attr, BitField):
            if not isinstance(value, int):
                raise TypeError("Can only set value of bitfield to int")

            attr._check_size(value)

            self._value = (self._value & ~attr.mask) | (value << attr.lsb)
            self._state.modified = True

    def _read(self) -> None:
        # Update the value stored in the register from the interface
        self._value = self._interface.read(self._address)

    def _write(self) -> None:
        # Write the value stored in the register back to the interface
        self._interface.write(self._address, self._value)

    def _obtain_lock(self) -> None:
        self._lock.acquire()
        self._state = State()

    def _release_lock(self) -> None:
        self._state = State
        self._lock.release()

    def __call__(self, *, mode: Mode) -> Register:
        self._obtain_lock()

        self._state.from_call = True
        self._state.mode = mode

        return self

    def __enter__(self) -> Register:
        if self._state.from_call is False:
            self._obtain_lock()

        self._value = 0

        if self._state.mode != Mode.WO:
            try:
                self._read()
            except Exception:
                self._release_lock()
                raise

        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        try:
            if self._state.modified:
                if self._state.mode == Mode.RO:
                    warnings.warn("Attempted to modify register in read only mode")
                else:
                    self._write()
        finally:
            self._release_lock()

    def __str__(self) -> str:
        spacer = len(self._name) * " "
        s = f"<Register @ {hex(self._address)}>\n"
        s += f"{self._name}\n"

        for bitfield in self._bitfields:
            value = (self._value & bitfield.mask) >> bitfield.lsb
            s += f"{spacer}.{bitfield} = {value}\n"

        return s
