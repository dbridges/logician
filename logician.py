#!/usr/bin/env python

import sys
import os
import random
import time

import serial
from serial.tools import list_ports
from PySide import QtGui, QtCore

import util
import models
from ui.main_window import Ui_MainWindow

class AcquireThread(QtCore.QThread):
    """
    Asynchronous serial thread to gather data from hardware.

    Parameters
    ----------
    com_desc : string
        A description of the com port device. The com ports are
        searched and the first port that has com_desc in its
        description is connected to.

    com_name : string
        If com_desc is not given com_name can be given. This is
        the path to the com port ('COM2', '/dev/tty0', etc)

    baud : int
        The baud rate to connect with.

    This object polls the serial port and emits an acquisiton when
    it is received. It then kills the thread.
    """

    dataReady = QtCore.Signal(object)

    def __init__(self, command, parent=None, com_name=None, baud=115200):
        super(AcquireThread, self).__init__()
        self._running = False
        self.serial = None
        self.serialStatusOk = False
        self.baud = baud
        self.com_name = com_name
        self.command = command

    def findSerialPort(self):
        """
        Returns a serial port string to connect to.
        """
        if self.com_name == None:
            try:
                com = ''
                for item in list_ports.comports():
                    if 'usb' in item[2]:
                        return item[0]
                if com == '':
                    raise NameError('Could not find com port named %s.' %
                                    item[0])
            except:
                self.serialStatusOk = False
                self._running = False
                return False
        return self.com_name

    def run(self):
        """
        Main serial thread run routine. First try to open serial port. If that
        is successful then poll port and return lines of data as they are
        received.
        """
        try:
            self.serial = serial.Serial(self.findSerialPort(),
                                        115200,
                                        timeout=0.4)
        except:
            self.serialStatusOk = False
            self._running = False
            return False

        self.serialStatusOk = True
        self._running = True
        serial_buffer = ''
        self.serial.flushInput()
        self.serial.flushOutput()

        self.serial.write(self.command.command_bytes)

        while self._running:
            # Wait for data to arrive
            start_time = time.time()
            while self.serial.inWaiting() < 128:
                if (time.time() - start_time) > 5:
                    self.serialStatusOk = False
                    self._running = False
                    self.serial.close()
                    return False
            # Read incoming data
            new_data = self.serial.read(128)
            while len(new_data) == 128:
                serial_buffer += new_data
                new_data = self.serial.read(128)
                self.msleep(5)
            serial_buffer += new_data

            self.dataReady.emit(serial_buffer)
            self._running = False
            self.serial.close()

    def stop(self, wait=False):
        """
        Stops the serial thread. If wait is True
        this will wait until serial thread exits naturally,
        preventing possible errors by a quick kill.
        """
        self._running = False
        if self.serial != None:
            self.serial.close()
            self.finished.emit()
            self.exit()
        if wait:
            self.wait()


class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    """
    Subclass of QMainWindow
    """
    def __init__(self, parent_app, parent=None):
        super(MainWindow, self).__init__(parent)
        self.app = parent_app
        self.acquireThread = None
        self.setupUi(self)
        self.toolBar.addWidget(self.topRowLayoutWidget)
        self.analyzerWidget.showMessage.connect(self.statusBar.showMessage,
                                    QtCore.Qt.QueuedConnection)
        self.show()
        self.loadSettings()

    @QtCore.Slot()
    def on_startButton_clicked(self):
        self.startButton.setEnabled(False)
        self.acquireThread = AcquireThread(
            models.AnalyzerCommand(
                trigger_type=self.triggerSlopeComboBox.currentIndex(),
                trigger_channel=self.triggerChannelComboBox.currentIndex()))
        self.acquireThread.dataReady.connect(self.on_acquireThread_data,
                                             QtCore.Qt.QueuedConnection)
        self.acquireThread.finished.connect(self.on_acquireThread_finished,
                                            QtCore.Qt.QueuedConnection)
        self.acquireThread.start()

    @QtCore.Slot()
    def on_actionOpen_triggered(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open data file.',
                                                     os.getcwd(),
                                                     "CSV Files (*.csv)")[0]
        if filename == '':
            return
        try:
            data = util.read_csv(filename)
        except:
            msg = QtGui.QMessageBox();
            msg.setText('Error loading file.')
            msg.exec_()
            return
        self.analyzerWidget.setData(data)

    def on_acquireThread_data(self, data_bytes):
        self.analyzerWidget.setData(
            models.Acquisition(data_bytes,channel_count=4))

    def on_acquireThread_finished(self):
        self.startButton.setEnabled(True)

    def loadSettings(self):
        try:
            settings = QtCore.QSettings('dbridges', 'Logician')
            settings.beginGroup('MainWindow')
            self.restoreGeometry(settings.value('geometry'))
            if settings.value('maximized', 'false') == 'true':
                self.showMaximized()
            settings.endGroup()
        except Exception as e:
            logging.error('Error loading gui settings. %s' % str(e))

    def saveSettings(self):
        settings = QtCore.QSettings('dbridges', 'Logician')
        settings.beginGroup('MainWindow')
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('maximized', self.isMaximized())
        settings.endGroup()

    def closeEvent(self, event):
        """
        Called when window is trying to be closed.
        Call event.accept() to allow the window to be
        closed.
        """
        self.saveSettings()
        event.accept()

if __name__ == '__main__':
    QtGui.QFont.insertSubstitution(".Lucida Grande UI", "Lucida Grande")
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow(app)
    mainWindow.show()
    mainWindow.activateWindow()
    mainWindow.raise_()
    sys.exit(app.exec_())
