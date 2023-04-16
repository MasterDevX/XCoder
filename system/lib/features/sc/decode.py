import os
import shutil
from pathlib import Path

from loguru import logger

from system.lib.features.cut_sprites import render_objects
from system.lib.swf import SupercellSWF
from system.localization import locale

IN_COMPRESSED_PATH = Path("./SC/In-Compressed")
OUT_DECOMPRESSED = Path("./SC/Out-Decompressed")
OUT_SPRITES_PATH = Path("./SC/Out-Sprites")


def decode_textures_only():
    input_folder = IN_COMPRESSED_PATH
    output_folder = OUT_DECOMPRESSED

    files = os.listdir(input_folder)
    for file in files:
        if not file.endswith("_tex.sc"):
            continue

        swf = SupercellSWF()
        base_name = os.path.basename(file).rsplit(".", 1)[0]
        try:
            texture_loaded, use_lzham = swf.load(f"{input_folder / file}")
            if not texture_loaded:
                logger.error(locale.not_found % f"{base_name}_tex.sc")
                continue

            base_name = get_file_basename(swf)

            objects_output_folder = _create_objects_output_folder(
                output_folder, base_name
            )

            _save_meta_file(
                swf, objects_output_folder, base_name.rstrip("_"), use_lzham
            )
            _save_textures(swf, objects_output_folder, base_name)
        except Exception as exception:
            logger.exception(
                locale.error
                % (
                    exception.__class__.__module__,
                    exception.__class__.__name__,
                    exception,
                )
            )

        print()


def decode_and_render_objects():
    input_folder = IN_COMPRESSED_PATH
    output_folder = OUT_SPRITES_PATH
    files = os.listdir(input_folder)

    for file in files:
        if file.endswith("_tex.sc"):
            continue

        try:
            base_name = os.path.basename(file).rsplit(".", 1)[0]

            swf = SupercellSWF()
            texture_loaded, use_lzham = swf.load(input_folder / file)
            if not texture_loaded:
                logger.error(locale.not_found % f"{base_name}_tex.sc")
                continue

            base_name = get_file_basename(swf)

            objects_output_folder = _create_objects_output_folder(
                output_folder, base_name
            )

            _save_textures(swf, objects_output_folder / "textures", base_name)
            render_objects(swf, objects_output_folder)
            _save_meta_file(swf, objects_output_folder, base_name, use_lzham)
        except Exception as exception:
            logger.exception(
                locale.error
                % (
                    exception.__class__.__module__,
                    exception.__class__.__name__,
                    exception,
                )
            )

        print()


def get_file_basename(swf: SupercellSWF):
    return os.path.basename(swf.filename).rsplit(".", 1)[0]


def _create_objects_output_folder(output_folder: Path, base_name: str) -> Path:
    objects_output_folder = output_folder / base_name
    if os.path.isdir(objects_output_folder):
        shutil.rmtree(objects_output_folder)
    os.mkdir(objects_output_folder)
    return objects_output_folder


def _save_textures(swf: SupercellSWF, textures_output: Path, base_name: str) -> None:
    os.makedirs(textures_output, exist_ok=True)
    for img_index in range(len(swf.textures)):
        filename = base_name + "_" * img_index
        swf.textures[img_index].image.save(textures_output / f"{filename}.png")


def _save_meta_file(
    swf: SupercellSWF, objects_output_folder: Path, base_name: str, use_lzham: bool
) -> None:
    with open(objects_output_folder / f"{base_name}.xcod", "wb") as xcod_file:
        xcod_file.write(b"XCOD")
        xcod_file.write(bool.to_bytes(use_lzham, 1, "big"))
        xcod_file.write(int.to_bytes(len(swf.textures), 1, "big"))
        xcod_file.write(swf.xcod_writer.getvalue())
