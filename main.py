# Refactored by Vorono4ka
# Finished ~85%

from lib import *

clear()

cfg_path = './system/config.json'


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

    config.update({'lang': lang})
    json.dump(config, open(cfg_path, 'w'))


def init(ret=True):
    if ret:
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

    config.update({'inited': True, 'version': get_tags('vorono4ka', 'xcoder')[0]['name'][1:]})
    json.dump(config, open(cfg_path, 'w'))

    params()

    if ret:
        input(locale.to_continue)


def params():
    # config.update({'autoupdate': Console.question(locale.aupd_qu)})
    json.dump(config, open(cfg_path, 'w'))


def clear_dirs():
    files = os.listdir('./')
    for i in ['In', 'Out']:
        for k in ['Compressed', 'Decompressed', 'Sprites']:
            folder = f'SC/{i}-{k}'
            if folder in files:
                if os.path.isdir(folder):
                    shutil.rmtree(folder)
                make_dirs(folder)

    for i in ['In', 'Out']:
        for k in ['Compressed', 'Decompressed']:
            folder = f'CSV/{i}-{k}'
            if folder in files:
                if os.path.isdir(folder):
                    shutil.rmtree(folder)
                make_dirs(folder)


if __name__ == '__main__':
    logger = Logger('en-EU')
    if os.path.isfile(cfg_path):
        try:
            config = json.load(open(cfg_path))
        except Exception as e:
            logger.write(e)
            config = {'inited': False, 'version': None}
    else:
        config = {'inited': False, 'version': None}

    if not config.get('lang'):
        select_lang()
    logger = Logger(config['lang'])
    locale = Locale()
    locale.load_from(config['lang'])

    if not config['inited']:
        init()
        try:
            run('python%s "%s"' % ('' if is_windows else '3', __file__))
        except Exception as e:
            logger.write(e)
        exit()

    if is_windows:
        import ctypes

        ctypes.windll.kernel32.SetConsoleTitleW(locale.xcoder % config['version'])
        del ctypes

    if (not ('last_update' in config)) or time.time() - config['last_update'] > 60 * 60 * 24 * 7:
        check_update()

    if not config['updated']:
        Console.done_text(locale.update_done % '')
        if Console.question(locale.done[:-1] + '?'):
            latest_tag = get_tags('vorono4ka', 'xcoder')[0]
            latest_tag_name = latest_tag['name'][1:]

            config.update({'updated': True, 'version': latest_tag_name, 'last_update': int(time.time())})
            json.dump(config, open(config_path, 'w'))
        else:
            exit()

    while 1:
        try:
            errors = 0

            clear()
            answer = welcome_text()
            if {
                '-1': lambda: sc1_encode(True),
                '1': sc_decode,
                '2': sc_encode,
                '3': sc1_decode,
                '4': sc1_encode,
                '5': decompress_csv,
                '6': compress_csv,
                '101': check_update,
                '102': lambda: init(ret=False),
                '103': lambda: (select_lang(), locale.load_from(config['lang'])),
                '104': lambda: clear_dirs() if Console.question(locale.clear_qu) else 'null',
                '105': lambda: (clear(), exit())
            }.get(answer, lambda: 'null')() == 'null':
                continue

            if errors > 0:
                Console.error(locale.done_err % errors)
            else:
                Console.done_text(locale.done)

            pause()

        except KeyboardInterrupt:
            if Console.question(locale.want_exit):
                clear()
                break
