from OpenGL.GL import *
from glfw_keys import glfwKeyNames
import glfw

import imgui
from imgui.integrations.glfw import GlfwRenderer as ImGuiGlfwRenderer

from ObjLoader import load_obj
from camera import OrbitCamera
from lighting import LightingManager

import objects
import gltypes
import shaders
import math


class ProgramManager:
    camera = None
    lighting = None
    children = []
    textures = {}

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
        # Create camera & lighting manager
        self.camera = OrbitCamera()
        self.lighting = LightingManager()

        # Load up shaders and models
        coolShader = shaders.buildShader("PhongUntextured")
        coolShader2 = shaders.buildShader("PhongTexturedEnvmap")
        coolShader3 = shaders.buildShader("DiffuseTextured")

        groundModel = load_obj("models/ground.obj")
        building1Model = load_obj("models/building1.obj")
        building2Model = load_obj("models/building2.obj")

        # Load up ground textures
        ground_texture = {"ground": shaders.loadTexture("textures/ground.png")}

        # Load up textures required for the buildings
        building_textures = {
            "windows": {
                "diffuse": shaders.loadTexture("textures/building_test.png"),
                "specular": shaders.loadTexture("textures/building_spec.png"),
            },
            "rooftop": {
                "diffuse": shaders.loadTexture("textures/building_roof.png"),
                "specular": shaders.loadTexture("textures/no_specular.png"),
            },
        }

        building_shaders = {"rooftop": coolShader3}

        # Create the renderable objects
        ground = objects.ObjModel(
            groundModel, shader=coolShader3, mat_textures=ground_texture
        )

        building1 = objects.ObjModel(
            building1Model,
            shader=coolShader2,
            position=gltypes.vec3(0, 0, 0),
            mat_textures=building_textures,
            mat_shaders=building_shaders,
        )

        building2 = objects.ObjModel(
            building2Model,
            shader=coolShader2,
            position=gltypes.vec3(100, 0, 0),
            mat_textures=building_textures,
            mat_shaders=building_shaders,
        )

        # Build renderable objects using models + shaders
        self.children.append(building1)
        self.children.append(building2)
        self.children.append(ground)

        # Load cubemap textures and assign them to the lighting manager
        self.textures["dayCubemap"] = shaders.loadCubemap("textures/cube/day_FACE.png")
        self.textures["nightCubemap"] = nightCubemap = shaders.loadCubemap(
            "textures/cube/night_FACE.png"
        )
        self.lighting.day_texture = self.textures["dayCubemap"]
        self.lighting.night_texture = self.textures["nightCubemap"]

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
