import os
import struct

from PIL import Image
from loguru import logger

from system.bytestream import Writer
from system.lib.console import Console
from system.lib.features.files import write_sc
from system.lib.images import get_pixel_size, split_image, rgba2bytes
from system.localization import locale


def compile_sc(_dir, from_memory=None, img_data=None, folder_export=None):
    sc_data = None

    name = _dir.split('/')[-2]
    if from_memory:
        files = from_memory
    else:
        files = []
        [files.append(i) if i.endswith('.png') else None for i in os.listdir(_dir)]
        files.sort()
        if not files:
            return logger.info(locale.dir_empty % _dir.split('/')[-2])
        files = [Image.open(f'{_dir}{i}') for i in files]

    logger.info(locale.collecting_inf)
    sc = Writer()

    has_xcod = False
    use_lzham = False
    if from_memory:
        use_lzham = img_data['use_lzham']
    else:
        try:
            sc_data = open(f'{_dir}/{name}.xcod', 'rb')
            sc_data.read(4)
            use_lzham, = struct.unpack('?', sc_data.read(1))
            sc_data.read(1)
            has_xcod = True
        except OSError:
            logger.info(locale.not_xcod)
            logger.info(locale.default_types)

    for picture_index in range(len(files)):
        img = files[picture_index]
        print()

        if from_memory:
            file_type = img_data['data'][picture_index]['file_type']
            pixel_type = img_data['data'][picture_index]['pixel_type']
        else:
            if has_xcod:
                file_type, pixel_type, width, height = struct.unpack('>BBHH', sc_data.read(6))

                if (width, height) != img.size:
                    logger.info(locale.illegal_size % (width, height, img.width, img.height))
                    if Console.question(locale.resize_qu):
                        logger.info(locale.resizing)
                        img = img.resize((width, height), Image.ANTIALIAS)
            else:
                file_type, pixel_type = 1, 0

        width, height = img.size
        pixel_size = get_pixel_size(pixel_type)

        file_size = width * height * pixel_size + 5

        logger.info(locale.about_sc % (name, picture_index, pixel_type, width, height))

        sc.write(struct.pack('<BIBHH', file_type, file_size, pixel_type, width, height))

        if file_type in (27, 28):
            split_image(img)
            print()

        rgba2bytes(sc, img, pixel_type)
        print()

    sc.write(bytes(5))
    print()

    write_sc(f'{folder_export}/{name}.sc', sc.getvalue(), use_lzham)
