#!/usr/bin/env python

import itertools

from PySide import QtGui, QtCore, QtOpenGL

import models

class AnalyzerWidget(QtGui.QGraphicsView):
    """
    The main display widget for the acquired waveforms and their analyzer
    labels.
    """
    showMessage = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(AnalyzerWidget, self).__init__(parent)
        self.scene = QtGui.QGraphicsScene(self)
        self.setScene(self.scene)
        self.data = models.Acquisition([[],[],[],[]])

        colors = [QtGui.QColor(0x3C, 0x9D, 0xD0, 255),
                  QtGui.QColor(0xB9, 0x39, 0xD3, 255),
                  QtGui.QColor(0xDF, 0xFA, 0x00, 255),
                  QtGui.QColor(0xFF, 0x8B, 0x00, 255)]
        self.channelPens = []
        for n in range(4):
            p = QtGui.QPen()
            p.setColor(colors[n])
            p.setWidth(2)
            p.setCosmetic(True)
            self.channelPens.append(p)

        self._subviewMargin = 24
        self._pulseWidthCoords = None
        self.grabGesture(QtCore.Qt.PinchGesture)
        self.setViewport(QtOpenGL.QGLWidget())
        self.setAutoFillBackground(False)
        self.viewport().setAutoFillBackground(False)
        self.redraw()

    def setData(self, data):
        """
        Parameters
        ----------
        data : Acquisition object
            An acquisition object holding the channel data.
        """
        self.data = data
        self.redraw()

    def drawSignals(self):
        if len(self.data[0]) == 0:
            return
        subviewHeight = self.height() / 4 - self._subviewMargin / 2
        for i, data in enumerate(self.data):
            item = AnalyzerChannelGraphicsItem(data, subviewHeight,
                                               self.channelPens[i])
            item.setY(i*subviewHeight + i*self._subviewMargin / 2)
            self.scene.addItem(item)

    def redraw(self):
        x_scale = self.transform().m11()
        self.resetTransform()
        self.scene.clear()
        self.drawSignals()
        self.setScale(x_scale, 1)
        self.scene.setSceneRect(0, 0, len(self.data[0]),
                                self.height() - self._subviewMargin/2)

    def event(self, event):
        if event.type() == QtCore.QEvent.Gesture:
            return self.gestureEvent(event)
        return super(AnalyzerWidget, self).event(event)

    def drawForeground(self, painter, rect):
        """
        Paints the hud overlay on top of the widget.
        """
        painter.resetTransform()
        painter.setPen(QtGui.QPen(QtGui.QColor(228, 228, 228, 255)))
        self.drawWidthMeasurement(painter)
        painter.setPen(QtGui.QPen(QtGui.QColor(128, 128, 128, 255)))

        ch_height = self.height() / self.data.channel_count

        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0)))
        sidebar_width = 110
        painter.setBrush(QtGui.QBrush(QtGui.QColor(80, 80, 80, 220)))
        painter.drawRect(0, 0, sidebar_width, self.height())
        painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 255)))
        painter.drawLine(sidebar_width, 0, sidebar_width, self.height())

        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 255)))
        for n in range(self.data.channel_count):
            painter.drawText(0, ch_height*n, sidebar_width, ch_height,
                             QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter,
                             'Channel %d' % n)

        for n in range(self.data.channel_count):
            painter.drawLine(0, n*ch_height, self.width(), n*ch_height)

    def drawWidthMeasurement(self, painter):
        if self._pulseWidthCoords is None:
            return
        waveformHeight = self.height() / len(self.data)
        y = (self._pulseWidthCoords[0] * waveformHeight
             + (waveformHeight / 2))
        x1 = self._pulseWidthCoords[1] + 3
        x2 = self._pulseWidthCoords[2] - 2
        painter.drawLine(x1, y, x2, y)
        painter.drawLine(x1, y-3, x1, y+3)
        painter.drawLine(x2, y-3, x2, y+3)

    def resizeEvent(self, event):
        super(AnalyzerWidget, self).resizeEvent(event)
        self.redraw()

    def gestureEvent(self, event):
        """
        Override gesutreEvent to provide pinch zooming.
        """
        if len(self.data[0]) == 0:
            return True
        self._pulseWidthCoords = None
        gesture = event.gesture(QtCore.Qt.PinchGesture)
        if gesture:
            x_scale = self.transform().m11()
            new_scale = x_scale * gesture.scaleFactor()
            self.setScale(new_scale, 1)
        return True

    def setScale(self, x_scale, y_scale=1):
        """
        Sets the display scale, limiting the zoom to zoom no further out than
        to display the entire waveform.

        Parameters
        ----------
        x_scale : float
            The requested x_scale factor.
        y_scale : float
            The requested y_scale factor. This should normally be 1.

        Notes
        -----
        An x_scale factor of 1 means that samples are spaced 1px apart.
        """
        if len(self.data[0]) != 0:
            min_scale = float(self.width()) / len(self.data[0])
        else:
            min_scale = 1
        if x_scale > 2:
            x_scale = 2
        elif x_scale < min_scale:
            x_scale = min_scale
        self.resetTransform()
        super(AnalyzerWidget, self).scale(x_scale, y_scale)

    def mouseMoveEvent(self, event):
        if len(self.data[0]) < 1:
            return
        pt = self.mapToScene(event.pos())
        # Find transition points on either side of mouse pos.
        waveform_i = int(pt.y() // (self.height() / len(self.data)))
        index = int(pt.x())
        start_index = index
        finish_index = index
        while (start_index > 0 and
               self.data[waveform_i][start_index] ==
               self.data[waveform_i][index]):
               start_index -= 1
        while (finish_index < self.data.acquisition_length and
               self.data[waveform_i][finish_index] ==
               self.data[waveform_i][index]):
               finish_index += 1

        self._pulseWidthCoords = \
            [waveform_i,
             self.mapFromScene(start_index, 0).x(),
             self.mapFromScene(finish_index, 0).x()]
        t = pt.x() * self.data.dt
        dt = (finish_index - start_index - 1 ) * self.data.dt
        # Choose correct units for display
        if t < 1e-3:
            msg = 't: %0d us' % int(1e6*t)
        else:
            msg = 't: %0.2f ms' % (1e3*t)
        if dt < 1e-3:
            msg += '    dt: %d us' % int(1e6*dt)
        else:
            msg += '    dt: %0.2f ms' % (1e3*dt)
        self.showMessage.emit(msg)
        self.update()


class AnalyzerChannelGraphicsItem(QtGui.QGraphicsItemGroup):
    """
    The view of a single channel, including the waveform and labels.

    Parameters
    ----------
    data : array
        A 1d array of 1's or 0's.
    height : int
        The height that the waveform should be drawn, including room
        for the top margin for label display.
    pen : QPen
        A QPen object to draw the waveform with.
    """
    def __init__(self, data, height, pen, parent=None):
        super(AnalyzerChannelGraphicsItem, self).__init__(parent)
        self.data = data
        self.pen = pen
        self.height = height
        topMargin = 32
        waveformHeight = height - topMargin

        # Build path with as few lines as possible.
        path = QtGui.QPainterPath(QtCore.QPointF(0, -data[0]*waveformHeight))
        x = 0
        y = self.data[0]
        while x < len(self.data):
            while x < len(self.data) and self.data[x] == y:
                x += 1
            path.lineTo(x, -y*waveformHeight)
            y = 0 if y == 1 else 1
            if x != len(self.data):
                path.lineTo(x, -y*waveformHeight)
        path.translate(0, waveformHeight + topMargin)


        self.waveformPathItem = QtGui.QGraphicsPathItem(path, self)
        self.waveformPathItem.setPen(pen)
        self.addToGroup(self.waveformPathItem)

class HorizontalArrowGraphicsItem(QtGui.QGraphicsItem):
    """
    Draws an arrow from x1, y1 to x2, y2
    """
    def __init__(self, x1, y1, x2, y2,
                 pen=QtGui.QPen(QtGui.QColor(255, 255, 255, 255))):
        super(HorizontalArrowGraphicsItem, self).__init__()
        self._coords = [x1, y1, x2, y2]
        self._height = 10
        self.pen = pen

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.drawLine(*self._coords)
        painter.drawLine(self._coords[0],
                         self._coords[1] - self._height / 2,
                         self._coords[0],
                         self._coords[1] + self._height / 2)
        painter.drawLine(self._coords[2],
                         self._coords[1] - self._height / 2,
                         self._coords[2],
                         self._coords[1] + self._height / 2)

    def boundingRect(self):
        return QtCore.QRectF(self._coords[0],
                             self._coords[1] - self._height/2,
                             self._coords[2] - self._coords[0],
                             self._height)


