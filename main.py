#!/usr/bin/env python

import ctypes
import sys
import time

import numpy as np

import pyrr
from PySide2.QtCore import Slot, QTimer
from PySide2.QtGui import (
    QSurfaceFormat, QOpenGLContext, QOpenGLFunctions, QOpenGLVertexArrayObject, QOpenGLBuffer,
    QOpenGLShaderProgram, QOpenGLShader
)
from PySide2.QtWidgets import QApplication, QMainWindow, QOpenGLWidget, QMessageBox
from shiboken2.shiboken2 import VoidPtr

from geometry import CUBE_VERTICES, CUBE_INDICES

try:
    import OpenGL.GL as gl
except ImportError:
    app = QApplication(sys.argv)
    messageBox = QMessageBox(
        QMessageBox.Critical,
        "ContextInfo",
        "PyOpenGL must be installed to run this example",
        QMessageBox.Close,
    )
    messageBox.setDetailedText("Run:\npip install PyOpenGL")
    messageBox.exec_()
    sys.exit(1)


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
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.ebo = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
        self.vao = QOpenGLVertexArrayObject()

        self.world_loc = None
        self.projection_loc = None
        self.attrib_loc = None

        self.world = None
        self.projection = None

        self.setFormat(fmt)
        self.context = QOpenGLContext(self)
        if not self.context.create():
            raise RuntimeError("Unable to create GL context")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(10)

    def initializeGL(self) -> None:
        self.context.aboutToBeDestroyed.connect(self.cleanup)

        self.initializeOpenGLFunctions()
        self.build_shaders()
        self.create_vbo()
        self.glClearColor(0.1, 0.0, 0.1, 0.5)

    def paintGL(self) -> None:
        self.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        self.glEnable(gl.GL_DEPTH_TEST)
        self.render()

    def resizeGL(self, width: int, height: int) -> None:
        self.width, self.height = width, height
        self.glViewport(0, 0, width, height)
        self.projection = pyrr.matrix44.create_perspective_projection_matrix(45, width/height, 0.1, 100)

    def render(self) -> None:
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)
        if not self.program.isLinked():
            raise RuntimeError("Shaders not linked")
        self.program.bind()

        rot_x = pyrr.Matrix44.from_x_rotation(0.6 * time.time())
        rot_y = pyrr.Matrix44.from_y_rotation(0.2 * time.time())
        rot_z = pyrr.Matrix44.from_z_rotation(0.1 * time.time())

        rotation = pyrr.matrix44.multiply(rot_x, rot_y)
        rotation = pyrr.matrix44.multiply(rotation, rot_z)
        rotation = pyrr.matrix44.multiply(self.scale, rotation)
        self.world = pyrr.matrix44.multiply(rotation, self.translation)

        gl.glUniformMatrix4fv(self.projection_loc, 1, gl.GL_FALSE, self.projection)  # TODO: switch to Qt functions (doesn't work
        gl.glUniformMatrix4fv(self.world_loc, 1, gl.GL_FALSE, self.world)  # TODO: switch to Qt functions (doesn't work)

        self.glDrawElements(gl.GL_TRIANGLES, len(CUBE_INDICES), gl.GL_UNSIGNED_INT, VoidPtr(0))

        self.program.release()
        vao_binder = None

    def build_shaders(self) -> None:
        if not self.program.addShaderFromSourceFile(QOpenGLShader.Vertex, "vertex_shader.glsl"):
            raise FileNotFoundError("Unable to load vertex shader")
        if not self.program.addShaderFromSourceFile(QOpenGLShader.Fragment, "fragment_shader.glsl"):
            raise FileNotFoundError("Unable to load fragment shader")
        if not self.program.link():
            raise RuntimeError("Unable to link shader programme")

    def create_vbo(self) -> None:
        self.program.bind()  # suspicious behaviour
        self.vao.create()
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)

        self.vbo.create()
        self.vbo.bind()
        self.vbo.allocate(CUBE_VERTICES, CUBE_VERTICES.nbytes)

        self.attrib_loc = self.program.attributeLocation("a_position")
        self.world_loc = self.program.uniformLocation("world")
        self.projection_loc = self.program.uniformLocation("projection")

        self.translation = pyrr.matrix44.create_from_translation(pyrr.Vector3([1.0, 0.0, -3.0]))
        self.scale = pyrr.matrix44.create_from_scale(pyrr.Vector3([2, 1, 1]))

        # TODO: create IBO
        self.ebo.create()
        self.ebo.bind()
        self.ebo.allocate(CUBE_INDICES, CUBE_INDICES.nbytes)

        float_size = ctypes.sizeof(ctypes.c_float)  # (4)
        null = VoidPtr(0)
        pointer = VoidPtr(3 * float_size)
        self.glEnableVertexAttribArray(0)
        self.glVertexAttribPointer(
            0, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * float_size, null
        )
        self.glEnableVertexAttribArray(1)
        self.glVertexAttribPointer(
            1, 3, gl.GL_FLOAT, gl.GL_FALSE, 6 * float_size, pointer
        )
        self.vao.release()
        self.vbo.release()
        self.ebo.release()

        self.program.release()
        vao_binder = None

    @Slot()
    def cleanup(self):
        if not self.makeCurrent():
            raise Exception("Could not make context current")
        self.vbo.destroy()
        self.program.bind()
        self.program.removeAllShaders()
        self.program.release()
        del self.program
        self.program = None
        self.doneCurrent()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(1280, 720)
    window.show()

    sys.exit(app.exec_())
