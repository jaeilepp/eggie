'''
Created on 8.1.2015

@author: Jaakko Leppakangas
'''

from PyQt4 import QtGui, QtCore
from PyQt4.Qt import QSettings

from threading import Thread, Event
from time import sleep
import sys

from general.caller import Caller
from ui_SaveDialog import Ui_SaveDialog

class SaveDialog(QtGui.QDialog):
    caller = Caller.Instance()
    e = Event()
    error = False # Boolean to notify error in worker thread.
    settings = QSettings("CIBR", "Eggie")
    
    def __init__(self, parent):
        """
        """
        QtGui.QDialog.__init__(self)

        self.ui = Ui_SaveDialog()
        self.ui.setupUi(self)
        self.parent = parent
        #self.ui.buttonBox.button(QtGui.QDialogButtonBox.Save).clicked.\
        #    connect(self.on_SaveClicked)
        
        #fName = self.caller.raw.info['filename']
        # Remove file-extension and add -pre.fif
        self.ui.lineEditPath.setText(self.settings.value("SaveFolder", "").\
                                     toString())
        fullPath = self.caller.raw.info['filename'].\
            rsplit('.', 1)[0] + '-pre.fif'
        fName = fullPath.rsplit('/', 1)
        if len(fName) == 2:
            self.ui.lineEditFileName.setText(fName[1])
            if self.ui.lineEditPath.text() == "":
                self.ui.lineEditPath.setText(fName[0])
        
        #self.caller.raw.save(fName, preload=True)
        
    def on_pushButtonBrowse_clicked(self, checked=None):
        """
        Called when browse button is clicked.
        Opens a dialog for choosing a directory.
        """
        if checked is None: return
        path = str(QtGui.QFileDialog.getExistingDirectory(self, 'Select path',
                            self.ui.lineEditPath.text()))
        if path != '':
            self.ui.lineEditPath.setText(path)
        
    def saveFile(self):
        """
        Method for saving the file.
        """
        fName = str(self.ui.lineEditPath.text()) + '/' + \
                str(self.ui.lineEditFileName.text())
        try:
            self.caller.raw.save(fName)
            self.caller.setRaw(fName, self.parent)
        except IOError as e:
            self.error = True
            sys.stderr.write("Could not save!\n")
            sys.stderr.write(str(e))
        finally:
            self.e.set()
            
    def accept(self, *args, **kwargs):
        """
        Saves the raw object to a file.
        """
        QtGui.QApplication.setOverrideCursor(QtGui.\
                                             QCursor(QtCore.Qt.WaitCursor))

        self.thread = Thread(target = self.saveFile)
        self.thread.start()
        while not (self.e.is_set()):
            sleep(0.5)
            self.parent.updateUi()
            if self.e.is_set(): break

        QtGui.QApplication.restoreOverrideCursor()
        self.e.clear()
        if self.error:
            messageBox = QtGui.QMessageBox()
            messageBox.setText("Error while saving data.")
            messageBox.exec_()
            self.error = False
        self.settings.setValue("SaveFolder", self.ui.lineEditPath.text())
        return QtGui.QDialog.accept(self, *args, **kwargs)