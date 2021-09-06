# Refactored by Vorono4ka
# Finished ~99%

from lib import *

clear()


def select_lang():
    lang = input(
        'Select Language\n'
        'Выберите язык\n\n'
        '1 - English\n'
        '2 - Русский\n\n>>> '
    )
    if lang == '1':
        lang = 'en-EU'
    elif lang == '2':
        lang = 'ru-RU'
    else:
        clear()
        select_lang()

    config.lang = lang
    config.dump()


def init(first_init=False):
    if first_init:
        clear()

    Console.info(locale.detected_os % platform.system())
    Console.info(locale.installing)

    required_packages = [pkg.rstrip('\n').lower() for pkg in open('requirements.txt').readlines()]
    installed_packages = [pkg[0].lower() for pkg in get_pip_info()]
    for package in required_packages:
        if package in installed_packages:
            continue

        if run(f'pip3 install {package}') == 0:
            Console.info(locale.installed % package)
        else:
            Console.info(locale.not_installed % package)
    Console.info(locale.crt_workspace)
    [[make_dirs(f'SC/{i}-{k}') for k in ['Compressed', 'Decompressed', 'Sprites']] for i in ['In', 'Out']]
    [[make_dirs(f'CSV/{i}-{k}') for k in ['Compressed', 'Decompressed']] for i in ['In', 'Out']]
    Console.info(locale.verifying)

    config.initialized = True
    config.version = get_tags('vorono4ka', 'xcoder')[0]['name'][1:]
    config.dump()

    if first_init:
        input(locale.to_continue)


def clear_dirs():
    for i in ['In', 'Out']:
        for k in ['Compressed', 'Decompressed', 'Sprites']:
            folder = f'SC/{i}-{k}'
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            make_dirs(folder)

    for i in ['In', 'Out']:
        for k in ['Compressed', 'Decompressed']:
            folder = f'CSV/{i}-{k}'
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            make_dirs(folder)


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

    if is_windows:
        import ctypes

        ctypes.windll.kernel32.SetConsoleTitleW(locale.xcoder_header % config.version)
        del ctypes

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
            answer = welcome_text()
            if {
                '1': sc_decode,
                '2': sc_encode,
                '3': sc1_decode,
                '4': sc1_encode,
                '5': lambda: sc1_encode(True),

                '11': decompress_csv,
                '12': compress_csv,

                '101': check_update,
                '102': check_for_outdated,
                '103': init,
                '104': lambda: (select_lang(), locale.load_from(config.lang)),
                '105': lambda: clear_dirs() if Console.question(locale.clear_qu) else -1,
                '106': toggle_auto_update,
                '107': lambda: (clear(), exit())
            }.get(answer, lambda: -1)() != -1:
                if errors > 0:
                    Console.error(locale.done_err % errors)
                else:
                    Console.done_text(locale.done)

                pause()

        except KeyboardInterrupt:
            if Console.question(locale.want_exit):
                clear()
                break
