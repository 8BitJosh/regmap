from regmap import Interface, Mode
from regmap import BitField, Register


class DeviceInterface(Interface):
    def read(self, address: int) -> int:
        # Function to go read a register from the device
        print(f"Reading value from register at address {address}")
        return 0

    def write(self, address: int, value: int) -> None:
        # Function to go write a value to a register on the device
        print(f"Writing value {value} to register at address {address}")


class config_reg_a_def(Register):
    _name = "config_reg_a"
    _address = 0x2000

    output = BitField(7, 1)
    enable = BitField(0)


class config_reg_b_def(Register):
    _name = "config_reg_b"
    _address = 0x2004

    setting2 = BitField(7, 5)
    setting1 = BitField(4, 2)
    setting0 = BitField(1, 0)


class Registers:
    def __init__(self, interface):
        self.config_reg_a = config_reg_a_def(interface)
        self.config_reg_b = config_reg_b_def(interface)


interface = DeviceInterface()
registers = Registers(interface)

# Perform read, modify, write
with registers.config_reg_a:
    registers.config_reg_a.output = 20
    registers.config_reg_a.enable = 1

# Perform read only, will warn if modifications were attempted
with registers.config_reg_a(mode=Mode.RO):
    print(registers.config_reg_a.output)

# Perform write only, zeros will be written in any unset fields
with registers.config_reg_b(mode=Mode.WO):
    registers.config_reg_b.setting1 = 2
