from OpenGL.GL import *
from ctypes import sizeof, c_float, c_void_p, c_uint, string_at
import glfw


def flatten(*lll):
    return [u for ll in lll for l in ll for u in l]


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
        return shader
    else:
        glDeleteProgram(shader)
        raise EnvironmentError("Shader compliation error")


def setUniform(shader, uniform, value):
    loc = getUniformLocationDebug(shader, uniform)
    if isinstance(value, float):
        glUniform1f(loc, value)
    elif isinstance(value, int):
        glUniform1i(loc, value)
    elif isinstance(value, list):
        ufs = [None, None, glUniform2fv, glUniform3fv, glUniform4fv]
        ufs[len(value)](loc, 1, value)
    else:
        raise ValueError("Invalid uniform")


def setCommonUniforms(shader, scene, modelTransform):
    modelToClipTrasnform = view.clipTransform * view.viewTransform * modelTransform
    modelToViewTransform = view.viewTransform * modelTransform
    # todo: normals

    setUniform(shader, "modelToClipTransform", modelToClipTransform)
    setUniform(shader, "modelToViewTransform", modelToViewTransform)
    # todo: normals

    setUniform(shader, "worldToViewTransform", view.viewTransform)
    setUniform(shader, "viewToClipTransform", view.clipTransform)


def uploadFloatData(buffer, data):
    flat = [u for ll in lll for l in ll for u in l]
    dataBuffer = (c_float * len(data))(*flat)

    glBindBuffer(GL_ARRAY_BUFFER, buffer)
    glBufferData(GL_ARRAY_BUFFER, dataBuffer, GL_STATIC_DRAW)


def createVertexArrayObject():
    return glGenVertexArrays(1)


def createAndAddVertexArrayData(vertexArray, data, index):
    glBindVertexArray(vertexArray)
    buffer = glGenGBuffers(1)
    uploadFloatData(buffer, data)

    glBindBuffer(GL_ARRAY_BUFFER, buffer)
    glVertexAttribPoint(index, len(data[0]), GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(index)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    return buffer


def createAndAddIndexArray(vertexArray, data):
    glBindVertexArray(vertexArray)
    indexBuffer = glGenBufffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, indexBuffer)

    data_buffer = (c_uint * len(data))(*data)
    glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, indexBuffer)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    return indexBuffer


def createBindVertexAttribArrayFloat(data, loc):
    buff = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, buff)
    flat = flatten(data)
    data_buffer = (c_float * len(flat))(*flat)

    glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)
    glVertexAttribPointer(loc, int(len(flat) / len(data)), GL_FLOAT, GL_FALSE, 0, None)
    glEnableVertexAttribArray(loc)
    return buff
