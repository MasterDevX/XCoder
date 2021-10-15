class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __add__(self, other):
        if isinstance(other, Point):
            self.x += other.x
            self.y += other.y
        return self

    def __sub__(self, other):
        return self + -other

    def __neg__(self):
        self.x *= -1
        self.y *= -1
        return self

    def __repr__(self):
        return str(self.position)

    @property
    def position(self):
        return self.x, self.y

    @position.setter
    def position(self, value):
        self.x = value[0]
        self.y = value[1]
