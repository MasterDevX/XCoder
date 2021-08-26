from system.bytestream import Writer
from system.lib.config import Config
from system.lib.logger import Logger
from system.localization import Locale

from system.lib.objects.texture import SWFTexture
from system.lib.objects.shape import Shape
from system.lib.objects.movie_clip import MovieClip

logger = Logger('en-EU')

try:
    import os
    import sys
    import time
    import json
    import struct
    import shutil
    import zipfile
    import hashlib
    import requests
    import platform
    import traceback
    import subprocess
    import colorama
    import tempfile

    from PIL import Image, ImageDraw
    from system.lib.images import *

    from sc_compression.signatures import Signatures
    from sc_compression import decompress, compress
except Exception as e:
    logger.write(e)

lzham_path = r'system\lzham'

is_windows = platform.system() == 'Windows'
null_output = f'{"nul" if is_windows else "/dev/null"} 2>&1'

config = Config()
locale = Locale()
locale.load_from(config.lang)


def run(command: str, output_path: str = null_output):
    return os.system(f'{command} > {output_path}')


def get_run_output(command: str):
    temp_filename = tempfile.mktemp('.temp')
    run(command, temp_filename)

    with open(temp_filename) as f:
        file_data = f.read()
        f.close()

    os.remove(temp_filename)

    return file_data


if is_windows:
    try:
        colorama.init()
    except Exception as e:
        logger.write(e)


    def clear():
        os.system('cls')


    def pause():
        print(locale.pause, end='')
        run('pause')
else:
    def clear():
        os.system('clear')


    def pause():
        if run(f'read -s -n 1 -p "{locale.pause}"'):
            input(locale.to_continue)


def make_dirs(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def print_feature_with_description(name: str, description: str = None, console_width: int = -1):
    print(name, end='')
    if description:
        print(' ' * (console_width // 2 - len(name)) + ': ' + description, end='')
    print()


def colored_print(text, color=None):
    if color is None:
        color = colorama.Back.GREEN
    return print(color + colorama.Fore.BLACK + text + ' ' * (10 - len(text)) + colorama.Style.RESET_ALL)


def welcome_text():
    locale.load_from(config.lang)

    console_width = shutil.get_terminal_size().columns
    print(
        (
            colorama.Back.BLACK + colorama.Fore.GREEN +
            locale.xcoder_header % config.version +
            colorama.Style.RESET_ALL
        ).center(console_width + 14)
    )
    print('github.com/Vorono4ka/XCoder'.center(console_width))
    print(console_width * '-')

    colored_print(locale.sc_label)
    print_feature_with_description(' 1   ' + locale.decode_sc, locale.decode_sc_description, console_width)
    print_feature_with_description(' 2   ' + locale.encode_sc, locale.encode_sc_description, console_width)
    print_feature_with_description(' 3   ' + locale.decode_by_parts, locale.decode_by_parts_description, console_width)
    print_feature_with_description(' 4   ' + locale.encode_by_parts, locale.encode_by_parts_description, console_width)
    print_feature_with_description(' 5   ' + locale.overwrite_by_parts, locale.overwrite_by_parts_description, console_width)
    print(console_width * '-')

    colored_print(locale.csv_label)
    print_feature_with_description(' 11   ' + locale.decompress_csv, locale.decompress_csv_description, console_width)
    print_feature_with_description(' 12   ' + locale.compress_csv, locale.compress_csv_description, console_width)
    print(console_width * '-')

    colored_print(locale.other_features_label)
    print_feature_with_description(' 101 ' + locale.check_update, locale.version % config.version, console_width)
    print_feature_with_description(' 102 ' + locale.check_for_outdated)
    print_feature_with_description(' 103 ' + locale.reinit, locale.reinit_description, console_width)
    print_feature_with_description(' 104 ' + locale.change_lang, locale.change_lang_description % config.lang, console_width)
    print_feature_with_description(' 105 ' + locale.clear_dirs, locale.clean_dirs_description, console_width)
    print_feature_with_description(
        ' 106 ' + locale.toggle_update_auto_checking,
        locale.enabled if config.auto_update else locale.disabled,
        console_width
    )
    print_feature_with_description(' 107 ' + locale.exit)
    print(console_width * '-')

    choice = input(locale.choice)
    print(console_width * '-')
    return choice


def get_pip_info(outdated: bool = False) -> list:
    output = get_run_output(f'pip --disable-pip-version-check list {"-o" if outdated else ""}')
    output = output.splitlines()
    output = output[2:]
    packages = [package.split() for package in output]

    return packages


def get_tags(owner: str, repo: str):
    api_url = 'https://api.github.com'
    tags = []

    try:
        tags = requests.get(api_url + '/repos/{owner}/{repo}/tags'.format(owner=owner, repo=repo)).json()
        tags = [
            {
                key: v for key, v in tag.items()
                if key in ['name', 'zipball_url']
            } for tag in tags
        ]
    except Exception:
        pass

    return tags


def toggle_auto_update():
    config.auto_update = not config.auto_update
    config.dump()


def check_update():
    tags = get_tags('vorono4ka', 'xcoder')

    if len(tags) > 0:
        latest_tag = tags[0]
        latest_tag_name = latest_tag['name'][1:]  # clear char 'v' at string start

        check_for_outdated()

        if config.version != latest_tag_name:
            Console.error(locale.not_latest)

            Console.info(locale.update_downloading)
            download_update(latest_tag['zipball_url'])


def check_for_outdated():
    Console.info(locale.check_for_outdated)
    required_packages = [pkg.rstrip('\n').lower() for pkg in open('requirements.txt').readlines()]
    outdated_packages = [pkg[0].lower() for pkg in get_pip_info(True)]
    for package in required_packages:
        if package in outdated_packages:
            run(f'pip3 install --upgrade {package}')


def download_update(zip_url):
    if not os.path.exists('updates'):
        os.mkdir('updates')

    with open('updates/update.zip', 'wb') as f:
        f.write(requests.get(zip_url).content)
        f.close()

    with zipfile.ZipFile('updates/update.zip') as zf:
        zf.extractall('updates/')
        zf.close()

        Console.done_text(locale.update_done % f'"{zf.namelist()[0]}"')
        config.has_update = True
        config.last_update = int(time.time())
        config.dump()
        input(locale.to_continue)
        exit()


def decompress_csv():
    folder = './CSV/In-Compressed'
    folder_export = './CSV/Out-Decompressed'

    for file in os.listdir(folder):
        if file.endswith('.csv'):
            try:
                with open(f'{folder}/{file}', 'rb') as f:
                    file_data = f.read()
                    f.close()

                with open(f'{folder_export}/{file}', 'wb') as f:
                    f.write(decompress(file_data)[0])
                    f.close()
            except Exception as exception:
                Console.error(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))
                logger.write(traceback.format_exc())

            print()


def compress_csv():
    from sc_compression.signatures import Signatures

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
                Console.error(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))
                logger.write(traceback.format_exc())

            print()


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
                Console.error(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))
                logger.write(traceback.format_exc())

            print()


