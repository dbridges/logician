#!/usr/bin/env python

import sys
import random
import time

import serial
from serial.tools import list_ports

from PySide import QtGui, QtCore
from ui.main_window import Ui_MainWindow

class AcquireThread(QtCore.QThread):
    """
    com_desc : string
        A description of the com port device. The com ports are
        searched and the first port that has com_desc in its
        description is connected to.

    com_name : string
        If com_desc is not given com_name can be given. This is
        the path to the com port ('COM2', '/dev/tty0', etc)

    baud : int
        The baud rate to connect with.

    Asynchronous serial thread to gather data.

    This object polls the serial port and emits whole lines of data
    as they are received.
    """

    dataReady = QtCore.Signal(object)

    def __init__(self, command_bytes, parent=None, com_name=None, baud=115200):
        super(AcquireThread, self).__init__()
        self._running = False
        self.serial = None
        self.serialStatusOk = False
        self.baud = baud
        self.com_name = com_name
        self.command_bytes = command_bytes

    def run(self):
        """
        Main serial thread run routine. First try to open
        serial port. If that is successful then poll port
        and return lines of data as they are received.
        """
        # Find a com port connected named com_name
        if self.com_name == None:
            try:
                com = ''
                for item in list_ports.comports():
                    if 'usb' in item[2]:
                        com = item[0]
                        break
                if com == '':
                    raise NameError('Could not find com port named %s.' %
                                    item[0])
                self.serial = serial.Serial(com, 115200, timeout=0.4)
            except:
                self.serialStatusOk = False
                self._running = False
                return False
        else:
            try:
                self.serial = serial.Serial(self.com_name,
                                            self.baud,
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

        out_string = (''.join([chr(x) for x in self.command_bytes]) +
            ' '*(64 - len(self.command_bytes)))    #Pad string to 64 bytes
        print out_string
        self.serial.write(out_string)

        while self._running:
            # Wait for data to arrive
            start_time = time.time()
            while self.serial.inWaiting() < 128:
                if (time.time() - start_time) > 5:
                    self.stop()
                    return
            # Read incoming data
            new_data = self.serial.read(128)
            while len(new_data) == 128:
                serial_buffer += new_data
                new_data = self.serial.read(128)
            serial_buffer += new_data

            self.dataReady.emit(serial_buffer)

            self.stop()

    def stop(self, wait=False):
        """
        Stops the serial thread. If wait is True
        this will wait until serial thread exits naturally,
        preventing possible errors by a quick kill.
        """
        self._running = False
        if self.serial != None:
            self.serial.close()
        if wait:
            self.wait()


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
        aq_len = 2000
        command_bytes = \
            [0x01,                                                  # Command
             (100 & 0x00FF), (100 >> 8),        # Sample Period (ms)
             (aq_len & 0x00FF), (aq_len >> 8)]                      # Acquisition Length (1/10th s)

        self.acquireThread = AcquireThread(command_bytes)
        self.acquireThread.dataReady.connect(self.on_acquireThread_data,
                                             QtCore.Qt.QueuedConnection)
        self.acquireThread.start()

    def on_acquireThread_data(self, data):
        sep_channel_data = [f(c) for c in data for f in (lambda x: ord(x) >> 4,
                                                         lambda x: ord(x) & 0x0F)]
        unpacked_data = [[int(i) for i in list(bin(d)[2:].zfill(4))]
                         for d in sep_channel_data]
        packed_data = zip(*unpacked_data)
        self.analyzerWidget.setData(packed_data)

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