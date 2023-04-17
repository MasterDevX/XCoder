from typing import List

from system.lib.matrices.color_transform import ColorTransform
from system.lib.matrices.matrix2x3 import Matrix2x3


class MatrixBank:
    def __init__(self):
        self.matrices: List[Matrix2x3] = []
        self.color_transforms: List[ColorTransform] = []

    def init(self, matrix_count: int, color_transform_count: int):
        self.matrices = []
        for i in range(matrix_count):
            self.matrices.append(Matrix2x3())

        self.color_transforms = []
        for i in range(color_transform_count):
            self.color_transforms.append(ColorTransform())

    def get_matrix(self, index: int) -> Matrix2x3:
        return self.matrices[index]

    def get_color_transform(self, index: int) -> ColorTransform:
        return self.color_transforms[index]
