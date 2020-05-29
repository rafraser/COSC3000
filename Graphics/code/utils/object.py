from OpenGL.GL import *
from OpenGL.arrays import vbo
from utils.gltypes import Vec3, Mat4
import utils.shader as shader
import numpy as np
import ctypes


class RenderObject:
    positions = np.array([(-1, -1), (-1, +1), (+1, -1), (+1, +1)], dtype=np.float32)
    colors = np.array(
        [(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (1, 1, 0, 1)], dtype=np.float32
    )

    attributes = {
        "positionAttribute": 0,
        "colorAttribute": 1,
    }

    def loadShader(self, filename):
        self.shader = shader.buildShader(filename, filename, self.attributes)

    def buildBuffers(self):
        self.loadShader("basic")

        self.vertexArrayObject = glGenVertexArrays(1)
        glBindVertexArray(self.vertexArrayObject)

        # Bind attributes
        self.positionBuffer = shader.createBindVertexAttribArrayFloat(self.positions, 0)
        self.colorBuffer = shader.createBindVertexAttribArrayFloat(self.colors, 1)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def render(self):
        glBindVertexArray(self.vertexArrayObject)
        glUseProgram(self.shader)

        glDrawArrays(GL_TRIANGLES, 0, 4)
        glUseProgram(0)
