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
        if True:
            return

        if imgui.tree_node("Object", imgui.TREE_NODE_DEFAULT_OPEN):
            _, x = imgui.slider_float("X", self.position[0], -10, 10)
            _, y = imgui.slider_float("Y", self.position[1], -10, 10)
            _, z = imgui.slider_float("Z", self.position[2], -10, 10)
            self.position = gltypes.vec3(x, y, z)
            imgui.tree_pop()

    def bindTextures(self, shader, material):
        """Bind all relevant textures for a material to the given shader

        Arguments:
            shader {int} -- Shader
            material {str} -- Material name to assign textures to
        """
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
        """Bind a single diffuse texture to a shader

        Arguments:
            shader {int} -- Shader
            texture {int} -- Texture ID to assign
        """
        shaders.setUniform(shader, "diffuseTexture", TEX_DIFFUSE)
        shaders.bindTexture(TEX_DIFFUSE, texture, GL_TEXTURE_2D)

    def bindSpecularTexture(self, shader, texture):
        """Bind a single specular texture to a shader

        Arguments:
            shader {int} -- Shader
            texture {int} -- Texture ID to assign
        """
        shaders.setUniform(shader, "specularTexture", TEX_SPECULAR)
        shaders.bindTexture(TEX_SPECULAR, texture, GL_TEXTURE_2D)

    def applyShaderUniforms(self, shader, transforms):
        """Utility function to assign a list of uniforms to a shader

        Arguments:
            shader {int} -- Shader
            transforms {dict} -- Name, value pairs of uniforms to assign
        """
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

    def get_material_shader(self, material):
        """Get the shader for a given material

        Arguments:
            material {str} -- Material name to lookup shader

        Returns:
            int -- Shader ID
        """
        # Check if we have the given material
        materials = [x[0] for x in self.data.materialIndexes]
        if material not in materials:
            return None

        if material in self.material_shaders:
            return self.material_shaders[material]
        else:
            return self.shader

    def draw_material(
        self, material, shader, worldToViewTransform, viewToClipTransform,
    ):
        """New and improved drawing function!
        This will only draw faces with a given material
        See main.py for some more complexity

        Arguments:
            material {[type]} -- [description]
            shader {[type]} -- [description]
            worldToViewTransform {[type]} -- [description]
            viewToClipTransform {[type]} -- [description]
        """
        # Check if we have the given material
        materials = [x[0] for x in self.data.materialIndexes]
        if material not in materials:
            return

        # Calculate transforms
        # These need to be done per-object unfortunately
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
        worldToModelTransform = gltypes.Mat3(modelToWorldTransform).inverse()

        transforms = {
            "modelToClipTransform": modelToClipTransform,
            "modelToViewTransform": modelToViewTransform,
            "modelToViewNormalTransform": modelToViewNormalTransform,
            "worldToModelTransform": worldToModelTransform,
        }

        # Apply model transformations
        self.applyShaderUniforms(shader, transforms)

        # Draw only the specific material
        glBindVertexArray(self.vertexArrayObject)
        for matidx, offset, count in self.data.materialIndexes:
            if matidx == material:
                glDrawArrays(GL_TRIANGLES, offset, count)
                break

        glBindVertexArray(0)
