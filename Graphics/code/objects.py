from OpenGL.GL import *
from gltypes import vec3, normalize, make_translation, make_scale
import gltypes

import shaders
import imgui
import random


class Object:
    """Basic object class
    This has some basic things that all objects can derive from

    Most useful functionality will be in the ObjModel class
    """

    position = gltypes.vec3(0, 0, 0)
    shader = None

    def ui(self):
        """Super lame UI for adjusting the position of the object
        """
        if imgui.tree_node("Object", imgui.TREE_NODE_DEFAULT_OPEN):
            _, x = imgui.slider_float("X", self.position[0], -10, 10)
            _, y = imgui.slider_float("Y", self.position[1], -10, 10)
            _, z = imgui.slider_float("Z", self.position[2], -10, 10)
            self.position = gltypes.vec3(x, y, z)
            imgui.tree_pop()


class ObjModel(Object):
    data = None

    def __init__(self, data, shader=None):
        """Build a vertex array object from an .obj model

        Arguments:
            data -- ObjData passed in from ObjLoader
        """
        self.data = data
        self.numVerts = data.size
        self.shader = shader

        # Create the vertex array + buffers
        self.vertexArrayObject = glGenVertexArrays(1)
        glBindVertexArray(self.vertexArrayObject)

        shaders.createAndAddVertexArrayData(self.vertexArrayObject, data.positions, 0)
        shaders.createAndAddVertexArrayData(self.vertexArrayObject, data.normals, 1)
        shaders.createAndAddVertexArrayData(self.vertexArrayObject, data.uvs, 2)

    def draw(self, worldToViewTransform, viewToClipTransform, lighting):
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
        glUseProgram(self.shader)

        # Apply lighting uniforms to the shader
        lighting.applyLightingToShader(self.shader, worldToViewTransform)

        # Set shader uniforms
        shaders.setUniform(self.shader, "modelToClipTransform", modelToClipTransform)
        shaders.setUniform(self.shader, "modelToViewTransform", modelToViewTransform)
        shaders.setUniform(
            self.shader, "modelToViewNormalTransform", modelToViewNormalTransform
        )

        # Bind vertex array
        glBindVertexArray(self.vertexArrayObject)

        # Draw the arrays for each material group
        # TODO: Actual handling for the materials
        for material, offset, count in self.data.materialIndexes:
            glDrawArrays(GL_TRIANGLES, offset, count)

        # Cleanup after ourselves
        glBindVertexArray(0)
        glUseProgram(0)
