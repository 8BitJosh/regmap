import pytest

from regmap import BitField, Interface, Register, RegMode


class DeviceInterface(Interface):
    def __init__(self, read_val: int) -> None:
        self.read_val = read_val
        self.written_val = None

    def read(self, address: int) -> int:
        return self.read_val

    def write(self, address: int, value: int) -> None:
        self.written_val = value


class test_reg(Register):
    _name = "test_reg"
    _address = 0x2000

    field4 = BitField(7, 4)
    field3 = BitField(3, 1)
    field1 = BitField(0)


def test_register_rmw_read():
    interface = DeviceInterface(0b1111_000_1)
    register = test_reg(interface)

    # Check we read ok
    with register:
        assert register.field4 == 0b1111
        assert register.field3 == 0b000
        assert register.field1 == 0b1

    # Check written value is same as start value
    assert interface.written_val == 0b1111_000_1


def test_register_rmw_write():
    interface = DeviceInterface(0b1111_000_1)
    register = test_reg(interface)

    with register:
        register.field3 = 0b111

    # Check we wrote correct value
    assert interface.written_val == 0b1111_111_1

    with register:
        register.field4 = 0b0000

    # Check we wrote correct value
    assert interface.written_val == 0b0000_000_1


def test_register_wo_blank():
    interface = DeviceInterface(0b1111_000_1)
    register = test_reg(interface)

    # Check vals are all 0 in write only mode
    with register(mode=RegMode.WO):
        assert register._value == 0
        assert register.field4 == 0b0000
        assert register.field3 == 0b000
        assert register.field1 == 0b0

    # Check we wrote zero as this is default if no modifications occured in RO
    assert interface.written_val == 0


def test_register_wo_values():
    interface = DeviceInterface(0b1111_000_1)
    register = test_reg(interface)

    # Check vals are all 0 in write only mode
    with register(mode=RegMode.WO):
        register.field1 = 1

    # Check we only wrote back the things we set
    assert interface.written_val == (1 << 0)


def test_register_ro():
    interface = DeviceInterface(0b1111_000_1)
    register = test_reg(interface)

    # Check we read ok
    with register(mode=RegMode.RO):
        assert register.field4 == 0b1111
        assert register.field3 == 0b000
        assert register.field1 == 0b1

    # Check we didnt write
    assert interface.written_val is None


def test_register_ro_write_warn():
    interface = DeviceInterface(0b1111_000_1)
    register = test_reg(interface)

    # Check we warn if we try to write in read only
    with pytest.warns(UserWarning):
        with register(mode=RegMode.RO):
            assert register.field4 == 0b1111
            assert register.field3 == 0b000
            assert register.field1 == 0b1

            register.field1 = 0

    # Check we didnt write a value
    assert interface.written_val is None


def test_register_write_full():
    interface = DeviceInterface(0b1111_000_1)
    register = test_reg(interface)

    # write the whole reg to zero
    with register:
        register._value = 0

    # Check we wrote the correct value
    assert interface.written_val == 0
