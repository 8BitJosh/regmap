from regmap import BitField, Interface, Register


class DeviceInterface(Interface):
    def __init__(self, read_val: int) -> None:
        self.read_val = read_val
        self.write_val = None

    def read(self, address: int) -> int:
        return self.read_val

    def write(self, address: int, value: int) -> None:
        self.write_val = value


class test_reg(Register):
    _name = "test_reg"
    _address = 0x2000

    field4 = BitField(7, 4)
    field3 = BitField(3, 1)
    field1 = BitField(0)


def test_register_rmw():
    interface = DeviceInterface(0)
    register = test_reg(interface)

    # Write to the field using the upper 4 bits
    with register:
        register.field4 = 10

    assert interface.write_val == (10 << 4)
