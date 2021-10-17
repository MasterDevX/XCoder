import os
import shutil

from loguru import logger

from system.lib.features.cut_sprites import cut_sprites
from system.lib.swf import SupercellSWF
from system.localization import locale


def sc1_decode():
    folder = './SC/In-Compressed'
    folder_export = './SC/Out-Sprites'
    files = os.listdir(folder)

    for file in files:
        if not file.endswith('_tex.sc'):
            xcod_file = None
            try:
                base_name = os.path.basename(file).rsplit('.', 1)[0]

                logger.info(locale.dec_sc)

                swf = SupercellSWF()
                has_texture, use_lzham = swf.load_internal(f'{folder}/{file}', False)
                if not has_texture:
                    file = base_name + '_tex.sc'
                    if file not in files:
                        logger.error(locale.not_found % file)
                        continue
                    _, use_lzham = swf.load_internal(f'{folder}/{file}', True)

                current_sub_path = file[::-1].split('.', 1)[1][::-1]
                if os.path.isdir(f'{folder_export}/{current_sub_path}'):
                    shutil.rmtree(f'{folder_export}/{current_sub_path}')
                os.mkdir(f'{folder_export}/{current_sub_path}')
                os.makedirs(f"{folder_export}/{current_sub_path}/textures", exist_ok=True)
                base_name = os.path.basename(file).rsplit('.', 1)[0]

                with open(f'{folder_export}/{current_sub_path}/{base_name}.xcod', 'wb') as xcod_file:
                    xcod_file.write(b'XCOD' + bool.to_bytes(use_lzham, 1, 'big') +
                                    int.to_bytes(len(swf.textures), 1, 'big'))

                    for img_index in range(len(swf.textures)):
                        filename = base_name + '_' * img_index
                        swf.textures[img_index].image.save(
                            f'{folder_export}/{current_sub_path}/textures/{filename}.png'
                        )

                    logger.info(locale.dec_sc)

                    cut_sprites(
                        swf,
                        f'{folder_export}/{current_sub_path}'
                    )
                    xcod_file.write(swf.xcod_writer.getvalue())
            except Exception as exception:
                if xcod_file is not None:
                    xcod_file.close()

                logger.exception(locale.error % (
                    exception.__class__.__module__,
                    exception.__class__.__name__,
                    exception
                ))

            print()
