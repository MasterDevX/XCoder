import requests
import zipfile

from system.localization import Locale
from system.lib.console import Console
from system.lib.logger import Logger
from system.lib.objects import *

from sc_compression import compression

logger = Logger('en-EU')
try:
    import io
    import os
    import sys
    import time
    import json
    import struct
    import shutil
    import hashlib
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
else:
    def set_title(message):
        sys.stdout.write(f'\x1b]2;{message}\x07')


    def clear():
        os.system('clear')


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
            return struct.unpack('B', data.read(1))

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
            return struct.pack('B', *pixel)

    if write_pixel is not None:
        width, height = img.size

        pix = img.load()
        point = -1
        for y in range(height):
            for x in range(width):
                sc.write(write_pixel(pix[x, y]))

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

    for l in range(_ha):
        for k in range(_wa):
            for j in range(a):
                for h in range(a):
                    p.append(loaded_img[h + (k * a), j + (l * a)])

        for j in range(a):
            for h in range(width % a):
                p.append(loaded_img[h + (width - (width % a)), j + (l * a)])
        Console.progress_bar(locale.split_pic, l, _ha)

    for k in range(width // a):
        for j in range(int(height % a)):
            for h in range(a):
                p.append(loaded_img[h + (k * a), j + (height - (height % a))])

    for j in range(ha):
        for h in range(width % a):
            p.append(loaded_img[h + (width - (width % a)), j + (height - (height % a))])
    img.putdata(p)


class Reader:
    def __init__(self, data):
        self.stream = io.BytesIO(data)

    def ubyte(self):
        return int.from_bytes(self.stream.read(1), 'little')

    def byte(self):
        return int.from_bytes(self.stream.read(1), 'little', signed=True)

    def uint16(self):
        return int.from_bytes(self.stream.read(2), 'little')

    def int16(self):
        return int.from_bytes(self.stream.read(2), 'little', signed=True)

    def uint32(self):
        return int.from_bytes(self.stream.read(4), 'little')

    def int32(self):
        return int.from_bytes(self.stream.read(4), 'little', signed=True)

    def string(self):
        length = self.byte()
        if length != -1:
            return self.stream.read(length).decode()
        return ''


def decompile_sc(file_name, current_sub_path, to_memory=False, folder=None, folder_export=None):
    sc_data = io.BytesIO()
    pictures_count = 0
    images = []

    use_lzham = False

    Console.info(locale.collecting_inf)
    with open(f'{folder}/{file_name}', 'rb') as fh:
        try:
            decompressor = compression.Decompressor()
            decompressed = decompressor.decompress(fh.read())
            signature = decompressor.get_signature()

            Console.info(locale.detected_comp % signature.upper())

            if signature == 'sclz':
                use_lzham = True
        except Exception as e:
            Console.info(locale.try_error)

        data = io.BytesIO(decompressed)

        while 1:
            temp = data.read(5)
            if temp == bytes(5):
                data = struct.pack('4s?B', b'XCOD', use_lzham, pictures_count) + sc_data.getvalue()
                if not to_memory:
                    with open(f'{folder_export}/{current_sub_path}/{base_name.rstrip("_")}.xcod', 'wb') as xc:
                        xc.write(data)
                    data = None

                return images, data

            file_type, file_size, sub_type, width, height = struct.unpack('<BIBHH', temp + data.read(5))

            base_name = os.path.basename(file_name)[::-1].split('.', 1)[1][::-1] + '_' * pictures_count
            Console.info(locale.about_sc % (base_name, file_type, file_size, sub_type, width, height))

            img = Image.new(pixel_type2str(sub_type), (width, height))
            pixels = []

            bytes2rgba(data, sub_type, img, pixels)

            print()

            if file_type in (27, 28):
                join_image(img, pixels)
                print()

            if to_memory:
                images.append(img)
            else:
                Console.info(locale.png_save)

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
    sc = io.BytesIO()

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

    for picCount in range(len(files)):
        print()
        img = files[picCount]

        if from_memory:
            file_type = img_data['data'][picCount]['file_type']
            sub_type = img_data['data'][picCount]['sub_type']
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
        img = img.convert(pixel_type2str(sub_type))

        file_size = width * height * pixel_size + 5

        Console.info(locale.about_sc % (name + '_' * picCount, file_type, file_size, sub_type, width, height))

        sc.write(struct.pack('<BIBHH', file_type, file_size, sub_type, width, height))

        if file_type in (27, 28):
            split_image(img)
            print()

        rgba2bytes(sc, img, sub_type)
        print()

    sc.write(bytes(5))
    sc = sc.getvalue()
    print()
    with open(f'{folder_export}/{name}.sc', 'wb') as fout:
        Console.info(locale.header_done)
        compressor = compression.Compressor()

        if use_lzham:
            Console.info(locale.compressing_with % 'LZHAM')
            fout.write(struct.pack('<4sBI', b'SCLZ', 18, len(sc)))
            compressed = compressor.compress(sc, 'sclz')

            fout.write(compressed)
        else:
            Console.info(locale.compressing_with % 'LZMA')
            compressed = compressor.compress(sc, 'sc')
            fout.write(compressed)
        Console.info(locale.compression_done)
        print()


def decode_sc(file_name, folder, sheet_image, check_lowres=True):
    decompressed = None

    with open(f'{folder}/{file_name}', 'rb') as fh:
        try:
            decompressor = compression.Decompressor()
            decompressed = decompressor.decompress(fh.read())
            signature = decompressor.get_signature()

            Console.info(locale.detected_comp % signature.upper())
        except Exception as e:
            Console.info(locale.try_error)

    reader = Reader(decompressed)
    data_length = len(decompressed)
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

    sheet_data = [SheetData() for x in range(sprite_globals.shape_count)]
    sprite_data = [SpriteData() for x in range(sprite_globals.shape_count)]

    reader.uint32()
    reader.byte()

    sprite_globals.export_count = reader.uint16()

    for i in range(sprite_globals.export_count):
        reader.uint16()

    for i in range(sprite_globals.export_count):
        reader.string()

    i = 1
    while data_length - reader.stream.tell():
        data_block_tag = '%02x' % reader.byte()
        data_block_size = reader.uint32()

        if data_block_tag in ['01', '18']:
            reader.byte()  # pixel_type

            sheet_data[offset_sheet].size = (reader.uint16(), reader.uint16())

            if check_lowres and sheet_image[offset_sheet].size != sheet_data[offset_sheet].size:
                i = 2

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

                    region.shape_points = [Point() for x in range(region.num_points)]
                    region.sheet_points = [Point() for x in range(region.num_points)]

                    for z in range(region.num_points):
                        region.shape_points[z].x = reader.int32()
                        region.shape_points[z].y = reader.int32()
                    for z in range(region.num_points):
                        region.sheet_points[z].x = int(
                            round(reader.uint16() * sheet_data[region.sheet_id].size[0] / 65535) / i
                        )
                        region.sheet_points[z].y = int(
                            round(reader.uint16() * sheet_data[region.sheet_id].size[1] / 65535) / i
                        )
                sprite_data[offset_shape].regions.append(region)

            reader.uint32()
            reader.byte()

            offset_shape += 1
            continue
        elif data_block_tag == '08':  # Matrix
            [reader.int32() for i in range(6)]
            continue
        elif data_block_tag == '0c':  # Animation
            reader.uint16()
            reader.byte()
            reader.uint16()

            cnt1 = reader.int32()

            for i in range(cnt1):
                reader.uint16()
                reader.uint16()
                reader.uint16()

            cnt2 = reader.uint16()

            for i in range(cnt2):
                reader.uint16()

            for i in range(cnt2):
                reader.byte()

            for i in range(cnt2):
                reader.string()

            while True:
                inline_data_type = reader.ubyte()
                reader.ubyte()  # data_length

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
        else:
            reader.stream.read(data_block_size)

    for shape_index in range(sprite_globals.shape_count):
        for region_index in range(len(sprite_data[shape_index].regions)):
            region = sprite_data[shape_index].regions[region_index]

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

                sheetpoint = region.sheet_points[z]

                tmp_x, tmp_y = sheetpoint.position

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

            sprite_data[shape_index].regions[region_index] = region

    return sprite_globals, sprite_data, sheet_data


def cut_sprites(sprite_globals, sprite_data, sheet_data, sheet_image, xcod, folder_export):
    xcod.write(struct.pack('>H', sprite_globals.shape_count))

    for x in range(sprite_globals.shape_count):
        xcod.write(struct.pack('>H', len(sprite_data[x].regions)))

        Console.progress_bar(locale.cut_sprites % (x + 1, sprite_globals.shape_count), x, sprite_globals.shape_count)

        for region_index in range(len(sprite_data[x].regions)):
            region = sprite_data[x].regions[region_index]
            polygon = [region.sheet_points[z].position for z in range(region.num_points)]

            xcod.write(
                struct.pack(
                    '>2B2H',
                    region.sheet_id,
                    region.num_points,
                    *sheet_data[region.sheet_id].size
                ) + b''.join(struct.pack('>2H', *i) for i in polygon) +
                struct.pack('?B', region.mirroring, region.rotation // 90)
            )

            img_mask = Image.new('L', sheet_data[region.sheet_id].size, 0)
            ImageDraw.Draw(img_mask).polygon(polygon, fill=255)
            bbox = img_mask.getbbox()
            if not bbox:
                continue

            region_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])
            tmp_region = Image.new('RGBA', region_size, None)

            tmp_region.paste(sheet_image[region.sheet_id].crop(bbox), None, img_mask.crop(bbox))
            if region.mirroring:
                tmp_region = tmp_region.transform(region_size, Image.EXTENT, (region_size[0], 0, 0, region_size[1]))

            tmp_region.rotate(region.rotation, expand=True) \
                .save(f'{folder_export}/{x}_{region_index}.png')
    print()


