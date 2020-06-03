from OpenGL.GL import *
from gltypes import vec3, normalize, make_translation, make_scale
import gltypes

import shaders
import imgui
import random

TEX_DIFFUSE = 0
TEX_SPECULAR = 1
TEX_NORMAL = 2  # Unused - normal maps aren't in this program (yet)
TEX_CUBEMAP = 4


class Object:
    """Basic object class
    This has some basic things that all objects can derive from

    Most useful functionality will be in the ObjModel class
    """

    position = gltypes.vec3(0, 0, 0)
    shader = None

    material_textures = {}
    material_shaders = {}

    def ui(self):
        """Super lame UI for adjusting the position of the object
        """
        if imgui.tree_node("Object", imgui.TREE_NODE_DEFAULT_OPEN):
            _, x = imgui.slider_float("X", self.position[0], -10, 10)
            _, y = imgui.slider_float("Y", self.position[1], -10, 10)
            _, z = imgui.slider_float("Z", self.position[2], -10, 10)
            self.position = gltypes.vec3(x, y, z)
            imgui.tree_pop()

    def bindTextures(self, shader, material):
        if material not in self.material_textures:
            return
        tex_data = self.material_textures[material]

        if isinstance(tex_data, dict):
            # Dictionary of textures, unpack
            if "diffuse" in tex_data:
                self.bindDiffuseTexture(shader, tex_data["diffuse"])

            if "specular" in tex_data:
                self.bindSpecularTexture(shader, tex_data["specular"])
            else:
                self.bindSpecularTexture(shader, -1)
        else:
            # Single texture, treat as diffuse only
            self.bindDiffuseTexture(shader, tex_data)

    def bindDiffuseTexture(self, shader, texture):
        shaders.setUniform(shader, "diffuseTexture", TEX_DIFFUSE)
        shaders.bindTexture(TEX_DIFFUSE, texture, GL_TEXTURE_2D)

    def bindSpecularTexture(self, shader, texture):
        shaders.setUniform(shader, "specularTexture", TEX_SPECULAR)
        shaders.bindTexture(TEX_SPECULAR, texture, GL_TEXTURE_2D)

    def applyShaderUniforms(self, shader, worldToView, lighting, transforms):
        lighting.applyLightingToShader(shader, worldToView)

        for name, value in transforms.items():
            shaders.setUniform(shader, name, value)


class ObjModel(Object):
    data = None

    def __init__(
        self,
        data,
        shader=None,
        position=gltypes.vec3(0, 0, 0),
        mat_textures=None,
        mat_shaders=None,
    ):
        """Build a vertex array object from an .obj model

        Arguments:
            data -- ObjData passed in from ObjLoader
        """
        self.shader = shader
        self.position = position
        self.material_textures = mat_textures or self.material_textures
        self.material_shaders = mat_shaders or self.material_shaders

        self.data = data
        self.numVerts = data.size

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
        viewToWorldRotationTransform = gltypes.Mat3(worldToViewTransform).inverse()

        # Apply transforms
        transforms = {
            "modelToClipTransform": modelToClipTransform,
            "modelToViewTransform": modelToViewTransform,
            "modelToViewNormalTransform": modelToViewNormalTransform,
            "viewToWorldRotationTransform": viewToWorldRotationTransform,
        }

        # For any additional material shaders, apply uniforms to them too
        # Things break if we do it in the actual draw step
        if self.material_shaders:
            for shader in self.material_shaders.values():
                glUseProgram(shader)
                self.applyShaderUniforms(
                    shader, worldToViewTransform, lighting, transforms
                )

        # Apply uniforms to default shader
        glUseProgram(self.shader)
        self.applyShaderUniforms(
            self.shader, worldToViewTransform, lighting, transforms
        )

        # Bind vertex array
        glBindVertexArray(self.vertexArrayObject)

        # Draw the arrays for each material group
        for material, offset, count in self.data.materialIndexes:
            # Some materials can have custom shaders assigned - how cool!
            shader = self.shader
            if material in self.material_shaders:
                shader = self.material_shaders[material]
                glUseProgram(shader)

            # Assign textures if applicable
            self.bindTextures(shader, material)

            # Draw the triangles
            glDrawArrays(GL_TRIANGLES, offset, count)

            # Cleanup custom shaders
            if material in self.material_shaders:
                glUseProgram(self.shader)

        # Cleanup after ourselves
        glBindVertexArray(0)
        glUseProgram(0)
