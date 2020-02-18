#!/usr/bin/env python

import ctypes
import sys

import numpy as np
from PySide2.QtCore import Slot
from PySide2.QtGui import (
    QSurfaceFormat, QOpenGLContext, QOpenGLFunctions, QOpenGLVertexArrayObject, QOpenGLBuffer,
    QOpenGLShaderProgram, QOpenGLShader,
)
from PySide2.QtWidgets import QApplication, QMainWindow, QOpenGLWidget, QMessageBox
from shiboken2.shiboken2 import VoidPtr

try:
    import OpenGL.GL as gl
except ImportError:
    app = QApplication(sys.argv)
    messageBox = QMessageBox(
        QMessageBox.Critical,
        "ContextInfo",
        "PyOpenGL must be installed to run this example.",
        QMessageBox.Close,
    )
    messageBox.setDetailedText("Run:\npip install PyOpenGL")
    messageBox.exec_()
    sys.exit(1)


VERTICES = [
    -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
    0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
    0.0, 0.5, 0.0, 0.0, 0.0, 1.0
]
VERTICES = np.array(VERTICES, dtype=np.float32)


def print_surface_format(surface_format: QSurfaceFormat) -> str:
    profile_name = 'core' if surface_format.profile() == QSurfaceFormat.CoreProfile else 'compatibility'

    return "{} version {}.{}".format(
        profile_name,
        surface_format.majorVersion(),
        surface_format.minorVersion(),
    )


def set_format() -> QSurfaceFormat:
    surface_format = QSurfaceFormat()
    surface_format.setVersion(4, 1)
    surface_format.setProfile(QSurfaceFormat.CoreProfile)
    surface_format.setSamples(4)
    QSurfaceFormat.setDefaultFormat(surface_format)

    return surface_format


class MainWindow(QMainWindow):

    def __init__(self, parent=None, *args, **kwargs):
        QMainWindow.__init__(self, parent, *args, **kwargs)

        self.surface_format = set_format()

        self.setWindowTitle("Hello Qt5")
        self.widget = OpenGLWidget(self.surface_format)
        self.setCentralWidget(self.widget)
        self.resize(800, 600)
        self.show()

        print(print_surface_format(self.surface_format))


class OpenGLWidget(QOpenGLWidget, QOpenGLFunctions):

    def __init__(self, fmt: QSurfaceFormat, parent=None, *args, **kwargs):
        QOpenGLWidget.__init__(self, parent, *args, **kwargs)
        QOpenGLFunctions.__init__(self, *args, **kwargs)

        self.program = QOpenGLShaderProgram()
        self.vbo = QOpenGLBuffer()
        self.vao = QOpenGLVertexArrayObject()

        self.setFormat(fmt)
        self.context = QOpenGLContext(self)
        if not self.context.create():
            raise Exception("Unable to create GL context")

    def initializeGL(self) -> None:
        self.context.aboutToBeDestroyed.connect(self.cleanup)
        self.initializeOpenGLFunctions()
        self.glClearColor(0.3, 0.0, 0.1, 1.0)

        self.program.addShaderFromSourceFile(QOpenGLShader.Vertex, "vertex_shader.glsl")
        self.program.addShaderFromSourceFile(QOpenGLShader.Fragment, "fragment_shader.glsl")
        self.program.bindAttributeLocation("vertex", 0)
        self.program.bindAttributeLocation("colour", 1)
        self.program.link()

        self.program.bind()

        self.vao.create()
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)

        self.vbo.create()
        self.vbo.bind()
        self.vbo.allocate(VERTICES, VERTICES.nbytes)

        self.vbo.bind()
        self.glEnableVertexAttribArray(0)
        self.glEnableVertexAttribArray(1)
        float_size = ctypes.sizeof(ctypes.c_float)
        null = VoidPtr(0)
        pointer = VoidPtr(3 * float_size)
        self.glVertexAttribPointer(
            0, 3, int(gl.GL_FLOAT), int(gl.GL_FALSE), 6 * float_size, null
        )
        self.glVertexAttribPointer(
            1, 3, int(gl.GL_FLOAT), int(gl.GL_FALSE), 6 * float_size, pointer
        )
        self.vbo.release()

        self.program.release()
        vao_binder = None

    def paintGL(self) -> None:
        self.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.glEnable(gl.GL_DEPTH_TEST)

        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)
        self.program.bind()
        self.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
        self.program.release()
        vao_binder = None

        self.update()

    def resizeGL(self, width: int, height: int) -> None:
        self.glViewport(0, 0, width, height)

    @Slot()
    def cleanup(self):
        self.makeCurrent()
        self.vbo.destroy()
        del self.program
        self.program = None
        self.doneCurrent()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(600, 400)
    window.show()

    sys.exit(app.exec_())
