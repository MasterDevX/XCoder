# Refactored by Vorono4ka
# Finished ~99%

import time

try:
    from loguru import logger
except ImportError:
    raise RuntimeError('Please, install loguru using pip')

from system import clear
from system.lib import config, locale, refill_menu, menu
from system.lib.features.initialization import initialize


def main():
    if not config.initialized:
        config.change_language(locale.change())

    if not config.initialized:
        initialize(True)
        exit()

    refill_menu()

    while True:
        handler = menu.choice()
        if handler is not None:
            start_time = time.time()
            with logger.catch():
                handler()
            logger.opt(colors=True).info(f'<green>{locale.done % (time.time() - start_time)}</green>')
            input(locale.to_continue)
        clear()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Exit.')
        pass
