import os

from PIL import Image, ImageDraw

from system.bytestream import Reader
from system.lib import Console
from system.localization import locale


def place_sprites(xcod, folder, overwrite=False):
    xcod = Reader(open(xcod, 'rb').read(), 'big')
    files = os.listdir(f'{folder}{"/overwrite" if overwrite else ""}')
    tex = os.listdir(f'{folder}/textures')

    xcod.read(4)
    use_lzham, pictures_count = xcod.read_ubyte(), xcod.read_ubyte()
    sheet_image = []
    sheet_image_data = {'use_lzham': use_lzham, 'data': []}
    for i in range(pictures_count):
        file_type, sub_type, width, height = xcod.read_ubyte(), \
                                             xcod.read_ubyte(), \
                                             xcod.read_uint16(), \
                                             xcod.read_uint16()
        sheet_image.append(
            Image.open(f'{folder}/textures/{tex[i]}')
            if overwrite else
            Image.new('RGBA', (width, height)))
        sheet_image_data['data'].append({'file_type': file_type, 'pixel_type': sub_type})

    shapes_count = xcod.read_uint16()
    for shape_index in range(shapes_count):
        Console.progress_bar(locale.place_sprites_process % (shape_index + 1, shapes_count), shape_index, shapes_count)
        shape_id = xcod.read_uint16()
        regions_count = xcod.read_uint16()

        for region_index in range(regions_count):
            texture_id, points_count = xcod.read_ubyte(), xcod.read_ubyte()
            texture_width, texture_height = sheet_image[texture_id].width, sheet_image[texture_id].height
            polygon = [(xcod.read_uint16(), xcod.read_uint16()) for _ in range(points_count)]
            mirroring, rotation = xcod.read_ubyte() == 1, xcod.read_ubyte() * 90

            filename = f'shape_{shape_id}_{region_index}.png'
            if filename not in files:
                continue

            tmp_region = Image.open(
                f'{folder}{"/overwrite" if overwrite else ""}/{filename}'
            ) \
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
