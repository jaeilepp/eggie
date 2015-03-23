# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'saveDialog.ui'
#
# Created: Mon Jan 19 06:13:18 2015
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

class Ui_SaveDialog(object):
    def setupUi(self, SaveDialog):
        SaveDialog.setObjectName(_fromUtf8("SaveDialog"))
        SaveDialog.resize(400, 142)
        self.gridLayout = QtGui.QGridLayout(SaveDialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.labelFileName = QtGui.QLabel(SaveDialog)
        self.labelFileName.setObjectName(_fromUtf8("labelFileName"))
        self.horizontalLayout.addWidget(self.labelFileName)
        self.lineEditFileName = QtGui.QLineEdit(SaveDialog)
        self.lineEditFileName.setText(_fromUtf8(""))
        self.lineEditFileName.setObjectName(_fromUtf8("lineEditFileName"))
        self.horizontalLayout.addWidget(self.lineEditFileName)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 2, 2)
        self.buttonBox = QtGui.QDialogButtonBox(SaveDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)
        self.label = QtGui.QLabel(SaveDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 5, 0, 1, 2)
        self.splitter = QtGui.QSplitter(SaveDialog)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.lineEditPath = QtGui.QLineEdit(self.splitter)
        self.lineEditPath.setObjectName(_fromUtf8("lineEditPath"))
        self.pushButtonBrowse = QtGui.QPushButton(self.splitter)
        self.pushButtonBrowse.setObjectName(_fromUtf8("pushButtonBrowse"))
        self.gridLayout.addWidget(self.splitter, 1, 0, 1, 1)

        self.retranslateUi(SaveDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SaveDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SaveDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SaveDialog)
        SaveDialog.setTabOrder(self.lineEditPath, self.pushButtonBrowse)
        SaveDialog.setTabOrder(self.pushButtonBrowse, self.lineEditFileName)
        SaveDialog.setTabOrder(self.lineEditFileName, self.buttonBox)

    def retranslateUi(self, SaveDialog):
        SaveDialog.setWindowTitle(_translate("SaveDialog", " Save file", None))
        self.labelFileName.setToolTip(_translate("SaveDialog", "Set the environment variable MNE_ROOT.", None))
        self.labelFileName.setText(_translate("SaveDialog", "File name:", None))
        self.lineEditFileName.setToolTip(_translate("SaveDialog", "Set the environment variable MNE_ROOT.", None))
        self.label.setText(_translate("SaveDialog", "Select the path:", None))
        self.pushButtonBrowse.setText(_translate("SaveDialog", "Browse...", None))

