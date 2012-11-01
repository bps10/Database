# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'guiDesign.ui'
#
# Created: Tue Oct 30 13:11:22 2012
#      by: PyQt4 UI code generator 4.8.6
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DockWidget(object):
    def setupUi(self, DockWidget):
        DockWidget.setObjectName(_fromUtf8("DockWidget"))
        DockWidget.resize(753, 697)
        DockWidget.setWindowTitle(QtGui.QApplication.translate("DockWidget", "DockWidget", None, QtGui.QApplication.UnicodeUTF8))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.treeView = QtGui.QTreeView(self.dockWidgetContents)
        self.treeView.setGeometry(QtCore.QRect(0, 0, 201, 521))
        self.treeView.setObjectName(_fromUtf8("treeView"))
        self.qwtPlot = Qwt5.QwtPlot(self.dockWidgetContents)
        self.qwtPlot.setGeometry(QtCore.QRect(210, 0, 521, 221))
        self.qwtPlot.setObjectName(_fromUtf8("qwtPlot"))
        self.scrollArea = QtGui.QScrollArea(self.dockWidgetContents)
        self.scrollArea.setGeometry(QtCore.QRect(430, 530, 271, 80))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 269, 78))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.lineEdit = QtGui.QLineEdit(self.dockWidgetContents)
        self.lineEdit.setGeometry(QtCore.QRect(220, 560, 171, 21))
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.lineEdit_2 = QtGui.QLineEdit(self.dockWidgetContents)
        self.lineEdit_2.setGeometry(QtCore.QRect(220, 530, 171, 21))
        self.lineEdit_2.setObjectName(_fromUtf8("lineEdit_2"))
        self.qwtPlot_2 = Qwt5.QwtPlot(self.dockWidgetContents)
        self.qwtPlot_2.setGeometry(QtCore.QRect(210, 240, 521, 231))
        self.qwtPlot_2.setObjectName(_fromUtf8("qwtPlot_2"))
        self.lineEdit_3 = QtGui.QLineEdit(self.dockWidgetContents)
        self.lineEdit_3.setGeometry(QtCore.QRect(220, 590, 171, 21))
        self.lineEdit_3.setObjectName(_fromUtf8("lineEdit_3"))
        self.label = QtGui.QLabel(self.dockWidgetContents)
        self.label.setGeometry(QtCore.QRect(170, 530, 46, 13))
        self.label.setText(QtGui.QApplication.translate("DockWidget", "Query", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(self.dockWidgetContents)
        self.label_2.setGeometry(QtCore.QRect(170, 560, 46, 13))
        self.label_2.setText(QtGui.QApplication.translate("DockWidget", "Query", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.label_3 = QtGui.QLabel(self.dockWidgetContents)
        self.label_3.setGeometry(QtCore.QRect(170, 590, 46, 13))
        self.label_3.setText(QtGui.QApplication.translate("DockWidget", "Query", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        DockWidget.setWidget(self.dockWidgetContents)

        self.retranslateUi(DockWidget)
        QtCore.QObject.connect(self.treeView, QtCore.SIGNAL(_fromUtf8("entered(QModelIndex)")), self.qwtPlot.replot)
        QtCore.QObject.connect(self.treeView, QtCore.SIGNAL(_fromUtf8("doubleClicked(QModelIndex)")), self.qwtPlot_2.replot)
        QtCore.QObject.connect(self.lineEdit, QtCore.SIGNAL(_fromUtf8("returnPressed()")), self.scrollArea.show)
        QtCore.QMetaObject.connectSlotsByName(DockWidget)

    def retranslateUi(self, DockWidget):
        pass

from PyQt4 import Qwt5
