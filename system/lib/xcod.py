from dataclasses import dataclass
from typing import List, Tuple

from system.bytestream import Reader


@dataclass
class SheetInfo:
    file_type: int
    pixel_type: int
    size: Tuple[int, int]

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]


@dataclass
class FileInfo:
    use_lzham: bool
    sheets: List[SheetInfo]


def parse_info(xcod_path: str) -> (FileInfo, Reader):
    with open(xcod_path, 'rb') as file:
        xcod = Reader(file.read(), 'big')

    magic = xcod.read(4)
    if magic != b'XCOD':
        raise IOError('Unknown file MAGIC: ' + magic.hex())

    use_lzham = xcod.read_ubyte()

    file_info = FileInfo(use_lzham, [])

    sheets_count = xcod.read_ubyte()
    for i in range(sheets_count):
        file_type = xcod.read_ubyte()
        pixel_type = xcod.read_ubyte()
        width = xcod.read_uint16()
        height = xcod.read_uint16()

        file_info.sheets.append(SheetInfo(file_type, pixel_type, (width, height)))

    return file_info, xcod
