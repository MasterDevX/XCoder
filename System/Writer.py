from io import BytesIO

class BinaryWriter:

    def __init__(self):
        self._buffer = BytesIO()

    @property
    def buffer(self):
        return self._buffer.getvalue()

    @buffer.setter
    def buffer(self, data):
        self._buffer.seek(0)
        self._buffer.truncate(0)
        self._buffer.write(data)

    def write(self, value):
        self._buffer.write(bytes(value))

    def write_uint8(self, value):
        self._buffer.write(value.to_bytes(1, 'little'))

    def write_int8(self, value):
        self._buffer.write(value.to_bytes(1, 'little', signed=True))

    def write_uint16(self, value):
        self._buffer.write(value.to_bytes(2, 'little'))

    def write_int16(self, value):
        self._buffer.write(value.to_bytes(2, 'little', signed=True))

    def write_uint32(self, value, byteorder='little'):
        self._buffer.write(value.to_bytes(4, byteorder))

    def write_int32(self, value):
        self._buffer.write(value.to_bytes(4, 'little'))
