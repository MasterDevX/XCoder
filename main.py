# Refactored by Vorono4ka
# Finished ~99%

from lib import *

clear()


if __name__ == '__main__':
    logger = Logger('en-EU')

    if not config.initialized:
        select_lang()

    logger = Logger(config.lang)
    locale = Locale()
    locale.load_from(config.lang)

    if not config.initialized:
        init(True)
        exit()

    menu = create_menu()

    if config.auto_update and time.time() - config.last_update > 60 * 60 * 24 * 7:
        check_update()
        config.last_update = int(time.time())
        config.dump()

    if config.has_update:
        Console.done_text(locale.update_done % '')
        if Console.question(locale.done[:-1] + '?'):
            latest_tag = get_tags('vorono4ka', 'xcoder')[0]
            latest_tag_name = latest_tag['name'][1:]

            config.has_update = False
            config.version = latest_tag_name
            config.last_update = int(time.time())
            config.dump()
        else:
            exit()

    while 1:
        try:
            errors = 0

            clear()
            handler = menu.choice()
            if handler is not None:
                handler()
                if errors > 0:
                    Console.error(locale.done_err % errors)
                else:
                    Console.done_text(locale.done)

                pause()
        except KeyboardInterrupt:
            if Console.question(locale.want_exit):
                clear()
                break
