import numpy as np
import math


class Mat4:
    data = None

    def __init__(self, p=None):
        if p is not None:
            self.data = np.matrix(p)
        else:
            self.data = np.identity(4)

    def __mul__(self, other):
        return Mat4(self.data.dot(other.data))


class Mat3:
    data = None

    def __init__(self, p=None):
        if p is not None:
            self.data = np.matrix(p)
        else:
            self.data = np.identity(3)

    def __mul__(self, other):
        return Mat4(self.data.dot(other.data))


class Vec3:
    data = (0, 0, 0)

    def __init__(self, x, y, z):
        self.data = [x, y, z]

    def normalize(self):
        return normalize(self)

    def __mul__(self, other):
        return dot(self, other)

    def mix(self, other, t):
        return mix(self, other, t)

    def length(self):
        return length(self)

    def cross(self, other):
        return cross(self, other)

    def to_numpy(self):
        return np.array([self.data[0], self.data[1], self.data[2]])


# Vector operations
def normalize(v):
    if isinstance(v, Vec3):
        norm = np.linalg.norm(v.data)
        return v.data / norm
    else:
        norm = np.linalg.norm(v)
        print(v, norm)
        return v / norm


def dot(a, b):
    if isinstance(a, Vec3):
        return np.dot(a.data, b.data)
    else:
        return np.dot(a, b)


def mix(a, b, t):
    return a.data * (1.0 - t) + b.data * t


def cross(a, b):
    if isinstance(a, Vec3):
        return np.cross(a.data, b.data)
    else:
        return np.cross(a, b)


def length(v):
    if isinstance(v, Vec3):
        return np.linalg.norm(v.data)
    else:
        return np.linalg.norm(v)


# Helper functions to get common matrices


def make_translation(x, y, z):
    return Mat4([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]])


def make_translation_vec(vec):
    return make_translation(vec[0], vec[1], vec[2])


def make_scale(x, y, z):
    return Mat4([[x, 0, 0, 0], [0, y, 0, 0], [0, 0, z, 0], [0, 0, 0, 1]])


def make_scale_vec(vec):
    return make_translation(vec[0], vec[1], vec[2])


def make_rotation_y(angle):
    return Mat4(
        [
            [math.cos(angle), 0, -math.sin(angle), 0],
            [0, 1, 0, 0],
            [math.sin(angle), 0, math.cos(angle), 0],
            [0, 0, 0, 1],
        ]
    )


def make_rotation_x(angle):
    return Mat4(
        [
            [1, 0, 0, 0],
            [0, math.cos(angle), -math.sin(angle), 0],
            [0, math.sin(angle), math.cos(angle), 0],
            [0, 0, 0, 1],
        ]
    )


def make_rotation_z(angle):
    return Mat4(
        [
            [math.cos(angle), -math.sin(angle), 0, 0],
            [math.sin(angle), math.cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )
