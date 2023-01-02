from math import ceil, degrees, atan2
from typing import List, Tuple

from PIL import Image, ImageDraw

from system.lib.helper import get_sides, get_size
from system.lib.matrices.matrix2x3 import Matrix2x3
from system.lib.objects.point import Point


class Shape:
    def __init__(self):
        self.id = 0
        self.regions: List[Region] = []

    def load(self, swf, tag: int):
        self.id = swf.reader.read_ushort()

        swf.reader.read_ushort()  # regions_count
        if tag == 18:
            swf.reader.read_ushort()  # point_count

        while True:
            region_tag = swf.reader.read_char()
            region_length = swf.reader.read_uint()

            if region_tag == 0:
                return
            elif region_tag in (4, 17, 22,):
                region = Region()
                region.load(swf, region_tag)
                self.regions.append(region)
            else:
                swf.reader.read(region_length)

    def render(self, matrix=None):
        for region in self.regions:
            region.apply_matrix(matrix)

        shape_left, shape_top, shape_right, shape_bottom = self.get_sides()

        width, height = get_size(shape_left, shape_top, shape_right, shape_bottom)
        size = ceil(width), ceil(height)

        image = Image.new('RGBA', size)

        for region in self.regions:
            rendered_region = region.render()

            region_left, region_top = region.get_position()

            x = int(abs(shape_left) + region_left)
            y = int(abs(shape_top) + region_top)

            image.paste(rendered_region, (x, y), rendered_region)

        return image

    def apply_matrix(self, matrix: Matrix2x3 = None) -> None:
        """Calls apply_matrix method for all regions.

        :param matrix: Affine matrix
        """

        for region in self.regions:
            region.apply_matrix(matrix)

    def get_position(self) -> Tuple[float, float]:
        left, top, _, _ = self.get_sides()
        return left, top

    def get_sides(self) -> Tuple[float, float, float, float]:
        left = 0
        top = 0
        right = 0
        bottom = 0
        for region in self.regions:
            region_left, region_top, region_right, region_bottom = region.get_sides()
            left = min(left, region_left)
            right = max(right, region_right)
            top = min(top, region_top)
            bottom = max(bottom, region_bottom)

        return left, top, right, bottom


