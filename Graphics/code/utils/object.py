from OpenGL.GL import *
from gltypes import Vec3, Mat4


class RenderObject:
    position = Vec3(0, 0, 0)
    vertices = []

    def render(self, scene):
        if self.shader:
            glUseProgram(self.shader)
            shader.setCommonUniforms(self.shader, scene)

        self.preRenderObject()

        glBindVertexArray(self.vertices)
        glDrawElements(GL_TRIANGLES, 0, GL_UNSIGNED_INT, None)

        glBindVertexArray(0)
        glUseProgram(0)

    def preRenderObject(self):
        pass

    def addVertex(self, v):
        self.vertices.append(v)

    def addCube(self, b1, b2):
        (x1, y1, z1) = b1.data
        (x2, y2, z2) = b2.data

        cube = []
        cube.append(Vec3(x1, y1, z1))
        cube.append(Vec3(x1, y2, z1))

        cube.append(Vec3(x2, y1, z1))
        cube.append(Vec3(x2, y2, z1))

        cube.append(Vec3(x2, y1, z2))
        cube.append(Vec3(x2, y2, z2))

        cube.append(Vec3(x1, y1, z2))
        cube.append(Vec3(x1, y2, z2))

        cube.append(Vec3(x1, y1, z1))
        cube.append(Vec3(x1, y2, z1))
        self.vertices += cube
    
    def prepareBuffer():
        pass
        self.vertexArray = shader.createVertexArrayObject()
        self.vertexData =
        self.indexData = shader.createAndAddIndexArray(self.vertexArray, 


class Cube(RenderObject):
    def __init__(self):
        addCube(self, Vec3(-1, -1, -1), Vec3(1, 1, 1))
