import math
from utils.gltypes import Mat4, Vec3
import utils.gltypes as gltypes
import numpy as np


class Camera:
    # Camera perspective properties
    aspect = 16 / 9
    fov = math.radians(45)
    near = 0
    far = 0

    # Camera location properties
    eye = Vec3(0, 0, 0)
    direction = Vec3(0, 0, 0)
    up = Vec3(0, 0, 1)

    def __init__(self, aspect=None, fov=None, near=None, far=None):
        self.aspect = aspect or (float(16) / float(9))
        self.fov = fov or math.radians(45)
        self.near = near or 0.01
        self.far = far or 100

    def update_perspective(self, aspect=None, fov=None, near=None, far=None):
        self.aspect = aspect or self.aspect
        self.fov = fov or self.fov
        self.near = near or self.near
        self.far = far or self.far

    def update_position(self, eye=None, direction=None, up=None):
        self.eye = eye or self.eye
        self.direction = direction or self.direction
        self.up = up or self.up

    def make_perspective(self):
        tfov = math.tan(self.fov / 2)
        sx = 1.0 / (tfov * self.aspect)
        sy = 1.0 / (tfov)

        zz = -(self.far + self.near) / (self.far - self.near)
        zw = -(2.0 * self.far * self.near) / (self.far - self.near)
        return Mat4([[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, zz, zw], [0, 0, -1, 0]])

    def make_lookFrom(self):
        f = gltypes.normalize(self.direction)
        c = f.cross(self.up)
        s = c.normalize()
        u = np.cross(s, f)

        M = np.matrix(np.identity(4))
        M[:3, :3] = np.vstack([s, u, -f])
        T = types.make_translation_vec(self.eye)
        return Mat4(M) * T

    def make_lookFrom2(eye, direction, up):
        eye = eye.to_numpy()
        up = up.to_numpy()

        f = gltypes.normalize(direction)
        c = gltypes.cross(f, up)
        s = gltypes.normalize(c)
        u = gltypes.cross(s, f)

        M = np.matrix(np.identity(4))
        M[:3, :3] = np.vstack([s, u, -f])

        T = gltypes.make_translation_vec(eye)
        return Mat4(M) * T

    def make_lookAt(self, target):
        return Camera.make_lookFrom2(
            self.eye, np.array(target.data[:3]) - np.array(self.eye.data[:3]), self.up
        )
