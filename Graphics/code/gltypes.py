from OpenGL.GL import *
import numpy as np
import math


def vec2(x, y=None):
    """Generate a vec2 object

    Arguments:
        x {float} -- x position

    Keyword Arguments:
        y {float} -- y position (default: use x)

    Returns:
        np.array -- Nicely formatted vec2 object
    """
    if y == None:
        return np.array([x, x], dtype=np.float32)
    return np.array([x, y], dtype=np.float32)


def vec3(x, y=None, z=None):
    """Generate a vec3 object

    Arguments:
        x {float} -- x position

    Keyword Arguments:
        y {float} -- y position (default: use x)
        z {float} -- z position (default: use y)

    Returns:
        np.array -- Nicely formatted vec3 object
    """
    if y == None:
        return np.array([x, x, x], dtype=np.float32)
    if z == None:
        return np.array([x, y, y], dtype=np.float32)
    return np.array([x, y, z], dtype=np.float32)


def rgb(r, g, b):
    """Utility function to convert an rgb color into a vec3

    Arguments:
        r {int} -- 0-255 red value
        g {int} -- 0-255 green value
        b {int} -- 0-255 blue value

    Returns:
        np.array -- vec3 with 0..1 values
    """
    x = r / 255
    y = g / 255
    z = b / 255
    return np.array([x, y, z], dtype=np.float32)


def hexc(string):
    """Utility function to convert a hexadecimal color into a vec3

    Arguments:
        string {str} -- Hex color string

    Returns:
        np.array -- vec3 with 0..1 values
    """
    h = string.lstrip("#")
    (r, g, b) = tuple(int(h[i : i + 2], 16) for i in [0, 2, 4])
    return rgb(r, g, b)


def normalize(v):
    """Normalize a vector

    Arguments:
        v {np.array} -- Vector to normalize

    Returns:
        np.array -- Normalized vector
    """
    norm = np.linalg.norm(v)
    return v / norm


class Mat4:
    """Helper class to represent an OpenGL Mat4 object
    """

    matData = None

    def __init__(self, p=[[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]):
        """Create a Mat4 object from an initial data set
        If no data is specified, identity matrix is used
        If a Mat3 is given, it will be copied into the corresponding location

        Keyword Arguments:
            p {list} -- Data to initialise matrix with (default: identity matrix)
        """
        if isinstance(p, Mat3):
            self.matData = np.matrix(np.identity(4))
            self.matData[:3, :3] = p.matData
        else:
            self.matData = np.matrix(p)

    def __mul__(self, other):
        """Handle matrix multiplication

        Arguments:
            other -- Vector or matrix to multiply by

        Returns:
            Vector or Mat4 with result
        """
        if isinstance(other, (list, np.ndarray)):
            return list(self.matData.dot(other).flat)
        return Mat4(self.matData.dot(other.matData))

    def getData(self):
        """Get data as a contiguous array
        Useful for uploading to OpenGL

        Returns:
            np.array -- Contiguous array of matrix data
        """
        return np.ascontiguousarray(self.matData, dtype=np.float32)

    def inverse(self):
        """Return matrix inverse
        This is not in-place!

        Returns:
            Mat4 -- Inverse of this matrix
        """
        return Mat4(np.linalg.inv(self.matData))

    def transpose(self):
        """Return transpose of this matrix
        This is not in-place!

        Returns:
            Mat4 -- Transpose of this matrix
        """
        return Mat4(self.matData.T)

    def _set_open_gl_uniform(self, loc):
        """Upload the data in this matrix to an OpenGL uniform
        Make sure the correct shader is set!!!

        Arguments:
            loc {int} -- Uniform location to upload to
        """
        glUniformMatrix4fv(loc, 1, GL_TRUE, self.getData())


class Mat3:
    """Helper class to represent an OpenGL Mat3 object
    """

    matData = None

    def __init__(self, p=[[1, 0, 0], [0, 1, 0], [0, 0, 1]]):
        """Create a Mat3 object from an initial data set
        If no data is specified, identity matrix is used
        If a Mat4 is given, it will be cropped

        Keyword Arguments:
            p {list} -- Data to initialise matrix with (default: identity matrix)
        """
        if isinstance(p, Mat4):
            self.matData = p.matData[:3, :3]
        else:
            self.matData = np.matrix(p)

    def __mul__(self, other):
        """Handle matrix multiplication

        Arguments:
            other -- Vector or matrix to multiply by

        Returns:
            Vector or Mat4 with result
        """
        if isinstance(other, (list, np.ndarray)):
            return list(self.matData.dot(other).flat)
        return Mat3(self.matData.dot(other.matData))

    def getData(self):
        """Get data as a contiguous array
        Useful for uploading to OpenGL

        Returns:
            np.array -- Contiguous array of matrix data
        """
        return np.ascontiguousarray(self.matData, dtype=np.float32)

    def inverse(self):
        """Return matrix inverse
        This is not in-place!

        Returns:
            Mat3 -- Inverse of this matrix
        """
        return Mat3(np.linalg.inv(self.matData))

    def transpose(self):
        """Return transpose of this matrix
        This is not in-place!

        Returns:
            Mat3 -- Transpose of this matrix
        """
        return Mat3(self.matData.T)

    def _set_open_gl_uniform(self, loc):
        """Upload the data in this matrix to an OpenGL uniform
        Make sure the correct shader is set!!!

        Arguments:
            loc {int} -- Uniform location to upload to
        """
        glUniformMatrix3fv(loc, 1, GL_TRUE, self.getData())


def make_translation(x, y, z):
    """Make a translation matrix

    Arguments:
        x {float} -- x position
        y {float} -- y position
        z {float} -- z position

    Returns:
        Mat4 -- Translation matrix for the given position
    """
    return Mat4([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]])


