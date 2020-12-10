from sc_compression import compression

from system.bytestream import Reader, Writer
from system.lib.console import Console
from system.lib.logger import Logger
from system.lib.objects import *
from system.localization import Locale

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
    from PIL import Image, ImageDraw
except Exception as e:
    logger.write(e)

lzham_path = r'system\lzham'

is_windows = platform.system() == 'Windows'
nul = f' > {"nul" if is_windows else "/dev/null"} 2>&1'

locale = Locale()
config_path = './system/config.json'

config = {'inited': False, 'version': None, 'lang': 'en-EU', 'updated': True}
if os.path.isfile(config_path):
    try:
        config = json.load(open(config_path))
    except Exception as e:
        logger.write(e)
json.dump(config, open(config_path, 'w'))
locale.load_from(config['lang'])

if is_windows:
    try:
        colorama.init()
    except Exception as e:
        logger.write(e)

    import ctypes

    set_title = ctypes.windll.kernel32.SetConsoleTitleW
    del ctypes


    def clear():
        os.system('cls')

    def pause():
        print(locale.pause, end='')
        os.system(f'pause{nul}')
else:
    def set_title(message):
        sys.stdout.write(f'\x1b]2;{message}\x07')

    def clear():
        os.system('clear')

    def pause():
        if os.system(f'read -s -n 1 -p "{locale.pause}"'):
            input(locale.to_continue)

def load_locale():
    config.update(json.load(open(config_path)))
    locale.load_from(config['lang'])


