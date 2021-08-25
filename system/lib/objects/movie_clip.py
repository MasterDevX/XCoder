class MovieClip:
    def __init__(self):
        super().__init__()

        self.id = -1
        self.export_name = None
        self.fps = None
        self.frames_count = None
        self.transforms = {}
        self.blends = []
        self.binds = []

    def load(self, swf, tag: int):
        self.id = swf.reader.read_uint16()

        self.export_name = swf.get_export_by_id(self.id)
        self.fps = swf.reader.read_byte()
        self.frames_count = swf.reader.read_uint16()

        transforms_count = swf.reader.read_uint32()

        for i in range(transforms_count):
            bind_index = swf.reader.read_uint16()
            matrix_id = swf.reader.read_uint16()
            color_transform_id = swf.reader.read_uint16()

            if not (bind_index in self.transforms):
                self.transforms[bind_index] = {'matrices': [], 'color_transforms': []}
            self.transforms[bind_index]['matrices'].append(matrix_id)
            self.transforms[bind_index]['color_transforms'].append(color_transform_id)

        binds_count = swf.reader.read_uint16()

        for i in range(binds_count):
            bind_id = swf.reader.read_uint16()  # bind_id
            self.binds.append(bind_id)

        for i in range(binds_count):
            blend = swf.reader.read_byte()  # blend
            self.blends.append(blend)

        for i in range(binds_count):
            swf.reader.read_string()  # bind_name

        while True:
            inline_data_type = swf.reader.read_ubyte()
            swf.reader.read_int32()  # data_length

            if inline_data_type == 0:
                break

            if inline_data_type == 11:
                swf.reader.read_int16()  # frame_id
                swf.reader.read_string()  # frame_name
            elif inline_data_type == 31:
                for x in range(4):
                    swf.reader.read_ubyte()
                    swf.reader.read_ubyte()
                    swf.reader.read_string()
                    swf.reader.read_string()

    def render(self, swf):
        # shape_min_x = 0
        # shape_min_y = 0
        # shape_max_x = 0
        # shape_max_y = 0
        #
        # rendered_shapes = []
        # shapes_origins = []
        #
        # for bind_index in range(len(self.binds)):
        #     bind_id = self.binds[bind_index]
        #
        #     if not (bind_id in swf.shapes):
        #         continue
        #
        #     shape: Shape = swf.shapes[bind_id]
        #     matrix = None
        #
        #     transform = self.transforms[bind_index]
        #     if transform['matrices'][0] != 65535:
        #         matrix = swf.matrices[transform['matrices'][0]]
        #
        #     rendered_shapes.append(shape.render(swf, matrix))
        #
        #     region_min_x = 0
        #     region_min_y = 0
        #     region_max_x = 0
        #     region_max_y = 0
        #
        #     for region in shape.regions:
        #         region_min_x = min(point.x for point in region.transformed_points)
        #         region_min_y = min(point.y for point in region.transformed_points)
        #         region_max_x = max(point.x for point in region.transformed_points)
        #         region_max_y = max(point.y for point in region.transformed_points)
        #         shape_min_x = min(shape_min_x, region_min_x)
        #         shape_min_y = min(shape_min_y, region_min_y)
        #         shape_max_x = max(shape_max_x, region_max_x)
        #         shape_max_y = max(shape_max_y, region_max_y)
        #
        #         # If rotation != 0 i should to swap coordinates
        #
        #     shapes_origins.append((region_min_x, region_max_y))
        #
        # width, height = shape_max_x - shape_min_x, shape_max_y - shape_min_y
        # size = ceil(width), ceil(height)
        # image = Image.new('RGBA', size)
        #
        # # left up corner always is a (min x, max y)
        # for i in range(len(rendered_shapes)):
        #     bbox = int(shape_min_x-shapes_origins[i][0]), int(shape_max_y-shapes_origins[i][1])
        #     image.paste(rendered_shapes[i], bbox, rendered_shapes[i])
        #
        # return image
        pass
