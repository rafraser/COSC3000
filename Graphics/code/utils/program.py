from OpenGL.GL import *
from utils.gltypes import Mat4, Vec3
from utils.camera import Camera
import glfw


class SceneProperties:
    width = None
    height = None
    clipTransform = None
    viewTransform = None

    def __init__(self, width, height):
        self.width = width
        self.height = height


class ProgramManager:
    camera = None
    children = []

    def __init__(self):
        if not glfw.init():
            print("Failed to initialize GLFW")
            return

        # Create a window for GLFW
        window = glfw.create_window(1600, 900, "Hello World!", None, None)
        if not window:
            print("Failed to create GLFW window")
            glfw.terminate()
            return

        glfw.make_context_current(window)

        # Create a new camera (with default settings)
        self.camera = Camera()

        # GLFW window loop
        while not glfw.window_should_close(window):
            self.render(window)
            glfw.swap_buffers(window)
            glfw.poll_events()

        glfw.terminate()

    def buildScene(self):
        pass

    def render(self, window):
        width, height = glfw.get_framebuffer_size(window)
        aspect = float(width) / float(height)

        self.camera.update_perspective(aspect=aspect)

        glViewport(0, 0, width, height)
        glClear(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT)

        # Setup some scene properties
        scene = SceneProperties(width, height)
        scene.clipTransform = self.camera.make_perspective()
        scene.viewTransform = self.camera.make_lookAt(Vec3(10, 0, 0))

        for child in self.children:
            child.render(scene, self)
