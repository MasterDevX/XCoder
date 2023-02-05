import os

from loguru import logger

from system.lib.features.sc import compile_sc
from system.lib.xcod import parse_info
from system.localization import locale


def sc_encode():
    input_folder = "./SC/In-Decompressed"
    output_folder = "./SC/Out-Compressed"

    for folder in os.listdir(input_folder):
        try:
            file_info, _ = parse_info(f"{input_folder}/{folder}/{folder}.xcod")

            compile_sc(
                f"{input_folder}/{folder}/", file_info, output_folder=output_folder
            )
        except FileNotFoundError:
            logger.info(locale.xcod_not_found % folder)
        except Exception as exception:
            logger.exception(
                locale.error
                % (
                    exception.__class__.__module__,
                    exception.__class__.__name__,
                    exception,
                )
            )

        print()
