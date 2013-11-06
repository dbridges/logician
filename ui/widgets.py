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

    def resizeEvent(self, event):
        super(AnalyzerWidget, self).resizeEvent(event)
        self.redraw()

    def gestureEvent(self, event):
        """
        Override gesutreEvent to provide pinch zooming.
        """
        if len(self.data[0]) == 0:
            return True
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
        An x_scale factor of 1 means that a samples are spaced 1px apart.
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
        pt = self.mapToScene(event.pos())
        self.showMessage.emit('%0.2f' % pt.x())


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
