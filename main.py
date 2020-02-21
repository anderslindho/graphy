#!/usr/bin/env python

import sys

from PySide2.QtWidgets import QApplication, QMainWindow, QMessageBox

from opengl import print_surface_format, set_format, OpenGLWidget


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


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(1280, 720)
    window.show()

    sys.exit(app.exec_())