class Region:
    def __init__(self):
        self.texture_index = 0
        self.rotation = 0
        self.is_mirrored = 0

        self._points_count = 0
        self._xy_points: List[Point] = []
        self._uv_points: List[Point] = []
        self._transformed_points: List[Point] or None = None

        self.texture = None

    def load(self, swf, tag: int):
        self.texture_index = swf.reader.read_uchar()

        self.texture = swf.textures[self.texture_index]

        self._points_count = 4
        if tag != 4:
            self._points_count = swf.reader.read_uchar()

        self._xy_points = [_class() for _class in [Point] * self._points_count]
        self._uv_points = [_class() for _class in [Point] * self._points_count]

        multiplier = 0.5 if swf.use_lowres_texture else 1

        for i in range(self._points_count):
            self._xy_points[i].x = swf.reader.read_int() / 20
            self._xy_points[i].y = swf.reader.read_int() / 20
        for i in range(self._points_count):
            u, v = (swf.reader.read_ushort() * swf.textures[self.texture_index].width / 0xffff * multiplier,
                    swf.reader.read_ushort() * swf.textures[self.texture_index].height / 0xffff * multiplier)
            u_rounded, v_rounded = map(ceil, (u, v))
            if int(u) == u_rounded:
                u_rounded += 1
            if int(v) == v_rounded:
                v_rounded += 1

            self._uv_points[i].position = (u_rounded, v_rounded)

    def render(self):
        self._transformed_points = self._xy_points

        left, top, right, bottom = self.get_sides()
        width, height = get_size(left, top, right, bottom)
        width, height = max(width, 1), max(height, 1)

        self.rotation, self.is_mirrored = self.calculate_rotation(True)

        rendered_region = self.get_image()
        if sum(rendered_region.size) == 2:
            fill_color = rendered_region.getpixel((0, 0))

            # noinspection PyTypeChecker
            rendered_polygon = Image.new(rendered_region.mode, (width, height))
            drawable_image = ImageDraw.Draw(rendered_polygon)
            drawable_image.polygon(
                [(point.x - left, point.y - top) for point in self._transformed_points],
                fill=fill_color
            )
            return rendered_polygon

        rendered_region = rendered_region.rotate(-self.rotation, expand=True)
        if self.is_mirrored:
            rendered_region = rendered_region.transpose(Image.FLIP_LEFT_RIGHT)
        rendered_region = rendered_region.resize((width, height), Image.ANTIALIAS)
        return rendered_region

    def get_image(self) -> Image:
        left, top, right, bottom = get_sides(self._uv_points)
        width, height = get_size(left, top, right, bottom)
        width, height = max(width, 1), max(height, 1)
        if width + height == 1:  # The same speed as without this return
            return Image.new('RGBA', (width, height), color=self.texture.image.get_pixel(left, top))

        if width == 1:
            right += 1

        if height == 1:
            bottom += 1

        bbox = left, top, right, bottom

        color = 255
        img_mask = Image.new('L', (self.texture.width, self.texture.height), 0)
        ImageDraw.Draw(img_mask).polygon([point.position for point in self._uv_points], fill=color)

        rendered_region = Image.new('RGBA', (width, height))
        rendered_region.paste(self.texture.image.crop(bbox), (0, 0), img_mask.crop(bbox))

        return rendered_region

    def get_points_count(self):
        return self._points_count

    def get_uv(self, index: int):
        return self._uv_points[index]

    def get_u(self, index: int):
        return self._uv_points[index].x

    def get_v(self, index: int):
        return self._uv_points[index].y

    def get_xy(self, index: int):
        return self._xy_points[index]

    def get_x(self, index: int):
        return self._xy_points[index].x

    def get_y(self, index: int):
        return self._xy_points[index].y

    def get_position(self) -> Tuple[float, float]:
        left, top, _, _ = get_sides(self._transformed_points)
        return left, top

    def get_sides(self) -> Tuple[float, float, float, float]:
        return get_sides(self._transformed_points)

    def apply_matrix(self, matrix: Matrix2x3 = None) -> None:
        """Applies affine matrix to shape (xy) points. If matrix is none, copies the points.

        :param matrix: Affine matrix
        """

        self._transformed_points = self._xy_points
        if matrix is not None:
            self._transformed_points = []
            for point in self._xy_points:
                self._transformed_points.append(Point(
                    matrix.apply_x(point.x, point.y),
                    matrix.apply_y(point.x, point.y)
                ))

    def calculate_rotation(self, round_to_nearest: bool = False, custom_points: List[Point] = None) -> (int, bool):
        """Calculates rotation and if region is mirrored.

        :param round_to_nearest: should round to a multiple of 90
        :param custom_points: transformed points, replacement of self._xy_points
        :return: rotation angle, is mirroring
        """

        def is_clockwise(points: List[Point]):
            points_sum = 0
            for i in range(len(points)):
                x1, y1 = points[(i + 1) % len(points)].position
                x2, y2 = points[i].position
                points_sum += (x1 - x2) * (y1 + y2)
            return points_sum > 0

        xy_points = self._xy_points
        if custom_points is not None:
            xy_points = custom_points

        is_uv_clockwise = is_clockwise(self._uv_points)
        is_xy_clockwise = is_clockwise(xy_points)

        mirroring = not (is_uv_clockwise == is_xy_clockwise)

        dx = xy_points[1].x - xy_points[0].x
        dy = xy_points[1].y - xy_points[0].y
        du = self._uv_points[1].x - self._uv_points[0].x
        dv = self._uv_points[1].y - self._uv_points[0].y

        angle_xy = degrees(atan2(dy, dx)) % 360
        angle_uv = degrees(atan2(dv, du)) % 360

        angle = angle_xy - angle_uv

        if mirroring:
            angle -= 180

        angle = (angle + 360) % 360

        if round_to_nearest:
            angle = round(angle / 90) * 90

        return angle, mirroring
