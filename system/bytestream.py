import io


class Reader(io.BytesIO):
    def __init__(self, buffer: bytes = b'', endian: str = 'little'):
        super().__init__(buffer)
        self.buffer = buffer
        self.endian = endian

    def read_int(self, length: int, signed=False):
        return int.from_bytes(self.read(length), self.endian, signed=signed)

    def read_ubyte(self):
        return self.read_int(1)

    def read_byte(self):
        return self.read_int(1, True)

    def read_uint16(self):
        return self.read_int(2)

    def read_int16(self):
        return self.read_int(2, True)

    def read_uint32(self):
        return self.read_int(4)

    def read_int32(self):
        return self.read_int(4, True)

    def read_string(self):
        length = self.read_ubyte()
        if length != 255:
            return self.read(length).decode()
        return ''


class Writer(io.BytesIO):
    def __init__(self, endian: str = 'little'):
        super().__init__()
        self.endian = endian

    def write_int(self, integer, length: int = 1, signed: bool = False):
        self.write(integer.to_bytes(length, self.endian, signed=signed))

    def write_ubyte(self, integer):
        self.write_int(integer)

    def write_byte(self, integer):
        self.write_int(integer, signed=True)

    def write_uint16(self, integer):
        self.write_int(integer, 2)

    def write_int16(self, integer):
        self.write_int(integer, 2, True)

    def write_uint32(self, integer):
        self.write_int(integer, 4)

    def write_int32(self, integer):
        self.write_int(integer, 4, True)

    def write_string(self, string: str = None):
        if string is None:
            self.write_byte(255)
            return
        encoded = string.encode()
        self.write_byte(len(encoded))
        self.write(encoded)
