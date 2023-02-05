import os
from typing import List, Tuple

from PIL import Image, ImageDraw

from system.lib import Console
from system.lib.helper import get_sides, get_size
from system.lib.images import get_format_by_pixel_type
from system.lib.xcod import FileInfo, parse_info
from system.localization import locale


def place_sprites(
    xcod_path: str, folder: str, overwrite: bool = False
) -> Tuple[List[Image.Image], FileInfo]:
    file_info, xcod = parse_info(xcod_path)

    files_to_overwrite = os.listdir(f'{folder}{"/overwrite" if overwrite else ""}')
    texture_files = os.listdir(f"{folder}/textures")

    sheets = []
    for i in range(len(file_info.sheets)):
        sheet_info = file_info.sheets[i]

        sheets.append(
            Image.open(f"{folder}/textures/{texture_files[i]}")
            if overwrite
            else Image.new(
                get_format_by_pixel_type(sheet_info.pixel_type), sheet_info.size
            )
        )

    shapes_count = xcod.read_ushort()
    for shape_index in range(shapes_count):
        Console.progress_bar(
            locale.place_sprites_process % (shape_index + 1, shapes_count),
            shape_index,
            shapes_count,
        )
        shape_id = xcod.read_ushort()

        regions_count = xcod.read_ushort()
        for region_index in range(regions_count):
            texture_id, points_count = xcod.read_uchar(), xcod.read_uchar()
            texture_width, texture_height = (
                sheets[texture_id].width,
                sheets[texture_id].height,
            )
            points = [
                (xcod.read_ushort(), xcod.read_ushort()) for _ in range(points_count)
            ]
            mirroring, rotation = xcod.read_uchar() == 1, xcod.read_char() * 90

            filename = f"shape_{shape_id}_{region_index}.png"
            if filename not in files_to_overwrite:
                continue

            img_mask = Image.new("L", (texture_width, texture_height), 0)
            color = 255
            ImageDraw.Draw(img_mask).polygon(points, fill=color)
            bbox = img_mask.getbbox()

            if not bbox:
                min_x = min(i[0] for i in points)
                min_y = min(i[1] for i in points)
                max_x = max(i[0] for i in points)
                max_y = max(i[1] for i in points)

                if max_y - min_y != 0:
                    for _y in range(max_y - min_y):
                        img_mask.putpixel((max_x - 1, min_y + _y - 1), color)

                elif max_x - min_x != 0:
                    for _x in range(max_x - min_x):
                        img_mask.putpixel((min_x + _x - 1, max_y - 1), color)
                else:
                    img_mask.putpixel((max_x - 1, max_y - 1), color)

            left, top, right, bottom = get_sides(points)
            if left == right:
                right += 1
            if top == bottom:
                bottom += 1

            width, height = get_size(left, top, right, bottom)

            bbox = int(left), int(top), int(right), int(bottom)

            tmp_region = Image.open(
                f'{folder}{"/overwrite" if overwrite else ""}/{filename}'
            ).convert("RGBA")
            if mirroring:
                tmp_region = tmp_region.transpose(Image.FLIP_LEFT_RIGHT)
            tmp_region = tmp_region.rotate(rotation, expand=True)
            tmp_region = tmp_region.resize((width, height), Image.ANTIALIAS)

            sheets[texture_id].paste(
                Image.new("RGBA", (width, height)), (left, top), img_mask.crop(bbox)
            )
            sheets[texture_id].paste(tmp_region, (left, top), tmp_region)
    print()

    return sheets, file_info
