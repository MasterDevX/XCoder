import os

from PIL import Image, ImageDraw

from system.lib import Console
from system.lib.images import pixel_type2str
from system.lib.xcod import parse_info, FileInfo
from system.localization import locale


def place_sprites(xcod_path: str, folder: str, overwrite: bool = False) -> (list, FileInfo):
    file_info, xcod = parse_info(xcod_path)

    files_to_overwrite = os.listdir(f'{folder}{"/overwrite" if overwrite else ""}')
    texture_files = os.listdir(f'{folder}/textures')

    sheets = []
    for i in range(len(file_info.sheets)):
        sheet_info = file_info.sheets[i]

        sheets.append(
            Image.open(f'{folder}/textures/{texture_files[i]}')
            if overwrite else
            Image.new(pixel_type2str(sheet_info.pixel_type), sheet_info.size)
        )

    shapes_count = xcod.read_uint16()
    for shape_index in range(shapes_count):
        Console.progress_bar(locale.place_sprites_process % (shape_index + 1, shapes_count), shape_index, shapes_count)
        shape_id = xcod.read_uint16()

        regions_count = xcod.read_uint16()
        for region_index in range(regions_count):
            texture_id, points_count = xcod.read_ubyte(), xcod.read_ubyte()
            texture_width, texture_height = sheets[texture_id].width, sheets[texture_id].height
            polygon = [(xcod.read_uint16(), xcod.read_uint16()) for _ in range(points_count)]
            mirroring, rotation = xcod.read_ubyte() == 1, xcod.read_ubyte() * 90

            filename = f'shape_{shape_id}_{region_index}.png'
            if filename not in files_to_overwrite:
                continue

            tmp_region = Image.open(
                f'{folder}{"/overwrite" if overwrite else ""}/{filename}'
            ).convert('RGBA').rotate(360 - rotation, expand=True)

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

            left, top, right, bottom = bbox
            if right - left - 1:
                right -= 1
            if bottom - top - 1:
                bottom -= 1

            bbox = left, top, right, bottom

            width = right - left
            height = bottom - top
            region_size = width, height
            tmp_region = tmp_region.resize(region_size, Image.ANTIALIAS)

            if mirroring:
                tmp_region = tmp_region.transform(region_size, Image.EXTENT,
                                                  (tmp_region.width, 0, 0, tmp_region.height))

            sheets[texture_id].paste(Image.new('RGBA', region_size), (left, top), img_mask.crop(bbox))
            sheets[texture_id].paste(tmp_region, (left, top), tmp_region)
    print()

    return sheets, file_info
