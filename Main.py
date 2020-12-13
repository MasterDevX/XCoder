# Refactored by Vorono4ka
# Finished ~85%


from system.Lib import *

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
    os.system(f'pip3 install -r requirements.txt{nul}')
    Console.info(locale.crt_workspace)
    [[os.system(f'mkdir {i}-{k}-SC{nul}') for k in ['Compressed', 'Decompressed', 'Sprites']] for i in ['In', 'Out']]
    Console.info(locale.verifying)
    for i in ['colorama', 'PIL', 'sc_compression', 'requests']:
        try:
            [exec(f'{k} {i}') for k in ['import', 'del']]
            Console.info(locale.installed % i)
        except Exception as e:
            logger.write(e)
            Console.info(locale.not_installed % i)

    config.update({'inited': True, 'version': get_tags('vorono4ka', 'xcoder')[0]['name'][1:]})
    json.dump(config, open(cfg_path, 'w'))

    params()

    if ret:
        input(locale.to_continue)


def params():
    # config.update({'autoupdate': Console.question(locale.aupd_qu), 'use_margins': Console.question(locale.marg_qu)})
    json.dump(config, open(cfg_path, 'w'))


def clear_dirs():
    files = os.listdir('./')
    for i in ['In', 'Out']:
        for k in ['Compressed', 'Decompressed', 'Sprites']:
            folder = f'{i}-{k}-SC'
            if folder in files:
                if os.path.isdir(folder):
                    shutil.rmtree(folder)
                os.system(f'mkdir {folder}{nul}')


def sc_decode():
    global errors
    folder = './In-Compressed-SC'
    folder_export = './Out-Decompressed-SC'

    for file in os.listdir(folder):
        if file.endswith('_tex.sc'):

            current_sub_path = file[::-1].split('.', 1)[1][::-1]
            if os.path.isdir(f'{folder_export}/{current_sub_path}'):
                shutil.rmtree(f'{folder_export}/{current_sub_path}')
            os.mkdir(f'{folder_export}/{current_sub_path}')
            try:
                decompile_sc(file, current_sub_path, folder=folder, folder_export=folder_export)
            except Exception as e:
                errors += 1
                Console.error(locale.error % (e.__class__.__module__, e.__class__.__name__, e))
                logger.write(traceback.format_exc())

            print()


def sc_encode():
    global errors
    folder = './In-Decompressed-SC'
    folder_export = './Out-Compressed-SC'

    for i in os.listdir(folder + '/'):
        try:
            compile_sc(f'{folder}/{i}/', folder_export=folder_export)
        except Exception as e:
            errors += 1
            Console.error(locale.error % (e.__class__.__module__, e.__class__.__name__, e))
            logger.write(traceback.format_exc())

        print()


def sc1_decode():
    global errors
    folder = './In-Compressed-SC'
    folder_export = './Out-Sprites-SC'
    files = os.listdir(folder)

    for file in files:
        if file.endswith('_tex.sc'):

            sc_file = file[:-7] + '.sc'
            if sc_file not in files:
                Console.error(locale.not_found % sc_file)
            else:
                current_sub_path = file[::-1].split('.', 1)[1][::-1]
                if os.path.isdir(f'{folder_export}/{current_sub_path}'):
                    shutil.rmtree(f'{folder_export}/{current_sub_path}')
                os.mkdir(f'{folder_export}/{current_sub_path}')
                try:
                    Console.info(locale.dec_sc_tex)
                    sheet_image, xcod = decompile_sc(
                        file,
                        current_sub_path,
                        folder,
                        folder_export,
                        True
                    )
                    Console.info(locale.dec_sc)
                    sprite_globals, sprite_data, sheet_data = decode_sc(sc_file, folder)
                    xc = open(f'{folder_export}/{current_sub_path}/{file[:-3]}.xcod', 'wb')
                    xc.write(xcod)
                    cut_sprites(
                        sprite_data,
                        sheet_data,
                        sheet_image,
                        xc,
                        f'{folder_export}/{current_sub_path}'
                    )
                except Exception as e:
                    errors += 1
                    Console.error(locale.error % (e.__class__.__module__, e.__class__.__name__, e))
                    logger.write(traceback.format_exc())

            print()


def sc1_encode(overwrite: bool = False):
    global errors
    folder = './In-Sprites-SC/'
    folder_export = './Out-Compressed-SC/'
    files = os.listdir(folder)

    for file in files:
        xcod = file + '.xcod'
        if xcod not in os.listdir(f'{folder}{file}/'):
            Console.error(locale.not_found % xcod)
        else:
            try:
                Console.info(locale.dec_sc_tex)
                sheet_image, sheet_image_data = place_sprites(f'{folder}{file}/{xcod}', f'{folder}{file}', overwrite)
                Console.info(locale.dec_sc)
                compile_sc(f'{folder}{file}/', sheet_image, sheet_image_data, folder_export)
            except Exception as e:
                errors += 1
                Console.error(f'Error while decoding! ({e.__class__.__module__}.{e.__class__.__name__}: {e})')
                logger.write(traceback.format_exc())
            print()


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
            os.system('python%s "%s"' % ('' if is_windows else '3', __file__))
        except Exception as e:
            logger.write(e)
        exit()

    if not config['updated']:
        Console.done_text(locale.update_done % '')
        if Console.question(locale.done[:-1] + '?'):
            latest_tag = get_tags('vorono4ka', 'xcoder')[0]
            latest_tag_name = latest_tag['name'][1:]

            config.update({'updated': True, 'version': latest_tag_name})
            json.dump(config, open(config_path, 'w'))

            try:
                os.system('python%s "%s"' % ('' if is_windows else '3', __file__))
            except Exception as e:
                logger.write(e)
        exit()

    from system.Lib import welcome_text

    set_title(locale.xcoder % config['version'])

    while 1:
        try:
            errors = 0
            [os.remove(i) for i in ('temp.sc', '_temp.sc') if os.path.isfile(i)]

            clear()
            answer = welcome_text()
            if {
                '1': sc_decode,
                '2': sc_encode,
                '3': sc1_decode,
                '4': sc1_encode,
                '5': lambda: sc1_encode(True),
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