def sc_encode():
    folder = './SC/In-Decompressed'
    folder_export = './SC/Out-Compressed'

    for file in os.listdir(folder):
        try:
            compile_sc(f'{folder}/{file}/', folder_export=folder_export)
        except Exception as exception:
            Console.error(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))
            logger.write(traceback.format_exc())

        print()


def sc1_decode():
    folder = './SC/In-Compressed'
    folder_export = './SC/Out-Sprites'
    files = os.listdir(folder)

    for file in files:
        if not file.endswith('_tex.sc'):
            xcod_file = None
            try:
                base_name = os.path.basename(file).rsplit('.', 1)[0]

                Console.info(locale.dec_sc)

                swf = SupercellSWF()
                has_texture, use_lzham = swf.load_internal(f'{folder}/{file}', False)
                if not has_texture:
                    file = base_name + '_tex.sc'
                    if file not in files:
                        Console.error(locale.not_found % file)
                        continue
                    _, use_lzham = swf.load_internal(f'{folder}/{file}', True)

                current_sub_path = file[::-1].split('.', 1)[1][::-1]
                if os.path.isdir(f'{folder_export}/{current_sub_path}'):
                    shutil.rmtree(f'{folder_export}/{current_sub_path}')
                os.mkdir(f'{folder_export}/{current_sub_path}')
                os.makedirs(f"{folder_export}/{current_sub_path}/textures", exist_ok=True)
                base_name = os.path.basename(file).rsplit('.', 1)[0]

                with open(f'{folder_export}/{current_sub_path}/{base_name}.xcod', 'wb') as xcod_file:
                    xcod_file.write(b'XCOD' + bool.to_bytes(use_lzham, 1, 'big') + int.to_bytes(len(swf.textures), 1, 'big'))

                    for img_index in range(len(swf.textures)):
                        filename = base_name + '_' * img_index
                        swf.textures[img_index].image.save(f'{folder_export}/{current_sub_path}/textures/{filename}.png')


                    Console.info(locale.dec_sc)

                    cut_sprites(
                        swf,
                        f'{folder_export}/{current_sub_path}'
                    )
                    xcod_file.write(swf.xcod_writer.getvalue())
            except Exception as exception:
                if xcod_file is not None:
                    xcod_file.close()

                Console.error(locale.error % (
                    exception.__class__.__module__,
                    exception.__class__.__name__,
                    exception
                ))
                logger.write(traceback.format_exc())

            print()


