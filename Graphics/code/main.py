from OpenGL.GL import *
from glfw_keys import glfwKeyNames
import glfw

import imgui
from imgui.integrations.glfw import GlfwRenderer as ImGuiGlfwRenderer

from ObjLoader import load_obj
from camera import FreeCamera, OrbitCamera
from lighting import LightingManager

import objects
import gltypes
import shaders
import math
import random


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
        # Create camera
        self.camera = FreeCamera()

        # Create lighting manager
        # This includes two sets of cubemap textures
        # Load cubemap textures and assign them to the lighting manager
        self.lighting = LightingManager()
        self.textures["dayCubemap"] = shaders.loadCubemap("textures/cube/day_FACE.png")
        self.textures["nightCubemap"] = nightCubemap = shaders.loadCubemap(
            "textures/cube/night_FACE.png"
        )
        self.lighting.day_texture = self.textures["dayCubemap"]
        self.lighting.night_texture = self.textures["nightCubemap"]

        # Compile shaders
        phongShader = shaders.buildShader("PhongTexturedEnvmap")
        diffuseShader = shaders.buildShader("DiffuseTextured")
        interiorShader = shaders.buildShader("InteriorMapping")
        unlitShader = shaders.buildShader("UnlitTextured")

        # Create the ground
        ground_texture = {"ground": shaders.loadTexture("textures/ground.png")}
        groundModel = load_obj("models/ground.obj")
        ground = objects.ObjModel(
            groundModel, shader=diffuseShader, mat_textures=ground_texture
        )
        self.children.append(ground)

        # Load up textures for the buildings
        building_textures = {
            "windows": {
                "diffuse": shaders.loadTexture("textures/building_test.png"),
                "specular": shaders.loadTexture("textures/building_spec.png"),
            },
            "rooftop": shaders.loadTexture("textures/building_roof.png"),
        }
        building_shaders = {"rooftop": diffuseShader}

        # Load up textures for the lanterns
        lantern_textures = {
            "lamp": shaders.loadTexture("textures/lamp.png"),
            "light": shaders.loadTexture("textures/light.png"),
        }

        lantern_shaders = {"light": unlitShader}

        # Pass over to the city builder function
        self.generate_city(
            interiorShader,
            building_textures,
            building_shaders,
            diffuseShader,
            lantern_textures,
            lantern_shaders,
        )

        # Build material groupings for efficient rendering
        self.process_material_groupings()

    def generate_city(
        self,
        buildingShader,
        building_textures,
        building_shaders,
        lanternShader,
        lantern_textures,
        lantern_shaders,
    ):
        # Load building models
        models = [load_obj("models/building1.obj"), load_obj("models/building2.obj")]

        # Load lamp model
        lamp_model = load_obj("models/lantern.obj")

        for xx in range(-300, 300, 200):
            for zz in range(-300, 300, 200):
                # This position marks the center of each concrete block
                # Each concrete block should have 8 street lights and 4 buildings
                position = gltypes.vec3(xx, 0, zz)

                for bpos in [(-45, -45), (-45, 45), (45, -45), (45, 45)]:
                    building_pos = position + gltypes.vec3(bpos[0], 0, bpos[1])
                    self.add_model(
                        random.choice(models),
                        buildingShader,
                        building_pos,
                        building_textures,
                        building_shaders,
                    )

                for lpos in [
                    (-70, -70),
                    (-70, 0),
                    (-70, 70),
                    (70, -70),
                    (70, 0),
                    (70, 70),
                    (0, -70),
                    (0, 70),
                ]:
                    lantern_pos = position + gltypes.vec3(lpos[0], 0, lpos[1])
                    self.add_model(
                        lamp_model,
                        lanternShader,
                        lantern_pos,
                        lantern_textures,
                        lantern_shaders,
                    )

    def add_model(self, model, defaultShader, position, textures, shaders):
        renderable_model = objects.ObjModel(
            model,
            shader=defaultShader,
            position=position,
            mat_textures=textures,
            mat_shaders=shaders,
        )
        self.children.append(renderable_model)

    def process_material_groupings(self):
        """Process all material groupings for the scene
        This only needs to be done when new materials are added to the scene

        This allows for more efficient rendering later on! Very important.
        """
        self.scene_materials = []
        for child in self.children:
            for material in [x[0] for x in child.data.materialIndexes]:
                if material not in self.scene_materials:
                    self.scene_materials.append(material)

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
        viewToWorldRotationTransform = gltypes.Mat3(self.worldToViewTransform).inverse()

        # Draw all children in an intelligent manner - draw by material!
        for material in self.scene_materials:
            # Get the shader from the first object
            shader = None
            for child in self.children:
                shader = child.get_material_shader(material)
                if shader is not None:
                    # Found the shader - bind textures while we're here
                    glUseProgram(shader)
                    child.bindTextures(shader, material)
                    break

            # Assign some global uniforms to this shader
            self.lighting.applyLightingToShader(shader, self.worldToViewTransform)
            shaders.setUniform(shader, "cameraPosition", self.camera.position)
            shaders.setUniform(
                shader, "viewToWorldRotationTransform", viewToWorldRotationTransform
            )

            # Todo: setting global uniforms (eg. lighting)
            for i, child in enumerate(self.children):
                if child.draw_material:
                    child.draw_material(
                        material,
                        shader,
                        self.worldToViewTransform,
                        self.viewToClipTransform,
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
