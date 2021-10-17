import os

from loguru import logger

from system.bytestream import Writer, Reader
from system.lib.features.files import open_sc
from system.lib.objects.movieclip import MovieClip
from system.lib.objects.shape import Shape
from system.lib.objects.texture import SWFTexture
from system.localization import locale


class SupercellSWF:
    def __init__(self):
        self.filename = None
        self.reader = None

        self.shape_count = 0
        self.movie_clips_count = 0
        self.textures_count = 0
        self.text_field_count = 0
        self.matrix_count = 0
        self.color_transformation_count = 0

        self.export_count = 0

        self.exports = {}

        self.shapes = []
        self.movieclips = []
        self.textures = []

        self.matrices = []

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
            self.shape_count = self.reader.read_uint16()
            self.movie_clips_count = self.reader.read_uint16()
            self.textures_count = self.reader.read_uint16()
            self.text_field_count = self.reader.read_uint16()
            self.matrix_count = self.reader.read_uint16()
            self.color_transformation_count = self.reader.read_uint16()

            self.shapes = [_class() for _class in [Shape] * self.shape_count]
            self.movieclips = [_class() for _class in [MovieClip] * self.movie_clips_count]
            self.textures = [_class() for _class in [SWFTexture] * self.textures_count]

            self.reader.read_uint32()
            self.reader.read_byte()

            self.export_count = self.reader.read_uint16()

            self.exports = [_function() for _function in [self.reader.read_uint16] * self.export_count]
            self.exports = {export_id: self.reader.read_string() for export_id in self.exports}

            has_texture = self.load_tags()

        print()
        return has_texture, use_lzham

    def load_tags(self):
        has_texture = True

        texture_id = 0
        loaded_movieclips = 0
        loaded_shapes = 0

        while True:
            tag = self.reader.read_byte()
            length = self.reader.read_uint32()

            if tag == 0:
                return has_texture
            elif tag in [1, 16, 28, 29, 34, 19, 24, 27]:
                if len(self.textures) <= texture_id:
                    # Костыль, такого в либе нет, но ради фичи с вытаскиванием только текстур, можно и добавить)
                    self.textures.append(SWFTexture())
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
            elif tag in [2, 18]:
                self.shapes[loaded_shapes].load(self, tag)
                loaded_shapes += 1
            elif tag in [3, 10, 12, 14, 35]:  # MovieClip
                self.movieclips[loaded_movieclips].load(self, tag)
                loaded_movieclips += 1
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
            else:
                self.reader.read(length)
