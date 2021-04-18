# Refactored by Vorono4ka
# Finished ~85%

from lib import *

clear()

cfg_path = './system/config.json'


def get_pip_info(outdated: bool = False) -> list:
    output = get_run_output(f'pip --disable-pip-version-check list {"-o" if outdated else ""}')
    output = output.splitlines()
    output = output[2:]
    packages = [package.split() for package in output]

    return packages


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

        if run(f'pip3 install {package}'):
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
    # config.update({'autoupdate': Console.question(locale.aupd_qu), 'use_margins': Console.question(locale.marg_qu)})
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


def decompress_csv():
    global errors
    folder = './CSV/In-Compressed'
    folder_export = './CSV/Out-Decompressed'

    for file in os.listdir(folder):
        if file.endswith('.csv'):
            try:
                with open(f'{folder}/{file}', 'rb') as f:
                    file_data = f.read()
                    f.close()

                with open(f'{folder_export}/{file}', 'wb') as f:
                    f.write(decompress(file_data))
                    f.close()
            except Exception as exception:
                errors += 1
                Console.error(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))
                logger.write(traceback.format_exc())

            print()


def compress_csv():
    from sc_compression.signatures import Signatures

    global errors
    folder = './CSV/In-Decompressed'
    folder_export = './CSV/Out-Compressed'

    for file in os.listdir(folder):
        if file.endswith('.csv'):
            try:
                with open(f'{folder}/{file}', 'rb') as f:
                    file_data = f.read()
                    f.close()

                with open(f'{folder_export}/{file}', 'wb') as f:
                    f.write(compress(file_data, Signatures.LZMA))
                    f.close()
            except Exception as exception:
                errors += 1
                Console.error(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))
                logger.write(traceback.format_exc())

            print()


def sc_decode():
    global errors
    folder = './SC/In-Compressed'
    folder_export = './SC/Out-Decompressed'

    for file in os.listdir(folder):
        if file.endswith('_tex.sc'):

            current_sub_path = file[::-1].split('.', 1)[1][::-1]
            if os.path.isdir(f'{folder_export}/{current_sub_path}'):
                shutil.rmtree(f'{folder_export}/{current_sub_path}')
            os.mkdir(f'{folder_export}/{current_sub_path}')
            try:
                swf = SupercellSWF()
                use_lzham = swf.load_internal(f'{folder}/{file}', True)

                data = struct.pack('4s?B', b'XCOD', use_lzham, len(swf.textures)) + swf.xcod_writer.getvalue()

                base_name = os.path.basename(file).rsplit('.', 1)[0]
                with open(f'{folder_export}/{current_sub_path}/{base_name.rstrip("_")}.xcod', 'wb') as xc:
                    xc.write(data)
                for img_index in range(len(swf.textures)):
                    filename = base_name + '_' * img_index
                    swf.textures[img_index].image.save(f'{folder_export}/{current_sub_path}/{filename}.png')
            except Exception as exception:
                errors += 1
                Console.error(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))
                logger.write(traceback.format_exc())

            print()


def sc_encode():
    global errors
    folder = './SC/In-Decompressed'
    folder_export = './SC/Out-Compressed'

    for file in os.listdir(folder):
        try:
            compile_sc(f'{folder}/{file}/', folder_export=folder_export)
        except Exception as exception:
            errors += 1
            Console.error(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))
            logger.write(traceback.format_exc())

        print()


def sc1_decode():
    global errors
    folder = './SC/In-Compressed'
    folder_export = './SC/Out-Sprites'
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

                xc = open(f'{folder_export}/{current_sub_path}/{file[:-3]}.xcod', 'wb')
                try:
                    Console.info(locale.dec_sc_tex)

                    swf = SupercellSWF()
                    swf.load_internal(f'{folder}/{sc_file}', False)
                    use_lzham = swf.load_internal(f'{folder}/{file}', True)
                    data = struct.pack('4s?B', b'XCOD', use_lzham, len(swf.textures)) + swf.xcod_writer.getvalue()

                    os.makedirs(f"{folder_export}/{current_sub_path}/textures", exist_ok=True)
                    base_name = os.path.basename(file).rsplit('.', 1)[0]
                    for img_index in range(len(swf.textures)):
                        filename = base_name + '_' * img_index
                        swf.textures[img_index].image.save(f'{folder_export}/{current_sub_path}/textures/{filename}.png')

                    xc.write(data)

                    Console.info(locale.dec_sc)

                    cut_sprites(
                        swf.movie_clips,
                        swf.textures,
                        xc,
                        f'{folder_export}/{current_sub_path}'
                    )
                except Exception as exception:
                    try:
                        xc.close()
                    except Exception:
                        pass

                    errors += 1
                    Console.error(locale.error % (
                        exception.__class__.__module__,
                        exception.__class__.__name__,
                        exception
                    ))
                    logger.write(traceback.format_exc())

            print()


def sc1_encode(overwrite: bool = False):
    global errors
    folder = './SC/In-Sprites/'
    folder_export = './SC/Out-Compressed/'
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
            except Exception as exception:
                errors += 1
                Console.error(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))
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
            run('python%s "%s"' % ('' if is_windows else '3', __file__))
        except Exception as e:
            logger.write(e)
        exit()

    if is_windows:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW(locale.xcoder % config['version'])
        del ctypes

    if (not ('last_update' in config)) or time.time() - config['last_update'] > 60*60*24*7:
        check_update()

    if not config['updated']:
        Console.done_text(locale.update_done % '')
        if Console.question(locale.done[:-1] + '?'):
            latest_tag = get_tags('vorono4ka', 'xcoder')[0]
            latest_tag_name = latest_tag['name'][1:]

            required_packages = [pkg.rstrip('\n').lower() for pkg in open('requirements.txt').readlines()]
            outdated_packages = [pkg[0].lower() for pkg in get_pip_info(True)]
            for package in required_packages:
                if package in outdated_packages:
                    run(f'pip3 install --upgrade {package}')

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
