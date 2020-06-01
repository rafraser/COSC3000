from OpenGL.GL import *
from ctypes import c_float
import numpy as np
import gltypes


def compileAndAttachShader(shaderProgram, shaderType, shaderFile):
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


def buildShader(vertexShaderFile, fragmentShaderFile, attributes):
    shader = glCreateProgram()
    vertexState = compileAndAttachShader(shader, GL_VERTEX_SHADER, vertexShaderFile)
    fragmentState = compileAndAttachShader(
        shader, GL_FRAGMENT_SHADER, fragmentShaderFile
    )

    if vertexState and fragmentState:
        # Link attributes
        for name, loc in attributes.items():
            glBindAttribLocation(shader, loc, name)

        glLinkProgram(shader)
        print("Shaders successfully built! Probably.")
        return shader
    else:
        glDeleteProgram(shader)
        raise EnvironmentError("Shader compliation error")


def setUniform(shader, uniformName, value):
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


def uniform(shader, uniforms):
    for name, value in uniforms.items():
        setUniform(shader, name, value)


def flatten(*lll):
    return [u for ll in lll for l in ll for u in l]


def uploadFloatData(bufferObject, floatData):
    flatData = flatten(floatData)
    data_buffer = (c_float * len(flatData))(*flatData)
    glBindBuffer(GL_ARRAY_BUFFER, bufferObject)
    glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)


def createVertexArrayObject():
    return glGenVertexArrays(1)


def createAndAddVertexArrayData(vertexArrayObject, data, attributeIndex):
    glBindVertexArray(vertexArrayObject)
    buffer = glGenBuffers(1)
    uploadFloatData(buffer, data)

    glBindBuffer(GL_ARRAY_BUFFER, buffer)
    glVertexAttribPointer(attributeIndex, len(data[0]), GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(attributeIndex)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    return buffer