def place_sprites(xcod, folder):
    xcod = open(xcod, 'rb')
    files = os.listdir(folder)

    xcod.read(4)
    use_lzham, pictures_count = struct.unpack('2B', xcod.read(2))
    sheet_image = []
    sheet_image_data = {'use_lzham': use_lzham, 'data': []}
    for i in range(pictures_count):
        file_type, sub_type, width, height = struct.unpack('>BBHH', xcod.read(6))
        sheet_image.append(Image.new('RGBA', (width, height)))
        sheet_image_data['data'].append({'file_type': file_type, 'sub_type': sub_type})

    shape_count, = struct.unpack('>H', xcod.read(2))

    for x in range(shape_count):

        Console.progress_bar(locale.place_sprites % (x + 1, shape_count), x, shape_count)

        regions_count, = struct.unpack('>H', xcod.read(2))

        for y in range(regions_count):

            sheet_id, num_points, x1, y1 = struct.unpack('>2B2H', xcod.read(6))
            polygon = [unpack('>2H', xcod.read(4)) for unpack in [struct.unpack] * num_points]
            mirroring, rotation = struct.unpack('?B', xcod.read(2))
            rotation *= 90

            if f'{x}_{y}.png' not in files:
                continue

            tmp_region = Image.open(f'{folder}/{x}_{y}.png') \
                .convert('RGBA') \
                .rotate(360 - rotation, expand=True)

            img_mask = Image.new('L', (x1, y1), 0)
            ImageDraw.Draw(img_mask).polygon(polygon, fill=255)
            bbox = img_mask.getbbox()
            if not bbox:
                continue

            region_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])

            if mirroring:
                tmp_region = tmp_region.transform(region_size, Image.EXTENT,
                                                  (tmp_region.width, 0, 0, tmp_region.height))

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

    region.mirroring = 0 if (shape_orientation == sheet_orientation) else 1

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
