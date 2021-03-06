#!/usr/bin/env python3

import sys
import os
import time

import serial
from serial.tools import list_ports
from PySide import QtGui, QtCore

import analyzers
import ui
from models import Acquisition, AnalyzerCommand, ThemeManager
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
        if self.com_name is None:
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
                                        timeout=10)
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
            serial_buffer = self.serial.read(self.command.sample_count / 2)

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
        if self.serial is not None:
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
        self.currentAnalyzer = None
        self.setupUi(self)
        for key in AnalyzerCommand.sample_counts:
            self.sampleCountComboBox.addItem(key)
        for key in AnalyzerCommand.sample_rates:
            self.sampleRateComboBox.addItem(key)
        self.toolBar.addWidget(self.topRowLayoutWidget)
        self.statusBar.addPermanentWidget(self.protocolComboBox)
        self.statusBar.addPermanentWidget(self.displayModeComboBox)
        self.analyzerWidget.showMessage.connect(
            self.statusBar.showMessage, QtCore.Qt.QueuedConnection)
        self.comboBoxes = {'sampleRateIndex':
                           self.sampleRateComboBox,
                           'sampleCountIndex':
                           self.sampleCountComboBox,
                           'triggerChannelIndex':
                           self.triggerChannelComboBox,
                           'triggerSlopeIndex':
                           self.triggerSlopeComboBox,
                           'protocolIndex':
                           self.protocolComboBox,
                           'displayModeIndex':
                           self.displayModeComboBox}
        # load themes
        self.themeManager = ThemeManager('ui/themes/')
        for name in self.themeManager.theme_names():
            action = self.menuTheme.addAction(name)
            action.setCheckable(True)

        self.analyzerWidget.setTheme(self.themeManager.theme_named('Dark'))
        for action in self.menuTheme.actions():
            if action.text() == 'Dark':
                action.setChecked(True)
                break
        self.show()
        self.loadSettings()

    @QtCore.Slot()
    def on_startButton_clicked(self):
        self.startButton.setEnabled(False)
        self.acquireThread = AcquireThread(
            AnalyzerCommand(
                AnalyzerCommand.sample_rates[
                    self.sampleRateComboBox.currentText()],
                AnalyzerCommand.sample_counts[
                    self.sampleCountComboBox.currentText()],
                trigger_type=self.triggerSlopeComboBox.currentIndex(),
                trigger_channel=self.triggerChannelComboBox.currentIndex()))
        self.acquireThread.dataReady.connect(self.on_acquireThread_data,
                                             QtCore.Qt.QueuedConnection)
        self.acquireThread.finished.connect(self.on_acquireThread_finished,
                                            QtCore.Qt.QueuedConnection)
        self.acquireThread.start()

    @QtCore.Slot()
    def on_actionOpen_triggered(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Open',
                                                     os.getcwd(),
                                                     "CSV Files (*.csv)")[0]
        if filename == '':
            return
        try:
            data = Acquisition(filename)
        except Exception as e:
            msg = QtGui.QMessageBox()
            msg.setText('Error loading file.\n\n%s' % e)
            msg.exec_()

            return
        self.setData(data, redraw=True)
        self.actionSave_to_Spreadsheet.setEnabled(True)

    @QtCore.Slot()
    def on_actionSave_to_Spreadsheet_triggered(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, 'Save As',
                                                     os.getcwd(),
                                                     "CSV Files (*.csv)")[0]
        if filename == '':
            return
        try:
            with open(filename, 'w') as f:
                f.write(self.analyzerWidget.data.csv_string())
        except IOError:
            msg = QtGui.QMessageBox()
            msg.setText('There was an error saving the file.')
            msg.exec_()

    @QtCore.Slot()
    def on_protocolComboBox_activated(self):
        if self.protocolComboBox.currentIndex() != 0:
            dialog = ui.widgets.AnalyzerDialog(self)
            dialog.protocolComboBox.setCurrentIndex(
                self.protocolComboBox.currentIndex() - 1)
            if dialog.exec_() == 1:
                self.currentAnalyzer = self.setAnalyzerFromDialog(dialog)
                self.protocolComboBox.setCurrentIndex(
                    dialog.protocolComboBox.currentIndex() + 1)
            self.reloadByteLabels()

    @QtCore.Slot()
    def on_displayModeComboBox_currentIndexChanged(self):
        self.analyzerWidget.setByteFormat(
            self.displayModeComboBox.currentText())

    @QtCore.Slot(QtGui.QAction)
    def on_menuTheme_triggered(self, action):
        self.analyzerWidget.setTheme(
            self.themeManager.theme_named(action.text()))
        for a in self.menuTheme.actions():
            if a != action:
                a.setChecked(False)

    def on_acquireThread_data(self, data_bytes):
        self.setData(
            Acquisition(data_bytes, sample_rate=1e6, channel_count=4))
        self.actionSave_to_Spreadsheet.setEnabled(True)

    def on_acquireThread_finished(self):
        self.startButton.setEnabled(True)

    def setData(self, data, redraw=False):
        self.analyzerWidget.setData(data, redraw)
        self.reloadByteLabels()

    def setAnalyzerFromDialog(self, dialog):
        data = self.analyzerWidget.data
        if 'USART' in dialog.protocolComboBox.currentText():
            analyzer = analyzers.USARTAnalyzer(data)
        elif 'I2C' in dialog.protocolComboBox.currentText():
            analyzer = analyzers.I2CAnalyzer(data)
        elif 'SPI' in dialog.protocolComboBox.currentText():
            analyzer = analyzers.SPIAnalyzer(data)
        return analyzer

    def reloadByteLabels(self):
        if self.currentAnalyzer is not None:
            self.analyzerWidget.setByteLabels(self.currentAnalyzer.labels(),
                                              redraw=True)

    def loadSettings(self):
        try:
            settings = QtCore.QSettings('dbridges', 'Logician')
            settings.beginGroup('MainWindow')
            self.restoreGeometry(settings.value('geometry'))
            if settings.value('maximized', 'false') == 'true':
                self.showMaximized()
            for k in self.comboBoxes:
                self.comboBoxes[k].setCurrentIndex(settings.value(k, 0))
            settings.endGroup()
        except:
            pass

    def saveSettings(self):
        settings = QtCore.QSettings('dbridges', 'Logician')
        settings.beginGroup('MainWindow')
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('maximized', self.isMaximized())
        for k in self.comboBoxes:
            settings.setValue(k, self.comboBoxes[k].currentIndex())
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
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow(app)
    mainWindow.show()
    mainWindow.activateWindow()
    mainWindow.raise_()
    sys.exit(app.exec_())
