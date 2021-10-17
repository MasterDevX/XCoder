import os
import platform

from loguru import logger

is_windows = platform.system() == 'Windows'
null_output = f'{"nul" if is_windows else "/dev/null"} 2>&1'


def run(command: str, output_path: str = null_output):
    return os.system(f'{command} > {output_path}')


if is_windows:
    with logger.catch():
        try:
            import colorama
            colorama.init()
        except Exception as e:
            logger.exception(e)

    def clear():
        os.system('cls')
else:
    def clear():
        os.system('clear')
