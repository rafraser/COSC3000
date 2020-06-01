from OpenGL.GL import *
from gltypes import vec3, normalize, make_translation, make_scale
import gltypes

import shaders
import imgui


class Object:
    position = gltypes.vec3(0, 0, 0)
    shader = None

    def __init__(self, position):
        pass

    def assign_shader(self, shader):
        pass

    def draw(self, scene):
        pass


class ObjModel(Object):
    data = None

    def __init__(self, data):
        self.data = data
        self.numVerts = data.size

        # Create the vertex array + buffers
        self.vertexArrayObject = glGenVertexArrays(1)
        glBindVertexArray(self.vertexArrayObject)

        shaders.createAndAddVertexArrayData(self.vertexArrayObject, data.positions, 0)
        shaders.createAndAddVertexArrayData(self.vertexArrayObject, data.normals, 1)
        shaders.createAndAddVertexArrayData(self.vertexArrayObject, data.uvs, 2)

    def draw(self, worldToViewTransform, viewToClipTransform):
        # For Obj models, each model often has multiple different materials in use
        # For efficiency, we render each material all at once
        # For improved performance -> handle this on a 'global' scale
        (x, y, z) = (self.position[0], self.position[1], self.position[2])
        modelToWorldTransform = make_translation(x, y, z)

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

        # Bind vertex array
        glBindVertexArray(self.vertexArrayObject)

        # Draw the arrays for each material group
        # TODO: Material handling
        for material, offset, count in self.data.materialIndexes:
            glDrawArrays(GL_TRIANGLES, offset, count)

        glUseProgram(0)

    def drawUi(self):
        if imgui.tree_node("Sphere", imgui.TREE_NODE_DEFAULT_OPEN):
            _, x = imgui.slider_float("X", self.position[0], -10, 10)
            _, y = imgui.slider_float("Y", self.position[1], -10, 10)
            _, z = imgui.slider_float("Z", self.position[2], -10, 10)
            self.position = gltypes.vec3(x, y, z)
            imgui.tree_pop()
