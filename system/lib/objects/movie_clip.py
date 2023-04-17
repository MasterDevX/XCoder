from math import ceil
from typing import TYPE_CHECKING, List, Tuple

from PIL import Image

from system.bytestream import Reader
from system.lib.helper import get_size
from system.lib.matrices.matrix_bank import MatrixBank
from system.lib.objects.shape import Shape

if TYPE_CHECKING:
    from system.lib.swf import SupercellSWF


class MovieClipFrame:
    def __init__(self):
        self._elements_count: int = 0
        self._label: str | None = None

        self._elements: List[Tuple[int, int, int]] = []

    def load(self, reader: Reader) -> None:
        self._elements_count = reader.read_short()
        self._label = reader.read_string()

    def get_elements_count(self) -> int:
        return self._elements_count

    def set_elements(self, elements: List[Tuple[int, int, int]]) -> None:
        self._elements = elements

    def get_elements(self) -> List[Tuple[int, int, int]]:
        return self._elements

    def get_element(self, index: int) -> Tuple[int, int, int]:
        return self._elements[index]


class MovieClip:
    def __init__(self):
        super().__init__()

        self.id = -1
        self.export_name: str | None = None
        self.fps: int = 30
        self.frames_count: int = 0
        self.frames: List[MovieClipFrame] = []
        self.frame_elements: List[Tuple[int, int, int]] = []
        self.blends: List[int] = []
        self.binds: List[int] = []
        self.matrix_bank_index: int = 0

    def load(self, swf: "SupercellSWF", tag: int):
        self.id = swf.reader.read_ushort()

        self.fps = swf.reader.read_char()
        self.frames_count = swf.reader.read_ushort()

        if tag in (3, 14):
            pass
        else:
            transforms_count = swf.reader.read_uint()

            for i in range(transforms_count):
                child_index = swf.reader.read_ushort()
                matrix_index = swf.reader.read_ushort()
                color_transform_index = swf.reader.read_ushort()

                self.frame_elements.append(
                    (child_index, matrix_index, color_transform_index)
                )

        binds_count = swf.reader.read_ushort()

        for i in range(binds_count):
            bind_id = swf.reader.read_ushort()  # bind_id
            self.binds.append(bind_id)

        if tag in (12, 35):
            for i in range(binds_count):
                blend = swf.reader.read_char()  # blend
                self.blends.append(blend)

        for i in range(binds_count):
            swf.reader.read_string()  # bind_name

        elements_used = 0

        while True:
            frame_tag = swf.reader.read_uchar()
            frame_length = swf.reader.read_int()

            if frame_tag == 0:
                break

            if frame_tag == 11:
                frame = MovieClipFrame()
                frame.load(swf.reader)
                frame.set_elements(
                    self.frame_elements[
                        elements_used : elements_used + frame.get_elements_count()
                    ]
                )
                self.frames.append(frame)

                elements_used += frame.get_elements_count()
            elif frame_tag == 41:
                self.matrix_bank_index = swf.reader.read_uchar()
            else:
                swf.reader.read(frame_length)

    def render(self, swf: "SupercellSWF", matrix=None) -> Image.Image:
        matrix_bank = swf.get_matrix_bank(self.matrix_bank_index)

        # TODO: make it faster
        left, top, right, bottom = self.get_sides(swf)

        width, height = get_size(left, top, right, bottom)
        size = ceil(width), ceil(height)
        image = Image.new("RGBA", size)

        frame = self.frames[0]
        for child_index, matrix_index, _ in frame.get_elements():
            if matrix_index != 65535:
                matrix = matrix_bank.get_matrix(matrix_index)
            else:
                matrix = None

            display_object = swf.get_display_object(self.binds[child_index])
            if isinstance(display_object, Shape):
                rendered_shape = display_object.render(matrix)

                # TODO: fix position
                position = display_object.get_position()
                x = int(abs(left) + position[0])
                y = int(abs(top) + position[1])

                image.paste(rendered_shape, (x, y), rendered_shape)

        return image

    def get_sides(self, swf: "SupercellSWF") -> Tuple[float, float, float, float]:
        matrix_bank: MatrixBank = swf.get_matrix_bank(self.matrix_bank_index)

        left = 0
        top = 0
        right = 0
        bottom = 0

        for frame in self.frames:
            for child_index, matrix_index, _ in frame.get_elements():
                if matrix_index != 65535:
                    matrix = matrix_bank.get_matrix(matrix_index)
                else:
                    matrix = None

                display_object = swf.get_display_object(self.binds[child_index])
                if isinstance(display_object, Shape):
                    display_object.apply_matrix(matrix)

                    (
                        shape_left,
                        shape_top,
                        shape_right,
                        shape_bottom,
                    ) = display_object.get_sides()

                    left = min(left, shape_left)
                    top = min(top, shape_top)
                    right = max(right, shape_right)
                    bottom = max(bottom, shape_bottom)

        return left, top, right, bottom
