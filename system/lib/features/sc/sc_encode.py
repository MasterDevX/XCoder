import os

from loguru import logger

from system.lib.features.sc import compile_sc
from system.localization import locale


def sc_encode():
    folder = './SC/In-Decompressed'
    folder_export = './SC/Out-Compressed'

    for file in os.listdir(folder):
        try:
            compile_sc(f'{folder}/{file}/', folder_export=folder_export)
        except Exception as exception:
            logger.exception(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))

        print()