import os

from PIL import Image

from system.lib.images import pixel_type2str, bytes2rgba, join_image, load_image_from_buffer


class SWFTexture:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.pixel_type = -1

        self.image = None

    def load(self, swf, tag: int, has_texture: bool):
        self.pixel_type = swf.reader.read_byte()
        self.width, self.height = (swf.reader.read_uint16(), swf.reader.read_uint16())

        if has_texture:
            img = Image.new(pixel_type2str(self.pixel_type), (self.width, self.height))

            bytes2rgba(swf.reader, self.pixel_type, img)

            if tag in (27, 28):
                join_image(img)
                print()
            else:
                load_image_from_buffer(img)

            os.remove('pixel_buffer')

            self.image = img
