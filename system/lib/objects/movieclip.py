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

        self.points = []

    def load(self, swf, tag: int):
        self.id = swf.reader.read_uint16()

        self.export_name = swf.get_export_by_id(self.id)
        self.fps = swf.reader.read_byte()
        self.frames_count = swf.reader.read_uint16()

        if tag in (3, 14,):
            pass
        else:
            transforms_count = swf.reader.read_uint32()

            for i in range(transforms_count):
                bind_id = swf.reader.read_uint16()
                matrix_id = swf.reader.read_uint16()
                color_transform_id = swf.reader.read_uint16()

                if not (bind_id in self.transforms):
                    self.transforms[bind_id] = {'matrices': [], 'color_transforms': []}
                self.transforms[bind_id]['matrices'].append(matrix_id)
                self.transforms[bind_id]['color_transforms'].append(color_transform_id)

        binds_count = swf.reader.read_uint16()

        for i in range(binds_count):
            bind_id = swf.reader.read_uint16()  # bind_id
            self.binds.append(bind_id)

        if tag in (12, 35,):
            for i in range(binds_count):
                blend = swf.reader.read_byte()  # blend
                self.blends.append(blend)

        for i in range(binds_count):
            swf.reader.read_string()  # bind_name

        while True:
            frame_tag = swf.reader.read_ubyte()
            frame_length = swf.reader.read_int32()

            if frame_tag == 0:
                break

            if frame_tag == 11:
                swf.reader.read_int16()  # frame_id
                swf.reader.read_string()  # frame_name
            else:
                swf.reader.read(frame_length)

    def render(self, swf):
        pass
