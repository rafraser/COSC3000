import gltypes
from gltypes import Mat3, Mat4, normalize, make_translation

import numpy as np
import math
import imgui


class Camera:
    """Base camera class

    This has a bunch of utility functions to generate key matrices
    This includes lookAt, lookFrom, and perspective
    """

    position = gltypes.vec3(0, 0, 0)
    up = gltypes.vec3(0.0, 1.0, 0.0)

    aspect = float(16 / 9)
    near = 0.1
    far = 1750
    fov = math.radians(45)

    def update(self, delta, keys):
        pass

    def ui(self):
        pass

    def update_perspective(self, aspect=None, near=None, far=None, fov=None):
        self.aspect = aspect or self.aspect
        self.near = near or self.near
        self.far = far or self.far
        self.fov = fov or self.fov

    def make_lookFrom(self, direction):
        f = normalize(direction)
        U = np.array(self.up[:3])
        s = normalize(np.cross(f, U))
        u = np.cross(s, f)
        M = np.matrix(np.identity(4))
        M[:3, :3] = np.vstack([s, u, -f])
        T = make_translation(-self.position[0], -self.position[1], -self.position[2])
        return Mat4(M) * T

    def make_lookAt(self, target):
        return self.make_lookFrom(np.array(target[:3]) - np.array(self.position[:3]))

    def make_perspective(self):
        tanHalf = math.tan(self.fov / 2.0)
        sx = 1.0 / (tanHalf * self.aspect)
        sy = 1.0 / tanHalf
        zz = -(self.far + self.near) / (self.far - self.near)
        zw = -(2.0 * self.far * self.near) / (self.far - self.near)

        return Mat4([[sx, 0, 0, 0], [0, sy, 0, 0], [0, 0, zz, zw], [0, 0, -1, 0]])

    def getWorldToViewMatrix(self):
        return gltypes.make_lookAt(self.position, gltypes.vec3(0, 0, 0), self.up)


class OrbitCamera(Camera):
    """Basic orbiting camera class

    Can be configured to rotate around a given point at a fixed distance
    Controlled by the left and right arrow keys or an imgui node
    """

    yaw = 10
    pitch = -30
    distance = 850
    rotate_speed = 45
    target = gltypes.vec3(0, 0, 0)

    def __init__(self, target=gltypes.vec3(0, 0, 0)):
        self.target = target

    def update(self, dt, keys):
        """Camera update function

        Left and right arrow keys to adjust the yaw

        Arguments:
            dt {float} -- Time, in seconds, since the last update
            keys {dict} -- Mapping of keys currently pressed
        """
        if keys["LEFT"]:
            self.yaw -= self.rotate_speed * dt

        if keys["RIGHT"]:
            self.yaw += self.rotate_speed * dt

        cameraRotation = Mat3(gltypes.make_rotation_y(math.radians(self.yaw))) * Mat3(
            gltypes.make_rotation_x(math.radians(self.pitch))
        )

        self.position = cameraRotation * gltypes.vec3(0, 0, self.distance)

    def ui(self):
        """Basic UI node to adjust yaw, pitch, and distance
        Yaw can also be controlled with arrow keys (see above)
        """
        if imgui.tree_node("Camera", imgui.TREE_NODE_DEFAULT_OPEN):
            _, self.yaw = imgui.slider_float("Yaw (Deg)", self.yaw, -180.00, 180.0)
            _, self.pitch = imgui.slider_float("Pitch (Deg)", self.pitch, -89.00, 89.0)
            _, self.distance = imgui.slider_float(
                "Distance", self.distance, 1.00, 1000.0
            )
            imgui.tree_pop()

    def getWorldToViewMatrix(self):
        """Generate a worldToViewTransformMatrix

        This is always looking at the target
        """
        return self.make_lookAt(self.target)


class FreeCamera(Camera):
    """More complicated freeform camera mode

    Controlled by WASD for movement and arrow keys for angle control
    """

    yaw = 10
    pitch = -30

    rotate_speed = 60
    pitch_speed = 60
    move_speed = 50

    position = gltypes.vec3(50, 10, 0)

    def __init__(self, target=gltypes.vec3(0, 0, 0)):
        self.target = target

    def update(self, dt, keys):
        """Camera update function

        Arrow keys for angular rotation
        WASD for freeform movement

        Arguments:
            dt {float} -- Time, in seconds, since the last update
            keys {dict} -- Mapping of keys currently pressed
        """
        forwardSpeed = 0
        strafeSpeed = 0
        yawSpeed = 0
        pitchSpeed = 0

        # Handle angular movement
        if keys["UP"]:
            pitchSpeed -= self.pitch_speed
        if keys["DOWN"]:
            pitchSpeed += self.pitch_speed
        if keys["RIGHT"]:
            yawSpeed += self.rotate_speed
        if keys["LEFT"]:
            yawSpeed -= self.rotate_speed

        # Handle positional movement
        if keys["W"]:
            forwardSpeed += self.move_speed
        if keys["S"]:
            forwardSpeed -= self.move_speed
        if keys["D"]:
            strafeSpeed -= self.move_speed
        if keys["A"]:
            strafeSpeed += self.move_speed

        # Rotate
        self.yaw += yawSpeed * dt
        self.pitch = min(60, max(-60, self.pitch + pitchSpeed * dt))

        # Generate rotation
        self.cameraRotation = Mat3(
            gltypes.make_rotation_y(math.radians(self.yaw))
        ) * Mat3(gltypes.make_rotation_x(math.radians(self.pitch)))

        # Movement
        self.position += np.array(self.cameraRotation * [0, 0, 1]) * forwardSpeed * dt
        self.position += np.array(self.cameraRotation * [1, 0, 0]) * strafeSpeed * dt

    def ui(self):
        """No UI for this camera because I'm lazy
        See the above function for controls
        """
        pass

    def getWorldToViewMatrix(self):
        """Generate a worldToViewTransform matrix
        This is a simple looking in the direction of the camera
        """
        return self.make_lookFrom(self.cameraRotation * [0, 0, 1])
