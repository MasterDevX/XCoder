from math import ceil, degrees, atan2
from typing import List, Tuple

from PIL import Image, ImageDraw

from system.lib.objects.point import Point


class Shape:
    def __init__(self):
        self.id = 0
        self.regions = []

    def load(self, swf, tag: int):
        self.id = swf.reader.read_uint16()

        swf.reader.read_uint16()  # regions_count
        if tag == 18:
            swf.reader.read_uint16()  # point_count

        while True:
            region_tag = swf.reader.read_byte()
            region_length = swf.reader.read_uint32()

            if region_tag == 0:
                return
            elif region_tag in (4, 17, 22,):
                region = Region()
                region.load(swf, region_tag)
                self.regions.append(region)
            else:
                swf.reader.read(region_length)

    def render(self, swf, matrix=None):
        if matrix is not None:
            for region in self.regions:
                region.transformed_points = []
                for index in range(region.get_points_count()):
                    region.transformed_points.append(Point(
                        region.get_x(index) * matrix[0] + region.get_y(index) * matrix[3] + matrix[2],
                        region.get_x(index) * matrix[1] + region.get_y(index) * matrix[4] + matrix[5]
                    ))

        shape_left = 0
        shape_top = 0
        shape_right = 0
        shape_bottom = 0
        for region in self.regions:
            shape_left = min(shape_left, min(point.x for point in region.transformed_points))
            shape_right = max(shape_right, max(point.x for point in region.transformed_points))
            shape_top = min(shape_top, min(point.y for point in region.transformed_points))
            shape_bottom = max(shape_bottom, max(point.y for point in region.transformed_points))

        width, height = shape_right - shape_left, shape_bottom - shape_top
        size = ceil(width), ceil(height)

        image = Image.new('RGBA', size)

        region: Region
        for region in self.regions:
            rendered_region = region.render(swf)

            left = min(point.x for point in region.transformed_points)
            top = min(point.y for point in region.transformed_points)

            x = int(left + abs(shape_left))
            y = int(top + abs(shape_top))

            image.paste(rendered_region, (x, y), rendered_region)

        return image


class Region:
    def __init__(self):
        self.texture_index = 0
        self.rotation = 0
        self.is_mirrored = 0
        self.transformed_points = []

        self._points_count = 0
        self._xy_points = []
        self._uv_points = []

        self.texture = None

    def load(self, swf, tag: int):
        self.texture_index = swf.reader.read_ubyte()

        self.texture = swf.textures[self.texture_index]

        self._points_count = 4
        if tag != 4:
            self._points_count = swf.reader.read_ubyte()

        self._xy_points = [_class() for _class in [Point] * self._points_count]
        self.transformed_points = self._xy_points
        self._uv_points = [_class() for _class in [Point] * self._points_count]

        multiplier = 0.5 if swf.use_lowres_texture else 1

        for i in range(self._points_count):
            self._xy_points[i].x = swf.reader.read_int32() / 20
            self._xy_points[i].y = swf.reader.read_int32() / 20
        for i in range(self._points_count):
            u, v = (swf.reader.read_uint16() * swf.textures[self.texture_index].width / 0xffff * multiplier,
                    swf.reader.read_uint16() * swf.textures[self.texture_index].height / 0xffff * multiplier)
            u_rounded, v_rounded = map(ceil, (u, v))
            if int(u) == u_rounded:
                u_rounded += 1
            if int(v) == v_rounded:
                v_rounded += 1

            self._uv_points[i].position = (u_rounded, v_rounded)

    def render(self, swf):
        width, height = get_size(*get_sides(self.transformed_points))
        width, height = max(width, 1), max(height, 1)

        self.rotation, self.is_mirrored = self.calculate_rotation(True)

        rendered_region = self.get_image()
        rendered_region = rendered_region.rotate(-self.rotation, expand=True)
        if self.is_mirrored:
            rendered_region = rendered_region.transpose(Image.FLIP_LEFT_RIGHT)
        rendered_region = rendered_region.resize((width, height), Image.ANTIALIAS)
        return rendered_region

    def get_image(self):
        img_mask = Image.new('L', (self.texture.width, self.texture.height), 0)

        color = 255
        ImageDraw.Draw(img_mask).polygon([point.position for point in self._uv_points], fill=color)

        left, top, right, bottom = get_sides(self._uv_points)
        width, height = get_size(left, top, right, bottom)
        width, height = max(width, 1), max(height, 1)

        if width == 1:
            right += 1

        if height == 1:
            bottom += 1

        bbox = left, top, right, bottom

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

    def calculate_rotation(self, round_to_nearest: bool = False) -> (int, bool):
        """Calculates rotation and if region is mirrored.

        :param round_to_nearest: should round to a multiple of 90
        :return: rotation angle, is mirroring
        """

        def is_clockwise(points):
            points_sum = 0
            for i in range(len(points)):
                x1, y1 = points[(i + 1) % len(points)].position
                x2, y2 = points[i].position
                points_sum += (x1 - x2) * (y1 + y2)
            return points_sum > 0

        is_uv_clockwise = is_clockwise(self._uv_points)
        is_xy_clockwise = is_clockwise(self._xy_points)

        mirroring = not (is_uv_clockwise == is_xy_clockwise)

        dx = self._xy_points[1].x - self._xy_points[0].x
        dy = self._xy_points[1].y - self._xy_points[0].y
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


def get_size(left: float, top: float, right: float, bottom: float) -> (int, int):
    """Returns width and height of given rect.

    :param left:
    :param top:
    :param right:
    :param bottom:
    :return: width, height
    """
    return int(right - left), int(bottom - top)


def get_sides(points: List[Tuple[float, float]] or List[Point]) -> (float, float, float, float):
    """Calculates and returns rect sides.

    :param points: polygon points
    :return: left, top, right, bottom
    """
    if len(points) > 0:
        point = points[0]
        if type(point) is Point:
            left = min(point.x for point in points)
            top = min(point.y for point in points)
            right = max(point.x for point in points)
            bottom = max(point.y for point in points)
        elif type(point) is tuple:
            left = min(x for x, _ in points)
            top = min(y for _, y in points)
            right = max(x for x, _ in points)
            bottom = max(y for _, y in points)
        else:
            raise TypeError('Unknown point type.')

        return left, top, right, bottom
    raise ValueError('Empty points list.')
