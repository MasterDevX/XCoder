import io
from typing import Literal, Optional


class Reader(io.BytesIO):
    def __init__(
        self,
        initial_buffer: bytes = b"",
        endian: Literal["little", "big"] = "little",
    ):
        super().__init__(initial_buffer)
        self.endian: Literal["little", "big"] = endian

    def read_integer(self, length: int, signed=False) -> int:
        return int.from_bytes(self.read(length), self.endian, signed=signed)

    def read_uchar(self) -> int:
        return self.read_integer(1)

    def read_char(self) -> int:
        return self.read_integer(1, True)

    def read_ushort(self) -> int:
        return self.read_integer(2)

    def read_short(self) -> int:
        return self.read_integer(2, True)

    def read_uint(self) -> int:
        return self.read_integer(4)

    def read_int(self) -> int:
        return self.read_integer(4, True)

    def read_twip(self) -> float:
        return self.read_int() / 20

    def read_string(self) -> str:
        length = self.read_uchar()
        if length != 255:
            return self.read(length).decode()
        return ""


class Writer(io.BytesIO):
    def __init__(self, endian: Literal["little", "big"] = "little"):
        super().__init__()
        self._endian: Literal["little", "big"] = endian

    def write_int(self, integer: int, length: int = 1, signed: bool = False):
        self.write(integer.to_bytes(length, self._endian, signed=signed))

    def write_ubyte(self, integer: int):
        self.write_int(integer)

    def write_byte(self, integer: int):
        self.write_int(integer, signed=True)

    def write_uint16(self, integer: int):
        self.write_int(integer, 2)

    def write_int16(self, integer: int):
        self.write_int(integer, 2, True)

    def write_uint32(self, integer: int):
        self.write_int(integer, 4)

    def write_int32(self, integer: int):
        self.write_int(integer, 4, True)

    def write_string(self, string: Optional["str"] = None):
        if string is None:
            self.write_byte(255)
            return
        encoded = string.encode()
        self.write_byte(len(encoded))
        self.write(encoded)
