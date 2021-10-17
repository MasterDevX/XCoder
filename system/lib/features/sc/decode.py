import os
import shutil
import struct

from loguru import logger

from system.lib.swf import SupercellSWF
from system.localization import locale


def sc_decode():
    folder = './SC/In-Compressed'
    folder_export = './SC/Out-Decompressed'

    files = os.listdir(folder)
    for file in files:
        if file.endswith('.sc'):
            swf = SupercellSWF()
            base_name = os.path.basename(file).rsplit('.', 1)[0]
            try:
                has_texture, use_lzham = swf.load_internal(f'{folder}/{file}', file.endswith('_tex.sc'))

                if not has_texture:
                    base_name += '_tex'
                    file = base_name + '.sc'
                    if file in files:
                        files.remove(file)

                        has_texture, use_lzham = swf.load_internal(f'{folder}/{file}', True)
                    else:
                        continue

                current_sub_path = file[::-1].split('.', 1)[1][::-1]
                if os.path.isdir(f'{folder_export}/{current_sub_path}'):
                    shutil.rmtree(f'{folder_export}/{current_sub_path}')
                os.mkdir(f'{folder_export}/{current_sub_path}')

                data = struct.pack('4s?B', b'XCOD', use_lzham, len(swf.textures)) + swf.xcod_writer.getvalue()

                with open(f'{folder_export}/{current_sub_path}/{base_name.rstrip("_")}.xcod', 'wb') as xc:
                    xc.write(data)
                for img_index in range(len(swf.textures)):
                    filename = base_name + '_' * img_index
                    swf.textures[img_index].image.save(f'{folder_export}/{current_sub_path}/{filename}.png')
            except Exception as exception:
                logger.exception(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))

            print()
