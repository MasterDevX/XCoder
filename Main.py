# Refactored by Vorono4ka
# Finished ~45%


from system.Lib import *

Clear()

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
        Clear()
        select_lang()

    config.update({'lang': lang})
    json.dump(config, open(cfg_path, 'w'))


def init(ret=True):
    if ret:
        Clear()
    Console.info(locale.detected_os % platform.system())
    Console.info(locale.installing)
    [os.system(f'pip3 install {i}{nul}') for i in ['colorama', 'pillow', 'lzma', 'pylzham']]
    Console.info(locale.crt_workspace)
    [[os.system(f'mkdir {i}-{k}-SC{nul}') for k in ['Compressed', 'Decompressed', 'Sprites']] for i in ['In', 'Out']]
    Console.info(locale.verifying)
    for i in ['colorama', 'PIL', 'lzma', 'lzham']:
        try:
            [exec(f"{k} {i}") for k in ['import', 'del']]
            Console.info(locale.installed % i)
        except Exception as e:
            logger.write(e)
            Console.info(locale.not_installed % i)

    config.update({'inited': True})
    json.dump(config, open(cfg_path, 'w'))
    if ret:
        input(locale.to_continue)


def clear_dirs():
    files = os.listdir('./')
    for i in ['In', 'Out']:
        for k in ['Compressed', 'Decompressed', 'Sprites']:
            folder = f'{i}-{k}-SC'
            if folder in files:
                shutil.rmtree(folder)
                os.system(f'mkdir {folder}{nul}')


def sc_decode():
    global errors
    folder = "./In-Compressed-SC/"
    folder_export = "./Out-Decompressed-SC/"

    for file in os.listdir(folder):
        if file.endswith("_tex.sc"):

            current_sub_path = file[::-1].split('.', 1)[1][::-1] + '/'
            if os.path.isdir(f"{folder_export}{current_sub_path}"):
                shutil.rmtree(f"{folder_export}{current_sub_path}")
            os.mkdir(f"{folder_export}{current_sub_path}")
            try:
                decompileSC(f"{folder}{file}", current_sub_path, folder=folder, folder_export=folder_export)
            except Exception as e:
                errors += 1
                Console.err_text(locale.error % (e.__class__.__module__, e.__class__.__name__, e))
                logger.write(traceback.format_exc())

            print()


def sc_encode():
    global errors
    folder = './In-Decompressed-SC/'
    folder_export = './Out-Compressed-SC/'

    for i in os.listdir(folder):
        try:
            compileSC(f"{folder}{i}/", folder_export=folder_export)
        except Exception as e:
            errors += 1
            Console.err_text(locale.error % (e.__class__.__module__, e.__class__.__name__, e))
            logger.write(traceback.format_exc())

        print()


def sc1_decode():
    global errors
    folder = "./In-Compressed-SC/"
    folder_export = "./Out-Sprites-SC/"
    files = os.listdir(folder)

    for file in files:
        if file.endswith("_tex.sc"):

            scfile = file[:-7] + '.sc'
            if scfile not in files:
                Console.err_text(locale.not_found % scfile)
            else:
                current_sub_path = file[::-1].split('.', 1)[1][::-1] + '/'
                if os.path.isdir(f"{folder_export}{current_sub_path}"):
                    shutil.rmtree(f"{folder_export}{current_sub_path}")
                os.mkdir(f"{folder_export}{current_sub_path}")
                try:
                    Console.info(locale.dec_sc_tex)
                    sheet_image, xcod = decompileSC(f"{folder}{file}",
                                                    current_sub_path,
                                                    to_memory=True,
                                                    folder_export=folder_export)
                    Console.info(locale.dec_sc)
                    sprite_globals, sprite_data, sheet_data = decodeSC(f"{folder}{scfile}", sheet_image)
                    xc = open(f"{folder_export}{current_sub_path}" + file[:-3] + '.xcod', 'wb')
                    xc.write(xcod)
                    cut_sprites(sprite_globals, sprite_data, sheet_data, sheet_image, xc,
                                f"{folder_export}{current_sub_path}")
                except Exception as e:
                    errors += 1
                    Console.err_text(locale.error % (e.__class__.__module__, e.__class__.__name__, e))
                    logger.write(traceback.format_exc())

            print()


def sc1_encode():
    global errors
    folder = "./In-Sprites-SC/"
    folder_export = "./Out-Compressed-SC/"
    files = os.listdir(folder)

    for file in files:
        print(file)

        xcod = file + '.xcod'
        if xcod not in os.listdir(f'{folder}{file}/'):
            Console.err_text(locale.not_found % xcod)
        else:
            try:
                Console.info(locale.dec_sc_tex)
                sheet_image, sheet_image_data = place_sprites(f"{folder}{file}/{xcod}", f"{folder}{file}")
                Console.info(locale.dec_sc)
                compileSC(f'{folder}{file}/', sheet_image, sheet_image_data, folder_export)
            except Exception as e:
                errors += 1
                Console.err_text(f"Error while decoding! ({e.__class__.__module__}.{e.__class__.__name__}: {e})")
                logger.write(traceback.format_exc())
            print()


if __name__ == '__main__':
    logger = Logger('en-EU')
    if os.path.isfile(cfg_path):
        try:
            config = json.load(open(cfg_path))
        except Exception as e:
            logger.write(e)
            config = {'inited': False, 'version': version}
    else:
        config = {'inited': False, 'version': version}

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

    from system.Lib import welcome_text

    Title(locale.xcoder % config['version'])

    while 1:
        try:
            errors = 0
            [os.remove(i) if os.path.isfile(i) else None for i in ('temp.sc', '_temp.sc')]

            Clear()
            answer = welcome_text()
            print()
            if answer == '1':
                sc_decode()
            elif answer == '2':
                sc_encode()
            elif answer == '3':
                sc1_decode()
            elif answer == '4':
                sc1_encode()
            elif answer == '101':
                print(locale.not_implemented)
            elif answer == '102':
                init(ret=False)
            elif answer == '103':
                select_lang()
                locale.load_from(config['lang'])
            elif answer == '104':
                if not Console.question(locale.clear_qu):
                    continue
                clear_dirs()
            elif answer == '105':
                Clear()
                break
            else:
                continue

            if errors > 0:
                Console.err_text(locale.done_err % errors)
            else:
                Console.done_text(locale.done)

            input(locale.to_continue)

        except KeyboardInterrupt:
            if Console.question(locale.want_exit):
                Clear()
                break
