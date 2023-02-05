import os

from PIL import Image

from system.lib.images import (
    get_format_by_pixel_type,
    load_texture,
    join_image,
    load_image_from_buffer,
)


class SWFTexture:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.pixel_type = -1

        self.image = None

    def load(self, swf, tag: int, has_texture: bool):
        self.pixel_type = swf.reader.read_char()
        self.width, self.height = (swf.reader.read_ushort(), swf.reader.read_ushort())

        if has_texture:
            img = Image.new(
                get_format_by_pixel_type(self.pixel_type), (self.width, self.height)
            )

            load_texture(swf.reader, self.pixel_type, img)

            if tag in (27, 28, 29):
                join_image(img)
            else:
                load_image_from_buffer(img)

            os.remove("pixel_buffer")

            self.image = img
