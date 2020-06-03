from OpenGL.GL import *
from ctypes import c_float
from PIL import Image
import numpy as np
import gltypes


def compileAndAttachShader(shaderProgram, shaderType, shaderFile):
    """Compile and attach a given vertex or fragment shader

    Arguments:
        shaderProgram -- shader program to attach outcome to
        shaderType -- GL_VERTEX_SHADER or GL_FRAGMENT_SHADER
        shaderFile -- filename to load filename.vert or filename.frag

    Raises:
        EnvironmentError: if shaders fail to compile

    Returns:
        Boolean if the shader was succesfully attached
    """
    # Load and compile shader source
    shader = glCreateShader(shaderType)
    shaderExtensions = {GL_VERTEX_SHADER: ".vert", GL_FRAGMENT_SHADER: ".frag"}
    with open("shaders/" + shaderFile + shaderExtensions.get(shaderType)) as f:
        shaderText = f.read()
        glShaderSource(shader, shaderText)
        glCompileShader(shader)

    # Raise an error if the shader did not compile successfully
    compileState = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if not compileState:
        err = glGetShaderInfoLog(shader).decode()
        print(err)
        raise EnvironmentError("Shader compliation error")

    # Attach the shader to the program
    glAttachShader(shaderProgram, shader)
    glDeleteShader(shader)
    return True


def buildShader(filename):
    """Build a shader program given a shader filename
    This will attach the corresponding shaders/file.vert and shaders/file.frag

    Arguments:
        filename -- Filename to load corresponding shader files from

    Raises:
        EnvironmentError: if shaders fail to compile

    Returns:
        Shader program
    """
    shader = glCreateProgram()
    vertexState = compileAndAttachShader(shader, GL_VERTEX_SHADER, filename)
    fragmentState = compileAndAttachShader(shader, GL_FRAGMENT_SHADER, filename)

    if vertexState and fragmentState:
        glLinkProgram(shader)
        print("Shaders successfully built! Probably.")
        return shader
    else:
        glDeleteProgram(shader)
        raise EnvironmentError("Shader compliation error")


def setUniform(shader, uniformName, value):
    """Set a uniform value on a shader

    Arguments:
        shader -- Shader program to set
        uniformName -- Name of uniform to set
        value -- Value to set uniform to
    """
    loc = glGetUniformLocation(shader, uniformName)
    if isinstance(value, float):
        glUniform1f(loc, value)
    elif isinstance(value, int):
        glUniform1i(loc, value)
    elif isinstance(value, (np.ndarray, list)):
        if len(value) == 2:
            glUniform2fv(loc, 1, value)
        if len(value) == 3:
            glUniform3fv(loc, 1, value)
        if len(value) == 4:
            glUniform4fv(loc, 1, value)
    elif isinstance(value, (gltypes.Mat3, gltypes.Mat4)):
        value._set_open_gl_uniform(loc)
    else:
        assert False


def setUniforms(shader, uniforms):
    """Utility function to set multiple uniforms at once

    Arguments:
        shader -- Shader program to set uniforms on
        uniforms -- Dictonary of uniform name / value pairs
    """
    for name, value in uniforms.items():
        setUniform(shader, name, value)


def flatten(*lll):
    """Flatten a list of lists, up to three dimensions

    Returns:
        Flattened list object
    """
    return [u for ll in lll for l in ll for u in l]


def uploadFloatData(bufferObject, floatData):
    """Upload float data to a buffer

    Arguments:
        bufferObject -- Buffer object
        floatData -- Raw float data
    """
    flatData = flatten(floatData)
    data_buffer = (c_float * len(flatData))(*flatData)
    glBindBuffer(GL_ARRAY_BUFFER, bufferObject)
    glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)


def createVertexArrayObject():
    """yep

    Returns:
        new vertex array object
    """
    return glGenVertexArrays(1)


def createAndAddVertexArrayData(vertexArrayObject, data, attributeIndex):
    """Add data to a given vertex array

    Arguments:
        vertexArrayObject -- Vertex array object to add data to
        data -- Float data to upload
        attributeIndex -- Attribute index to append data to

    Returns:
        Resulting data buffer attached to the vertex array
    """
    glBindVertexArray(vertexArrayObject)
    buffer = glGenBuffers(1)
    uploadFloatData(buffer, data)

    glBindBuffer(GL_ARRAY_BUFFER, buffer)
    glVertexAttribPointer(attributeIndex, len(data[0]), GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(attributeIndex)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return buffer


def loadTexImage(tex, im):
    data = im.tobytes("raw", "RGBX" if im.mode == "RGB" else "RGBA", 0, -1)
    glTexImage2D(
        tex,
        0,
        GL_SRGB_ALPHA,
        im.size[0],
        im.size[1],
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        data,
    )


def loadTexture(filename):
    tex = glGenTextures(1)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, tex)

    try:
        im = Image.open(filename).convert("RGBA")
        loadTexImage(GL_TEXTURE_2D, im)

        glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)
        return tex
    except Exception as e:
        print(e)
        raise EnvironmentError("Failed to load texture")


def loadCubemap(basename):
    tex = glGenTextures(1)
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_CUBE_MAP, tex)

    texSuffixFaceMap = {
        "px": GL_TEXTURE_CUBE_MAP_POSITIVE_X,
        "nx": GL_TEXTURE_CUBE_MAP_NEGATIVE_X,
        "py": GL_TEXTURE_CUBE_MAP_POSITIVE_Y,
        "ny": GL_TEXTURE_CUBE_MAP_NEGATIVE_Y,
        "pz": GL_TEXTURE_CUBE_MAP_POSITIVE_Z,
        "nz": GL_TEXTURE_CUBE_MAP_NEGATIVE_Z,
    }

    try:
        for suffix, face in texSuffixFaceMap.items():
            facename = basename.replace("_FACE", "_" + suffix)
            im = Image.open(facename)
            im = im.transpose(Image.FLIP_TOP_BOTTOM)
            loadTexImage(face, im)

        glGenerateMipmap(GL_TEXTURE_CUBE_MAP)
        glBindTexture(GL_TEXTURE_CUBE_MAP, 0)
        return tex
    except:
        raise EnvironmentError("Failed to load texture")


def bindTexture(unit, id, textype=GL_TEXTURE_2D):
    glActiveTexture(GL_TEXTURE0 + unit)
    glBindTexture(textype, id)
