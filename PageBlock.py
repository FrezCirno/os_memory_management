import sys
import random
from PyQt5 import QtCore, QtGui, QtWidgets


class PageBlock(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PageBlock, self).__init__(parent)
        self._highlight = -1
        self._highlight_color = QtCore.Qt.red

    def fget_highlight(self):
        return self._highlight

    def fset_highlight(self, v):
        self._highlight = v
        self.update()

    def fget_highlight_color(self):
        return self._highlight_color

    def fset_highlight_color(self, v):
        self._highlight_color = v
        self.update()

    highlight = QtCore.pyqtProperty(int, fget_highlight, fset_highlight)
    color = QtCore.pyqtProperty(QtGui.QColor, fget_highlight_color, fset_highlight_color)

    def paintEvent(self, event: QtGui.QPaintEvent):
        # self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        painter = QtGui.QPainter(self)
        paint_rect = QtCore.QRect(0, 0, self.width(), self.height())
        painter.setViewport(paint_rect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        for x in range(10):
            painter.setPen(QtCore.Qt.NoPen)
            painter.setBrush(self._highlight_color if x == self.highlight else QtCore.Qt.green)
            paint_rect.setRect(x * self.width() // 10 + 1, 2, self.width() // 10 - 2, self.height() - 4)
            painter.drawRect(paint_rect)

        painter.setPen(QtCore.Qt.black)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRoundedRect(self.rect(), 6, 6)