def sc1_encode(overwrite: bool = False):
    folder = './SC/In-Sprites/'
    folder_export = './SC/Out-Compressed/'
    files = os.listdir(folder)

    for file in files:
        xcod = file + '.xcod'
        if xcod not in os.listdir(f'{folder}{file}/'):
            Console.error(locale.not_found % xcod)
        else:
            try:
                Console.info(locale.dec_sc)
                sheet_image, sheet_image_data = place_sprites(f'{folder}{file}/{xcod}', f'{folder}{file}', overwrite)
                Console.info(locale.dec_sc)
                compile_sc(f'{folder}{file}/', sheet_image, sheet_image_data, folder_export)
            except Exception as exception:
                Console.error(locale.error % (exception.__class__.__module__, exception.__class__.__name__, exception))
                logger.write(traceback.format_exc())
            print()


def write_sc(output_filename: str, buffer: bytes, use_lzham: bool):
    with open(output_filename, 'wb') as file_out:
        Console.info(locale.header_done)

        if use_lzham:
            Console.info(locale.compressing_with % 'LZHAM')
            file_out.write(struct.pack('<4sBI', b'SCLZ', 18, len(buffer)))
            compressed = compress(buffer, Signatures.SCLZ)

            file_out.write(compressed)
        else:
            Console.info(locale.compressing_with % 'LZMA')
            compressed = compress(buffer, Signatures.SC, 1)
            file_out.write(compressed)
        Console.info(locale.compression_done)


def open_sc(input_filename: str):
    decompressed = None
    use_lzham = False

    Console.info(locale.collecting_inf)
    with open(input_filename, 'rb') as f:
        filedata = f.read()
        f.close()

    try:
        decompressed, signature = decompress(filedata)
        #
        # Console.info(locale.detected_comp % signature.upper())
        #
        if signature == Signatures.SCLZ:
            use_lzham = True
    except Exception:
        Console.info(locale.decompression_error)
        exit(1)

    return decompressed, use_lzham


def compile_sc(_dir, from_memory=None, img_data=None, folder_export=None):
    sc_data = None

    name = _dir.split('/')[-2]
    if from_memory:
        files = from_memory
    else:
        files = []
        [files.append(i) if i.endswith('.png') else None for i in os.listdir(_dir)]
        files.sort()
        if not files:
            return Console.info(locale.dir_empty % _dir.split('/')[-2])
        files = [Image.open(f'{_dir}{i}') for i in files]

    Console.info(locale.collecting_inf)
    sc = Writer()

    has_xcod = False
    use_lzham = False
    if from_memory:
        use_lzham = img_data['use_lzham']
    else:
        try:
            sc_data = open(f'{_dir}/{name}.xcod', 'rb')
            sc_data.read(4)
            use_lzham, = struct.unpack('?', sc_data.read(1))
            sc_data.read(1)
            has_xcod = True
        except Exception:
            Console.info(locale.not_xcod)
            Console.info(locale.default_types)

    for picture_index in range(len(files)):
        img = files[picture_index]
        print()

        if from_memory:
            file_type = img_data['data'][picture_index]['file_type']
            pixel_type = img_data['data'][picture_index]['pixel_type']
        else:
            if has_xcod:
                file_type, pixel_type, width, height = struct.unpack('>BBHH', sc_data.read(6))

                if (width, height) != img.size:
                    Console.info(locale.illegal_size % (width, height, img.width, img.height))
                    if Console.question(locale.resize_qu):
                        Console.info(locale.resizing)
                        img = img.resize((width, height), Image.ANTIALIAS)
            else:
                file_type, pixel_type = 1, 0

        width, height = img.size
        pixel_size = get_pixel_size(pixel_type)

        img = img.convert('RGBA')
        x = Image.new('RGBA', img.size, (0, 0, 0, 1))
        x.paste(img, (0, 0), img)
        img = x

        img = img.convert(pixel_type2str(pixel_type))

        file_size = width * height * pixel_size + 5

        Console.info(locale.about_sc % (name, picture_index, pixel_type, width, height))

        sc.write(struct.pack('<BIBHH', file_type, file_size, pixel_type, width, height))

        if file_type in (27, 28):
            split_image(img)
            print()

        rgba2bytes(sc, img, pixel_type)
        print()

    sc.write(bytes(5))
    print()

    write_sc(f'{folder_export}/{name}.sc', sc.getvalue(), use_lzham)


