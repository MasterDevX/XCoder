from math import ceil

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
        for region in self.regions:
            region.transformed_points = list(region.shape_points)

            if matrix is not None:
                region.transformed_points = []
                for point in region.shape_points:
                    region.transformed_points.append(Point(
                        point.x * matrix[0] + point.y * matrix[3] + matrix[2],
                        point.x * matrix[1] + point.y * matrix[4] + matrix[5]
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
        self.texture_id = 0
        self.points_count = 0
        self.rotation = 0
        self.mirroring = 0
        self.shape_points = []
        self.transformed_points = []
        self.sheet_points = []
        self.size = (0, 0)

        self.texture = None

    def load(self, swf, tag: int):
        self.texture_id = swf.reader.read_ubyte()

        self.texture = swf.textures[self.texture_id]

        self.points_count = 4
        if tag != 4:
            self.points_count = swf.reader.read_ubyte()

        self.shape_points = [_class() for _class in [Point] * self.points_count]
        self.sheet_points = [_class() for _class in [Point] * self.points_count]

        for z in range(self.points_count):
            self.shape_points[z].x = swf.reader.read_int32() / 20
            self.shape_points[z].y = swf.reader.read_int32() / 20
        for z in range(self.points_count):
            w, h = [swf.reader.read_uint16() * swf.textures[self.texture_id].width / 0xffff,
                    swf.reader.read_uint16() * swf.textures[self.texture_id].height / 0xffff]
            x, y = [ceil(i) for i in (w, h)]
            if int(w) == x:
                x += 1
            if int(h) == y:
                y += 1

            self.sheet_points[z].position = (x, y)

    def render(self, swf):
        sheet_left = min(point.x for point in self.sheet_points)
        sheet_right = max(point.x for point in self.sheet_points)
        sheet_top = min(point.y for point in self.sheet_points)
        sheet_bottom = max(point.y for point in self.sheet_points)

        shape_left = min(point.x for point in self.transformed_points)
        shape_right = max(point.x for point in self.transformed_points)
        shape_top = min(point.y for point in self.transformed_points)
        shape_bottom = max(point.y for point in self.transformed_points)

        width, height = shape_right - shape_left, shape_bottom - shape_top
        self.size = ceil(width), ceil(height)

        self.rotation = calculate_rotation(self)
        if self.rotation in (90, 270):
            self.size = self.size[::-1]

        img_mask = Image.new('L', (self.texture.width, self.texture.height), 0)
        color = 255
        ImageDraw.Draw(img_mask).polygon([point.position for point in self.sheet_points], fill=color)
        bbox = img_mask.getbbox()
        if not bbox:
            if sheet_bottom - sheet_top != 0:
                for _y in range(sheet_bottom - sheet_top):
                    img_mask.putpixel((sheet_right - 1, sheet_top + _y - 1), color)
            elif sheet_right - sheet_left != 0:
                for _x in range(sheet_right - sheet_left):
                    img_mask.putpixel((sheet_left + _x - 1, sheet_bottom - 1), color)
            else:
                img_mask.putpixel((sheet_right - 1, sheet_bottom - 1), color)
            bbox = img_mask.getbbox()

        a, b, c, d = bbox
        if c - a - 1:
            c -= 1
        if d - b - 1:
            d -= 1

        bbox = a, b, c, d

        region_size = (bbox[2] - bbox[0], bbox[3] - bbox[1])

        tmp_region = Image.new('RGBA', region_size)
        tmp_region.paste(self.texture.image.crop(bbox), (0, 0), img_mask.crop(bbox))
        if self.mirroring:
            tmp_region = tmp_region.transform(region_size, Image.EXTENT, (region_size[0], 0, 0, region_size[1]))
        tmp_region = tmp_region.resize(self.size, Image.ANTIALIAS).rotate(self.rotation, expand=True)
        return tmp_region


def calculate_rotation(region):
    def calc_sum(points):
        x1, y1 = points[(z + 1) % num_points].position
        x2, y2 = points[z].position
        return (x1 - x2) * (y1 + y2)

    sum_sheet = 0
    sum_shape = 0
    num_points = region.points_count

    for z in range(num_points):
        sum_sheet += calc_sum(region.sheet_points)
        sum_shape += calc_sum(region.transformed_points)

    sheet_orientation = -1 if (sum_sheet < 0) else 1
    shape_orientation = -1 if (sum_shape < 0) else 1

    region.mirroring = int(not (shape_orientation == sheet_orientation))

    sheet_pos_0 = region.sheet_points[0]
    sheet_pos_1 = region.sheet_points[1]
    shape_pos_0 = region.transformed_points[0]
    shape_pos_1 = region.transformed_points[1]

    if sheet_pos_0 == sheet_pos_1:
        sheet_pos_0 = Point(sheet_pos_0.x + 1, sheet_pos_0.y)

    if region.mirroring:
        shape_pos_0 = Point(shape_pos_0.x * -1, shape_pos_0.y)
        shape_pos_1 = Point(shape_pos_1.x * -1, shape_pos_1.y)

    if sheet_pos_1.x > sheet_pos_0.x:
        sheet_x = 1
    elif sheet_pos_1.x < sheet_pos_0.x:
        sheet_x = 2
    else:
        sheet_x = 3

    if sheet_pos_1.y < sheet_pos_0.y:
        sheet_y = 1
    elif sheet_pos_1.y > sheet_pos_0.y:
        sheet_y = 2
    else:
        sheet_y = 3

    if shape_pos_1.x > shape_pos_0.x:
        shape_x = 1
    elif shape_pos_1.x < shape_pos_0.x:
        shape_x = 2
    else:
        shape_x = 3

    if shape_pos_1.y > shape_pos_0.y:
        shape_y = 1
    elif shape_pos_1.y < shape_pos_0.y:
        shape_y = 2
    else:
        shape_y = 3

    rotation = 0
    if sheet_x == shape_x and sheet_y == shape_y:
        rotation = 0
    elif sheet_x == 3:
        if sheet_x == shape_y:
            if sheet_y == shape_x:
                rotation = 1
            else:
                rotation = 3
        else:
            rotation = 2
    elif sheet_y == 3:
        if sheet_y == shape_x:
            if sheet_x == shape_y:
                rotation = 3
            else:
                rotation = 1
        else:
            rotation = 2
    elif sheet_x != shape_x and sheet_y != shape_y:
        rotation = 2
    elif sheet_x == sheet_y:
        if sheet_x != shape_x:
            rotation = 3
        elif sheet_y != shape_y:
            rotation = 1
    elif sheet_x != sheet_y:
        if sheet_x != shape_x:
            rotation = 1
        elif sheet_y != shape_y:
            rotation = 3

    if sheet_orientation == -1 and rotation in (1, 3):
        rotation += 2
        rotation %= 4

    return rotation * 90
