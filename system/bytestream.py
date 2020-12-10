import io


class Reader(io.BytesIO):
    def __init__(self, buffer: bytes = b'', endian: str = 'little'):
        super().__init__(buffer)
        self.buffer = buffer
        self.endian = endian

    def read_int(self, length: int, signed=False):
        return int.from_bytes(self.read(length), self.endian, signed=signed)

    def ubyte(self):
        return self.read_int(1)

    def byte(self):
        return self.read_int(1, True)

    def uint16(self):
        return self.read_int(2)

    def int16(self):
        return self.read_int(2, True)

    def uint32(self):
        return self.read_int(4)

    def int32(self):
        return self.read_int(4, True)

    def string(self):
        length = self.ubyte()
        if length != 255:
            return self.read(length).decode()
        return ''


class Writer(io.BytesIO):
    def __init__(self):
        super().__init__()

    def write_int(self, integer, length: int = 1, signed: bool = False):
        self.write(integer.to_bytes(length, 'little', signed=signed))

    def ubyte(self, integer):
        self.write_int(integer)

    def byte(self, integer):
        self.write_int(integer, signed=True)

    def uint16(self, integer):
        self.write_int(integer, 2)

    def int16(self, integer):
        self.write_int(integer, 2, True)

    def uint32(self, integer):
        self.write_int(integer, 4)

    def int32(self, integer):
        self.write_int(integer, 4, True)

    def string(self, string: str = None):
        if string is None:
            self.byte(255)
            return
        encoded = string.encode()
        self.byte(len(encoded))
        self.write(encoded)
