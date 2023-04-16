import os
from pathlib import Path
from typing import List

from PIL import Image, ImageDraw

from system.lib import Console
from system.lib.helper import get_sides, get_size
from system.lib.images import get_format_by_pixel_type
from system.lib.xcod import FileInfo
from system.localization import locale

MASK_COLOR = 255


def place_sprites(
    file_info: FileInfo, folder: Path, overwrite: bool = False
) -> List[Image.Image]:
    files_to_overwrite = os.listdir(folder / ("overwrite" if overwrite else ""))
    texture_files = os.listdir(folder / "textures")

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

    shapes_count = len(file_info.shapes)
    for shape_index, shape_info in enumerate(file_info.shapes):
        Console.progress_bar(
            locale.place_sprites_process % (shape_index + 1, shapes_count),
            shape_index,
            shapes_count,
        )

        for region_index, region_info in enumerate(shape_info.regions):
            texture_size = (
                sheets[region_info.texture_id].width,
                sheets[region_info.texture_id].height,
            )

            filename = f"shape_{shape_info.id}_{region_index}.png"
            if filename not in files_to_overwrite:
                continue

            img_mask = Image.new("L", texture_size, 0)
            ImageDraw.Draw(img_mask).polygon(region_info.points, fill=MASK_COLOR)
            bbox = img_mask.getbbox()

            if not bbox:
                min_x = min(i[0] for i in region_info.points)
                min_y = min(i[1] for i in region_info.points)
                max_x = max(i[0] for i in region_info.points)
                max_y = max(i[1] for i in region_info.points)

                if max_y - min_y != 0:
                    for _y in range(max_y - min_y):
                        img_mask.putpixel((max_x - 1, min_y + _y - 1), MASK_COLOR)

                elif max_x - min_x != 0:
                    for _x in range(max_x - min_x):
                        img_mask.putpixel((min_x + _x - 1, max_y - 1), MASK_COLOR)
                else:
                    img_mask.putpixel((max_x - 1, max_y - 1), MASK_COLOR)

            left, top, right, bottom = get_sides(region_info.points)
            if left == right:
                right += 1
            if top == bottom:
                bottom += 1

            width, height = get_size(left, top, right, bottom)
            left = int(left)
            top = int(top)

            bbox = int(left), int(top), int(right), int(bottom)

            tmp_region = Image.open(
                f'{folder}{"/overwrite" if overwrite else ""}/{filename}'
            ).convert("RGBA")
            if region_info.is_mirrored:
                tmp_region = tmp_region.transpose(Image.FLIP_LEFT_RIGHT)
            tmp_region = tmp_region.rotate(region_info.rotation, expand=True)
            tmp_region = tmp_region.resize((width, height), Image.ANTIALIAS)

            sheets[region_info.texture_id].paste(
                Image.new("RGBA", (width, height)), (left, top), img_mask.crop(bbox)
            )
            sheets[region_info.texture_id].paste(tmp_region, (left, top), tmp_region)
    print()

    return sheets
