#!/usr/bin/env python

from PySide import QtGui, QtCore

class AnalyzerWidget(QtGui.QGraphicsView):
    def __init__(self, parent=None):
        super(AnalyzerWidget, self).__init__(parent)
        self.scene = QtGui.QGraphicsScene(self)
        self.setScene(self.scene)
        self._data = [[0],[0],[0],[0]]
        self._scale = 20

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
        self._data = data
        self.redraw()

    def drawSignals(self):
        subviewHeight = self.height() / 4 - self._subviewMargin / 2
        for i, line in enumerate(self._data):
            path = QtGui.QPainterPath(QtCore.QPointF(0, line[0]))
            last_val = line[0]
            for j, d in enumerate(line):
                if d == last_val:
                    path.lineTo(j, d*subviewHeight)
                else:
                    path.lineTo(j - 1, d*subviewHeight)
                    path.lineTo(j, d*subviewHeight)
                last_val = d
            path.translate(0, i*subviewHeight + i*self._subviewMargin / 2)
            self.scene.addPath(path, self.channelPens[i])

    def redraw(self):
        self.resetTransform()
        self.scene.clear()
        self.drawSignals()
        self.scale(self._scale, 1)
        self.scene.setSceneRect(0, 0, len(self._data[0]),
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
            self._scale *= gesture.scaleFactor()
            if self._scale < 1:
                self._scale = 1
            self.redraw()
        return True
