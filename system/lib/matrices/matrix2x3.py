from system.bytestream import Reader

DEFAULT_MULTIPLIER = 1024
PRECISE_MULTIPLIER = 65535


class Matrix2x3:
    def __init__(self):
        self.shear_x: float = 0
        self.shear_y: float = 0
        self.scale_x: float = 1
        self.scale_y: float = 1
        self.x: float = 0
        self.y: float = 0

    def load(self, reader: Reader, tag: int):
        divider: int
        if tag == 8:
            divider = DEFAULT_MULTIPLIER
        elif tag == 36:
            divider = PRECISE_MULTIPLIER
        else:
            raise ValueError(f"Unsupported matrix tag: {tag}")

        self.scale_x = reader.read_int() / divider
        self.shear_x = reader.read_int() / divider
        self.shear_y = reader.read_int() / divider
        self.scale_y = reader.read_int() / divider
        self.x = reader.read_twip()
        self.y = reader.read_twip()

    def apply_x(self, x: float, y: float):
        return x * self.scale_x + y * self.shear_y + self.x

    def apply_y(self, x: float, y: float):
        return y * self.scale_y + x * self.shear_x + self.y
