'''
Created on Dec 16, 2014

@author: Jaakko Leppakangas
'''
import os
import subprocess
from threading import Thread, Event
from time import sleep

import mne

from PyQt4 import QtGui, QtCore
from PyQt4.Qt import QFileDialog
from PyQt4.QtCore import pyqtSignal

from ui_EdfToFifDialog import Ui_EdfToFifDialog
from ui_InfoDialog import Ui_infoDialog
from InfoDialog import InfoDialog

class EdfToFifDialog(QtGui.QDialog):
    edfConverted = pyqtSignal(str)
    updateUi = pyqtSignal()
    e = Event()
    
    def __init__(self, mneRoot = ""):
        """
        Init method for the dialog.
        """
        QtGui.QDialog.__init__(self)

        self.ui = Ui_EdfToFifDialog()
        self.ui.setupUi(self)

        os.environ['MNE_ROOT'] = str(mneRoot)
        
    def on_browseButton_clicked(self, checked=None):
        """
        Called when browse button for selecting the edf file is clicked.
        Opens a dialog for selecting a file.
        """
        if checked is None: return
        fileDialog = QFileDialog()

        self.fName = str(fileDialog.getOpenFileName(self, 
                                            'Select a file to convert',
                                            '/home/'))
        if self.fName != '':
            self.fName = self.fName.replace(" ", "\ ")
            self.ui.lineEditEdfName.setText(self.fName)
            splitted = str.split(self.fName, '/')
            destPath = '/'.join(splitted[:-1])
            #destPath = destPath.replace(" ", "\ ")
            self.ui.lineEditDestPath.setText(destPath)
            fifName = splitted[-1][:-4] + '.fif'
            #fifName = fifName.replace(" ", "\ ")
            self.ui.lineEditFifName.setText(fifName)
            
    def on_pushButtonShowInfo_clicked(self, checked=None):
        """
        """
        if checked is None: return
        fName = str(self.ui.lineEditEdfName.text())
        fName = fName.replace("\\", "")
        try:
            raw = mne.io.read_raw_edf(fName)
        except Exception as e:
            print str(e)
            return
        info = Ui_infoDialog()
        infoDialog = InfoDialog(raw, info, True)
        QtGui.QApplication.restoreOverrideCursor()
        infoDialog.exec_()
    
    def on_browseDestButton_clicked(self, checked=None):
        """
        Called when browse button for destination is clicked.
        Opens a dialog for selecting a path.
        """
        if checked is None: return
        fileDialog = QFileDialog()

        path = str(fileDialog.getExistingDirectory(self, 'Set directory',
                                                   '/home/'))
        if path != '':
            path = path.replace(" ", "\ ")
            self.ui.lineEditDestPath.setText(path)
            
            
    def accept(self, *args, **kwargs):
        """
        Overrided method for OK button.
        Converts the file to fif.
        """
        #if os.environ.get('MNE_ROOT') is None: return
        QtGui.QApplication.setOverrideCursor(QtGui.\
                                             QCursor(QtCore.Qt.WaitCursor))
        self.e.clear()
        fifName = str(self.ui.lineEditFifName.text())
        path = str(self.ui.lineEditDestPath.text())
        if ' ' in path:
            QtGui.QApplication.restoreOverrideCursor()
            QtGui.QMessageBox.critical(self, "Error",
                    "Do not use white spaces in the destination path!",
                    "Ok")
            return
        thread = Thread(target = self.convert, args=(fifName, path))
        thread.start()
        while not self.e.is_set():
            sleep(0.5)
            self.updateUi.emit()
            if self.e.is_set():
                break
        
        if self.retval == 0:
            self.edfConverted.emit(path + '/' + fifName)
        QtGui.QApplication.restoreOverrideCursor()
        return QtGui.QDialog.accept(self, *args, **kwargs)
    
    def convert(self, fifName, path):
        """
        A method that converts given edf to fif.
        Parameters:
        fifName - A name for the fif-file
        path    - A destination path for the file.
        """
        try:
            proc = subprocess.Popen('. $MNE_ROOT/bin/mne_setup_sh',
                                    shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        except:
            self.retval = 1
            self.e.set()
            return
        for line in proc.stdout.readlines():
            print line
        self.retval = proc.wait()
        print "the program return code was %d" % self.retval
        
        #fifName = fifName.replace(" ", "\ ")
        #command = str('mne_edf2fiff --edf /space/jaeilepp/R2rename/PSN_R2_101_20140807.edf --fif ' + self.path + '/' + fifName)
        
        command = str('mne_edf2fiff --edf ' + self.fName + \
        ' --fif ' + path + '/' + fifName)
        try:
            proc = subprocess.Popen(command,
                                    shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
        except:
            self.retval = 1
            self.e.set()
            return
        for line in proc.stdout.readlines():
            print line
        self.retval = proc.wait()
        print "the program return code was %d" % self.retval
        self.e.set()