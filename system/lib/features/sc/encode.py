import os
from pathlib import Path

from loguru import logger
from PIL import Image

from system.lib.features.place_sprites import place_sprites
from system.lib.features.sc import compile_sc
from system.lib.xcod import parse_info
from system.localization import locale

OUT_COMPRESSED_PATH = Path("./SC/Out-Compressed")
IN_DECOMPRESSED_PATH = Path("./SC/In-Decompressed")
IN_SPRITES_PATH = Path("./SC/In-Sprites/")


def encode_textures_only():
    input_folder = IN_DECOMPRESSED_PATH
    output_folder = OUT_COMPRESSED_PATH

    for folder in os.listdir(input_folder):
        textures_input_folder = input_folder / folder

        if not os.path.isdir(textures_input_folder):
            continue

        xcod_path = _ensure_metadata_exists(textures_input_folder, folder)
        if xcod_path is None:
            continue

        file_info = parse_info(xcod_path, False)
        sheets = _load_sheets(textures_input_folder)
        compile_sc(output_folder, file_info, sheets)


def collect_objects_and_encode(overwrite: bool = False) -> None:
    input_folder = IN_SPRITES_PATH
    output_folder = OUT_COMPRESSED_PATH

    for folder in os.listdir(input_folder):
        objects_input_folder = input_folder / folder

        if not os.path.isdir(objects_input_folder):
            continue

        xcod_path = _ensure_metadata_exists(objects_input_folder, folder)
        if xcod_path is None:
            continue

        file_info = parse_info(xcod_path, True)
        sheets = place_sprites(file_info, objects_input_folder, overwrite)
        compile_sc(output_folder, file_info, sheets)


def _ensure_metadata_exists(input_folder: Path, file: str) -> Path | None:
    metadata_file_name = f"{file}.xcod"
    metadata_file_path = input_folder / metadata_file_name

    if not os.path.exists(metadata_file_path):
        logger.error(locale.not_found % metadata_file_name)
        print()
        return None

    return metadata_file_path


def _load_sheets(input_folder: Path) -> list[Image.Image]:
    files = []
    for i in os.listdir(input_folder):
        if i.endswith(".png"):
            files.append(i)
    files.sort()

    if not files:
        raise RuntimeError(locale.dir_empty % input_folder.name)
    return [Image.open(input_folder / file) for file in files]