def ceil(integer) -> int:
    return round(integer + 0.5)


class SupercellSWF:
    def __init__(self):
        self.filename = None
        self.reader = None

        self.shape_count = 0
        self.movie_clips_count = 0
        self.textures_count = 0
        self.text_field_count = 0
        self.matrix_count = 0
        self.color_transformation_count = 0

        self.export_count = 0

        self.exports = {}

        self.shapes = []
        self.movie_clips = []
        self.textures = []

        self.matrices = []

        self.xcod_writer = Writer('big')

    def get_export_by_id(self, movie_clip):
        return self.exports.get(movie_clip, '_movieclip_%s' % movie_clip)

    def load_internal(self, filepath: str, is_texture: bool):
        decompressed, use_lzham = open_sc(filepath)
        self.reader = Reader(decompressed)
        del decompressed

        self.filename = os.path.basename(filepath)

        if is_texture:
            has_texture = self.load_tags()
        else:
            self.shape_count = self.reader.read_uint16()
            self.movie_clips_count = self.reader.read_uint16()
            self.textures_count = self.reader.read_uint16()
            self.text_field_count = self.reader.read_uint16()
            self.matrix_count = self.reader.read_uint16()
            self.color_transformation_count = self.reader.read_uint16()

            self.shapes = [_class() for _class in [Shape] * self.shape_count]
            self.movie_clips = [_class() for _class in [MovieClip] * self.movie_clips_count]
            self.textures = [_class() for _class in [SWFTexture] * self.textures_count]

            self.reader.read_uint32()
            self.reader.read_byte()

            self.export_count = self.reader.read_uint16()

            self.exports = [_function() for _function in [self.reader.read_uint16] * self.export_count]
            self.exports = {export_id: self.reader.read_string() for export_id in self.exports}

            has_texture = self.load_tags()

        print()
        return has_texture, use_lzham

    def load_tags(self):
        has_texture = True

        texture_id = 0
        loaded_movie_clips = 0
        loaded_shapes = 0

        while True:
            tag = self.reader.read_byte()
            length = self.reader.read_uint32()

            if tag == 0:
                return has_texture
            elif tag in [1, 16, 28, 29, 34, 19, 24, 27]:
                if len(self.textures) <= texture_id:
                    # Костыль, такого в либе нет, но ради фичи с вытаскиванием только текстур, можно и добавить)
                    self.textures.append(SWFTexture())
                texture = self.textures[texture_id]
                texture.load(self, tag, has_texture)

                if has_texture:
                    Console.info(locale.about_sc % (self.filename, texture_id, texture.pixel_type, texture.width, texture.height))
                    print()

                    self.xcod_writer.write_ubyte(tag)
                    self.xcod_writer.write_ubyte(texture.pixel_type)
                    self.xcod_writer.write_uint16(texture.width)
                    self.xcod_writer.write_uint16(texture.height)
                self.textures[texture_id] = texture
                texture_id += 1
            elif tag in [2, 18]:
                self.shapes[loaded_shapes].load(self, tag)
                loaded_shapes += 1
            elif tag in [3, 10, 12, 14, 35]:  # MovieClip
                self.movie_clips[loaded_movie_clips].load(self, tag)
                loaded_movie_clips += 1
            elif tag == 8:  # Matrix
                scale_x = self.reader.read_int32() / 1024
                rotation_x = self.reader.read_int32() / 1024
                rotation_y = self.reader.read_int32() / 1024
                scale_y = self.reader.read_int32() / 1024
                x = self.reader.read_int32() / 20
                y = self.reader.read_int32() / 20

                self.matrices.append([
                    scale_x, rotation_x, x,
                    rotation_y, scale_y, y
                ])
            elif tag == 26:
                has_texture = False
            else:
                self.reader.read(length)


