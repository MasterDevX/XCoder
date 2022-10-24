import os

from loguru import logger

from system.bytestream import Writer, Reader
from system.lib.features.files import open_sc
from system.lib.objects.movieclip import MovieClip
from system.lib.objects.shape import Shape
from system.lib.objects.texture import SWFTexture
from system.localization import locale


class SupercellSWF:
    TEXTURES_TAGS = (1, 16, 28, 29, 34, 19, 24, 27)
    SHAPES_TAGS = (2, 18)
    MOVIE_CLIPS_TAGS = (3, 10, 12, 14, 35)

    TEXTURE_EXTENSION = '_tex.sc'

    def __init__(self):
        self.filepath = None
        self.filename = None
        self.reader = None

        self.use_lowres_texture = False
        self.use_uncommon_texture = False
        self.uncommon_texture_path = None

        self.lowres_suffix = '_lowres'
        self.highres_suffix = '_highres'

        self.shape_count = 0
        self.movie_clips_count = 0
        self.textures_count = 0
        self.text_field_count = 0
        self.matrix_count = 0
        self.color_transformation_count = 0

        self.export_count = 0

        self.exports = {}

        self.shapes = []
        self.movie_clips = []
        self.textures = []

        self.matrices = []

        self.xcod_writer = Writer('big')

    def load(self, filepath: str) -> (bool, bool):
        self.filepath = filepath

        texture_loaded, use_lzham = self._load_internal(filepath, filepath.endswith('_tex.sc'))

        if not texture_loaded:
            if self.use_uncommon_texture:
                texture_loaded, use_lzham = self._load_internal(self.uncommon_texture_path, True)
            else:
                texture_path = self.filepath[:-3] + SupercellSWF.TEXTURE_EXTENSION
                texture_loaded, use_lzham = self._load_internal(texture_path, True)

        return texture_loaded, use_lzham

    def _load_internal(self, filepath: str, is_texture: bool) -> (bool, bool):
        self.filename = os.path.basename(filepath)

        decompressed_data, use_lzham = open_sc(filepath)
        self.reader = Reader(decompressed_data)
        del decompressed_data

        if not is_texture:
            self.shape_count = self.reader.read_uint16()
            self.movie_clips_count = self.reader.read_uint16()
            self.textures_count = self.reader.read_uint16()
            self.text_field_count = self.reader.read_uint16()
            self.matrix_count = self.reader.read_uint16()
            self.color_transformation_count = self.reader.read_uint16()

            self.shapes = [_class() for _class in [Shape] * self.shape_count]
            self.movie_clips = [_class() for _class in [MovieClip] * self.movie_clips_count]
            self.textures = [_class() for _class in [SWFTexture] * self.textures_count]

            self.reader.read_uint32()
            self.reader.read_byte()

            self.export_count = self.reader.read_uint16()

            self.exports = [_function() for _function in [self.reader.read_uint16] * self.export_count]
            self.exports = {export_id: self.reader.read_string() for export_id in self.exports}

        loaded = self._load_tags()

        print()
        return loaded, use_lzham

    def _load_tags(self):
        has_texture = True

        texture_id = 0
        movie_clips_loaded = 0
        shapes_loaded = 0

        while True:
            tag = self.reader.read_byte()
            length = self.reader.read_uint32()

            if tag == 0:
                return has_texture
            elif tag in SupercellSWF.TEXTURES_TAGS:
                texture = self.textures[texture_id]
                texture.load(self, tag, has_texture)

                if has_texture:
                    logger.info(locale.about_sc % (
                        self.filename,
                        texture_id,
                        texture.pixel_type,
                        texture.width,
                        texture.height
                    ))
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
            elif tag == 8:  # Matrix
                scale_x = self.reader.read_int32() / 1024
                rotation_x = self.reader.read_int32() / 1024
                rotation_y = self.reader.read_int32() / 1024
                scale_y = self.reader.read_int32() / 1024
                x = self.reader.read_int32() / 20
                y = self.reader.read_int32() / 20

                self.matrices.append([
                    scale_x, rotation_x, x,
                    rotation_y, scale_y, y
                ])
            elif tag == 26:
                has_texture = False
            elif tag == 30:
                self.use_uncommon_texture = True
                highres_texture_path = self.filepath[:-3] + self.highres_suffix + SupercellSWF.TEXTURE_EXTENSION
                lowres_texture_path = self.filepath[:-3] + self.lowres_suffix + SupercellSWF.TEXTURE_EXTENSION

                self.uncommon_texture_path = highres_texture_path
                if not os.path.exists(highres_texture_path) and os.path.exists(lowres_texture_path):
                    self.uncommon_texture_path = lowres_texture_path
                    self.use_lowres_texture = True
            else:
                self.reader.read(length)

    def get_export_by_id(self, movie_clip):
        return self.exports.get(movie_clip, '_movieclip_%s' % movie_clip)
