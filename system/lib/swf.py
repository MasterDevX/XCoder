import os
from typing import List

from loguru import logger

from system.bytestream import Writer, Reader
from system.lib.features.files import open_sc

from system.lib.matrices.matrix_bank import MatrixBank
from system.lib.objects import Shape, MovieClip, SWFTexture
from system.localization import locale

DEFAULT_HIGHRES_SUFFIX = "_highres"
DEFAULT_LOWRES_SUFFIX = "_lowres"


class SupercellSWF:
    TEXTURES_TAGS = (1, 16, 28, 29, 34, 19, 24, 27)
    SHAPES_TAGS = (2, 18)
    MOVIE_CLIPS_TAGS = (3, 10, 12, 14, 35)

    TEXTURE_EXTENSION = "_tex.sc"

    def __init__(self):
        self.filename: str or None = None
        self.reader: Reader or None = None

        self.use_lowres_texture: bool = False
        self.use_uncommon_texture: bool = False
        self.uncommon_texture_path: str or None = None

        self.shapes: List[Shape] = []
        self.movie_clips: List[MovieClip] = []
        self.textures: List[SWFTexture] = []

        self.xcod_writer = Writer("big")

        self._filepath: str or None = None

        self._lowres_suffix: str = DEFAULT_LOWRES_SUFFIX
        self._highres_suffix: str = DEFAULT_HIGHRES_SUFFIX

        self._shape_count: int
        self._movie_clip_count: int
        self._texture_count: int
        self._text_field_count: int

        self._export_count: int
        self._export_ids: List[int] = []
        self._export_names: List[str] = []

        self._matrix_banks: List[MatrixBank] = []
        self._matrix_bank: MatrixBank

    def load(self, filepath: str) -> (bool, bool):
        self._filepath = filepath

        texture_loaded, use_lzham = self._load_internal(
            filepath, filepath.endswith("_tex.sc")
        )

        if not texture_loaded:
            if self.use_uncommon_texture:
                texture_loaded, use_lzham = self._load_internal(
                    self.uncommon_texture_path, True
                )
            else:
                texture_path = self._filepath[:-3] + SupercellSWF.TEXTURE_EXTENSION
                texture_loaded, use_lzham = self._load_internal(texture_path, True)

        return texture_loaded, use_lzham

    def _load_internal(self, filepath: str, is_texture: bool) -> (bool, bool):
        self.filename = os.path.basename(filepath)

        decompressed_data, use_lzham = open_sc(filepath)
        self.reader = Reader(decompressed_data)
        del decompressed_data

        if not is_texture:
            self._shape_count = self.reader.read_ushort()
            self._movie_clip_count = self.reader.read_ushort()
            self._texture_count = self.reader.read_ushort()
            self._text_field_count = self.reader.read_ushort()

            matrix_count = self.reader.read_ushort()
            color_transformation_count = self.reader.read_ushort()

            self._matrix_bank = MatrixBank()
            self._matrix_bank.init(matrix_count, color_transformation_count)
            self._matrix_banks.append(self._matrix_bank)

            self.shapes = [_class() for _class in [Shape] * self._shape_count]
            self.movie_clips = [
                _class() for _class in [MovieClip] * self._movie_clip_count
            ]
            self.textures = [_class() for _class in [SWFTexture] * self._texture_count]

            self.reader.read_uint()
            self.reader.read_char()

            self._export_count = self.reader.read_ushort()

            self._export_ids = []
            for _ in range(self._export_count):
                self._export_ids.append(self.reader.read_ushort())

            self._export_names = []
            for _ in range(self._export_count):
                self._export_names.append(self.reader.read_string())

        loaded = self._load_tags()

        for i in range(self._export_count):
            export_id = self._export_ids[i]
            export_name = self._export_names[i]

            movie_clip = self.get_display_object(
                export_id, export_name, raise_error=True
            )
            movie_clip.export_name = export_name

        print()
        return loaded, use_lzham

    def _load_tags(self):
        has_texture = True

        texture_id = 0
        movie_clips_loaded = 0
        shapes_loaded = 0
        matrices_loaded = 0

        while True:
            tag = self.reader.read_char()
            length = self.reader.read_uint()

            if tag == 0:
                return has_texture
            elif tag in SupercellSWF.TEXTURES_TAGS:
                texture = self.textures[texture_id]
                texture.load(self, tag, has_texture)

                if has_texture:
                    logger.info(
                        locale.about_sc
                        % (
                            self.filename,
                            texture_id,
                            texture.pixel_type,
                            texture.width,
                            texture.height,
                        )
                    )
                    print()

                    self.xcod_writer.write_ubyte(tag)
                    self.xcod_writer.write_ubyte(texture.pixel_type)
                    self.xcod_writer.write_uint16(texture.width)
                    self.xcod_writer.write_uint16(texture.height)
                self.textures[texture_id] = texture
                texture_id += 1
            elif tag in SupercellSWF.SHAPES_TAGS:
                self.shapes[shapes_loaded].load(self, tag)
                shapes_loaded += 1
            elif tag in SupercellSWF.MOVIE_CLIPS_TAGS:  # MovieClip
                self.movie_clips[movie_clips_loaded].load(self, tag)
                movie_clips_loaded += 1
            elif tag == 8 or tag == 36:  # Matrix
                self._matrix_bank.get_matrix(matrices_loaded).load(self.reader, tag)
                matrices_loaded += 1
            elif tag == 26:
                has_texture = False
            elif tag == 30:
                self.use_uncommon_texture = True
                highres_texture_path = (
                    self._filepath[:-3]
                    + self._highres_suffix
                    + SupercellSWF.TEXTURE_EXTENSION
                )
                lowres_texture_path = (
                    self._filepath[:-3]
                    + self._lowres_suffix
                    + SupercellSWF.TEXTURE_EXTENSION
                )

                self.uncommon_texture_path = highres_texture_path
                if not os.path.exists(highres_texture_path) and os.path.exists(
                    lowres_texture_path
                ):
                    self.uncommon_texture_path = lowres_texture_path
                    self.use_lowres_texture = True
            elif tag == 42:
                matrix_count = self.reader.read_ushort()
                color_transformation_count = self.reader.read_ushort()

                self._matrix_bank = MatrixBank()
                self._matrix_bank.init(matrix_count, color_transformation_count)
                self._matrix_banks.append(self._matrix_bank)

                matrices_loaded = 0
            else:
                self.reader.read(length)

    def get_display_object(
        self, target_id: int, name: str or None = None, *, raise_error: bool = False
    ):
        for shape in self.shapes:
            if shape.id == target_id:
                return shape

        for movie_clip in self.movie_clips:
            if movie_clip.id == target_id:
                return movie_clip

        if raise_error:
            exception_text = (
                f"Unable to find some DisplayObject id {target_id}, {self.filename}"
            )
            if name is not None:
                exception_text += f" needed by export name {name}"

            raise ValueError(exception_text)
        return None

    def get_matrix_bank(self, index: int) -> MatrixBank:
        return self._matrix_banks[index]
