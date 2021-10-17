import os

from loguru import logger

from system import run
from system.lib import config
from system.lib.features.update.download import download_update
from system.localization import locale


def get_run_output(command: str):
    import tempfile

    temp_filename = tempfile.mktemp('.temp')

    del tempfile
    run(command, temp_filename)

    with open(temp_filename) as f:
        file_data = f.read()
        f.close()

    os.remove(temp_filename)

    return file_data


def get_pip_info(outdated: bool = False) -> list:
    output = get_run_output(f'pip --disable-pip-version-check list {"-o" if outdated else ""}')
    output = output.splitlines()
    output = output[2:]
    packages = [package.split() for package in output]

    return packages


def get_tags(owner: str, repo: str):
    api_url = 'https://api.github.com'
    tags = []

    import requests
    try:
        tags = requests.get(api_url + '/repos/{owner}/{repo}/tags'.format(owner=owner, repo=repo)).json()
        tags = [
            {
                key: v for key, v in tag.items()
                if key in ['name', 'zipball_url']
            } for tag in tags
        ]
    except Exception:
        pass
    del requests

    return tags


def check_update():
    tags = get_tags('vorono4ka', 'xcoder')

    if len(tags) > 0:
        latest_tag = tags[0]
        latest_tag_name = latest_tag['name'][1:]  # clear char 'v' at string start

        check_for_outdated()

        if config.version != latest_tag_name:
            logger.error(locale.not_latest)

            logger.info(locale.update_downloading)
            download_update(latest_tag['zipball_url'])


def check_for_outdated():
    logger.info(locale.check_for_outdated)
    required_packages = [pkg.rstrip('\n').lower() for pkg in open('requirements.txt').readlines()]
    outdated_packages = [pkg[0].lower() for pkg in get_pip_info(True)]

    return [package for package in required_packages if package in outdated_packages]
