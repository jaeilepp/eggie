# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'edfToFifDialog.ui'
#
# Created: Tue Feb  3 03:39:13 2015
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

class Ui_EdfToFifDialog(object):
    def setupUi(self, EdfToFifDialog):
        EdfToFifDialog.setObjectName(_fromUtf8("EdfToFifDialog"))
        EdfToFifDialog.resize(501, 183)
        self.gridLayout = QtGui.QGridLayout(EdfToFifDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(EdfToFifDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.lineEditEdfName = QtGui.QLineEdit(self.splitter)
        self.lineEditEdfName.setObjectName(_fromUtf8("lineEditEdfName"))
        self.browseButton = QtGui.QPushButton(self.splitter)
        self.browseButton.setObjectName(_fromUtf8("browseButton"))
        self.gridLayout.addWidget(self.splitter, 0, 1, 1, 1)
        self.splitter_2 = QtGui.QSplitter(EdfToFifDialog)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.lineEditDestPath = QtGui.QLineEdit(self.splitter_2)
        self.lineEditDestPath.setObjectName(_fromUtf8("lineEditDestPath"))
        self.browseDestButton = QtGui.QPushButton(self.splitter_2)
        self.browseDestButton.setObjectName(_fromUtf8("browseDestButton"))
        self.gridLayout.addWidget(self.splitter_2, 3, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(EdfToFifDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 5, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.label = QtGui.QLabel(EdfToFifDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(EdfToFifDialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.lineEditFifName = QtGui.QLineEdit(EdfToFifDialog)
        self.lineEditFifName.setObjectName(_fromUtf8("lineEditFifName"))
        self.gridLayout.addWidget(self.lineEditFifName, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(EdfToFifDialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.pushButtonShowInfo = QtGui.QPushButton(EdfToFifDialog)
        self.pushButtonShowInfo.setEnabled(True)
        self.pushButtonShowInfo.setObjectName(_fromUtf8("pushButtonShowInfo"))
        self.gridLayout.addWidget(self.pushButtonShowInfo, 1, 1, 1, 1)

        self.retranslateUi(EdfToFifDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), EdfToFifDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), EdfToFifDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(EdfToFifDialog)
        EdfToFifDialog.setTabOrder(self.lineEditEdfName, self.browseButton)
        EdfToFifDialog.setTabOrder(self.browseButton, self.pushButtonShowInfo)
        EdfToFifDialog.setTabOrder(self.pushButtonShowInfo, self.lineEditFifName)
        EdfToFifDialog.setTabOrder(self.lineEditFifName, self.lineEditDestPath)
        EdfToFifDialog.setTabOrder(self.lineEditDestPath, self.browseDestButton)
        EdfToFifDialog.setTabOrder(self.browseDestButton, self.buttonBox)

    def retranslateUi(self, EdfToFifDialog):
        EdfToFifDialog.setWindowTitle(_translate("EdfToFifDialog", "Select a file for conversion", None))
        self.browseButton.setText(_translate("EdfToFifDialog", "Browse...", None))
        self.browseDestButton.setText(_translate("EdfToFifDialog", "Browse...", None))
        self.label.setText(_translate("EdfToFifDialog", "Select file to convert:", None))
        self.label_2.setText(_translate("EdfToFifDialog", "Select destination path:", None))
        self.label_3.setText(_translate("EdfToFifDialog", "Enter file name:", None))
        self.pushButtonShowInfo.setText(_translate("EdfToFifDialog", "Show info", None))

