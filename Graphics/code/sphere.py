from OpenGL.GL import *
from objects import Object
from gltypes import vec3, normalize, make_translation, make_scale
import gltypes
import shaders
import imgui


def subDivide(dest, v0, v1, v2, level):
    if level:
        v3 = normalize(v0 + v1)
        v4 = normalize(v1 + v2)
        v5 = normalize(v2 + v0)

        subDivide(dest, v0, v3, v5, level - 1)
        subDivide(dest, v3, v4, v5, level - 1)
        subDivide(dest, v3, v1, v4, level - 1)
        subDivide(dest, v5, v4, v2, level - 1)
    else:
        dest.append(v0)
        dest.append(v1)
        dest.append(v2)


def createSphere(numSubDivisionLevels):
    sphereVerts = []

    # The root level sphere is formed from 8 triangles in a diamond shape (two pyramids)
    subDivide(
        sphereVerts, vec3(0, 1, 0), vec3(0, 0, 1), vec3(1, 0, 0), numSubDivisionLevels
    )
    subDivide(
        sphereVerts, vec3(0, 1, 0), vec3(1, 0, 0), vec3(0, 0, -1), numSubDivisionLevels
    )
    subDivide(
        sphereVerts, vec3(0, 1, 0), vec3(0, 0, -1), vec3(-1, 0, 0), numSubDivisionLevels
    )
    subDivide(
        sphereVerts, vec3(0, 1, 0), vec3(-1, 0, 0), vec3(0, 0, 1), numSubDivisionLevels
    )

    subDivide(
        sphereVerts, vec3(0, -1, 0), vec3(1, 0, 0), vec3(0, 0, 1), numSubDivisionLevels
    )
    subDivide(
        sphereVerts, vec3(0, -1, 0), vec3(0, 0, 1), vec3(-1, 0, 0), numSubDivisionLevels
    )
    subDivide(
        sphereVerts,
        vec3(0, -1, 0),
        vec3(-1, 0, 0),
        vec3(0, 0, -1),
        numSubDivisionLevels,
    )
    subDivide(
        sphereVerts, vec3(0, -1, 0), vec3(0, 0, -1), vec3(1, 0, 0), numSubDivisionLevels
    )

    return sphereVerts


class Sphere(Object):
    radius = 1

    def __init__(self, radius):
        self.radius = radius

        sphereVerts = createSphere(4)
        self.numVerts = len(sphereVerts)
        self.vertexArrayObject = shaders.createVertexArrayObject()
        shaders.createAndAddVertexArrayData(self.vertexArrayObject, sphereVerts, 0)
        shaders.createAndAddVertexArrayData(self.vertexArrayObject, sphereVerts, 1)

    def draw(self, worldToViewTransform, viewToClipTransform):
        # Calculate world positioning
        # This also adds in scaling
        (x, y, z) = (self.position[0], self.position[1], self.position[2])
        modelToWorldTransform = make_translation(x, y, z) * make_scale(
            self.radius, self.radius, self.radius
        )
        # Calculate transformations
        modelToClipTransform = (
            viewToClipTransform * worldToViewTransform * modelToWorldTransform
        )
        modelToViewTransform = worldToViewTransform * modelToWorldTransform
        modelToViewNormalTransform = (
            gltypes.Mat3(modelToViewTransform).transpose().inverse()
        )

        # Set shader uniforms
        glUseProgram(self.shader)
        shaders.setUniform(self.shader, "modelToClipTransform", modelToClipTransform)
        shaders.setUniform(self.shader, "modelToViewTransform", modelToViewTransform)
        shaders.setUniform(
            self.shader, "modelToViewNormalTransform", modelToViewNormalTransform
        )

        # Bind vertex array and draw
        glBindVertexArray(self.vertexArrayObject)
        glDrawArrays(GL_TRIANGLES, 0, self.numVerts)
        glUseProgram(0)

    def ui(self):
        if imgui.tree_node("Sphere", imgui.TREE_NODE_DEFAULT_OPEN):
            _, x = imgui.slider_float("X", self.position[0], -10, 10)
            _, y = imgui.slider_float("Y", self.position[1], -10, 10)
            _, z = imgui.slider_float("Z", self.position[2], -10, 10)
            self.position = gltypes.vec3(x, y, z)
            imgui.tree_pop()
