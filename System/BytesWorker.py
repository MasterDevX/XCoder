import struct

class BytesWriter:
    def __init__(self, fileName):
        self.fileName = fileName
        self.handler = None
    
    def WStart(self):
        self.handler = open(self.fileName, "wb+")

    def WStop(self):
        self.handler.close()

    def WBytes(self, value):
        self.handler.write(bytes)

    def WByte(self, value):
        self.handler.write(struct.pack('<b', int(value)))

    def WUnsignedByte(self, value):
        self.handler.write(struct.pack('<B', int(value)))

    def W4Bytes(self, b, bb, bbb, bbbb):
        self.handler.write(struct.pack('4B', b, bb, bbb, bbbb))

    def WShort(self, value):
        self.handler.write(struct.pack('<h', int(value)))

    def WUnsignedShort(self, value):
        self.handler.write(struct.pack('<H', int(value)))

    def WInt(self, value):
        self.handler.write(struct.pack('<i', int(value)))

    def WUnsignedInt(self, value):
        self.handler.write(struct.pack('<I', int(value)))

    def WBool(self, value):
        self.handler.write(struct.pack('<?', int(value)))
