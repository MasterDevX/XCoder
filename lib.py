from system.bytestream import Reader, Writer
from system.localization import Locale
from system.lib.console import Console
from system.lib.logger import Logger
from system.lib.objects import *

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
    
    from sc_compression.decompressor import Decompressor
    from sc_compression.compressor import Compressor
    from sc_compression.signatures import Signatures

    from PIL import Image, ImageDraw
except Exception as e:
    logger.write(e)

lzham_path = r'system\lzham'

is_windows = platform.system() == 'Windows'
null_output = f'{"nul" if is_windows else "/dev/null"} 2>&1'

locale = Locale()
config_path = './system/config.json'

config = {'inited': False, 'version': None, 'lang': 'en-EU', 'updated': True, 'last_update': -1}
if os.path.isfile(config_path):
    try:
        config = json.load(open(config_path))
    except Exception as e:
        logger.write(e)
json.dump(config, open(config_path, 'w'))
locale.load_from(config['lang'])


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


def load_locale():
    config.update(json.load(open(config_path)))
    locale.load_from(config['lang'])


def make_dirs(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def specialize_print(console_width, first_string, second_string):
    print(first_string + (' ' * (console_width // 2 - len(first_string)) + ': ' + second_string))


def colored_print(text, color=None):
    if color is None:
        color = colorama.Back.GREEN
    return print(color + colorama.Fore.BLACK + text + ' ' * (10 - len(text)) + colorama.Style.RESET_ALL)


def decompress(buffer: bytes) -> (bytes, int):
    decompressor = Decompressor()
    decompressed = decompressor.decompress(buffer)

    return decompressed, decompressor.signatures.last_signature


def compress(buffer: bytes, signature: int) -> bytes:
    compressor = Compressor()
    compressed = compressor.compress(buffer, signature)

    return compressed


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
    print('github.com/Vorono4ka/XCoder'.center(console_width))
    print(console_width * '-')

    colored_print(locale.sc)
    specialize_print(console_width, ' 1   ' + locale.decode_sc, locale.decode_sc_desc)
    specialize_print(console_width, ' 2   ' + locale.encode_sc, locale.decode_sc_desc)
    specialize_print(console_width, ' 3   ' + locale.decode_by_parts, locale.experimental)
    specialize_print(console_width, ' 4   ' + locale.encode_by_parts, locale.experimental)
    specialize_print(console_width, ' 5   ' + locale.decompress_csv, locale.experimental)
    specialize_print(console_width, ' 6   ' + locale.compress_csv, locale.experimental)
    print(console_width * '-')

    colored_print(locale.other_features)
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
        json.dump(config, open(config_path, 'w'))
        input(locale.to_continue)

        config.update({'last_update': int(time.time())})
        json.dump(config, open(config_path, 'w'))
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

        if use_lzham:
            Console.info(locale.compressing_with % 'LZHAM')
            file_out.write(struct.pack('<4sBI', b'SCLZ', 18, len(buffer)))
            compressed = compress(buffer, Signatures.SCLZ)

            file_out.write(compressed)
        else:
            Console.info(locale.compressing_with % 'ZSTD')
            compressed = compress(buffer, Signatures.SC)
            file_out.write(compressed)
        Console.info(locale.compression_done)


def open_sc(input_filename: str):
    use_lzham = False

    Console.info(locale.collecting_inf)
    with open(input_filename, 'rb') as fh:
        try:
            decompressed, signature = decompress(fh.read())
            #
            # Console.info(locale.detected_comp % signature.upper())
            #
            if signature == Signatures.SCLZ:
                use_lzham = True
        except Exception:
            Console.info(locale.try_error)

        fh.close()

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

        Console.info(locale.about_sc % (name + '_' * picture_index, pixel_type, width, height))

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

        self.sprite_globals = SpriteGlobals()
        self.sprite_data = []
        self.exports = {}

        self.shapes = {}
        self.movie_clips = {}
        self.textures = []

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
            self.sprite_globals.shape_count = self.reader.uint16()
            self.sprite_globals.movie_clips_count = self.reader.uint16()
            self.sprite_globals.textures_count = self.reader.uint16()
            self.sprite_globals.text_field_count = self.reader.uint16()
            self.sprite_globals.matrix_count = self.reader.uint16()
            self.sprite_globals.color_transformation_count = self.reader.uint16()
    
            self.textures = [_class() for _class in [SWFTexture] * self.sprite_globals.textures_count]
            self.sprite_data = [_class() for _class in [SpriteData] * self.sprite_globals.shape_count]
    
            self.reader.uint32()
            self.reader.byte()
    
            self.sprite_globals.export_count = self.reader.uint16()

            self.exports = [_function() for _function in [self.reader.uint16] * self.sprite_globals.export_count]
            self.exports = {export_id: self.reader.string() for export_id in self.exports}
    
            has_texture = self.load_tags()
        
            for movieclip in self.movie_clips.values():
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
        print()
        return has_texture, use_lzham

    def load_tags(self):
        has_texture = True
    
        offset_shape = 0
        texture_id = 0
    
        while True:
            tag = self.reader.byte()
            length = self.reader.uint32()
    
            if tag == 0:
                return has_texture
            elif tag in [1, 16, 28, 29, 34, 19, 24, 27]:
                if len(self.textures) <= texture_id:
                    # Костыль, такого в либе нет, но ради фичи с вытаскиванием только текстур, можно и добавить)
                    self.textures.append(SWFTexture())
                texture = self.textures[texture_id]
                texture.pixel_type = self.reader.byte()  # pixel_type
                texture.width, texture.height = (self.reader.uint16(), self.reader.uint16())

                if has_texture:
                    Console.info(locale.about_sc % (self.filename, texture.pixel_type, texture.width, texture.height))

                    img = Image.new(pixel_type2str(texture.pixel_type), (texture.width, texture.height))
                    pixels = []

                    bytes2rgba(self.reader, texture.pixel_type, img, pixels)

                    if tag in (27, 28):
                        print()
                        join_image(img, pixels)
                        print()
                    print()

                    self.xcod_writer.ubyte(tag)
                    self.xcod_writer.ubyte(texture.pixel_type)
                    self.xcod_writer.uint16(texture.width)
                    self.xcod_writer.uint16(texture.height)
                    texture.image = img

                self.textures[texture_id] = texture
                texture_id += 1
                continue
            elif tag in [2, 18]:
                self.sprite_data[offset_shape].id = self.reader.uint16()
    
                regions_count = self.reader.uint16()
                self.reader.uint16()  # point_count
    
                for region_index in range(regions_count):
                    region = Region()
    
                    tag = self.reader.byte()
    
                    if tag == 22:
                        self.reader.uint32()  # data_block_length
                        region.sheet_id = self.reader.byte()
    
                        region.num_points = self.reader.byte()
    
                        region.shape_points = [_class() for _class in [Point] * region.num_points]
                        region.sheet_points = [_class() for _class in [Point] * region.num_points]
    
                        for z in range(region.num_points):
                            region.shape_points[z].x = self.reader.int32()
                            region.shape_points[z].y = self.reader.int32()
                        for z in range(region.num_points):
                            w, h = [self.reader.uint16() * self.textures[region.sheet_id].width / 0xffff,
                                    self.reader.uint16() * self.textures[region.sheet_id].height / 0xffff]
                            x, y = [ceil(i) for i in (w, h)]
                            if int(w) == x:
                                x += 1
                            if int(h) == y:
                                y += 1
    
                            region.sheet_points[z].position = (x, y)
                    self.sprite_data[offset_shape].regions.append(region)
                self.shapes[self.sprite_data[offset_shape].id] = self.sprite_data[offset_shape]
    
                self.reader.uint32()
                self.reader.byte()
    
                offset_shape += 1
                continue
            elif tag in [3, 10, 12, 14, 35]:  # MovieClip
                movie_clip_id = self.reader.uint16()
    
                movieclip = self.movie_clips.get(movie_clip_id)
                if not movieclip:
                    movieclip = MovieClip()
    
                movieclip.export_name = self.get_export_by_id(movie_clip_id)
                movieclip.fps = self.reader.byte()
                movieclip.frames_count = self.reader.uint16()
    
                cnt1 = self.reader.uint32()
    
                for i in range(cnt1):
                    self.reader.uint16()
                    self.reader.uint16()
                    self.reader.uint16()
    
                cnt2 = self.reader.uint16()
    
                for i in range(cnt2):
                    bind_id = self.reader.uint16()  # bind_id
                    if bind_id in self.shapes:
                        movieclip.shapes.append(self.shapes[bind_id])
    
                for i in range(cnt2):
                    blend = self.reader.byte()  # blend
                    movieclip.blends.append(blend)
    
                for i in range(cnt2):
                    self.reader.string()  # bind_name
    
                while True:
                    inline_data_type = self.reader.ubyte()
                    self.reader.int32()  # data_length
    
                    if inline_data_type == 0:
                        break
    
                    if inline_data_type == 11:
                        self.reader.int16()  # frame_id
                        self.reader.string()  # frame_name
                    elif inline_data_type == 31:
                        for x in range(4):
                            self.reader.ubyte()
                            self.reader.ubyte()
                            self.reader.string()
                            self.reader.string()
                self.movie_clips[movie_clip_id] = movieclip
                continue
            elif tag == 8:  # Matrix
                self.reader.int32()
                self.reader.int32()
                self.reader.int32()
                self.reader.int32()
                self.reader.int32()
                self.reader.int32()
                continue
            elif tag == 26:
                has_texture = False
                continue
            else:
                self.reader.read(length)


def cut_sprites(movie_clips, textures, xcod, folder_export):
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

        n = movieclip.export_name.encode()
        xcod.write(struct.pack('B', len(n)) + n + struct.pack('>H', len(movieclip.shapes)))

        for shape_index in range(len(movieclip.shapes)):
            shape = movieclip.shapes[shape_index]
            xcod.write(struct.pack('>H', len(shape.regions)))
            for y in range(len(shape.regions)):
                region = shape.regions[y]

                polygon = [region.sheet_points[z].position for z in range(region.num_points)]

                texture = textures[region.sheet_id]
                xcod.write(struct.pack('>2B2H', region.sheet_id, region.num_points, texture.width, texture.height) +
                           b''.join(struct.pack('>2H', *i) for i in polygon) +
                           struct.pack('?B', region.mirroring, region.rotation // 90))

                img_mask = Image.new('L', (texture.width, texture.height), 0)
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

                region_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])

                tmp_region = Image.new('RGBA', region_size)
                tmp_region.paste(texture.image.crop(bbox), (0, 0), img_mask.crop(bbox))
                if region.mirroring:
                    tmp_region = tmp_region.transform(region_size, Image.EXTENT, (region_size[0], 0, 0, region_size[1]))

                tmp_region.rotate(region.rotation, expand=True) \
                    .save(f'{folder_export}/{movieclip.export_name}_{shape_index}_{y}.png')
    print()


def place_sprites(xcod, folder, overwrite=False):
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
        sheet_image_data['data'].append({'file_type': file_type, 'pixel_type': sub_type})

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

                if f'{clip_name}_{shape_index}_{region_index}.png' not in files:
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
                if clip_name == '_movieclip_69':
                    tmp_region.show()
                    print()

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
