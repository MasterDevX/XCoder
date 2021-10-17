# Refactored by Vorono4ka
# Finished ~99%
import time

try:
    from loguru import logger
except ImportError:
    print('Please, install loguru using pip')
    exit()

from system import clear
from system.lib import config, Console, locale, refill_menu, menu
from system.lib.features.initialization import initialize


if __name__ == '__main__':
    if not config.initialized:
        config.change_language(locale.change())

    if not config.initialized:
        initialize(True)
        exit()

    refill_menu()

    while True:
        try:
            handler = menu.choice()
            if handler is not None:
                start_time = time.time()
                with logger.catch():
                    handler()
                logger.opt(colors=True).info(f'<green>{locale.done % (time.time() - start_time)}</green>')
                input(locale.to_continue)
            clear()
        except KeyboardInterrupt:
            if Console.question(locale.want_exit):
                clear()
                break
