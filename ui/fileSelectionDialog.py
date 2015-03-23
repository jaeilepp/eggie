'''
Created on Dec 16, 2014

@author: Jaakko Leppakangas
'''

import os
import mne

from PyQt4.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt4.Qt import QSettings
from PyQt4 import QtGui

from edfToFifDialog import EdfToFifDialog
from general.caller import Caller
from ui_FileSelectionDialog import Ui_FileSelectDialog
from ui.InfoDialog import InfoDialog
from ui.ui_InfoDialog import Ui_infoDialog

class FileSelectionDialog(QtGui.QDialog):
    """
    """
    fileChanged = pyqtSignal()
    settings = QSettings("CIBR", "Eggie")
    def __init__(self, parent):
        """
        Dialog for setting the raw file and environment variables.
        """
        QtGui.QDialog.__init__(self, parent)
        self.parent = parent
        self.ui = Ui_FileSelectDialog()
        self.ui.setupUi(self)
        mneRoot = os.environ.get('MNE_ROOT', '')
        if mneRoot == "":
            mneRoot = self.settings.value("MNE_ROOT", "").toString()
        self.ui.lineEditMneRoot.setText(mneRoot)
        self.show()
        
    def on_pushButtonConvertEdf_clicked(self, checked=None):
        """
        Opens a dialog for converting files to fif.
        """
        if checked is None: return
        self.mneRoot = self.ui.lineEditMneRoot.text()
        if str(self.mneRoot) is '':
            QtGui.QMessageBox.critical(self, "Cannot convert",
                    "MNE_ROOT must be set before conversion",
                    "Ok")
            return
        self.edfToFifDialog = EdfToFifDialog(self.mneRoot)
        self.edfToFifDialog.edfConverted.connect(self.edfConverted)
        self.edfToFifDialog.updateUi.connect(self.parent.updateUi)
        self.edfToFifDialog.show()
        
    def on_pushButtonBrowse_clicked(self, checked=None):
        """
        Opens a dialog for selecting a raw file.
        """
        if checked is None: return
        self.fname = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                            '/home/', "Fif-files (*.fif);;All files (*.*)"))
      
        if self.fname != '':        
            self.ui.lineEditRawFile.setText(self.fname)
        
    def on_pushButtonShowInfo_clicked(self, checked=None):
        """
        Opens a dialog for showing file info.
        Called when show info button is clicked.
        """
        if checked is None: return
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
        print str(self.ui.lineEditRawFile.text())
        try:
            raw = mne.io.Raw(str(self.ui.lineEditRawFile.text()))
        except Exception as e:
            messageBox = QtGui.QMessageBox()
            messageBox.setText(str(e))
            QtGui.QApplication.restoreOverrideCursor()
            messageBox.exec_()
        info = Ui_infoDialog()
        infoDialog = InfoDialog(raw, info, True)
        QtGui.QApplication.restoreOverrideCursor()
        infoDialog.exec_()
            
    @pyqtSlot(str)
    def edfConverted(self, fifName):
        """
        Slot for setting the file name to the line edit.
        Parameters:
        fifName - The name of the file.
        """
        self.ui.lineEditRawFile.setText(fifName)
        
    def accept(self, *args, **kwargs):
        """
        Called when ok button is clicked.
        If raw file is successfully loaded, a fileChanged -signal is emitted.
        """
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
        
        mneRoot = self.ui.lineEditMneRoot.text()
        if str(mneRoot) is '':
            messageBox = QtGui.QMessageBox()
            messageBox.setText("Environment variables MNE_ROOT " + 
                               "must be set!")
            messageBox.exec_()
            QtGui.QApplication.restoreOverrideCursor()
            return
        else:
            self.settings.setValue("MNE_ROOT", mneRoot)
        caller = Caller.Instance()
        preload = self.ui.checkBoxPreload.isChecked()
        try:
            caller.setRaw(str(self.ui.lineEditRawFile.text()), self.parent,
                          preload)
            self.fileChanged.emit()                          
        except Exception as e:
            messageBox = QtGui.QMessageBox()
            messageBox.setText("Cannot open file. ")
            messageBox.setInformativeText(str(e))
            messageBox.exec_()
            QtGui.QApplication.restoreOverrideCursor()
            
        QtGui.QDialog.accept(self, *args, **kwargs)
        QtGui.QApplication.restoreOverrideCursor()

        
