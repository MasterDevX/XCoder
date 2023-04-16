import struct
from pathlib import Path
from typing import List

from loguru import logger
from PIL import Image

from system.bytestream import Writer
from system.lib.console import Console
from system.lib.features.files import write_sc
from system.lib.images import get_byte_count_by_pixel_type, save_texture, split_image
from system.lib.xcod import FileInfo
from system.localization import locale


def compile_sc(
    output_folder: Path,
    file_info: FileInfo,
    sheets: List[Image.Image],
):
    sc = Writer()

    for picture_index in range(len(sheets)):
        sheet_info = file_info.sheets[picture_index]
        sheet = sheets[picture_index]

        file_type = sheet_info.file_type
        pixel_type = sheet_info.pixel_type

        if sheet.size != sheet_info.size:
            logger.info(
                locale.illegal_size
                % (sheet_info.width, sheet_info.height, sheet.width, sheet.height)
            )

            if Console.question(locale.resize_qu):
                logger.info(locale.resizing)
                sheet = sheet.resize(sheet_info.size, Image.ANTIALIAS)

        width, height = sheet.size
        pixel_size = get_byte_count_by_pixel_type(pixel_type)

        file_size = width * height * pixel_size + 5

        logger.info(
            locale.about_sc % (file_info.name, picture_index, pixel_type, width, height)
        )

        sc.write(struct.pack("<BIBHH", file_type, file_size, pixel_type, width, height))

        if file_type in (27, 28):
            split_image(sheet)

        save_texture(sc, sheet, pixel_type)
        print()

    sc.write(bytes(5))

    write_sc(output_folder / f"{file_info.name}.sc", sc.getvalue(), file_info.use_lzham)
