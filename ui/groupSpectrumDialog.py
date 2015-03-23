'''
Created on 14.1.2015

@author: Jaakko Leppakangas
'''
from PyQt4 import QtGui, QtCore
from PyQt4.Qt import QSettings
from os import listdir
from os.path import isfile, join

import numpy as np
from mne import find_events

from general.caller import Caller
from ui_GroupSpectrumDialog import Ui_GroupSpectrumDialog
from powerSpectrumWidget import PowerSpectrumWidget
from timeSeriesDialog import TimeSeriesDialog

class GroupSpectrumDialog(QtGui.QDialog):
    fileChanged = QtCore.pyqtSignal()
    caller = Caller.Instance()
    conditions = []
    tmax = 1000
    settings = QSettings("CIBR", "Eggie")
    
    def __init__(self, parent, conditions, fmin, fmax, nfft, logarithm, lout, 
                 tmax):
        """
        Init method for the dialog.
        Constructs a set of time series from the given parameters.
        Parameters:
        parent     - The parent window for this dialog.
        conditions - A list of PowerSpectrumWidgets. The data from these 
                     widgets are copied to this dialog.
        fmin       - Starting frequency of interest.
        fmax       - Ending frequency of interest.
        nfft       - The length of the tapers ie. the windows. 
                     The smaller it is the smoother are the PSDs.
        logarithm  - A boolean that determines if a logarithmic scale is used.
        lout       - A layout file name.
        """
        QtGui.QDialog.__init__(self)
        
        self.conditions = []
        self.ui = Ui_GroupSpectrumDialog()
        self.ui.setupUi(self)
        self.installEventFilters()
        self.parent = parent
        self.tmax = tmax
        if conditions == []:
            widget = PowerSpectrumWidget(tmax, self)
            widget.setStartTime(5)
            widget.setEndTime(tmax)
            self.conditions.append(widget)
            widget.index = 0
            widget.removeWidget.connect(self.on_RemoveWidget_clicked)
            widget.channelCopy.connect(self.copyChannels)
            self.ui.verticalLayoutConditions.addWidget(widget)
        else:
            i = 0
            for condition in conditions:
                widget = PowerSpectrumWidget(tmax, self)
                widget.setStartTime(condition.getStartTime())
                widget.setEndTime(condition.getEndTime())
                widget.setColor(condition.getColor())
                widget.setChannelColor(condition.getChannelColor())
                widget.on_ChannelsChanged(condition.getChannels())
                self.conditions.append(widget)
                widget.index = i
                widget.removeWidget.connect(self.on_RemoveWidget_clicked)
                widget.channelCopy.connect(self.copyChannels)
                self.ui.verticalLayoutConditions.addWidget(widget)
                i+=1
        
        self.ui.spinBoxFmin.setValue(fmin)
        self.ui.spinBoxFmax.setValue(fmax)
        self.ui.spinBoxNfft.setValue(nfft)
        self.ui.checkBoxLogarithm.setChecked(logarithm)
        self.ui.lineEditLayout.setText(lout)
        self.ui.buttonBox.addButton("Start", QtGui.QDialogButtonBox.AcceptRole)
        self.ui.buttonBox.addButton(QtGui.QDialogButtonBox.Close)
        self.ui.lineEditPath.editingFinished.connect(self.on_PathChanged)
        
    @QtCore.pyqtSlot(int)
    def on_RemoveWidget_clicked(self, index):
        """
        Called when a condition widget sends a remove signal.
        Removes a condition from the list.
        """
        widget = self.conditions.pop(index)
        self.ui.verticalLayoutConditions.removeWidget(widget)
        widget.deleteLater()
        widget = None
        # Restore order of indices:
        for i in xrange(len(self.conditions)):
            self.conditions[i].index = i
            
    @QtCore.pyqtSlot(int)
    def copyChannels(self, index):
        """
        """
        channels = self.conditions[index].getChannels()
        for widget in self.conditions:
            widget.on_ChannelsChanged(channels)
            
    @QtCore.pyqtSlot()
    def on_PathChanged(self):
        """
        Called when source path field loses focus. Loads the first fif file
        in the folder and uses it as a template for configuring the parameters.
        """
        QtGui.QApplication.setOverrideCursor(QtGui.\
                                             QCursor(QtCore.Qt.WaitCursor))
        data_path = str(self.ui.lineEditPath.text())
        try:
            fifFiles = [ f for f in listdir(data_path)\
                      if isfile(join(data_path,f)) and f.endswith('.fif') ]
        except Exception as e:
            messageBox = QtGui.QMessageBox()
            messageBox.setText("Cannot open folder.")
            messageBox.setInformativeText(str(e))
            messageBox.exec_()
            QtGui.QApplication.restoreOverrideCursor()
            return
        if len(fifFiles) == 0:
            QtGui.QApplication.restoreOverrideCursor()
            return
        else:
            fName = data_path + '/' + fifFiles[0]   
            try:
                #raw = mne.io.Raw(fName, preload=True)
                self.caller.setRaw(fName, self, False)
            except Exception as e:
                messageBox = QtGui.QMessageBox()
                messageBox.setText("Cannot open file " + fName)
                messageBox.setInformativeText(str(e))
                messageBox.exec_()
                QtGui.QApplication.restoreOverrideCursor()
                return
        self.tmax = np.floor(self.caller.raw.index_as_time\
                             (self.caller.raw.n_times))
        for condition in self.conditions:
            condition.setMaxTime(self.tmax)
        triggers = []
        try:
            triggers = find_events(self.caller.raw, stim_channel='STI 014')
            for trigger in triggers:
                self.ui.comboBoxStart.addItem(str(trigger[2]))
                self.ui.comboBoxEnd.addItem(str(trigger[2]))
        except Exception as e:
            print 'Could not find triggers from STI 014.'
            print str(e)
        self.fileChanged.emit()
        messageBox = QtGui.QMessageBox()
        messageBox.setText("Working file changed to " + fName)
        QtGui.QApplication.restoreOverrideCursor()
        messageBox.exec_()
            
    def on_pushButtonBrowseLayout_clicked(self, checked=None):
        """
        Called when browse layout button is clicked.
        Opens a file dialog for selecting a file.
        """
        if checked is None: return
        fname = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                            '/home/', 
                            "Layout-files (*.lout *.lay);;All files (*.*)"))
        self.ui.lineEditLayout.setText(fname)
        self.settings.setValue("Layout", fname)
    
    def on_pushButtonBrowseDest_clicked(self, checked=None):
        """
        Called when browse destination path button is clicked.
        Opens a file dialog for selecting a directory.
        """
        if checked is None: return
        dest = str(QtGui.QFileDialog.getExistingDirectory(self,
                                                        'Set destination path',
                                                        '/home/'))
        self.ui.lineEditDestPath.setText(dest)
        
    def on_pushButtonBrowsePath_clicked(self, checked=None):
        """
        Called when browse path button is clicked.
        Opens a file dialog for selecting a directory.
        """
        if checked is None: return
        path = str(QtGui.QFileDialog.getExistingDirectory(self,
                                                        'Set source path',
                                                        '/home/'))
        self.ui.lineEditPath.setText(path)
        self.on_PathChanged()
        
    def on_pushButtonAddTimeSeries_clicked(self, checked=None):
        """
        Called when the add condition button is clicked.
        Adds a new condition to the list.
        """
        if checked is None: return
        index = len(self.conditions)
        channels = self.conditions[0].getChannels()
        widget = PowerSpectrumWidget(self.tmax, self)
        widget.index = index
        widget.on_ChannelsChanged(channels)
        self.conditions.append(widget)
        self.ui.verticalLayoutConditions.addWidget(widget)
        widget.removeWidget.connect(self.on_RemoveWidget_clicked)
        widget.channelCopy.connect(self.copyChannels)
    
    def accept(self, *args, **kwargs):
        """
        Begins the plotting of power spectral densities to files.
        """
        self.caller.clearGroups()
        destPath = str(self.ui.lineEditDestPath.text())
        if destPath == "":
            messageBox = QtGui.QMessageBox()
            messageBox.setText("You must set a destination "\
                                + "path for the images.")
            messageBox.exec_()
            return
            
        QtGui.QApplication.setOverrideCursor(QtGui.\
                                             QCursor(QtCore.Qt.WaitCursor))
        colors = []
        times = [] # Array for start and end times.
        channelColors = dict()
        i = 0
        for condition in self.conditions:
            start = condition.getStartTime()
            end = condition.getEndTime()
            if end < start:
                messageBox = QtGui.QMessageBox()
                messageBox.setText\
                            ("End time must be higher than the start time.")
                messageBox.exec_()
                QtGui.QApplication.restoreOverrideCursor()
                return 
            times.append((start, end))
            
            colors.append(condition.getColor())
            channels = condition.getChannels()
            channelColors[i] = (condition.getChannelColor(), channels)
            i += 1
        if len(times) == 0:
            messageBox = QtGui.QMessageBox()
            messageBox.setText("Could not find data. Check parameters!")
            messageBox.exec_()
            QtGui.QApplication.restoreOverrideCursor()
            return 
        params = dict()
        params['times'] = times
        params['fmin'] = self.ui.spinBoxFmin.value()
        params['fmax'] = self.ui.spinBoxFmax.value()
        params['nfft'] = self.ui.spinBoxNfft.value()
        params['log']  = self.ui.checkBoxLogarithm.isChecked()
        params['lout'] = str(self.ui.lineEditLayout.text())
        params['dpi']  = self.ui.spinBoxResolution.value()
        params['format'] = str(self.ui.comboBoxFormat.currentText())
        params['groupAverage'] = self.ui.checkBoxGroupAverage.isChecked()
        params['plotChannels'] = self.ui.checkBoxPlotChannels.isChecked()
        
        origRaw = self.caller.raw.info['filename']
        data_path = str(self.ui.lineEditPath.text())
        try:
            fifFiles = [ f for f in listdir(data_path)\
                      if isfile(join(data_path,f)) and f.endswith('.fif') ]
        except OSError as e:
            messageBox = QtGui.QMessageBox()
            messageBox.setText("Error reading files.")
            messageBox.setInformativeText(str(e))
            messageBox.exec_()
            QtGui.QApplication.restoreOverrideCursor()
            return
        print "Found {!s} fif-files.\n".format(len(fifFiles))
        self.parent.ui.progressBar.setVisible(True)
        if params['groupAverage']:
            self.parent.ui.progressBar.setRange(0, len(fifFiles) + 1)
        else:
            self.parent.ui.progressBar.setRange(0, len(fifFiles))
        self.parent.ui.progressBar.setValue(0)
        counter = 0
        for fName in fifFiles:
            print "Working on {!s}...\n".format(fName)
            raw = data_path + '/' + fName
            try:
                self.caller.setRaw(raw, self)
            except Exception as e:
                messageBox = QtGui.QMessageBox()
                messageBox.setText("Cannot open file " + raw)
                messageBox.setInformativeText(str(e))
                messageBox.exec_()
                break
            self.parent.updateUi()
            if self.ui.checkBoxTriggers.isChecked():
                times = []
                try:
                    events = find_events(self.caller.raw, 'STI 014')
                except Exception as e:
                    print "Could not find events from STI 014. Aborting..."
                    print str(e)
                    continue
                triggerStart, _ = self.ui.comboBoxStart.currentText().toInt()
                #triggerStart = int(triggerStart)
                triggerEnd, _ = self.ui.comboBoxEnd.currentText().toInt()
                #triggerEnd = int(triggerEnd))
                tmin = np.where(events[:,2]==triggerStart)[0][0]
                tmax = np.where(events[:,2]==triggerEnd)[0][0]
                tmin = self.caller.raw.index_as_time(events[tmin][0])
                tmax = self.caller.raw.index_as_time(events[tmax][0])
                times.append((int(tmin[0]), int(tmax[0])))
                print times
                params['times'] = times
            try:
                self.caller.plotSpectrum(self, params, colors, channelColors,
                                         destPath)
            except IOError as e:
                messageBox = QtGui.QMessageBox()
                messageBox.setText("IO error occurred:")
                messageBox.setInformativeText(str(e))
                messageBox.exec_()
                break
            except RuntimeError as e:
                messageBox = QtGui.QMessageBox()
                messageBox.setText("Runtime error occurred:")
                messageBox.setInformativeText(str(e))
                messageBox.exec_()
                break
            except Exception as e:
                messageBox = QtGui.QMessageBox()
                messageBox.setText("Error occurred:")
                messageBox.setInformativeText(str(e))
                messageBox.exec_()
                break
            counter = counter + 1
            self.parent.ui.progressBar.setValue(counter)
        
        if params['groupAverage']:
            print "Calculating group averages..."
            self.updateUi()
            self.caller.createGroupAverage(destPath, colors, channelColors, params['format'], 
                                           params['dpi'], params['log'], params['lout'])
            counter = counter + 1
            
        self.parent.ui.progressBar.setValue(counter)
        self.updateUi()
        self.caller.setRaw(origRaw, self)
        self.parent.ui.progressBar.setVisible(False)
        QtGui.QApplication.restoreOverrideCursor()
    
    @QtCore.pyqtSlot(int)   
    def on_comboBoxStart_currentIndexChanged(self, index):
        """
        Method for setting time on the start time spinbox after trigger 
        selection has changed.
        Parameters:
        index - Index of the selection in combobox.
        """
        if not self.ui.checkBoxTriggers.isChecked(): return
        triggers = find_events(self.caller.raw, stim_channel='STI 014')
        triggerStart, _ = self.ui.comboBoxStart.currentText().toInt()
        tmin = np.where(triggers[:,2]==triggerStart)[0][0]
        tmin = self.caller.raw.index_as_time(triggers[tmin][0])
        tmin = int(tmin[0])
        self.conditions[0].setStartTime(tmin)
        
    @QtCore.pyqtSlot(int)   
    def on_comboBoxEnd_currentIndexChanged(self, index):
        """
        Method for setting time on the end time spinbox after trigger selection
        has changed.
        Parameters:
        index - Index of the selection in combobox.
        """
        if not self.ui.checkBoxTriggers.isChecked(): return
        triggers = find_events(self.caller.raw, stim_channel='STI 014')
        triggerEnd, _ = self.ui.comboBoxEnd.currentText().toInt()
        tmax = np.where(triggers[:,2]==triggerEnd)[0][0]
        tmax = self.caller.raw.index_as_time(triggers[tmax][0])
        tmax = int(tmax[0])
        self.conditions[0].setEndTime(tmax)
        
    @QtCore.pyqtSlot(bool)
    def on_checkBoxTriggers_toggled(self, toggled):
        """
        A slot for setting the powerspectrumwidgets according to trigger 
        settings. Called when trigger check box is toggled.
        Parameters:
        toggled - A boolean that determines if check box is ticked.
        """
        if toggled:
            for condition in reversed(self.conditions):
                index = condition.index
                if index != 0:
                    self.on_RemoveWidget_clicked(index)
                else:
                    condition.disableSpinBoxes(toggled)
            self.ui.pushButtonAddTimeSeries.setEnabled(False)
            index = self.ui.comboBoxStart.currentIndex()
            self.on_comboBoxStart_currentIndexChanged(index)
            index = self.ui.comboBoxEnd.currentIndex()
            self.on_comboBoxEnd_currentIndexChanged(index)
        else:
            self.conditions[0].disableSpinBoxes(False)
            self.ui.pushButtonAddTimeSeries.setEnabled(True)
                        
    def on_pushButtonSeriesFromTriggers_clicked(self, checked=None):
        """
        Opens a TimeSeriesDialog.
        Called when construct time series from triggers -button is clicked.
        """
        if checked is None or self.caller.raw is None: return
        dialog = TimeSeriesDialog()
        dialog.timeSeriesChanged.connect(self.on_TimeSeriesChanged)
        dialog.exec_()
        
    @QtCore.pyqtSlot(list)    
    def on_TimeSeriesChanged(self, conditions):
        """
        Slot for adding a set of PowerSpectrumWidgets to this dialog.
        Called from TimeSeriesDialog.
        Parameters:
        conditions - A list of PowerSpectrumWidgets.
        """
        if conditions == []: return
        for widget in self.conditions:
            self.on_RemoveWidget_clicked(widget.index)
        i = 0
        tmax = np.floor(self.caller.raw.index_as_time(self.caller.raw.n_times))
        for condition in conditions:
            widget = PowerSpectrumWidget(tmax, self)
            widget.setStartTime(condition.getStartTime())
            widget.setEndTime(condition.getEndTime())
            widget.setColor(condition.getColor())
            widget.setChannelColor(condition.getChannelColor())
            widget.on_ChannelsChanged(condition.getChannels())
            self.conditions.append(widget)
            widget.index = i
            widget.removeWidget.connect(self.on_RemoveWidget_clicked)
            widget.channelCopy.connect(self.copyChannels)
            self.ui.verticalLayoutConditions.addWidget(widget)
            i+=1
        self.ui.scrollAreaConditions.updateGeometry()
        
    def updateUi(self):
        self.parent.updateUi()
        
    def keyPressEvent(self, qKeyEvent):
        """
        Overrided method to prevent enter or return from starting the plotting.
        Parameters:
        qKeyEvent - Qt key event.
        """
        key = qKeyEvent.key()
        if key == QtCore.Qt.Key_Return or key == QtCore.Qt.Key_Enter:
            return
        return QtGui.QDialog.keyPressEvent(self, qKeyEvent)
    
    def installEventFilters(self):
        """
        Helper method for disabling wheel events on all widgets.
        """
        self.ui.spinBoxFmin.installEventFilter(self)
        self.ui.spinBoxFmax.installEventFilter(self)
        self.ui.comboBoxFormat.installEventFilter(self)
        self.ui.spinBoxNfft.installEventFilter(self)
        self.ui.spinBoxResolution.installEventFilter(self)
    
    def eventFilter(self, source, event):
        """
        Event filter for disabling wheel events on spin boxes and such.
        """
        if (event.type() == QtCore.QEvent.Wheel):
            return True
        return QtGui.QWidget.eventFilter(self, source, event)
        
