import OpenGL.GL as gl
import glfw

def render(window):
    width, height = glfw.get_framebuffer_size(window)
    ratio = width / float(height)

    gl.glViewport(0, 0, width, height)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(-ratio, ratio, -1, 1, 1, -1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    gl.glBegin(gl.GL_TRIANGLES)
    gl.glColor3f(1, 0, 0)
    gl.glVertex3f(-0.6, -0.4, 0)
    gl.glColor3f(0, 1, 0)
    gl.glVertex3f(0.6, -0.4, 0)
    gl.glColor3f(0, 0, 1)
    gl.glVertex3f(0, 0.6, 0)
    gl.glEnd()


def startProgram():
    if not glfw.init():
        return

    window = glfw.create_window(1600, 900, "Hello World!", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    while not glfw.window_should_close(window):
        render(window)
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()