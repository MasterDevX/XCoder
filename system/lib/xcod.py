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


def parse_info(xcod_path: str) -> Tuple[FileInfo, Reader]:
    with open(xcod_path, "rb") as file:
        xcod = Reader(file.read(), "big")

    magic = xcod.read(4)
    if magic != b"XCOD":
        raise IOError("Unknown file MAGIC: " + magic.hex())

    use_lzham = xcod.read_uchar() == 1

    file_info = FileInfo(use_lzham, [])

    sheets_count = xcod.read_uchar()
    for i in range(sheets_count):
        file_type = xcod.read_uchar()
        pixel_type = xcod.read_uchar()
        width = xcod.read_ushort()
        height = xcod.read_ushort()

        file_info.sheets.append(SheetInfo(file_type, pixel_type, (width, height)))

    return file_info, xcod
