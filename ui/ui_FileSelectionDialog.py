# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'fileSelectionDialog.ui'
#
# Created: Thu Mar 19 02:56:18 2015
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

class Ui_FileSelectDialog(object):
    def setupUi(self, FileSelectDialog):
        FileSelectDialog.setObjectName(_fromUtf8("FileSelectDialog"))
        FileSelectDialog.resize(498, 288)
        self.gridLayout_2 = QtGui.QGridLayout(FileSelectDialog)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.groupBox = QtGui.QGroupBox(FileSelectDialog)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(self.groupBox)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.lineEditRawFile = QtGui.QLineEdit(self.splitter)
        self.lineEditRawFile.setObjectName(_fromUtf8("lineEditRawFile"))
        self.pushButtonBrowse = QtGui.QPushButton(self.splitter)
        self.pushButtonBrowse.setObjectName(_fromUtf8("pushButtonBrowse"))
        self.gridLayout.addWidget(self.splitter, 2, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.pushButtonShowInfo = QtGui.QPushButton(self.groupBox)
        self.pushButtonShowInfo.setObjectName(_fromUtf8("pushButtonShowInfo"))
        self.horizontalLayout_3.addWidget(self.pushButtonShowInfo)
        self.gridLayout.addLayout(self.horizontalLayout_3, 3, 0, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.labelMneRoot = QtGui.QLabel(self.groupBox)
        self.labelMneRoot.setObjectName(_fromUtf8("labelMneRoot"))
        self.horizontalLayout.addWidget(self.labelMneRoot)
        self.lineEditMneRoot = QtGui.QLineEdit(self.groupBox)
        self.lineEditMneRoot.setText(_fromUtf8(""))
        self.lineEditMneRoot.setObjectName(_fromUtf8("lineEditMneRoot"))
        self.horizontalLayout.addWidget(self.lineEditMneRoot)
        self.gridLayout.addLayout(self.horizontalLayout, 5, 0, 1, 1)
        self.pushButtonConvertEdf = QtGui.QPushButton(self.groupBox)
        self.pushButtonConvertEdf.setObjectName(_fromUtf8("pushButtonConvertEdf"))
        self.gridLayout.addWidget(self.pushButtonConvertEdf, 0, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_4.addWidget(self.label)
        self.checkBoxPreload = QtGui.QCheckBox(self.groupBox)
        self.checkBoxPreload.setChecked(True)
        self.checkBoxPreload.setObjectName(_fromUtf8("checkBoxPreload"))
        self.horizontalLayout_4.addWidget(self.checkBoxPreload)
        self.gridLayout.addLayout(self.horizontalLayout_4, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem1, 6, 0, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(FileSelectDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_2.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(FileSelectDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), FileSelectDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), FileSelectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(FileSelectDialog)
        FileSelectDialog.setTabOrder(self.pushButtonConvertEdf, self.lineEditRawFile)
        FileSelectDialog.setTabOrder(self.lineEditRawFile, self.pushButtonBrowse)
        FileSelectDialog.setTabOrder(self.pushButtonBrowse, self.pushButtonShowInfo)
        FileSelectDialog.setTabOrder(self.pushButtonShowInfo, self.lineEditMneRoot)
        FileSelectDialog.setTabOrder(self.lineEditMneRoot, self.buttonBox)

    def retranslateUi(self, FileSelectDialog):
        FileSelectDialog.setWindowTitle(_translate("FileSelectDialog", "Select a file for processing", None))
        self.groupBox.setTitle(_translate("FileSelectDialog", "File selection", None))
        self.pushButtonBrowse.setText(_translate("FileSelectDialog", "Browse...", None))
        self.pushButtonShowInfo.setText(_translate("FileSelectDialog", "Show file info", None))
        self.labelMneRoot.setToolTip(_translate("FileSelectDialog", "Set the environment variable MNE_ROOT.", None))
        self.labelMneRoot.setText(_translate("FileSelectDialog", "Mne root directory:", None))
        self.lineEditMneRoot.setToolTip(_translate("FileSelectDialog", "Set the environment variable MNE_ROOT.", None))
        self.pushButtonConvertEdf.setText(_translate("FileSelectDialog", "Convert from edf to fif...", None))
        self.label.setText(_translate("FileSelectDialog", "Select a raw file for pre-processing:", None))
        self.checkBoxPreload.setToolTip(_translate("FileSelectDialog", "Preload data into memory for data manipulation and faster indexing. If True,\n"
"the data will be preloaded into memory (fast, requires large amount of\n"
"memory). If preload is a string, preload is the file name of a memory-mapped\n"
"file which is used to store the data on the hard drive (slower, requires less memory).", None))
        self.checkBoxPreload.setText(_translate("FileSelectDialog", "Preload", None))

