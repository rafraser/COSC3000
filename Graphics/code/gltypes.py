from OpenGL.GL import *
import numpy as np
import math


def vec2(x, y=None):
    if y == None:
        return np.array([x, x], dtype=np.float32)
    return np.array([x, y], dtype=np.float32)


def vec3(x, y=None, z=None):
    if y == None:
        return np.array([x, x, x], dtype=np.float32)
    if z == None:
        return np.array([x, y, y], dtype=np.float32)
    return np.array([x, y, z], dtype=np.float32)


def rgb(r, g, b):
    x = r / 255
    y = g / 255
    z = b / 255
    return np.array([x, y, z], dtype=np.float32)


def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm


class Mat4:
    matData = None

    def __init__(self, p=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]):
        if isinstance(p, Mat3):
            self.matData = np.matrix(np.identity(4))
            self.matData[:3, :3] = p.matData
        else:
            self.matData = np.matrix(p)

    def __mul__(self, other):
        if isinstance(other, (list, np.ndarray)):
            return list(self.matData.dot(other).flat)
        return Mat4(self.matData.dot(other.matData))

    # Helper to get data as a contiguous array for upload to OpenGL
    def getData(self):
        return np.ascontiguousarray(self.matData, dtype=np.float32)

    def inverse(self):
        return Mat4(np.linalg.inv(self.matData))

    def transpose(self):
        return Mat4(self.matData.T)

    def _set_open_gl_uniform(self, loc):
        glUniformMatrix4fv(loc, 1, GL_TRUE, self.getData())


class Mat3:
    matData = None
    # Construct a Mat4 from a python array
    def __init__(self, p=[[1, 0, 0], [0, 1, 0], [0, 0, 1]]):
        if isinstance(p, Mat4):
            self.matData = p.matData[:3, :3]
        else:
            self.matData = np.matrix(p)

    def __mul__(self, other):
        if isinstance(other, (list, np.ndarray)):
            return list(self.matData.dot(other).flat)
        return Mat3(self.matData.dot(other.matData))

    def getData(self):
        return np.ascontiguousarray(self.matData, dtype=np.float32)

    def inverse(self):
        return Mat3(np.linalg.inv(self.matData))

    def transpose(self):
        return Mat3(self.matData.T)

    def _set_open_gl_uniform(self, loc):
        glUniformMatrix3fv(loc, 1, GL_TRUE, self.getData())


def make_translation(x, y, z):
    return Mat4([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]])


def make_translation(x, y, z):
    return Mat4([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]])


def make_scale(x, y, z):
    return Mat4([[x, 0, 0, 0], [0, y, 0, 0], [0, 0, z, 0], [0, 0, 0, 1]])


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


def transform_point(m4, point):
    x, y, z, w = m4 * [point[0], point[1], point[2], 1.0]
    return vec3(x, y, z) / w
