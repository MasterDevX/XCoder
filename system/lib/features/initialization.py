import os
import platform

from loguru import logger

from system import run, clear
from system.lib import config
from system.lib.features.update.check import get_pip_info, get_tags
from system.localization import locale


@logger.catch()
def initialize(first_init=False):
    if first_init:
        clear()

    logger.info(locale.detected_os % platform.system())
    logger.info(locale.installing)

    required_packages = [pkg.rstrip('\n').lower() for pkg in open('requirements.txt').readlines()]
    installed_packages = [pkg[0].lower() for pkg in get_pip_info()]
    for package in required_packages:
        if package in installed_packages:
            continue

        if run(f'pip3 install {package}') == 0:
            logger.info(locale.installed % package)
        else:
            logger.info(locale.not_installed % package)
    logger.info(locale.crt_workspace)
    [[os.makedirs(f'SC/{i}-{k}', exist_ok=True) for k in ['Compressed', 'Decompressed', 'Sprites']] for i in ['In', 'Out']]
    [[os.makedirs(f'CSV/{i}-{k}', exist_ok=True) for k in ['Compressed', 'Decompressed']] for i in ['In', 'Out']]
    logger.info(locale.verifying)

    config.initialized = True
    try:
        import requests
        del requests
        config.version = get_tags('vorono4ka', 'xcoder')[0]['name'][1:]
    except ImportError as exception:
        logger.exception(exception)
    config.dump()

    if first_init:
        input(locale.to_continue)
