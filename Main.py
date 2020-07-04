from system.Lib import *

Clear()

cfg_path = './system/config.json'

def select_lang():
    global string
    lang = input(
            'Select Language\n'
            'Выберите язык\n\n'
            '1 - English\n'
            '2 - Русский\n\n>>> ')
    if lang == '1':
        lang = 'en'
    elif lang == '2':
        lang = 'ru'
    else:
        Clear()
        select_lang()

    config.update({'lang': lang})
    json.dump(config, open(cfg_path, 'w'))
    from system.strings import string
    string = string[config['lang']]


def init(ret=True):
    if ret:
        Clear()
    info(string.detected_os % platform.system())
    info(string.installing)
    [os.system(f'pip3 install {i}{nul}') for i in ['colorama', 'pillow', 'lzma', 'pylzham']]
    info(string.crt_workspace)
    [[os.system(f'mkdir {i}-{k}-SC{nul}') for k in ['Compressed', 'Decompressed', 'Sprites']] for i in ['In', 'Out']]
    info(string.verifying)
    for i in ['colorama', 'PIL', 'lzma', 'lzham']:
        try:
            [exec(f"{k} {i}") for k in ['import', 'del']]
            info(string.installed % i)
        except:
            info(string.not_installed % i)

    config.update({'inited': True})
    json.dump(config, open(cfg_path, 'w'))
    if ret:
        input(string.to_continue)

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

            CurrentSubPath = file[::-1].split('.', 1)[1][::-1] + '/'
            if os.path.isdir(f"{folder_export}{CurrentSubPath}"):
                shutil.rmtree(f"{folder_export}{CurrentSubPath}")
            os.mkdir(f"{folder_export}{CurrentSubPath}")
            try:
                decompileSC(f"{folder}{file}", CurrentSubPath, folder = folder, folder_export = folder_export)
            except Exception as e:
                errors += 1
                err_text(string.err % (e.__class__.__module__, e.__class__.__name__, e))
                write_log(traceback.format_exc())

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
            err_text(string.err % (e.__class__.__module__, e.__class__.__name__, e))
            write_log(traceback.format_exc())

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
                err_text(string.not_found % scfile)
            else:
                CurrentSubPath = file[::-1].split('.', 1)[1][::-1] + '/'
                if os.path.isdir(f"{folder_export}{CurrentSubPath}"):
                    shutil.rmtree(f"{folder_export}{CurrentSubPath}")
                os.mkdir(f"{folder_export}{CurrentSubPath}")
                try:
                    info(string.dec_sctex)
                    sheetimage, xcod = decompileSC(f"{folder}{file}", CurrentSubPath, to_memory=True, folder_export=folder_export)
                    info(string.dec_sc)
                    spriteglobals, spritedata, sheetdata = decodeSC(f"{folder}{scfile}", sheetimage)
                    xc = open(f"{folder_export}{CurrentSubPath}" + file[:-3] + '.xcod', 'wb')
                    xc.write(xcod)
                    cut_sprites(spriteglobals, spritedata, sheetdata, sheetimage, xc, f"{folder_export}{CurrentSubPath}")
                except Exception as e:
                    errors += 1
                    err_text(string.err % (e.__class__.__module__, e.__class__.__name__, e))
                    write_log(traceback.format_exc())

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
            err_text(string.not_found % xcod)
        else:
            
            try:
                info(string.dec_sctex)
                sheetimage, sheetimage_data = place_sprites(f"{folder}{file}/{xcod}", f"{folder}{file}")
                info(string.dec_sc)
                compileSC(f'{folder}{file}/', sheetimage, sheetimage_data, folder_export)
            except Exception as e:
                errors += 1
                err_text(f"Error while decoding! ({e.__class__.__module__}.{e.__class__.__name__}: {e})")
                write_log(traceback.format_exc())
            print()


v = '2.0.0-prerelease'

if __name__ == '__main__':
    if os.path.isfile(cfg_path):
        try:
            config = json.load(open(cfg_path))
        except:
            config = {'inited': False, 'version': v}
    else:
        config = {'inited': False, 'version': v}

    if not config.get('lang'):
        select_lang()

    if not config['inited']:
        init()
        try: os.system('python%s "%s"' % ('' if isWin else '3', __file__))
        except: pass
        exit()

    from system.strings import string, console
    Title(string['en'].xcoder % config['version'])

    while 1:
        try:
            string = string[config['lang']]
            break
        except:
            select_lang()

    locale(config['lang'])
    

    while 1:
        try:
            errors = 0
            [os.remove(i) if os.path.isfile(
                i) else None for i in ('temp.sc', '_temp.sc')]
            
            Clear()
            answer = console(config)
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
                print(string.not_implemented)
            elif answer == '102':
                init(ret=False)
            elif answer == '103':
                select_lang()
                locale(config['lang'])
            elif answer == '104':
                if not question(string.clear_qu):
                    continue
                clear_dirs()
                    
            elif answer == '105':
                Clear()
                break

            else:
                continue

            if errors > 0:
                err_text(string.done_err % errors)
            else:
                done_text(string.done)

            input(string.to_continue)
        
        except KeyboardInterrupt:
            if question(string.want_exit):
                Clear()
                break
