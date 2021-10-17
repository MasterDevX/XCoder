import os
import time

from loguru import logger

from system import run
from system.lib import config
from system.localization import locale


def update_outdated(outdated):
    for package in outdated:
        update_package(package)


def update_package(package):
    run(f'pip3 install --upgrade {package}')


def download_update(zip_url):
    if not os.path.exists('updates'):
        os.mkdir('updates')

    try:
        import requests

        with open('updates/update.zip', 'wb') as f:
            f.write(requests.get(zip_url).content)
            f.close()

        import zipfile

        with zipfile.ZipFile('updates/update.zip') as zf:
            zf.extractall('updates/')
            zf.close()

            folder_name = f' "{zf.namelist()[0]}"'
            logger.opt(colors=True).info(f'<green>{locale.update_done % folder_name}</green>')
            config.has_update = True
            config.last_update = int(time.time())
            config.dump()
            input(locale.to_continue)
            exit()

        del requests
    except ImportError as exception:
        logger.exception(exception)
