import math
import struct

from PIL import Image

from system.bytestream import Reader
from system.lib.console import Console
from system.localization import locale


def load_image_from_buffer(img):
    width, height = img.size
    img_loaded = img.load()

    with open('pixel_buffer', 'rb') as pixel_buffer:
        channels_count = int.from_bytes(pixel_buffer.read(1), 'little')

        for y in range(height):
            for x in range(width):
                img_loaded[x, y] = tuple(pixel_buffer.read(channels_count))


def join_image(img):
    with open('pixel_buffer', 'rb') as pixel_buffer:
        channels_count = int.from_bytes(pixel_buffer.read(1), 'little')

        width, height = img.size
        loaded_img = img.load()
        chunk_size = 32

        x_chunks_count = width // chunk_size
        y_chunks_count = height // chunk_size
        x_rest = width % chunk_size
        y_rest = height % chunk_size

        for y_chunk in range(y_chunks_count):
            for x_chunk in range(x_chunks_count):
                for y in range(chunk_size):
                    for x in range(chunk_size):
                        loaded_img[x_chunk * chunk_size + x, y_chunk * chunk_size + y] = tuple(
                            pixel_buffer.read(channels_count)
                        )

            for y in range(chunk_size):
                for x in range(x_rest):
                    loaded_img[(width - x_rest) + x, y_chunk * chunk_size + y] = tuple(
                        pixel_buffer.read(channels_count)
                    )
            Console.progress_bar(locale.join_pic, y_chunk, y_chunks_count)
        for x_chunk in range(x_chunks_count):
            for y in range(y_rest):
                for x in range(chunk_size):
                    loaded_img[x_chunk * chunk_size + x, (height - y_rest) + y] = tuple(
                        pixel_buffer.read(channels_count)
                    )

        for y in range(y_rest):
            for x in range(x_rest):
                loaded_img[x + (width - x_rest), y + (height - y_rest)] = tuple(pixel_buffer.read(channels_count))


