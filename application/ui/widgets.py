#!/usr/bin/env python

from PySide import QtGui, QtCore

class AnalyzerWidget(QtGui.QGraphicsView):
    def __init__(self, parent=None):
        super(AnalyzerWidget, self).__init__(parent)
        self.scene = QtGui.QGraphicsScene(self)
        self.setScene(self.scene)
        self.data = [[0],[0],[0],[0]]
        self.zoomLevel = 20
        self.channelCount = 4

        colors = [QtGui.QColor(0x3C, 0x9D, 0xD0, 255),
                  QtGui.QColor(0xB9, 0x39, 0xD3, 255),
                  QtGui.QColor(0xDF, 0xFA, 0x00, 255),
                  QtGui.QColor(0xFF, 0x8B, 0x00, 255)]
        self.channelPens = []
        for n in range(4):
            p = QtGui.QPen()
            p.setColor(colors[n])
            p.setWidth(2.0)
            p.setCosmetic(True)
            self.channelPens.append(p)

        self._subviewMargin = 24
        self.grabGesture(QtCore.Qt.PinchGesture)

    def setData(self, data):
        self.data = data
        self.redraw()

    def drawSignals(self):
        subviewHeight = self.height() / 4 - self._subviewMargin / 2
        for i, data in enumerate(self.data):
            item = AnalyzerChannelGraphicsItem(data, subviewHeight,
                                               self.channelPens[i])
            item.setY(i*subviewHeight + i*self._subviewMargin / 2)
            self.scene.addItem(item)

    def redraw(self):
        self.resetTransform()
        self.scene.clear()
        self.drawSignals()
        self.scale(self.zoomLevel, 1)
        self.scene.setSceneRect(0, 0, len(self.data[0]),
                                self.height() - self._subviewMargin/2)

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
            self.zoomLevel *= gesture.scaleFactor()
            if self.zoomLevel < 1:
                self.zoomLevel = 1
            self.redraw()
        return True

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

        # Build path
        path = QtGui.QPainterPath(QtCore.QPointF(0, data[0] + topMargin))
        last_val = data[0]
        for i, d in enumerate(data):
            if d == last_val:
                path.lineTo(i, d*waveformHeight + topMargin)
            else:
                path.lineTo(i - 1, d*waveformHeight + topMargin)
                path.lineTo(i, d*waveformHeight + topMargin)
            last_val = d
        self.waveformPathItem = QtGui.QGraphicsPathItem(path, self)
        self.waveformPathItem.setPen(pen)
        self.addToGroup(self.waveformPathItem)
