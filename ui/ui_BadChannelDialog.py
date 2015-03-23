# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'badChannelDialog.ui'
#
# Created: Mon Jan  5 04:37:11 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_BadChannnelDialog(object):
    def setupUi(self, BadChannnelDialog):
        BadChannnelDialog.setObjectName(_fromUtf8("BadChannnelDialog"))
        BadChannnelDialog.resize(289, 358)
        self.gridLayout = QtGui.QGridLayout(BadChannnelDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.listWidgetBads = QtGui.QListWidget(BadChannnelDialog)
        self.listWidgetBads.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
        self.listWidgetBads.setObjectName(_fromUtf8("listWidgetBads"))
        self.gridLayout.addWidget(self.listWidgetBads, 2, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(BadChannnelDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 1)
        self.label = QtGui.QLabel(BadChannnelDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)

        self.retranslateUi(BadChannnelDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), BadChannnelDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), BadChannnelDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(BadChannnelDialog)

    def retranslateUi(self, BadChannnelDialog):
        BadChannnelDialog.setWindowTitle(_translate("BadChannnelDialog", "Edit bad channels", None))
        self.label.setText(_translate("BadChannnelDialog", "Select the channels to be marked bad.", None))