def make_scale(x, y, z):
    """Make a scale matrix

    Arguments:
        x {float} -- scaling along x axis
        y {float} -- scaling along y axis
        z {float} -- scaling along z axis

    Returns:
        Mat4 -- Scale matrix
    """
    return Mat4([[x, 0, 0, 0], [0, y, 0, 0], [0, 0, z, 0], [0, 0, 0, 1]])


def make_rotation_x(angle):
    """Generate a rotation matrix along the x-axis

    Arguments:
        angle {float} -- Angle in radians

    Returns:
        Mat4 -- Rotation matrix
    """
    return Mat4(
        [
            [1, 0, 0, 0],
            [0, math.cos(angle), -math.sin(angle), 0],
            [0, math.sin(angle), math.cos(angle), 0],
            [0, 0, 0, 1],
        ]
    )


def make_rotation_y(angle):
    """Generate a rotation matrix along the y-axis

    Arguments:
        angle {float} -- Angle in radians

    Returns:
        Mat4 -- Rotation matrix
    """
    return Mat4(
        [
            [math.cos(angle), 0, -math.sin(angle), 0],
            [0, 1, 0, 0],
            [math.sin(angle), 0, math.cos(angle), 0],
            [0, 0, 0, 1],
        ]
    )


def make_rotation_z(angle):
    """Generate a rotation matrix along the z-axis

    Arguments:
        angle {float} -- Angle in radians

    Returns:
        Mat4 -- Rotation matrix
    """
    return Mat4(
        [
            [math.cos(angle), -math.sin(angle), 0, 0],
            [math.sin(angle), math.cos(angle), 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )


def transform_point(m4, point):
    """Transform a given point by a Mat4

    Arguments:
        m4 {Mat4} -- Transformation matrix
        point {vec3} -- Point to transformation

    Returns:
        vec3 -- Transformed point
    """
    x, y, z, w = m4 * [point[0], point[1], point[2], 1.0]
    return vec3(x, y, z) / w
