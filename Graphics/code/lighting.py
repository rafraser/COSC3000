from OpenGL.GL import GL_TEXTURE_CUBE_MAP
from objects import TEX_CUBEMAP
import gltypes
import shaders
import imgui
import math

from gltypes import rgb, hexc


def color_gradient_helper(gradient, t):
    for i in range(len(gradient)):
        if t <= gradient[i][0]:
            # Intepolate between stop i - 1 and stop i
            d = (t - gradient[i - 1][0]) / (gradient[i][0] - gradient[i - 1][0])
            c1 = gradient[i - 1][1]
            c2 = gradient[i][1]

            # These should already be 0 .. 1 coordinates
            r = c1[0] + (c2[0] - c1[0]) * d
            g = c1[1] + (c2[1] - c1[1]) * d
            b = c1[2] + (c2[2] - c1[2]) * d
            return gltypes.vec3(r, g, b)

    # Return last color if all else has gone terribly wrong
    return gradient[-1][1]


def float_gradient_helper(gradient, t):
    for i in range(len(gradient)):
        if t <= gradient[i][0]:
            # Intepolate between stop i - 1 and stop i
            d = (t - gradient[i - 1][0]) / (gradient[i][0] - gradient[i - 1][0])
            return gradient[i - 1][1] + (gradient[i][1] - gradient[i - 1][1]) * d

    # Return last color if all else has gone terribly wrong
    return gradient[-1][1]


class LightingManager:
    sun_yaw = -50.0
    sun_pitch = -75
    sun_speed = 10
    sun_distance = 1000

    sun_gradient = [
        (0.00, hexc("#0f0f0f")),
        (0.15, hexc("#dc730f")),
        (0.30, hexc("#fff096")),
        (0.50, hexc("#d2e1f0")),
        (0.70, hexc("#fff096")),
        (0.85, hexc("#dc730f")),
        (1.00, hexc("#0f0f0f")),
    ]

    ambient_gradient = [
        (0.00, hexc("#404040")),
        (0.05, hexc("#280537")),
        (0.15, hexc("#ffe1c8")),
        (0.50, hexc("#c8d2ff")),
        (0.85, hexc("#ffe1c8")),
        (0.95, hexc("#280537")),
        (1.00, hexc("#404040")),
    ]

    ambient_strength_gradient = [
        (0.00, 0.25),
        (0.15, 0.1),
        (0.50, 0.2),
        (0.85, 0.1),
        (1.00, 0.25),
    ]

    night_sun_color = hexc("#0f0f0f")
    night_sun_pitch = -85
    night_ambient_color = hexc("#404040")
    night_ambient_strength = 0.25

    day_texture = None
    night_texture = None

    def is_night(self):
        return self.sun_pitch < 180

    def get_sun_color(self):
        if self.is_night():
            return self.night_sun_color
        else:
            day_stage = (self.sun_pitch - 180) / 180
            return color_gradient_helper(self.sun_gradient, day_stage)

    def get_ambient_color(self):
        if self.is_night():
            return self.night_ambient_color
        else:
            day_stage = (self.sun_pitch - 180) / 180
            return color_gradient_helper(self.ambient_gradient, day_stage)

    def get_ambient_strength(self):
        if self.is_night():
            return self.night_ambient_strength
        else:
            day_stage = (self.sun_pitch - 180) / 180
            return float_gradient_helper(self.ambient_strength_gradient, day_stage)

    def position(self, worldToViewTransform):
        pitch = (self.sun_pitch + 180) if self.is_night() else self.sun_pitch
        rotation = gltypes.Mat3(gltypes.make_rotation_y(math.radians(self.sun_yaw)))
        rotation = rotation * gltypes.Mat3(gltypes.make_rotation_x(math.radians(pitch)))

        position = gltypes.vec3(0, 0, 0) + rotation * gltypes.vec3(
            0, 0, self.sun_distance
        )
        position = gltypes.transform_point(worldToViewTransform, position)
        return position

    def update(self, delta, keys):
        speed = self.sun_speed * 2.5 if self.is_night() else self.sun_speed
        self.sun_pitch = self.sun_pitch + (delta * speed)
        self.sun_pitch = self.sun_pitch % 360

    def ui(self):
        if imgui.tree_node("Lighting", imgui.TREE_NODE_DEFAULT_OPEN):
            _, self.sun_yaw = imgui.slider_float(
                "Yaw (Deg)", self.sun_yaw, -180.00, 180.0
            )
            _, self.sun_pitch = imgui.slider_float(
                "Pitch (Deg)", self.sun_pitch, -180.00, 180.0
            )
            imgui.tree_pop()

    def applyLightingToShader(self, shader, worldToViewTransform):
        shaders.setUniform(shader, "sunPosition", self.position(worldToViewTransform))
        shaders.setUniform(shader, "sunColor", self.get_sun_color())
        shaders.setUniform(shader, "ambientColor", self.get_ambient_color())
        shaders.setUniform(shader, "ambientStrength", self.get_ambient_strength())

        # Environment cubemaps
        if self.is_night() and self.night_texture:
            shaders.setUniform(shader, "environmentCubeTexture", TEX_CUBEMAP)
            shaders.bindTexture(TEX_CUBEMAP, self.night_texture, GL_TEXTURE_CUBE_MAP)
        elif self.day_texture:
            shaders.setUniform(shader, "environmentCubeTexture", TEX_CUBEMAP)
            shaders.bindTexture(TEX_CUBEMAP, self.day_texture, GL_TEXTURE_CUBE_MAP)