def specialize_print(console_width, first_string, second_string):
    print(first_string + (' ' * (console_width // 2 - len(first_string)) + ': ' + second_string))


def colored_print(text, color=None):
    if color is None:
        color = colorama.Back.GREEN
    return print(color + colorama.Fore.BLACK + text + ' ' * (10 - len(text)) + colorama.Style.RESET_ALL)


def welcome_text():
    load_locale()

    console_width = shutil.get_terminal_size().columns
    print(
        (
            colorama.Back.BLACK + colorama.Fore.GREEN +
            locale.xcoder % config['version'] +
            colorama.Style.RESET_ALL
        ).center(console_width + 14)
    )
    print('github.com/MasterDevX/XCoder'.center(console_width))
    print(
        (
            'Modified by Vorono4ka'
        ).center(console_width)
    )
    print(console_width * '-')

    colored_print(locale.sc)
    specialize_print(console_width, ' 1   ' + locale.dsc, locale.dsc_desc)
    specialize_print(console_width, ' 2   ' + locale.esc, locale.esc_desc)
    specialize_print(console_width, ' 3   ' + locale.d1sc, locale.experimental)
    specialize_print(console_width, ' 4   ' + locale.e1sc, locale.experimental)
    print(console_width * '-')

    colored_print(locale.oth)
    specialize_print(console_width, ' 101 ' + locale.check_update, locale.version % config['version'])
    specialize_print(console_width, ' 102 ' + locale.reinit, locale.reinit_desc)
    specialize_print(console_width, ' 103 ' + locale.relang, locale.relang_desc % config['lang'])
    specialize_print(console_width, ' 104 ' + locale.clean_dirs, locale.clean_dirs_desc)
    print(' 105 ' + locale.exit)
    print(console_width * '-')

    choice = input(locale.choice)
    print(console_width * '-')
    return choice


def get_tags(owner: str, repo: str):
    api_url = 'https://api.github.com'

    tags = requests.get(api_url + '/repos/{owner}/{repo}/tags'.format(owner=owner, repo=repo)).json()
    tags = [
        {
            key: v for key, v in tag.items()
            if key in ['name', 'zipball_url']
        } for tag in tags
    ]

    return tags


def check_update():
    tags = get_tags('vorono4ka', 'xcoder')

    if len(tags) > 0:
        latest_tag = tags[0]
        latest_tag_name = latest_tag['name'][1:]  # clear char 'v' at string start
        if config['version'] != latest_tag_name:
            Console.error(locale.not_latest)

            Console.info(locale.update_downloading)
            download_update(latest_tag['zipball_url'])


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
        config.update({'updated': False})
        print(config)
        json.dump(config, open(config_path, 'w'))
        input(locale.to_continue)
        exit()


def get_pixel_size(_type):
    if _type in (0, 1):
        return 4
    if _type in (2, 3, 4, 6):
        return 2
    if _type in (10,):
        return 1
    raise Exception(locale.unk_type % _type)


def pixel_type2str(_type):
    if _type in range(4):
        return 'RGBA'
    if _type in (4,):
        return 'RGB'
    if _type in (6,):
        return 'LA'
    if _type in (10,):
        return 'L'
    raise Exception(locale.unk_type % _type)


def bytes2rgba(data, _type, img, pix):
    read_pixel = None
    if _type in (0, 1):
        def read_pixel():
            return struct.unpack('4B', data.read(4))
    elif _type == 2:
        def read_pixel():
            p, = struct.unpack('<H', data.read(2))
            return (p >> 12 & 15) << 4, (p >> 8 & 15) << 4, (p >> 4 & 15) << 4, (p >> 0 & 15) << 4
    elif _type == 3:
        def read_pixel():
            p, = struct.unpack('<H', data.read(2))
            return (p >> 11 & 31) << 3, (p >> 6 & 31) << 3, (p >> 1 & 31) << 3, (p & 255) << 7
    elif _type == 4:
        def read_pixel():
            p, = struct.unpack('<H', data.read(2))
            return (p >> 11 & 31) << 3, (p >> 5 & 63) << 2, (p & 31) << 3
    elif _type == 6:
        def read_pixel():
            return struct.unpack('2B', data.read(2))[::-1]
    elif _type == 10:
        def read_pixel():
            return struct.unpack('B', data.read(1))[0]

    if read_pixel is not None:
        width, height = img.size
        point = -1
        for y in range(height):
            for x in range(width):
                pix.append(read_pixel())

            curr = Console.percent(y, height)
            if curr > point:
                Console.progress_bar(locale.crt_pic, y, height)
                point = curr

        img.putdata(pix)


def rgba2bytes(sc, img, _type):
    write_pixel = None
    if _type in (0, 1):
        def write_pixel(pixel):
            return struct.pack('4B', *pixel)
    if _type == 2:
        def write_pixel(pixel):
            r, g, b, a = pixel
            return struct.pack('<H', a >> 4 | b >> 4 << 4 | g >> 4 << 8 | r >> 4 << 12)
    if _type == 3:
        def write_pixel(pixel):
            r, g, b, a = pixel
            return struct.pack('<H', a >> 7 | b >> 3 << 1 | g >> 3 << 6 | r >> 3 << 11)
    if _type == 4:
        def write_pixel(pixel):
            r, g, b = pixel
            return struct.pack('<H', b >> 3 | g >> 2 << 5 | r >> 3 << 11)
    if _type == 6:
        def write_pixel(pixel):
            return struct.pack('2B', *pixel[::-1])
    if _type == 10:
        def write_pixel(pixel):
            return struct.pack('B', pixel)

    if write_pixel is not None:
        width, height = img.size

        pix = img.getdata()
        point = -1
        for y in range(height):
            for x in range(width):
                sc.write(write_pixel(pix[y * width + x]))

            curr = Console.percent(y, height)
            if curr > point:
                Console.progress_bar(locale.writing_pic, y, height)
                point = curr


def join_image(img, p):
    width, height = img.size
    loaded_img = img.load()
    x = 0
    a = 32

    _ha = height // a
    _wa = width // a
    ha = height % a
    wa = width % a

    for l in range(_ha):
        for k in range(_wa):
            for j in range(a):
                for h in range(a):
                    loaded_img[h + k * a, j + l * a] = p[x]
                    x += 1

        for j in range(a):
            for h in range(wa):
                loaded_img[h + (width - wa), j + l * a] = p[x]
                x += 1
        Console.progress_bar(locale.join_pic, l, _ha)

    for k in range(_wa):
        for j in range(ha):
            for h in range(a):
                loaded_img[h + k * a, j + (height - ha)] = p[x]
                x += 1

    for j in range(ha):
        for h in range(wa):
            loaded_img[h + (width - wa), j + (height - ha)] = p[x]
            x += 1


def split_image(img):
    p = []
    width, height = img.size
    loaded_img = img.load()
    a = 32

    _ha = height // a
    _wa = width // a
    ha = height % a
    wa = width % a

    for l in range(_ha):
        for k in range(_wa):
            for j in range(a):
                for h in range(a):
                    p.append(loaded_img[h + (k * a), j + (l * a)])

        for j in range(a):
            for h in range(wa):
                p.append(loaded_img[h + (width - wa), j + (l * a)])
        Console.progress_bar(locale.split_pic, l, _ha)

    for k in range(width // a):
        for j in range(ha):
            for h in range(a):
                p.append(loaded_img[h + (k * a), j + (height - ha)])

    for j in range(ha):
        for h in range(wa):
            p.append(loaded_img[h + (width - wa), j + (height - ha)])
    img.putdata(p)


def write_sc(output_filename: str, buffer: bytes, use_lzham: bool):
    with open(output_filename, 'wb') as file_out:
        Console.info(locale.header_done)
        compressor = compression.Compressor()

        if use_lzham:
            Console.info(locale.compressing_with % 'LZHAM')
            file_out.write(struct.pack('<4sBI', b'SCLZ', 18, len(buffer)))
            compressed = compressor.compress(buffer, 'sclz')

            file_out.write(compressed)
        else:
            Console.info(locale.compressing_with % 'LZMA')
            compressed = compressor.compress(buffer, 'sc')
            file_out.write(compressed)
        Console.info(locale.compression_done)


def open_sc(input_filename: str):
    use_lzham = False

    Console.info(locale.collecting_inf)
    with open(input_filename, 'rb') as fh:
        try:
            decompressor = compression.Decompressor()
            decompressed = decompressor.decompress(fh.read())
            signature = decompressor.get_signature()

            Console.info(locale.detected_comp % signature.upper())

            if signature == 'sclz':
                use_lzham = True
        except Exception as e:
            Console.info(locale.try_error)

        fh.close()

    return decompressed, use_lzham


def decompile_sc(file_name, current_sub_path, folder=None, folder_export=None, to_memory=False):
    sc_data = Writer()
    pictures_count = 0
    images = []

    decompressed, use_lzham = open_sc(f'{folder}/{file_name}')
    reader = Reader(decompressed)
    del decompressed

    if to_memory:
        os.makedirs(f"{folder_export}/{current_sub_path}/textures", exist_ok=True)

    while 1:
        temp = reader.read(5)
        if temp == bytes(5):
            data = struct.pack('4s?B', b'XCOD', use_lzham, pictures_count) + sc_data.getvalue()
            if not to_memory:
                with open(f'{folder_export}/{current_sub_path}/{base_name.rstrip("_")}.xcod', 'wb') as xc:
                    xc.write(data)
                data = None

            return images, data

        file_type, file_size, sub_type, width, height = struct.unpack('<BIBHH', temp + reader.read(5))

        base_name = os.path.basename(file_name)[::-1].split('.', 1)[1][::-1] + '_' * pictures_count
        Console.info(locale.about_sc % (base_name, file_type, file_size, sub_type, width, height))

        img = Image.new(pixel_type2str(sub_type), (width, height))
        pixels = []

        bytes2rgba(reader, sub_type, img, pixels)

        print()

        if file_type in (27, 28):
            join_image(img, pixels)
            print()

        Console.info(locale.png_save)
        if to_memory:
            img.save(f"{folder_export}/{current_sub_path}/textures/{base_name}.png")
            images.append(img)
        else:
            img.save(f'{folder_export}/{current_sub_path}/{base_name}.png')
        Console.info(locale.saved)
        pictures_count += 1
        sc_data.write(struct.pack('>BBHH', file_type, sub_type, width, height))
        print()


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
        except Exception as e:
            Console.info(locale.not_xcod)
            Console.info(locale.default_types)

    for picture_index in range(len(files)):
        img = files[picture_index]
        print()

        if from_memory:
            file_type = img_data['data'][picture_index]['file_type']
            sub_type = img_data['data'][picture_index]['sub_type']
        else:
            if has_xcod:
                file_type, sub_type, width, height = struct.unpack('>BBHH', sc_data.read(6))

                if (width, height) != img.size:
                    Console.info(locale.illegal_size % (width, height, img.width, img.height))
                    if Console.question(locale.resize_qu):
                        Console.info(locale.resizing)
                        img = img.resize((width, height), Image.ANTIALIAS)
            else:
                file_type, sub_type = 1, 0

        width, height = img.size
        pixel_size = get_pixel_size(sub_type)

        img = img.convert('RGBA')
        x = Image.new('RGBA', img.size, (0, 0, 0, 1))
        x.paste(img, (0, 0), img)
        img = x

        img = img.convert(pixel_type2str(sub_type))

        file_size = width * height * pixel_size + 5

        Console.info(locale.about_sc % (name + '_' * picture_index, file_type, file_size, sub_type, width, height))

        sc.write(struct.pack('<BIBHH', file_type, file_size, sub_type, width, height))

        if file_type in (27, 28):
            split_image(img)
            print()

        rgba2bytes(sc, img, sub_type)
        print()

    sc.write(bytes(5))
    print()

    write_sc(f'{folder_export}/{name}.sc', sc.getvalue(), use_lzham)


def ceil(integer) -> int:
    return round(integer + 0.5)


def decode_sc(file_name, folder):
    decompressed, use_lzham = open_sc(f'{folder}/{file_name}')
    reader = Reader(decompressed)
    del decompressed

    offset_shape = 0
    offset_sheet = 0

    sprite_globals = SpriteGlobals()

    sprite_globals.shape_count = reader.uint16()
    sprite_globals.total_animations = reader.uint16()
    sprite_globals.total_textures = reader.uint16()
    sprite_globals.text_field_count = reader.uint16()
    sprite_globals.matrix_count = reader.uint16()
    sprite_globals.color_transformation_count = reader.uint16()

    sheet_data = [_class() for _class in [SheetData] * sprite_globals.total_textures]
    sprite_data = [_class() for _class in [SpriteData] * sprite_globals.shape_count]

    reader.uint32()
    reader.byte()

    sprite_globals.export_count = reader.uint16()

    exports = [_function() for _function in [reader.uint16] * sprite_globals.export_count]
    exports = {i: reader.string() for i in exports}

    shapes = {}
    movie_clips = {}

    def get_export_by_id(movie_clip):
        return exports.get(movie_clip, '_movieclip_%s' % movie_clip)

    while True:
        data_block_tag = '%02x' % reader.byte()
        data_block_size = reader.uint32()

        if data_block_tag in ['01', '18']:
            reader.byte()  # pixel_type

            sheet_data[offset_sheet].size = (reader.uint16(), reader.uint16())

            offset_sheet += 1
            continue
        elif data_block_tag == '12':
            sprite_data[offset_shape].id = reader.uint16()

            regions_count = reader.uint16()
            reader.uint16()  # point_count

            for region_index in range(regions_count):
                region = Region()

                data_block_tag = '%02x' % reader.byte()

                if data_block_tag == '16':
                    reader.uint32()  # data_block_length
                    region.sheet_id = reader.byte()

                    region.num_points = reader.byte()

                    region.shape_points = [_class() for _class in [Point] * region.num_points]
                    region.sheet_points = [_class() for _class in [Point] * region.num_points]

                    for z in range(region.num_points):
                        region.shape_points[z].x = reader.int32()
                        region.shape_points[z].y = reader.int32()
                    for z in range(region.num_points):
                        w, h = [reader.uint16() * sheet_data[region.sheet_id].size[i] / 0xffff for i in range(2)]
                        x, y = [ceil(i) for i in (w, h)]
                        if int(w) == x:
                            x += 1
                        if int(h) == y:
                            y += 1

                        region.sheet_points[z].position = (x, y)
                sprite_data[offset_shape].regions.append(region)
            shapes[sprite_data[offset_shape].id] = sprite_data[offset_shape]

            reader.uint32()
            reader.byte()

            offset_shape += 1
            continue
        elif data_block_tag == '08':  # Matrix
            reader.int32()
            reader.int32()
            reader.int32()
            reader.int32()
            reader.int32()
            reader.int32()
            continue
        elif data_block_tag == '0c':  # MovieClip
            movie_clip_id = reader.uint16()

            if not movie_clips.get(movie_clip_id):
                movie_clips[movie_clip_id] = MovieClip()

            movie_clips[movie_clip_id].name = get_export_by_id(movie_clip_id)
            movie_clips[movie_clip_id].fps = reader.byte()
            movie_clips[movie_clip_id].frames_count = reader.uint16()

            cnt1 = reader.uint32()

            for i in range(cnt1):
                reader.uint16()
                reader.uint16()
                reader.uint16()

            cnt2 = reader.uint16()

            for i in range(cnt2):
                bind_id = reader.uint16()  # bind_id
                if bind_id in shapes:
                    movie_clips[movie_clip_id].shapes.append(shapes[bind_id])

            for i in range(cnt2):
                blend = reader.byte()  # blend
                movie_clips[movie_clip_id].blends.append(blend)

            for i in range(cnt2):
                reader.string()  # bind_name

            while True:
                inline_data_type = reader.ubyte()
                reader.int32()  # data_length

                if inline_data_type == 0:
                    break

                if inline_data_type == 11:
                    reader.int16()  # frame_id
                    reader.string()  # frame_name
                elif inline_data_type == 31:
                    for x in range(4):
                        reader.ubyte()
                        reader.ubyte()
                        reader.string()
                        reader.string()
            continue
        elif data_block_tag == '00':
            break
        else:
            reader.read(data_block_size)

    for movieclip in movie_clips.values():
        for shape_index in range(len(movieclip.shapes)):
            for region_index in range(len(movieclip.shapes[shape_index].regions)):
                region = movieclip.shapes[shape_index].regions[region_index]

                region_min_x = 32767
                region_max_x = -32767
                region_min_y = 32767
                region_max_y = -32767
                for z in range(region.num_points):
                    tmp_x, tmp_y = region.shape_points[z].position

                    if tmp_y > region.top:
                        region.top = tmp_y
                    if tmp_x < region.left:
                        region.left = tmp_x
                    if tmp_y < region.bottom:
                        region.bottom = tmp_y
                    if tmp_x > region.right:
                        region.right = tmp_x

                    sheet_point = region.sheet_points[z]

                    tmp_x, tmp_y = sheet_point.position

                    if tmp_x < region_min_x:
                        region_min_x = tmp_x
                    if tmp_x > region_max_x:
                        region_max_x = tmp_x
                    if tmp_y < region_min_y:
                        region_min_y = tmp_y
                    if tmp_y > region_max_y:
                        region_max_y = tmp_y

                region = region_rotation(region)

                tmp_x, tmp_y = region_max_x - region_min_x, region_max_y - region_min_y
                size = (tmp_x, tmp_y)

                if region.rotation in (90, 270):
                    size = size[::-1]

                region.size = size

                movieclip.shapes[shape_index].regions[region_index] = region

    return sprite_globals, movie_clips, sheet_data


def cut_sprites(movie_clips, sheet_data, sheet_image, xcod, folder_export):
    os.makedirs(f'{folder_export}/overwrite', exist_ok=True)

    movie_clips = list(movie_clips.values())
    movie_clips_count = len(movie_clips)
    xcod.write(struct.pack('>H', movie_clips_count))

    for movieclip_index in range(movie_clips_count):
        Console.progress_bar(
            locale.cut_sprites % (movieclip_index + 1, movie_clips_count),
            movieclip_index,
            movie_clips_count
        )
        movieclip = movie_clips[movieclip_index]

        n = movieclip.name.encode()
        xcod.write(struct.pack('B', len(n)) + n + struct.pack('>H', len(movieclip.shapes)))

        for shape_index in range(len(movieclip.shapes)):
            shape = movieclip.shapes[shape_index]
            xcod.write(struct.pack('>H', len(shape.regions)))
            for y in range(len(shape.regions)):
                region = shape.regions[y]

                polygon = [region.sheet_points[z].position for z in range(region.num_points)]

                xcod.write(struct.pack('>2B2H', region.sheet_id, region.num_points,
                                       *sheet_data[region.sheet_id].size) + b''.join(
                    struct.pack('>2H', *i) for i in polygon) + struct.pack('?B', region.mirroring,
                                                                           region.rotation // 90))

                img_mask = Image.new('L', sheet_data[region.sheet_id].size, 0)
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
                            img_mask.putpixel((max_x, min_y + _y), color)

                    elif max_x - min_x != 0:
                        for _x in range(max_x - min_x):
                            img_mask.putpixel((min_x + _x, max_y), color)
                    else:
                        img_mask.putpixel((max_x, max_y), color)
                    bbox = img_mask.getbbox()

                a, b, c, d = bbox
                if c - a - 1:
                    c -= 1
                if d - b - 1:
                    d -= 1

                bbox = a, b, c, d

                region_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])

                tmp_region = Image.new('RGBA', region_size)
                tmp_region.paste(sheet_image[region.sheet_id].crop(bbox), (0, 0), img_mask.crop(bbox))
                if region.mirroring:
                    tmp_region = tmp_region.transform(region_size, Image.EXTENT, (region_size[0], 0, 0, region_size[1]))

                tmp_region.rotate(region.rotation, expand=True) \
                    .save(f'{folder_export}/{movieclip.name}_{movieclip_index}_{y}.png')
    print()


def place_sprites(xcod, folder, overwrite=False, margins=False):
    xcod = Reader(open(xcod, 'rb').read(), 'big')
    files = os.listdir(f'{folder}{"/overwrite" if overwrite else ""}')
    tex = os.listdir(f'{folder}/textures')

    xcod.read(4)
    use_lzham, pictures_count = xcod.ubyte(), xcod.ubyte()
    sheet_image = []
    sheet_image_data = {'use_lzham': use_lzham, 'data': []}
    for i in range(pictures_count):
        file_type, sub_type, width, height = xcod.ubyte(), xcod.ubyte(), xcod.uint16(), xcod.uint16()
        sheet_image.append(
            Image.open(f'{folder}/textures/{tex[i]}')
            if overwrite else
            Image.new('RGBA', (width, height)))
        sheet_image_data['data'].append({'file_type': file_type, 'sub_type': sub_type})

    clips_count = xcod.uint16()

    for clip_index in range(clips_count):
        Console.progress_bar(locale.place_sprites % (clip_index + 1, clips_count), clip_index, clips_count)
        clip_name = xcod.string()
        shape_count = xcod.uint16()

        for shape_index in range(shape_count):
            regions_count = xcod.uint16()

            for region_index in range(regions_count):
                sheet_id, num_points, x1, y1 = xcod.ubyte(), xcod.ubyte(), xcod.uint16(), xcod.uint16()
                polygon = [(_function(), _function()) for _function in [xcod.uint16] * num_points]
                mirroring, rotation = xcod.ubyte() == 1, xcod.ubyte()
                rotation *= 90

                if f'{clip_index}_{region_index}.png' not in files:
                    continue

                tmp_region = Image.open(
                    f'{folder}{"/overwrite" if overwrite else ""}/'
                    f'{clip_name}_{shape_index}_{region_index}.png') \
                    .convert('RGBA') \
                    .rotate(360 - rotation, expand=True)

                img_mask = Image.new('L', (x1, y1), 0)
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
                            img_mask.putpixel((max_x, min_y + _y), color)

                    elif max_x - min_x != 0:
                        for _x in range(max_x - min_x):
                            img_mask.putpixel((min_x + _x, max_y), color)
                    else:
                        img_mask.putpixel((max_x, max_y), color)
                    bbox = img_mask.getbbox()

                a, b, c, d = bbox
                if c - a - 1:
                    c -= 1
                if d - b - 1:
                    d -= 1

                if margins:
                    pass
                    # if a > 0:
                    #     j = int(a > 1) + 1
                    #     o = tmp_region.crop((0, 0, 1, tmp_region.height))
                    #     tmp_region = tmp_region.crop((-j, 0) + tmp_region.size)
                    #     for v in range(j):
                    #         tmp_region.paste(o, (v, 0), o)
                    #     o = img_mask.crop((0, 0, 1, img_mask.height))
                    #     img_mask = img_mask.crop((-j, 0) + img_mask.size)
                    #     for v in range(j):
                    #         img_mask.paste(o, (v, 0), o)
                    #     a -= j
                    # if b > 0:
                    #     j = int(b > 1) + 1
                    #     print(j)
                    #     o = tmp_region.crop((0, 0, tmp_region.width, 1))
                    #     tmp_region = tmp_region.crop((0, -j) + tmp_region.size)
                    #     for v in range(j):
                    #         tmp_region.paste(o, (0, v), o)
                    #     o = img_mask.crop((0, 0, img_mask.width, 1))
                    #     img_mask = img_mask.crop((0, -j) + img_mask.size)
                    #     for v in range(j):
                    #         img_mask.paste(o, (0, v), o)
                    #     b -= j
                    #
                    # if c < sheet_image[sheet_id].width:
                    #     j = int(sheet_image[sheet_id].width - c > 1) + 1
                    #     o = tmp_region.crop((tmp_region.width - 1, 0, tmp_region.width, tmp_region.height))
                    #     tmp_region = tmp_region.crop((0, 0, tmp_region.width + j, tmp_region.height))
                    #     for v in range(j):
                    #         tmp_region.paste(o, (tmp_region.width - v - 1, 0), o)
                    #     o = img_mask.crop((img_mask.width - 1, 0, img_mask.width, img_mask.height))
                    #     img_mask = img_mask.crop((0, 0, img_mask.width + j, img_mask.height))
                    #     for v in range(j):
                    #         img_mask.paste(o, (img_mask.width - v - 1, 0), o)
                    #     c += j
                    # if d < sheet_image[sheet_id].height:
                    #     j = int(sheet_image[sheet_id].height - d > 1) + 1
                    #     o = tmp_region.crop((0, tmp_region.height - 1, tmp_region.width, tmp_region.height))
                    #     tmp_region = tmp_region.crop((0, 0, tmp_region.width, tmp_region.height + j))
                    #     for v in range(j):
                    #         tmp_region.paste(o, (0, tmp_region.height - v - 1), o)
                    #     o = img_mask.crop((0, img_mask.height - 1, img_mask.width, img_mask.height))
                    #     img_mask = img_mask.crop((0, 0, img_mask.width, img_mask.height + j))
                    #     for v in range(j):
                    #         img_mask.paste(o, (0, img_mask.height - v - 1), o)
                    #     d += j

                bbox = a, b, c, d

                region_size = bbox[2] - bbox[0], bbox[3] - bbox[1]
                tmp_region = tmp_region.resize(region_size, Image.ANTIALIAS)

                if mirroring:
                    tmp_region = tmp_region.transform(region_size, Image.EXTENT,
                                                      (tmp_region.width, 0, 0, tmp_region.height))

                sheet_image[sheet_id].paste(Image.new('RGBA', region_size), bbox[:2], img_mask.crop(bbox))
                sheet_image[sheet_id].paste(tmp_region, bbox[:2], tmp_region)
    print()

    return sheet_image, sheet_image_data


def region_rotation(region):
    def calc_sum(points):
        x1, y1 = points[(z + 1) % num_points].position
        x2, y2 = points[z].position
        return (x1 - x2) * (y1 + y2)

    sum_sheet = 0
    sum_shape = 0
    num_points = region.num_points

    for z in range(num_points):
        sum_sheet += calc_sum(region.sheet_points)
        sum_shape += calc_sum(region.shape_points)

    sheet_orientation = -1 if (sum_sheet < 0) else 1
    shape_orientation = -1 if (sum_shape < 0) else 1

    region.mirroring = int(not (shape_orientation == sheet_orientation))

    if region.mirroring:
        for x in range(num_points):
            pos = region.shape_points[x].position
            region.shape_points[x].position = (pos[0] * - 1, pos[1])

    pos00 = region.sheet_points[0].position
    pos01 = region.sheet_points[1].position
    pos10 = region.shape_points[0].position
    pos11 = region.shape_points[1].position

    if pos01[0] > pos00[0]:
        px = 1
    elif pos01[0] < pos00[0]:
        px = 2
    else:
        px = 3

    if pos01[1] < pos00[1]:
        py = 1
    elif pos01[1] > pos00[1]:
        py = 2
    else:
        py = 3

    if pos11[0] > pos10[0]:
        qx = 1
    elif pos11[0] < pos10[0]:
        qx = 2
    else:
        qx = 3

    if pos11[1] > pos10[1]:
        qy = 1
    elif pos11[1] < pos10[1]:
        qy = 2
    else:
        qy = 3

    rotation = 0
    if px == qx and py == qy:
        rotation = 0

    elif px == 3:
        if px == qy:
            if py == qx:
                rotation = 1
            else:
                rotation = 3
        else:
            rotation = 2

    elif py == 3:
        if py == qx:
            if px == qy:
                rotation = 3
            else:
                rotation = 1
        else:
            rotation = 2

    elif px != qx and py != qy:
        rotation = 2

    elif px == py:
        if px != qx:
            rotation = 3
        elif py != qy:
            rotation = 1

    elif px != py:
        if px != qx:
            rotation = 1
        elif py != qy:
            rotation = 3

    if sheet_orientation == -1 and rotation in (1, 3):
        rotation += 2
        rotation %= 4

    region.rotation = rotation * 90
    return region


# Testing TIME!
if __name__ == '__main__':
    welcome_text()
