import os
import sys
import time
import threading
import Queue

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg

import serial
from serial.tools import list_ports

serial_thread_done = False

################################################################################
##                           Session Configuration                            ##
################################################################################

# Acquisition options
sample_rate = 100                                           # In Samples/sec
no_channels = 3
acquisition_length = 30.0                                    # In seconds

# GUI options
dummy = False
send_only = False
timer_interval = 50
x_range = 200

buffer_size = (no_channels)*4*int(sample_rate*timer_interval/1000)
if buffer_size == 0:
    raise ValueError('Buffer cannot be length 0.')
try:
    serial_port = [f for f in os.listdir('/dev')
                   if f.startswith('tty.usb') or f.startswith('ttyACM')][0]
    serial_port = '/dev/' + serial_port
except:
    raise IOerror('no suitable usb ports found')

sample_period = int(1000/sample_rate)
aq_len = int(acquisition_length * 10)

command_bytes = \
    [0x01,                                                  # Command
     (sample_period & 0x00FF), (sample_period >> 8),        # Sample Period (ms)
     (aq_len & 0x00FF), (aq_len >> 8)]                      # Acquisition Length (1/10th s)

for c in command_bytes:
    print ('0x%02x,' % c),

if send_only:
    ser = serial.Serial(serial_port,
                        baudrate=1000000, timeout=0.5)
    out_string = (''.join([chr(x) for x in command_bytes]) +
            ' '*(64 - len(command_bytes)))    #Pad string to 64 bytes
    ser.write(out_string)
    ser.flush()
    sys.exit()

################################################################################
##                              Serial Stuff                                  ##
################################################################################

class SerialThread(threading.Thread):
    def __init__(self, target_queue, buffer_size, command_bytes, dummy=False):
        threading.Thread.__init__(self)
        self.buffer_size = buffer_size
        self.target_queue = target_queue
        self.dummy = dummy
        self.command_bytes = command_bytes

    def run(self):
        if self.dummy:
            self.run_dummy()
        else:
            self.run_serial()

    def run_dummy(self):
        """
        A thread that sends dummy data.
        """
        global serial_thread_done
        for n in range(15):
            dist = 0.01*np.arange(10256)
            force = np.linspace(0, 5, 10256)
            self.target_queue.put((dist, force))
            time.sleep(0.05)
        serial_thread_done = True

    def run_serial(self):
        """
        A thread that reads from the serial port
        and enques data to target_queue. The thread ends
        when the length of the serial data is less than
        buffer_size.
        """
        global serial_thread_done, acquisition_length
        try:
            self.ser = serial.Serial(serial_port,
                                     baudrate=1000000, timeout=0.5)
        except serial.SerialException:
            serial_thread_done = True
            raise
            print 'Error with serial port.'
            return
        self.ser.flushInput()
        self.ser.flushOutput()
        out_string = (''.join([chr(x) for x in self.command_bytes]) +
                ' '*(64 - len(self.command_bytes)))    #Pad string to 64 bytes
        self.ser.write(out_string)
        self.ser.flush()

        serial_data = self.ser.read(self.buffer_size)
        while len(serial_data) != 0:
            data = np.fromstring(serial_data, dtype='<i2')
            new_data = []
            for n in range(no_channels):
                new_data.append(data[n::no_channels])
            self.target_queue.put(new_data)

            serial_data = self.ser.read(self.buffer_size)

        data = np.fromstring(serial_data, dtype='<i2')
        new_data = []
        for n in range(no_channels):
            new_data.append(data[n::no_channels])
        self.target_queue.put(new_data)

        self.ser.close()
        serial_thread_done = True

#pg.setConfigOption('background', 'w')
#pg.setConfigOption('foreground', 'k')
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="Data Acquistion")
win.resize(1300,500)

plots = []
curves = []
data = [np.array([]) for n in range(no_channels)]
for n in range(no_channels):
    p = win.addPlot(title="Channel "+str(n))
    p.enableAutoRange('x', False)
    plots.append(p)
    curves.append(p.plot(pen='y'))
    win.nextRow()

data_queue = Queue.Queue()
def update():
    global win, data, curves, serial_thread_done
    if not serial_thread_done:
        try:
            new_data = data_queue.get()
        except Queue.Empty:
            new_data = [np.array([]) for n in range(no_channels)]
        for n in range(no_channels):
            data[n] = np.append(data[n], new_data[n])
            curves[n].setData(data[n])
            if len(data[n]) > x_range:
                plots[n].setRange(xRange=(len(data[n])-x_range, len(data[n])))
            else:
                plots[n].setRange(xRange=(0,x_range))

    else:
        timer.stop()

timer = QtCore.QTimer()
timer.timeout.connect(update)

serial_thread = SerialThread(data_queue, buffer_size,
                             command_bytes, dummy)

# Center window and move to front.
win.raise_()
win.show()
resolution = QtGui.QDesktopWidget().screenGeometry()
win.move((resolution.width() / 2) - (win.frameSize().width() / 2),
            (resolution.height() / 2) - (win.frameSize().height() / 2))
serial_thread.start()
timer.start(timer_interval)

sys.exit(app.exec_())