def split_image(img: Image):
    def add_pixel(pixel: tuple):
        loaded_image[pixel_index % width, int(pixel_index / width)] = pixel

    width, height = img.size
    loaded_image = img.load()
    loaded_clone = img.copy().load()
    chunk_size = 32

    x_chunks_count = width // chunk_size
    y_chunks_count = height // chunk_size
    x_rest = width % chunk_size
    y_rest = height % chunk_size

    pixel_index = 0

    for y_chunk in range(y_chunks_count):
        for x_chunk in range(x_chunks_count):
            for y in range(chunk_size):
                for x in range(chunk_size):
                    add_pixel(loaded_clone[x + (x_chunk * chunk_size), y + (y_chunk * chunk_size)])
                    pixel_index += 1

        for y in range(chunk_size):
            for x in range(x_rest):
                add_pixel(loaded_clone[x + (width - x_rest), y + (y_chunk * chunk_size)])
                pixel_index += 1
        Console.progress_bar(locale.split_pic, y_chunk, y_chunks_count)

    for x_chunk in range(width // chunk_size):
        for y in range(y_rest):
            for x in range(chunk_size):
                add_pixel(loaded_clone[x + (x_chunk * chunk_size), y + (height - y_rest)])
                pixel_index += 1

    for y in range(y_rest):
        for x in range(x_rest):
            add_pixel(loaded_clone[x + (width - x_rest), y + (height - y_rest)])
            pixel_index += 1


def get_pixel_size(_type):
    if _type in (0, 1):
        return 4
    elif _type in (2, 3, 4, 6):
        return 2
    elif _type == 10:
        return 1
    raise Exception(locale.unk_type % _type)


def pixel_type2str(_type):
    if _type in range(4):
        return 'RGBA'
    elif _type == 4:
        return 'RGB'
    elif _type == 6:
        return 'LA'
    elif _type == 10:
        return 'L'

    raise Exception(locale.unk_type % _type)


def bytes2rgba(data: Reader, _type, img):
    read_pixel = None
    channels_count = 4
    if _type in (0, 1):
        def read_pixel():
            return data.read_ubyte(), data.read_ubyte(), data.read_ubyte(), data.read_ubyte()
    elif _type == 2:
        def read_pixel():
            p = data.read_uint16()
            return (p >> 12 & 15) << 4, (p >> 8 & 15) << 4, (p >> 4 & 15) << 4, (p >> 0 & 15) << 4
    elif _type == 3:
        def read_pixel():
            p = data.read_uint16()
            return (p >> 11 & 31) << 3, (p >> 6 & 31) << 3, (p >> 1 & 31) << 3, (p & 255) << 7
    elif _type == 4:
        channels_count = 3

        def read_pixel():
            p = data.read_uint16()
            return (p >> 11 & 31) << 3, (p >> 5 & 63) << 2, (p & 31) << 3
    elif _type == 6:
        channels_count = 2

        def read_pixel():
            return (data.read_ubyte(), data.read_ubyte())[::-1]
    elif _type == 10:
        channels_count = 1

        def read_pixel():
            return data.read_ubyte()

    if read_pixel is None:
        return

    with open('pixel_buffer', 'wb') as pixel_buffer:
        pixel_buffer.write(channels_count.to_bytes(1, 'little'))

        width, height = img.size
        point = -1
        for y in range(height):
            for x in range(width):
                pixel = read_pixel()
                for channel in pixel:
                    pixel_buffer.write(channel.to_bytes(1, 'little'))

            curr = Console.percent(y, height)
            if curr > point:
                Console.progress_bar(locale.crt_pic, y, height)
                point = curr
    print()


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


def transform_image(image, scale_x, scale_y, angle, x, y):
    im_orig = image
    image = Image.new('RGBA', im_orig.size, (255, 255, 255, 255))
    image.paste(im_orig)

    w, h = image.size
    angle = -angle

    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)

    scaled_w, scaled_h = w * scale_x, h * scale_y

    scaled_rotated_w = int(math.ceil(math.fabs(cos_theta * scaled_w) + math.fabs(sin_theta * scaled_h)))
    scaled_rotated_h = int(math.ceil(math.fabs(sin_theta * scaled_w) + math.fabs(cos_theta * scaled_h)))

    translated_w = int(math.ceil(scaled_rotated_w + math.fabs(x)))
    translated_h = int(math.ceil(scaled_rotated_h + math.fabs(y)))
    if x > 0:
        x = 0
    if y > 0:
        y = 0

    cx = w / 2.
    cy = h / 2.
    translate_x = scaled_rotated_w / 2. - x
    translate_y = scaled_rotated_h / 2. - y

    a = cos_theta / scale_x
    b = sin_theta / scale_x
    c = cx - translate_x * a - translate_y * b
    d = -sin_theta / scale_y
    e = cos_theta / scale_y
    f = cy - translate_x * d - translate_y * e

    return image.transform((translated_w, translated_h), Image.AFFINE, (a, b, c, d, e, f), resample=Image.BILINEAR)


def translate_image(image, x, y):
    w, h = image.size

    translated_w = int(math.ceil(w + math.fabs(x)))
    translated_h = int(math.ceil(h + math.fabs(y)))
    if x > 0:
        x = 0
    if y > 0:
        y = 0

    return image.transform((translated_w, translated_h), Image.AFFINE, (1, 0, -x, 0, 1, -y), resample=Image.BILINEAR)


def transform_image_by_matrix(image, matrix: list or tuple):
    scale_x, rotation_x, x = matrix[:3]
    rotation_y, scale_y, y = matrix[3:]
    return transform_image(image, scale_x, scale_y, math.atan2(rotation_x, rotation_y), x, y)


if __name__ == '__main__':
    transform_image_by_matrix(
        Image.open('../../test_0.png'),
        [1.0458984375, 0.0, -127.65,
         0.0, 1.0458984375, -700.]
    ).show()
    input()
