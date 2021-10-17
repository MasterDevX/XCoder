import sys
import time

from system import clear
from system.lib.config import config
from system.lib.console import Console
from system.lib.features.directories import clear_directories
from system.lib.features.initialization import initialize
from system.lib.features.update.check import check_update, check_for_outdated, get_tags
from system.lib.menu import menu, Menu
from system.localization import locale

from loguru import logger

logger.remove()
logger.add(
    './logs/info/{time:YYYY-dd-MM}.log',
    format='[{time:HH:mm:ss}] [{level}]: {message}',
    encoding="utf8",
    level='INFO'
)
logger.add(
    './logs/errors/{time:YYYY-dd-MM}.log',
    format='[{time:HH:mm:ss}] [{level}]: {message}',
    backtrace=True,
    diagnose=True,
    encoding="utf8",
    level='ERROR'
)
logger.add(sys.stdout, format='<lvl>[{level}] {message}</lvl>', level='INFO')


locale.load(config.language)


try:
    import requests
    del requests

    if config.auto_update and time.time() - config.last_update > 60 * 60 * 24 * 7:
        check_update()
        config.last_update = int(time.time())
        config.dump()

    if config.has_update:
        logger.opt(colors=True).info(f'<green>{locale.update_done % ""}</green>')
        if Console.question(locale.done_qu):
            latest_tag = get_tags('vorono4ka', 'xcoder')[0]
            latest_tag_name = latest_tag['name'][1:]

            config.has_update = False
            config.version = latest_tag_name
            config.last_update = int(time.time())
            config.dump()
        else:
            exit()
except ImportError:
    pass


@logger.catch()
def refill_menu():
    menu.categories.clear()

    try:
        import sc_compression
        del sc_compression

        from system.lib.features.csv.compress import compress_csv
        from system.lib.features.csv.decompress import decompress_csv

        try:
            import PIL
            del PIL

            from system.lib.features.sc.assembly_encode import sc1_encode
            from system.lib.features.sc.decode import sc_decode
            from system.lib.features.sc.decode_and_cut import sc1_decode
            from system.lib.features.sc.sc_encode import sc_encode

            sc_category = Menu.Category(0, locale.sc_label)
            sc_category.add(Menu.Item(
                locale.decode_sc,
                locale.decode_sc_description,
                sc_decode
            ))
            sc_category.add(Menu.Item(
                locale.encode_sc,
                locale.encode_sc_description,
                sc_encode
            ))
            sc_category.add(Menu.Item(
                locale.decode_by_parts,
                locale.decode_by_parts_description,
                sc1_decode
            ))
            sc_category.add(Menu.Item(
                locale.encode_by_parts,
                locale.encode_by_parts_description,
                sc1_encode
            ))
            sc_category.add(Menu.Item(
                locale.overwrite_by_parts,
                locale.overwrite_by_parts_description,
                lambda: sc1_encode(True)
            ))
            menu.add_category(sc_category)
        except ImportError:
            logger.warning(locale.install_to_unlock % 'PILLOW')

        csv_category = Menu.Category(1, locale.csv_label)
        csv_category.add(Menu.Item(
            locale.decompress_csv,
            locale.decompress_csv_description,
            decompress_csv
        ))
        csv_category.add(Menu.Item(
            locale.compress_csv,
            locale.compress_csv_description,
            compress_csv
        ))
        menu.add_category(csv_category)
    except ImportError:
        logger.warning(locale.install_to_unlock % 'sc-compression')

    other = Menu.Category(10, locale.other_features_label)
    try:
        import requests
        del requests

        other.add(Menu.Item(
            locale.check_update,
            locale.version % config.version,
            check_update
        ))
    except ImportError:
        logger.warning(locale.install_to_unlock % 'requests')

    other.add(Menu.Item(
        locale.check_for_outdated,
        None,
        check_for_outdated
    ))
    other.add(Menu.Item(
        locale.reinit,
        locale.reinit_description,
        lambda: (initialize(), refill_menu())
    ))
    other.add(Menu.Item(
        locale.change_language,
        locale.change_lang_description % config.language,
        lambda: (config.change_language(locale.change()), refill_menu())
    ))
    other.add(Menu.Item(
        locale.clear_directories,
        locale.clean_dirs_description,
        lambda: clear_directories() if Console.question(locale.clear_qu) else -1
    ))
    other.add(Menu.Item(
        locale.toggle_update_auto_checking,
        locale.enabled if config.auto_update else locale.disabled,
        lambda: (config.toggle_auto_update(), refill_menu())
    ))
    other.add(Menu.Item(locale.exit, None, lambda: (clear(), exit())))
    menu.add_category(other)
