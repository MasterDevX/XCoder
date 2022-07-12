import os
import struct

from PIL import Image
from loguru import logger

from system.bytestream import Writer
from system.lib.console import Console
from system.lib.features.files import write_sc
from system.lib.images import get_pixel_size, split_image, save_texture
from system.lib.xcod import FileInfo
from system.localization import locale


def compile_sc(_dir, file_info: FileInfo, sheets: list = None, output_folder: str = None):
    name = _dir.split('/')[-2]

    if sheets:
        files = sheets
    else:
        files = []
        [files.append(i) if i.endswith('.png') else None for i in os.listdir(_dir)]
        files.sort()
        if not files:
            return logger.info(locale.dir_empty % _dir.split('/')[-2])
        files = [Image.open(f'{_dir}{i}') for i in files]

    logger.info(locale.collecting_inf)
    sc = Writer()

    use_lzham = file_info.use_lzham

    for picture_index in range(len(files)):
        sheet_info = file_info.sheets[picture_index]
        img = files[picture_index]
        print()

        file_type = sheet_info.file_type
        pixel_type = sheet_info.pixel_type

        if img.size != sheet_info.size:
            logger.info(locale.illegal_size % (sheet_info.width, sheet_info.height, img.width, img.height))

            if Console.question(locale.resize_qu):
                logger.info(locale.resizing)
                img = img.resize(sheet_info.size, Image.ANTIALIAS)

        width, height = img.size
        pixel_size = get_pixel_size(pixel_type)

        file_size = width * height * pixel_size + 5

        logger.info(locale.about_sc % (name, picture_index, pixel_type, width, height))

        sc.write(struct.pack('<BIBHH', file_type, file_size, pixel_type, width, height))

        if file_type in (27, 28):
            split_image(img)
            print()

        save_texture(sc, img, pixel_type)
        print()

    sc.write(bytes(5))
    print()

    write_sc(f'{output_folder}/{name}.sc', sc.getvalue(), use_lzham)
