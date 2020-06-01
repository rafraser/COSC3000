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


class ProgramManager:
    def __init__(self):
        if not glfw.init():
            raise EnvironmentError("Failed to initialize GLFW.")

        # Create window
        window = glfw.create_window(1600, 900, "Hello World!", None, None)
        if not window:
            glfw.terminate()
            raise EnvironmentError("Failed to create window.")

        glfw.make_context_current(window)
        imgui.create_context()
        impl = ImGuiGlfwRenderer(window)

        self.buildScene()

        currentTime = glfw.get_time()

        # Window loop
        while not glfw.window_should_close(window):
            prevTime = currentTime
            currentTime = glfw.get_time()
            delta = currentTime - prevTime

            # Key bindings
            keyStates = {}
            for name, id in glfwKeyNames.items():
                keyStates[name] = glfw.get_key(window, id) == glfw.PRESS

            # Handle rendering
            self.update(delta, keyStates)
            self.render(window)
            self.ui(window)

            impl.render(imgui.get_draw_data())
            glfw.swap_buffers(window)
            glfw.poll_events()
            impl.process_inputs()

        glfw.terminate()

    def buildScene(self):
        coolShader = shaders.buildShader("sphere", "sphere", {})
        coolModel = load_obj("models/building.obj")

        self.sphere = objects.ObjModel(coolModel)
        self.sphere.shader = coolShader
        self.camera = OrbitCamera([0, 0, 0], 100, 0.0, 0.0)

    def update(self, delta, keys):
        self.camera.update(delta, keys)

    def render(self, window):
        width, height = glfw.get_framebuffer_size(window)
        aspect = float(width) / float(height)

        glViewport(0, 0, width, height)
        glClearColor(0.05, 0.1, 0.05, 1.0)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glEnable(GL_FRAMEBUFFER_SRGB)

        self.viewToClipTransform = self.camera.make_perspective()
        self.worldToViewTransform = self.camera.getWorldToViewMatrix()

        # self.camera.target = self.sphere.position
        self.sphere.draw(self.worldToViewTransform, self.viewToClipTransform)

    def ui(self, window):
        imgui.new_frame()
        imgui.begin("UI", 0)

        self.camera.drawUi()
        self.sphere.drawUi()

        imgui.end()
        imgui.render()


if __name__ == "__main__":
    input("Press ENTER to start!")
    ProgramManager()