def cut_sprites(swf: SupercellSWF, folder_export):
    os.makedirs(f'{folder_export}/overwrite', exist_ok=True)
    os.makedirs(f'{folder_export}/shapes', exist_ok=True)

    shapes_count = len(swf.shapes)
    swf.xcod_writer.write_uint16(shapes_count)

    for shape_index in range(shapes_count):
        Console.progress_bar(
            locale.cut_sprites_process % (shape_index + 1, shapes_count),
            shape_index,
            shapes_count
        )

        shape = swf.shapes[shape_index]

        rendered_shape = shape.render(swf)
        rendered_shape.save(f'{folder_export}/shapes/{shape.id}.png')

        regions_count = len(shape.regions)
        swf.xcod_writer.write_uint16(regions_count)
        for region_index in range(regions_count):
            region = shape.regions[region_index]

            swf.xcod_writer.write_ubyte(region.texture_id)
            swf.xcod_writer.write_ubyte(region.points_count)

            for point in region.sheet_points:
                swf.xcod_writer.write_uint16(int(point.x))
                swf.xcod_writer.write_uint16(int(point.y))
            swf.xcod_writer.write_ubyte(1 if region.mirroring else 0)
            swf.xcod_writer.write_ubyte(region.rotation // 90)

            rendered_region = region.render(swf)
            rendered_region.save(f'{folder_export}/shape_{shape.id}_{region_index}.png')
    print()


def place_sprites(xcod, folder, overwrite=False):
    xcod = Reader(open(xcod, 'rb').read(), 'big')
    files = os.listdir(f'{folder}{"/overwrite" if overwrite else ""}')
    tex = os.listdir(f'{folder}/textures')

    xcod.read(4)
    use_lzham, pictures_count = xcod.read_ubyte(), xcod.read_ubyte()
    sheet_image = []
    sheet_image_data = {'use_lzham': use_lzham, 'data': []}
    for i in range(pictures_count):
        file_type, sub_type, width, height = xcod.read_ubyte(), xcod.read_ubyte(), xcod.read_uint16(), xcod.read_uint16()
        sheet_image.append(
            Image.open(f'{folder}/textures/{tex[i]}')
            if overwrite else
            Image.new('RGBA', (width, height)))
        sheet_image_data['data'].append({'file_type': file_type, 'pixel_type': sub_type})

    shapes_count = xcod.read_uint16()
    for shape_index in range(shapes_count):
        Console.progress_bar(locale.place_sprites_process % (shape_index + 1, shapes_count), shape_index, shapes_count)
        regions_count = xcod.read_uint16()

        for region_index in range(regions_count):
            texture_id, points_count = xcod.read_ubyte(), xcod.read_ubyte()
            texture_width, texture_height = sheet_image[texture_id].width, sheet_image[texture_id].height
            polygon = [(xcod.read_uint16(), xcod.read_uint16()) for _ in range(points_count)]
            mirroring, rotation = xcod.read_ubyte() == 1, xcod.read_ubyte() * 90

            if f'shape_{shape_index}_{region_index}.png' not in files:
                continue

            tmp_region = Image.open(
                f'{folder}{"/overwrite" if overwrite else ""}/'
                f'shape_{shape_index}_{region_index}.png') \
                .convert('RGBA') \
                .rotate(360 - rotation, expand=True)

            img_mask = Image.new('L', (texture_width, texture_height), 0)
            color = 255
            ImageDraw.Draw(img_mask).polygon(polygon, fill=color)
            bbox = img_mask.getbbox()

            if not bbox:
                min_x = min(i[0] for i in polygon)
                min_y = min(i[1] for i in polygon)
                max_x = max(i[0] for i in polygon)
                max_y = max(i[1] for i in polygon)

                if max_y - min_y != 0:
                    for _y in range(max_y - min_y):
                        img_mask.putpixel((max_x - 1, min_y + _y - 1), color)

                elif max_x - min_x != 0:
                    for _x in range(max_x - min_x):
                        img_mask.putpixel((min_x + _x - 1, max_y - 1), color)
                else:
                    img_mask.putpixel((max_x - 1, max_y - 1), color)
                bbox = img_mask.getbbox()

            a, b, c, d = bbox
            if c - a - 1:
                c -= 1
            if d - b - 1:
                d -= 1

            bbox = a, b, c, d

            region_size = bbox[2] - bbox[0], bbox[3] - bbox[1]
            tmp_region = tmp_region.resize(region_size, Image.ANTIALIAS)

            if mirroring:
                tmp_region = tmp_region.transform(region_size, Image.EXTENT,
                                                  (tmp_region.width, 0, 0, tmp_region.height))

            sheet_image[texture_id].paste(Image.new('RGBA', region_size), bbox[:2], img_mask.crop(bbox))
            sheet_image[texture_id].paste(tmp_region, bbox[:2], tmp_region)
    print()

    return sheet_image, sheet_image_data


# Testing TIME!
if __name__ == '__main__':
    welcome_text()
