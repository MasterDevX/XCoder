import struct
from typing import Callable, TypeAlias

from system.bytestream import Reader

PixelChannels: TypeAlias = tuple[int, ...]
WriteFunction: TypeAlias = Callable[[PixelChannels], bytes]
ReadFunction: TypeAlias = Callable[[Reader], PixelChannels]


def get_read_function(pixel_type: int) -> ReadFunction | None:
    if pixel_type in _read_functions:
        return _read_functions[pixel_type]
    return None


def get_write_function(pixel_type: int) -> WriteFunction | None:
    if pixel_type in _write_functions:
        return _write_functions[pixel_type]
    return None


def get_channel_count_by_pixel_type(pixel_type: int) -> int:
    if pixel_type == 4:
        return 3
    elif pixel_type == 6:
        return 2
    elif pixel_type == 10:
        return 1
    return 4


def _read_rgba8(reader: Reader) -> PixelChannels:
    return (
        reader.read_uchar(),
        reader.read_uchar(),
        reader.read_uchar(),
        reader.read_uchar(),
    )


def _read_rgba4(reader: Reader) -> PixelChannels:
    p = reader.read_ushort()
    return (
        (p >> 12 & 15) << 4,
        (p >> 8 & 15) << 4,
        (p >> 4 & 15) << 4,
        (p >> 0 & 15) << 4,
    )


def _read_rgb5a1(reader: Reader) -> PixelChannels:
    p = reader.read_ushort()
    return (
        (p >> 11 & 31) << 3,
        (p >> 6 & 31) << 3,
        (p >> 1 & 31) << 3,
        (p & 255) << 7,
    )


def _read_rgb565(reader: Reader) -> PixelChannels:
    p = reader.read_ushort()
    return (p >> 11 & 31) << 3, (p >> 5 & 63) << 2, (p & 31) << 3


def _read_luminance8_alpha8(reader: Reader) -> PixelChannels:
    return (reader.read_uchar(), reader.read_uchar())[::-1]


def _read_luminance8(reader: Reader) -> PixelChannels:
    return (reader.read_uchar(),)


def _write_rgba8(pixel: PixelChannels) -> bytes:
    return struct.pack("4B", *pixel)


def _write_rgba4(pixel: PixelChannels) -> bytes:
    r, g, b, a = pixel
    return struct.pack("<H", a >> 4 | b >> 4 << 4 | g >> 4 << 8 | r >> 4 << 12)


def _write_rgb5a1(pixel: PixelChannels) -> bytes:
    r, g, b, a = pixel
    return struct.pack("<H", a >> 7 | b >> 3 << 1 | g >> 3 << 6 | r >> 3 << 11)


def _write_rgb565(pixel: PixelChannels) -> bytes:
    r, g, b = pixel
    return struct.pack("<H", b >> 3 | g >> 2 << 5 | r >> 3 << 11)


def _write_luminance8_alpha8(pixel: PixelChannels) -> bytes:
    return struct.pack("2B", *pixel[::-1])


def _write_luminance8(pixel: PixelChannels) -> bytes:
    return struct.pack("B", pixel)


_write_functions: dict[int, WriteFunction] = {
    0: _write_rgba8,
    1: _write_rgba8,
    2: _write_rgba4,
    3: _write_rgb5a1,
    4: _write_rgb565,
    6: _write_luminance8_alpha8,
    10: _write_luminance8,
}

_read_functions: dict[int, ReadFunction] = {
    0: _read_rgba8,
    1: _read_rgba8,
    2: _read_rgba4,
    3: _read_rgb5a1,
    4: _read_rgb565,
    6: _read_luminance8_alpha8,
    10: _read_luminance8,
}
