'''
Created on Dec 16, 2014

@author: Jaakko Leppakangas
'''

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignal
from PyQt4.Qt import QApplication, QSettings, pyqtSlot

from time import sleep
import numpy as np
import matplotlib.pyplot as plt
import sys
from threading import Thread, Event

from general.caller import Caller
from ui_PreprocessDialog import Ui_MainWindow
from ui.ui_InfoDialog import Ui_infoDialog
from ui.InfoDialog import InfoDialog
from ui.projectionDialog import ProjectionDialog
from ui.channelSelectionDialog import ChannelSelectionDialog
from ui.saveDialog import SaveDialog
from ui.powerSpectrumWidget import PowerSpectrumWidget
from ui.groupSpectrumDialog import GroupSpectrumDialog
from ui.fileSelectionDialog import FileSelectionDialog
from ui.timeSeriesDialog import TimeSeriesDialog

class PreprocessDialog(QtGui.QMainWindow):
    """
    """
    e = Event()
    filterFinished = pyqtSignal()
    caller = Caller.Instance()
    conditions = []
    settings = QSettings("CIBR", "Eggie")
    
    def __init__(self):
        """
        Init method for the preprocessing dialog.
        Redirects stdout to dialog's console.
        """
        QtGui.QMainWindow.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.progressBar.setVisible(False)

        self.installEventFilters()
        self.ui.tableWidgetEvents.setSortingEnabled(False)
        #Signals
        self.ui.tableWidgetEvents.currentItemChanged.connect(self.\
                                            on_currentChanged)
        self.ui.checkBoxLowCutOff.stateChanged.connect(self.on_StateChanged)
        self.ui.checkBoxHighCutOff.stateChanged.connect(self.on_StateChanged)
        self.ui.checkBoxNotch.stateChanged.connect(self.on_StateChanged)
        self.ui.doubleSpinBoxLowCutOff.valueChanged.connect(self.\
                                            ui.pushButtonFilter.setEnabled)
        self.ui.doubleSpinBoxHighCutOff.valueChanged.connect(self.\
                                            ui.pushButtonFilter.setEnabled)
        self.ui.doubleSpinBoxNotchFilter.valueChanged.connect(self.\
                                            ui.pushButtonFilter.setEnabled)
        
        self.ui.actionDirectOutput.triggered.connect(self.directOutput)
        self.ui.actionOpen.triggered.connect(self.on_actionOpen)
        self.ui.actionExit.triggered.connect(self.on_actionExit)
        
        sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
        sys.stderr = EmittingStream(textWritten=self.errorOutputWritten)
        self.on_actionOpen()
        self.ui.lineEditLayout.setText(self.settings.value("Layout", "").\
                                       toString())
    
    def initialize(self):
        """
        Method for initializing the dialog.
        """
        if not self.caller.raw: return
        self.ui.labelRaw.setText(self.caller.raw.info.get('filename'))
        
        self.ui.comboBoxChannelSelect.addItems(self.caller.raw.info.\
                                               get('ch_names'))
        index = self.ui.comboBoxChannelSelect.findText('17')
        self.ui.comboBoxChannelSelect.setCurrentIndex(index)
        self.ui.pushButtonFilter.setEnabled(True)
        
        self.ui.tableWidgetEvents.setSelectionBehavior(1)        
        self.ui.tableWidgetEvents.setColumnCount(4)
        self.ui.tableWidgetEvents.setHorizontalHeaderLabels(["Time (s)",
                                                             "Sample",
                                                             "Prev. id",
                                                             "Current id"])
        
        tmax = np.floor(self.caller.raw.index_as_time(self.caller.raw.n_times))# / 1000.0))
        if len(self.conditions) == 0:
            spectrumWidget = PowerSpectrumWidget(tmax, self)
            spectrumWidget.index = 0
            spectrumWidget.removeWidget.connect(self.on_RemoveWidget_clicked)
            spectrumWidget.channelCopy.connect(self.copyChannels)
            self.ui.verticalLayoutConditions.addWidget(spectrumWidget)
            self.conditions.append(spectrumWidget)
        
    def directOutput(self):
        """
        Method for directing stdout to the console and back.
        """
        if self.ui.actionDirectOutput.isChecked():
            sys.stdout = EmittingStream(textWritten=self.normalOutputWritten)
            sys.stderr = EmittingStream(textWritten=self.errorOutputWritten)
        else:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
        
    def on_actionOpen(self):
        """
        Opens a dialog for selecting a file.
        """
        fileDialog = FileSelectionDialog(self)
        fileDialog.fileChanged.connect(self.on_FileChanged)
        fileDialog.show()
       
    def on_actionExit(self):
        """
        Closes the main window.
        """
        self.close()
        
    def on_pushButtonFilter_clicked(self, checked=None):
        """
        Called when filter button is clicked.
        """
        if checked is None or not self.caller.raw: return
        self.ui.pushButtonFilter.setEnabled(False)
        QtGui.QApplication.setOverrideCursor(QtGui.\
                                             QCursor(QtCore.Qt.WaitCursor))
        self.e.clear()
        self.thread = Thread(target = self.callFilter)
        self.thread.start()
        #while (self.thread.is_alive()):
        #    time.sleep(1)
        #self.e.wait()
        self.on_FilterFinished()
        QtGui.QApplication.restoreOverrideCursor() 
    
    def callFilter(self):
        """
        A function for calling filtering function in mne.
        Performed in a worker thread.
        """
        if self.ui.checkBoxHighCutOff.isChecked():
            highCutOff = self.ui.doubleSpinBoxHighCutOff.value()
        else:
            highCutOff = None
        if self.ui.checkBoxLowCutOff.isChecked():
            lowCutOff = self.ui.doubleSpinBoxLowCutOff.value()
        else:
            lowCutOff = None
        try:
            self.caller.raw.filter(l_freq=lowCutOff, h_freq=highCutOff,
                                   n_jobs=2)
        except Exception as e:
            print str(e)
            self.e.set()
            return
        print self.caller.raw.info['bads']
        if self.ui.checkBoxNotch.isChecked():
            print "Applying notch filter...\n"
            notchFreq = self.ui.doubleSpinBoxNotchFilter.value()
            try:
                self.caller.raw.notch_filter(freqs=notchFreq)
            except Exception as e:
                print str(e)
                self.e.set()
                return
        print self.caller.raw.info['bads']
        print "Launching mne_browse_raw...\n"
        self.e.set()
        
    def on_FilterFinished(self):
        """
        Function for adding bad channels via mne_browse_raw.
        """
        while not (self.e.is_set()):
            sleep(0.5)
            self.updateUi()
            if self.e.is_set(): break

        self.caller.raw.plot(scalings=dict(eeg=40e-6))
        plt.show()
        self.ui.listWidgetBads.clear()
        self.ui.listWidgetBads.addItems(self.caller.raw.info['bads'])
        self.e.clear()
        print "Finished\n"
        self.ui.pushButtonSave.setEnabled(True)
        
    def on_pushButtonAddBads_clicked(self, checked=None):
        """
        Called as the add-button is clicked.
        Opens a dialog for adding bad channels by hand.
        """
        if checked is None or not self.caller.raw: return
        
        badsDialog = ChannelSelectionDialog(self.caller.raw.info['bads'],
                                            "Select bad channels:")
        badsDialog.channelsChanged.connect(self.on_BadsChanged)
        badsDialog.exec_()
        
    def on_pushButtonFindEogEvents_clicked(self, checked=None):
        """
        Finds EOG-events from the raw data.
        Called when find eog events -button is clicked.
        """
        if checked is None or not self.caller.raw: return
        QtGui.QApplication.setOverrideCursor(QtGui.\
                                             QCursor(QtCore.Qt.WaitCursor))
        params = dict()
        event_id = int(self.ui.labelBlinkId.text())
        params['event_id'] = event_id
        params['ch_name'] = str(self.ui.comboBoxChannelSelect.currentText())
        params['l_freq'] = float(self.ui.doubleSpinBoxLowPass.value())
        params['h_freq'] = float(self.ui.doubleSpinBoxHighPass.value())
        params['filter_length'] = str(self.ui.spinBoxFilterLength.value())+'s'
        params['tstart'] = float(self.ui.doubleSpinBoxStart.value())
        
        try:
            #sfreq = self.caller.raw.info['sfreq']
            eog_events = self.caller.findEogEvents(params)
            #eog_events = self.caller.raw.index_as_time(eog_events)
            self.ui.tableWidgetEvents.clear()
            self.ui.tableWidgetEvents.setRowCount(0)
            for i in range(0, len(eog_events)):
                self.ui.tableWidgetEvents.insertRow(i)
                self.ui.tableWidgetEvents.setItem(i,0,QtGui.\
                            QTableWidgetItem(str(self.caller.raw.index_as_time(eog_events[i][0])[0])))
                self.ui.tableWidgetEvents.setItem(i,1,QtGui.\
                            QTableWidgetItem(str(int(eog_events[i][0]))))
                self.ui.tableWidgetEvents.setItem(i,2,QtGui.\
                            QTableWidgetItem(str(eog_events[i][1])))
                self.ui.tableWidgetEvents.setItem(i,3,QtGui.\
                            QTableWidgetItem(str(eog_events[i][2])))
        except Exception as e:
            print str(e)
        finally:
            self.ui.tableWidgetEvents.setHorizontalHeaderLabels(["Time (s)",
                                                                 "Sample",
                                                                 "Prev. id",
                                                                 "Current id"])
            QtGui.QApplication.restoreOverrideCursor()
    
    @QtCore.pyqtSlot(int)
    def on_StateChanged(self, checked):
        """
        Slot for activating filter button.
        """
        if checked == 2:
            self.ui.pushButtonFilter.setEnabled(True)
    
    @QtCore.pyqtSlot()
    def on_FileChanged(self):
        """
        Called when raw file has changed.
        """
        self.ui.listWidgetBads.clear()
        self.ui.listWidgetBads.addItems(self.caller.raw.info['bads'])
        self.ui.tableWidgetEvents.clear()
        self.ui.tableWidgetEvents.setRowCount(0)
        for condition in reversed(self.conditions):
            index = condition.index
            self.on_RemoveWidget_clicked(index)
        self.initialize()
            
    @QtCore.pyqtSlot()
    def on_currentChanged(self):
        """
        Called when tableWidgetEvent row selection is changed.
        """
        index = self.ui.tableWidgetEvents.currentIndex().row()
        if index < 0:
            self.ui.pushButtonDelete.setEnabled(False)
        else:
            self.ui.pushButtonDelete.setEnabled(True)
            
    @QtCore.pyqtSlot(list)
    def on_BadsChanged(self, bads):
        """
        Called when bad channels are changed by hand
        Parameters:
        bads - The list of bad channels.
        """
        self.ui.listWidgetBads.clear()
        self.caller.raw.info['bads'] = bads
        self.ui.listWidgetBads.addItems(self.caller.raw.info['bads'])
        
    @QtCore.pyqtSlot(int)
    def on_EventsChanged(self, index):
        """
        Slot removing an event from the table.
        Parameters:
        index - Index of the item on the table.
        """
        self.ui.tableWidgetEvents.removeRow(index)
            
    def on_pushButtonDelete_clicked(self, checked=None):
        """
        Called when delete button of eventlist is clicked.
        """
        if checked is None: return
        index = self.ui.tableWidgetEvents.currentRow()
        self.ui.tableWidgetEvents.removeRow(index)
        
    def on_pushButtonCalculateSSP_clicked(self, checked=None):
        """
        Called when calculate SSP projections -button is clicked.
        """
        if checked is None or not self.caller.raw: return
        events = []
        rowCount = self.ui.tableWidgetEvents.rowCount()
        for i in xrange(0, rowCount):
            time, _ = self.ui.tableWidgetEvents.item(i, 1).text().toFloat()
            prev, _ = self.ui.tableWidgetEvents.item(i, 2).text().toFloat()
            curr, _ = self.ui.tableWidgetEvents.item(i, 3).text().toFloat()
            events.append([time, prev, curr])
        if events == []: 
            print "Cannot remove blinks without events!"
            return
        projectionDialog = ProjectionDialog(np.array(events), curr, self)
        projectionDialog.badsChanged.connect(self.on_BadsChanged)
        projectionDialog.eventsChanged.connect(self.on_EventsChanged)
        projectionDialog.exec_()
        
    def on_pushButtonSave_clicked(self, checked=None):
        """
        Called when save button is clicked.
        """
        if checked is None or not self.caller.raw: return
        saveDialog = SaveDialog(self)
        saveDialog.exec_()
        self.ui.labelRaw.setText(self.caller.raw.info.get('filename'))
        
    def on_pushButtonSeriesFromTriggers_clicked(self, checked=None):
        """
        Opens a dialog for constructing a set of time series for PSDs
        from triggers.
        """
        if checked is None or self.caller.raw is None: return
        dialog = TimeSeriesDialog()
        dialog.timeSeriesChanged.connect(self.on_TimeSeriesChanged)
        dialog.exec_()
        
    @QtCore.pyqtSlot(list)    
    def on_TimeSeriesChanged(self, conditions):
        """
        Slot for adding a set of time series for PSDs.
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


    def on_pushButtonAddTimeSeries_clicked(self, checked=None):
        """
        Called when condition add button is clicked.
        """
        if checked is None or not self.caller.raw: return
        tmax = np.floor(self.caller.raw.index_as_time(self.caller.raw.n_times)) # ms to s
        index = len(self.conditions)
        channels = self.conditions[0].getChannels()
        widget = PowerSpectrumWidget(tmax, self)
        widget.index = index
        widget.on_ChannelsChanged(channels)
        self.conditions.append(widget)
        self.ui.verticalLayoutConditions.addWidget(widget)
        widget.removeWidget.connect(self.on_RemoveWidget_clicked)
        widget.channelCopy.connect(self.copyChannels)
        
    def on_pushButtonFileInfo_clicked(self, checked=None):
        """
        Opens the info dialog.
        """
        if checked is None or not self.caller.raw: return
        info = Ui_infoDialog()
        infoDialog = InfoDialog(self.caller.raw, info, True)
        infoDialog.exec_()
        
    @QtCore.pyqtSlot(int)
    def on_RemoveWidget_clicked(self, index):
        """
        Called when a condition widget sends a remove signal.
        Removes a condition from the list.
        Parameters:
        index - The index of the widget.
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
            
    def on_pushButtonPlot_clicked(self, checked=None):
        """
        Called when plot spectrum button is clicked.
        """
        if checked is None or not self.caller.raw: return
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
                messageBox.setText("End time must be higher than the " + \
                                   "start time.")
                QtGui.QApplication.restoreOverrideCursor()
                messageBox.exec_()
                return 
            times.append((start, end))
            
            colors.append(condition.getColor())
            channels = condition.getChannels()
            channelColors[i] = (condition.getChannelColor(), channels)
            i += 1
        if len(times) == 0:
            messageBox = QtGui.QMessageBox()
            messageBox.setText("Could not find data. Check parameters!")
            QtGui.QApplication.restoreOverrideCursor()
            messageBox.exec_()
            return 
        fmin = self.ui.spinBoxFmin.value()
        fmax = self.ui.spinBoxFmax.value()
        if fmin >= fmax:
            messageBox = QtGui.QMessageBox()
            messageBox.setText("End frequency must be higher than the " + \
                               "starting frequency.")
            QtGui.QApplication.restoreOverrideCursor()
            messageBox.exec_()
        params = dict()
        params['times'] = times
        params['fmin'] = fmin
        params['fmax'] = fmax
        params['nfft'] = self.ui.spinBoxNfft.value()
        params['log']  = self.ui.checkBoxLogarithm.isChecked()
        params['lout'] = str(self.ui.lineEditLayout.text())
        try:
            self.caller.plotSpectrum(self, params, colors, channelColors)
        except Exception as e:
            messageBox = QtGui.QMessageBox()
            messageBox.setText(str(e))
            QtGui.QApplication.restoreOverrideCursor()
            messageBox.exec_()
            return

        QtGui.QApplication.restoreOverrideCursor()
        
    def on_pushButtonBrowseLayout_clicked(self, checked=None):
        """
        Opens a dialog for selecting a layout file.
        """
        if checked is None: return
        fname = str(QtGui.QFileDialog.getOpenFileName(self, 'Open file',
                            '/home/', "Layout-files (*.lout *.lay);;All files (*.*)"))
        self.ui.lineEditLayout.setText(fname)
        self.settings.setValue("Layout", fname)
        
    def on_pushButtonGroupPlot_clicked(self, checked=None):
        """
        Opens a dialog for plotting power spectrums as a group.
        """
        if checked is None: return
        fmin = self.ui.spinBoxFmin.value()
        fmax = self.ui.spinBoxFmax.value()
        nfft = self.ui.spinBoxNfft.value()
        logarithm = self.ui.checkBoxLogarithm.isChecked()
        lout = self.ui.lineEditLayout.text()
        tmax = 10000
        if self.caller.raw:
            tmax = np.floor(self.caller.raw.index_as_time(self.caller.raw.n_times))
        groupSpectrumDialog = GroupSpectrumDialog(self, self.conditions, fmin,
                                                  fmax, nfft, logarithm, lout,
                                                  tmax)
        groupSpectrumDialog.fileChanged.connect(self.on_FileChanged)
        groupSpectrumDialog.exec_()
        
    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Delete:
            if self.ui.tabWidget.currentIndex() == 0:
                self.on_pushButtonDelete_clicked(1)
        
    def installEventFilters(self):
        """
        Helper method for disabling wheel events on all widgets.
        """
        #Preprocess tab:
        self.ui.doubleSpinBoxLowCutOff.installEventFilter(self)
        self.ui.doubleSpinBoxHighCutOff.installEventFilter(self)
        self.ui.doubleSpinBoxNotchFilter.installEventFilter(self)
        self.ui.comboBoxChannelSelect.installEventFilter(self)
        self.ui.doubleSpinBoxLowPass.installEventFilter(self)
        self.ui.doubleSpinBoxHighPass.installEventFilter(self)
        self.ui.spinBoxFilterLength.installEventFilter(self)
        self.ui.doubleSpinBoxStart.installEventFilter(self)
        #Power spectrum tab:
        self.ui.spinBoxFmin.installEventFilter(self)
        self.ui.spinBoxFmax.installEventFilter(self)
        self.ui.spinBoxNfft.installEventFilter(self)
        
    def eventFilter(self, source, event):
        """
        Event filter for disabling wheel events on spin boxes and such.
        """
        if (event.type() == QtCore.QEvent.Wheel):
            return True
        return QtGui.QWidget.eventFilter(self, source, event)
    
    @QtCore.pyqtSlot() 
    def updateUi(self):
        """
        Method for updating the UI.
        """
        QApplication.processEvents()
        
    def __del__(self):
        """
        Restores stdout at the end.
        """
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def normalOutputWritten(self, text):
        """
        Appends text to 'console' at the bottom of the dialog.
        Used for redirecting stdout.
        Parameters:
        text - Text to write to the console.
        """
        cursor = self.ui.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.textEdit.setTextCursor(cursor)
        self.ui.textEdit.ensureCursorVisible()
        
    def errorOutputWritten(self, text):
        """
        Appends text to 'console' at the bottom of the dialog.
        Used for redirecting stderr.
        Parameters:
        text - Text to write to the console.
        """
        cursor = self.ui.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.ui.textEdit.setTextCursor(cursor)
        self.ui.textEdit.ensureCursorVisible()


class EmittingStream(QtCore.QObject):

    textWritten = QtCore.pyqtSignal(str)

    def write(self, text):
        self.textWritten.emit(str(text))
        
    def flush(self):
        pass
        