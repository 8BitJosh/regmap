

class Interface:
    def read(self, address):
        raise NotImplementedError("write function not implimented")

    def write(self, address, value):
        raise NotImplementedError("read function not implimented")


class NullInterface(Interface):
    def read(self, address):
        print("NullInterface - read")
        return 0

    def write(self, address, value):
        print(f"NullInterface - write {address} {value}")
