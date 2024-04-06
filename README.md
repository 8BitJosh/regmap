# regmap

regmap is a lightweight library to manage direct register field manipulation.

Many times been in the situation where for development I have wanted to interact with an embedded system, where for testing I just want read and write raw register values.
Most of these devices contain registers with multiple fields of varying bit lengths.
This library abstracts away the awkward bit manipulation into a simple register definition.

## Installation

You can install regmap from PyPi with the following command:

```bash
pip install regmap
```

## Usage

### Define an interface

The interface is the code that interacts with the system containing the registers.
A read and a write method need to be defined.

```python
from regmap import Interface


class DeviceInterface(Interface):
    def read(self, address: int) -> int:
        # Function to go read a register from our device
        value = read_val_from_register(address)
        return value

    def write(self, address: int, value: int) -> None:
        # Function to go write a value to a register on our device
        write_val_to_register(address, value)
```

### Define our registers

```python
from regmap import BitField, Register


class config_reg_a_def(Register):
    _name = "config_reg_a"
    _address = 0x2000

    output = BitField(7:1)
    enable = BitField(0)


class config_reg_b_def(Register):
    _name = "config_reg_b"
    _address = 0x2004

    setting2 = BitField(7:5)
    setting1 = BitField(4:2)
    setting0 = BitField(1:0)


class Registers:
    def __init__(self, interface):
        self.config_reg_a = config_reg_a_def(interface)
        self.config_reg_b = config_reg_b_def(interface)
```

### Set some values

The context manager will deal with reading and writing to the register.
By default the context manager will do read, modify, write.
This can be changed to perform read-only or write-only operations.

```python
from regmap import Mode


interface = DeviceInterface()
registers = Registers(interface)

# Perform read, modify, write
with registers.config_reg_a:
    registers.config_reg_a.output = 20
    registers.config_reg_a.enable = 1

# Perform read only, will warn if modifications were attempted
with register.config_reg_a(Mode.RO):
    print(register.config_reg_a.output)

# Perform write only, zeros will be written in any unset fields
with register.config_reg_b(Mode.WO)
    registers.config_reg_b.setting1 = 2
```
