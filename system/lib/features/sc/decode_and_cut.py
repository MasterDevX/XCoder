import os
import shutil

from loguru import logger

from system.lib.features.cut_sprites import cut_sprites
from system.lib.swf import SupercellSWF
from system.localization import locale


def sc1_decode():
    input_folder = './SC/In-Compressed'
    output_folder = './SC/Out-Sprites'
    files = os.listdir(input_folder)

    for file in files:
        if file.endswith('_tex.sc'):
            continue

        xcod_file = None
        try:
            base_name = os.path.basename(file).rsplit('.', 1)[0]

            logger.info(locale.dec_sc)

            swf = SupercellSWF()
            texture_loaded, use_lzham = swf.load(f'{input_folder}/{file}')
            if not texture_loaded:
                logger.error(locale.not_found % (base_name + '_tex.sc'))
                continue

            base_name = os.path.basename(swf.filename).rsplit('.', 1)[0]
            if os.path.isdir(f'{output_folder}/{base_name}'):
                shutil.rmtree(f'{output_folder}/{base_name}')
            os.mkdir(f'{output_folder}/{base_name}')
            os.makedirs(f"{output_folder}/{base_name}/textures", exist_ok=True)

            with open(f'{output_folder}/{base_name}/{base_name}.xcod', 'wb') as xcod_file:
                xcod_file.write(b'XCOD' + bool.to_bytes(use_lzham, 1, 'big') +
                                int.to_bytes(len(swf.textures), 1, 'big'))

                for img_index in range(len(swf.textures)):
                    filename = base_name + '_' * img_index
                    swf.textures[img_index].image.save(
                        f'{output_folder}/{base_name}/textures/{filename}.png'
                    )

                logger.info(locale.dec_sc)

                cut_sprites(
                    swf,
                    f'{output_folder}/{base_name}'
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
