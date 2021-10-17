import os

from loguru import logger

from system.lib.features.place_sprites import place_sprites
from system.lib.features.sc import compile_sc
from system.localization import locale


def sc1_encode(overwrite: bool = False):
    folder = './SC/In-Sprites/'
    folder_export = './SC/Out-Compressed/'
    files = os.listdir(folder)

    for file in files:
        xcod = file + '.xcod'
        if xcod not in os.listdir(f'{folder}{file}/'):
            logger.error(locale.not_found % xcod)
        else:
            try:
                logger.info(locale.dec_sc)
                sheet_image, sheet_image_data = place_sprites(f'{folder}{file}/{xcod}', f'{folder}{file}', overwrite)
                logger.info(locale.dec_sc)
                compile_sc(f'{folder}{file}/', sheet_image, sheet_image_data, folder_export)
            except Exception as exception:
                logger.exception(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))
            print()
