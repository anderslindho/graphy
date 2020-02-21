import ctypes
import random
import time

import pyrr
from OpenGL import GL as gl
from PySide2.QtCore import QCoreApplication, QTimer, Slot, QPoint
from PySide2.QtGui import (
    QSurfaceFormat, QOpenGLFunctions, QOpenGLShaderProgram, QOpenGLBuffer,
    QOpenGLVertexArrayObject, QOpenGLContext, QOpenGLShader,
)
from PySide2.QtWidgets import QOpenGLWidget
from shiboken2.shiboken2 import VoidPtr

from camera import Camera
from geometry import Cube


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


class OpenGLWidget(QOpenGLWidget, QOpenGLFunctions):

    def __init__(self, fmt: QSurfaceFormat, parent=None, *args, **kwargs):
        QOpenGLWidget.__init__(self, parent, *args, **kwargs)
        QOpenGLFunctions.__init__(self, *args, **kwargs)
        self.width, self.height = 1280, 720

        self.program = QOpenGLShaderProgram()
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.ebo = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
        self.vao = QOpenGLVertexArrayObject()

        self.model_loc = None
        self.projection_loc = None
        self.camera_loc = None
        self.attrib_loc = None

        self.shape = Cube()
        self.models = []
        self.model = None
        self.projection = None

        self.camera = Camera()
        self.last_pos = QPoint(self.width / 2.0, self.height / 2.0)

        self.setFormat(fmt)
        self.context = QOpenGLContext(self)
        if not self.context.create():
            raise RuntimeError("Unable to create GL context")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(20)

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
        self.program.bind()
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)

        # TODO: switch to Qt functions (doesn't work)
        gl.glUniformMatrix4fv(self.projection_loc, 1, gl.GL_FALSE, self.projection)
        view = self.camera.get_view_matrix()
        gl.glUniformMatrix4fv(self.camera_loc, 1, gl.GL_FALSE, view)

        for model in self.models:
            # TODO: move to entity class ?
            rotation = pyrr.matrix44.create_from_axis_rotation(
                pyrr.vector3.create_from_matrix44_translation(model),
                time.time(),
            )
            scale = pyrr.matrix44.create_from_scale(
                pyrr.vector3.create_from_matrix44_translation(model) * 0.1,
            )
            rotation = pyrr.matrix44.multiply(scale, rotation)
            model = pyrr.matrix44.multiply(rotation, model)

            gl.glUniformMatrix4fv(self.model_loc, 1, gl.GL_FALSE, model)
            self.glDrawElements(gl.GL_TRIANGLES, len(self.shape.indices), gl.GL_UNSIGNED_INT, VoidPtr(0))

        self.program.release()
        vao_binder = None

    def build_shaders(self) -> None:
        if not self.program.addShaderFromSourceFile(QOpenGLShader.Vertex, "vertex_shader.glsl"):
            raise FileNotFoundError("Unable to load vertex shader")
        if not self.program.addShaderFromSourceFile(QOpenGLShader.Fragment, "fragment_shader.glsl"):
            raise FileNotFoundError("Unable to load fragment shader")
        if not self.program.link():
            raise RuntimeError("Unable to link shader program")

    def create_vbo(self) -> None:
        self.program.bind()  # suspicious behaviour ?

        self.vao.create()
        vao_binder = QOpenGLVertexArrayObject.Binder(self.vao)

        self.vbo.create()
        self.vbo.bind()
        self.vbo.allocate(self.shape.vertices, self.shape.vertices.nbytes)

        self.attrib_loc = self.program.attributeLocation("a_position")
        self.model_loc = self.program.uniformLocation("model")
        self.projection_loc = self.program.uniformLocation("projection")
        self.camera_loc = self.program.uniformLocation("camera")

        for i in range(50):
            x, y, z = random.uniform(-10, 10), random.uniform(-10, 10), random.uniform(-10, 10)
            self.models.append(pyrr.matrix44.create_from_translation(pyrr.Vector3([x, y, z])))

        self.ebo.create()
        self.ebo.bind()
        self.ebo.allocate(self.shape.indices, self.shape.indices.nbytes)

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

    def mousePressEvent(self, event):
        self.last_pos = QPoint(event.pos())

    def mouseMoveEvent(self, event):
        dx = event.x() - self.last_pos.x()
        dy = event.y() - self.last_pos.y()

        if event.buttons():
            self.camera.mouse_movement(float(dx), float(dy))

        self.last_pos = QPoint(event.pos())

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
