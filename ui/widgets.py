#!/usr/bin/env python

import itertools

from PySide import QtGui, QtCore

class AnalyzerWidget(QtGui.QGraphicsView):
    showMessage = QtCore.Signal(object)

    def __init__(self, parent=None):
        super(AnalyzerWidget, self).__init__(parent)
        self.scene = QtGui.QGraphicsScene(self)
        self.setScene(self.scene)
        self.data = [[],[],[],[]]
        self.channelCount = 4

        colors = [QtGui.QColor(0x3C, 0x9D, 0xD0, 255),
                  QtGui.QColor(0xB9, 0x39, 0xD3, 255),
                  QtGui.QColor(0xDF, 0xFA, 0x00, 255),
                  QtGui.QColor(0xFF, 0x8B, 0x00, 255)]
        self.channelPens = []
        for n in range(4):
            p = QtGui.QPen()
            p.setColor(colors[n])
            p.setWidth(0)
            self.channelPens.append(p)

        self._subviewMargin = 24
        self.grabGesture(QtCore.Qt.PinchGesture)

    def setData(self, data):
        data.reverse()
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
        self.scale(x_scale, 1)
        self.scene.setSceneRect(0, 0, len(self.data[0]),
                                self.height() - self._subviewMargin/2)

    def paintEvent(self, event):
        super(AnalyzerWidget, self).paintEvent(event)
        painter = QtGui.QPainter(self.viewport())
        pen = QtGui.QPen(QtGui.QColor(128, 128, 128, 255))
        painter.setPen(pen)

        ch_height = self.height() / len(self.data)

        for n in range(len(self.data)):
            painter.drawLine(0, n*ch_height, self.width(), n*ch_height)

        pen.setColor(QtGui.QColor(0, 0, 0, 0))
        painter.setPen(pen)
        sidebar_width = 110
        painter.setBrush(QtGui.QBrush(QtGui.QColor(80, 80, 80, 220)))
        painter.drawRect(0, 0, sidebar_width, self.height())
        pen.setColor(QtGui.QColor(0, 0, 0, 255))
        painter.setPen(pen)
        painter.drawLine(sidebar_width, 0, sidebar_width, self.height())

        painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255, 255)))
        for n in range(len(self.data)):
            painter.drawText(0, ch_height*n, sidebar_width, ch_height,
                             QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter,
                             'Channel %d' % n)

    def event(self, event):
        if event.type() == QtCore.QEvent.Gesture:
            return self.gestureEvent(event)
        return super(AnalyzerWidget, self).event(event)

    def resizeEvent(self, event):
        self.redraw()
        super(AnalyzerWidget, self).resizeEvent(event)

    def gestureEvent(self, event):
        gesture = event.gesture(QtCore.Qt.PinchGesture)
        if gesture:
            x_scale = self.transform().m11()
            new_scale = x_scale * gesture.scaleFactor()
            if new_scale > 20:
                new_scale = 20
            elif new_scale < 0.1:
                new_scale = 0.1
            self.resetTransform()
            self.scale(new_scale, 1)
        return True

    def mouseMoveEvent(self, event):
        pt = self.mapToScene(event.pos())
        self.showMessage.emit('%f, %f' % (pt.x(), pt.y()))


class AnalyzerChannelGraphicsItem(QtGui.QGraphicsItemGroup):
    """
    The view of a single channel, including the waveform and labels.
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
