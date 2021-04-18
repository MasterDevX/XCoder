class Point:
    def __init__(self):
        self.x = 0
        self.y = 0

    @property
    def position(self):
        return self.x, self.y

    @position.setter
    def position(self, value):
        self.x = value[0]
        self.y = value[1]


class SheetData:
    def __init__(self):
        self.size = (0, 0)


class MovieClip:
    def __init__(self):
        super().__init__()

        self.export_name = None
        self.fps = None
        self.frames_count = None
        self.shapes = []
        self.blends = []


class SpriteGlobals:
    def __init__(self):
        self.shape_count = 0
        self.movie_clips_count = 0
        self.textures_count = 0
        self.text_field_count = 0
        self.matrix_count = 0
        self.color_transformation_count = 0
        self.export_count = 0


class SpriteData:
    def __init__(self):
        self.id = 0
        self.regions = []


class SWFTexture:
    def __init__(self):
        self.width = 0
        self.height = 0

        self.pixel_type = -1

        self.image = None


class Region:
    def __init__(self):
        self.sheet_id = 0
        self.num_points = 0
        self.rotation = 0
        self.mirroring = 0
        self.shape_points = []
        self.sheet_points = []
        self.top = -32767
        self.left = 32767
        self.bottom = 32767
        self.right = -32767
        self.size = (0, 0)
