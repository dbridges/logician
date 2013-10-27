#!/usr/bin/env python

import sys

from PySide import QtGui, QtCore
from ui.main_window import Ui_MainWindow

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """
    Subclass of QMainWindow
    """
    def __init__(self, parent_app, parent=None):
        super(MainWindow, self).__init__(parent)
        self.app = parent_app
        self.setupUi(self)

    @QtCore.Slot()
    def on_startButton_clicked(self):
        print 'Start Clicked.'

    def closeEvent(self, event):
        """
        Called when window is trying to be closed.
        Call event.accept() to allow the window to be
        closed.
        """
        event.accept()

if __name__ == '__main__':
    QtGui.QFont.insertSubstitution(".Lucida Grande UI", "Lucida Grande")
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow(app)
    mainWindow.show()
    sys.exit(app.exec_())
