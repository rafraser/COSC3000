from OpenGL.GL import *
from glfw_keys import glfwKeyNames
import glfw

import imgui
from imgui.integrations.glfw import GlfwRenderer as ImGuiGlfwRenderer

from ObjLoader import load_obj
from camera import OrbitCamera
import objects
import gltypes
import shaders
import math


class LightingManager:
    sun_yaw = 25
    sun_pitch = -75
    sun_speed = 10
    sun_distance = 1000

    sun_color = gltypes.rgb(238, 200, 128)
    ambient_color = gltypes.rgb(103, 143, 184)
    ambient_strength = 0.5

    def position(self, worldToViewTransform):
        rotation = gltypes.Mat3(gltypes.make_rotation_y(math.radians(self.sun_yaw)))
        rotation = rotation * gltypes.Mat3(
            gltypes.make_rotation_x(math.radians(self.sun_pitch))
        )

        position = gltypes.vec3(0, 0, 0) + rotation * gltypes.vec3(
            0, 0, self.sun_distance
        )
        position = gltypes.transform_point(worldToViewTransform, position)
        return position

    def update(self, delta, keys):
        pass

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
        shaders.setUniform(shader, "sunColor", self.sun_color)
        shaders.setUniform(shader, "ambientColor", self.ambient_color)
        shaders.setUniform(shader, "ambientStrength", self.ambient_strength)


class ProgramManager:
    camera = None
    lighting = None
    children = []

    def __init__(self):
        """Initialise a program and start a rendering loop
        This creates a glfw window + an imgui context
        This also then handles an update and rendering loop

        Raises:
            EnvironmentError: if GLFW fails to initialize
            EnvironmentError: if GLFW fails to creat a window
        """
        if not glfw.init():
            raise EnvironmentError("Failed to initialize GLFW.")

        # Create window
        window = glfw.create_window(1600, 900, "Hello World!", None, None)
        if not window:
            glfw.terminate()
            raise EnvironmentError("Failed to create window.")

        # Add in an imgui context for debugging / UIs
        glfw.make_context_current(window)
        imgui.create_context()
        impl = ImGuiGlfwRenderer(window)

        # Build the scene and load resources
        self.buildScene()

        currentTime = glfw.get_time()
        # Window loop
        while not glfw.window_should_close(window):
            # Calculate delta time
            prevTime = currentTime
            currentTime = glfw.get_time()
            delta = currentTime - prevTime

            # Identify which keys are being pressed
            keyStates = {}
            for name, id in glfwKeyNames.items():
                keyStates[name] = glfw.get_key(window, id) == glfw.PRESS

            # Pass off to sub functions
            self.update(delta, keyStates)
            self.render(window)
            self.ui(window)

            # Render imgui stuff
            impl.render(imgui.get_draw_data())
            glfw.swap_buffers(window)
            glfw.poll_events()
            impl.process_inputs()

        # Exit gracefully once glfw wants to close the window
        glfw.terminate()

    def buildScene(self):
        """Build the scene and load in any required resources

        Lots to do in here
        """
        self.camera = OrbitCamera()
        self.lighting = LightingManager()

        coolShader = shaders.buildShader("sphere")
        coolModel = load_obj("models/shaderBall.obj")

        self.children.append(objects.ObjModel(coolModel, shader=coolShader))

    def update(self, delta, keys):
        """Update loop
        This takes in the key handler and passes it off to the camera

        Arguments:
            delta -- Time since the last frame
            keys -- Map of keynames that are currently pressed
        """
        self.camera.update(delta, keys)
        self.lighting.update(delta, keys)
        for child in self.children:
            if hasattr(child, "update"):
                child.update(delta, keys)

    def render(self, window):
        """Rendering loop

        Arguments:
            window -- Window handler to draw OpenGL stuff on
        """
        width, height = glfw.get_framebuffer_size(window)
        aspect = float(width) / float(height)

        # Update the camera perspective (in-case of window resize)
        self.camera.update_perspective(aspect=aspect)

        # Reset the scene
        glViewport(0, 0, width, height)
        glClearColor(0.05, 0.1, 0.05, 1.0)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_FRAMEBUFFER_SRGB)

        # Calculate camera matrices
        self.viewToClipTransform = self.camera.make_perspective()
        self.worldToViewTransform = self.camera.getWorldToViewMatrix()

        # Draw all children
        for child in self.children:
            if child.draw:
                child.draw(
                    self.worldToViewTransform, self.viewToClipTransform, self.lighting
                )

    def ui(self, window):
        """UI loop
        This creates the basic imgui frame and then passes off to child handlers

        Arguments:
            window -- Window handler to draw UI on
        """
        imgui.new_frame()
        imgui.begin("UI", 0)

        self.camera.ui()
        self.lighting.ui()
        for child in self.children:
            if child.ui:
                child.ui()

        imgui.end()
        imgui.render()


if __name__ == "__main__":
    input("Press ENTER to start!")
    ProgramManager()
