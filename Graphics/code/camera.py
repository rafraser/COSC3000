import gltypes
from gltypes import Mat3, Mat4
import math
import imgui


class OrbitCamera:
    target = gltypes.vec3(0.0, 0.0, 0.0)
    distance = 1.0
    yawDeg = 0.0
    pitchDeg = 0.0
    maxSpeed = 10
    angSpeed = 90
    position = gltypes.vec3(0.0, 0.0, 0.0)
    up = gltypes.vec3(0.0, 1.0, 0.0)

    fov = 45
    aspect = 16 / 9
    near = 0.1
    far = 1000

    def __init__(self, target, distance, yawDeg, pitchDeg):
        self.target = gltypes.vec3(*target)
        self.yawDeg = yawDeg
        self.pitchDeg = pitchDeg
        self.distance = distance

    def update(self, dt, keys):
        cameraRotation = Mat3(
            gltypes.make_rotation_y(math.radians(self.yawDeg))
        ) * Mat3(gltypes.make_rotation_x(math.radians(self.pitchDeg)))
        self.position = cameraRotation * gltypes.vec3(0, 0, self.distance)

    def drawUi(self):
        if imgui.tree_node("OrbitCamera", imgui.TREE_NODE_DEFAULT_OPEN):
            _, self.yawDeg = imgui.slider_float(
                "Yaw (Deg)", self.yawDeg, -180.00, 180.0
            )
            _, self.pitchDeg = imgui.slider_float(
                "Pitch (Deg)", self.pitchDeg, -89.00, 89.0
            )
            _, self.distance = imgui.slider_float(
                "Distance", self.distance, 1.00, 1000.0
            )
            imgui.tree_pop()

    def getWorldToViewMatrix(self):
        return gltypes.make_lookAt(self.position, self.target, self.up)

    def make_perspective(self):
        tanHalf = math.tan(self.fov / 2.0)
        sx = 1.0 / (tanHalf * self.aspect)
        sy = 1.0 / tanHalf
        zz = -(self.far + self.near) / (self.far - self.near)
        zw = -(2.0 * self.far * self.near) / (self.far - self.near)

        return gltypes.Mat4(
            [[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, zz, zw], [0, 0, -1, 0]]
        )
