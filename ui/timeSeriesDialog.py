'''
Created on 22.1.2015

@author: Jaakko Leppakangas
'''

from PyQt4 import QtGui, QtCore

import mne
import numpy as np

from ui_TimeSeriesDialog import Ui_TimeSeriesDialog
from powerSpectrumWidget import PowerSpectrumWidget
from general.caller import Caller

class TimeSeriesDialog(QtGui.QDialog):
    """
    """
    caller = Caller.Instance()
    widgets = []
    timeSeriesChanged = QtCore.pyqtSignal(list)
  
    def __init__(self):
        """
        Init method for time series dialog.
        """
        QtGui.QDialog.__init__(self)

        self.ui = Ui_TimeSeriesDialog()
        self.ui.setupUi(self)
        
        self.widgets = []  
        self.ui.comboBoxChannels.addItems(self.caller.raw.info['ch_names'])
        index = self.ui.comboBoxChannels.findText('STI 014')
        self.ui.comboBoxChannels.setCurrentIndex(index)
        
    def on_pushButtonFind_clicked(self, checked=None):
        """
        Finds events based on triggers on the selected channel.
        """
        if checked is None: return
        QtGui.QApplication.setOverrideCursor(QtGui.\
                                             QCursor(QtCore.Qt.WaitCursor))
        for widget in reversed(self.widgets):
            index = widget.index
            self.on_RemoveWidget_clicked(index)
        tstart = self.ui.spinBoxTstart.value()
        tend = self.ui.spinBoxTend.value()
        channel = str(self.ui.comboBoxChannels.currentText())
        try:
            events = mne.find_events(self.caller.raw, stim_channel=channel,
                                     verbose=True)
        except:
            QtGui.QApplication.restoreOverrideCursor()
            return
        tmax = np.floor(self.caller.raw.index_as_time(self.caller.raw.n_times)) # ms to s
        for i in xrange(len(events) - 1):
            widget = PowerSpectrumWidget(tmax, self)
            widget.index = i
            widget.ui.pushButtonRemove.setVisible(True)
            self.widgets.append(widget)
            widget.removeWidget.connect(self.on_RemoveWidget_clicked)
            widget.channelCopy.connect(self.copyChannels)
            self.ui.verticalLayoutConditions.addWidget(widget)
            widget.setStartTime(self.caller.raw.index_as_time(events[i][0]) + tstart)
            widget.setEndTime(self.caller.raw.index_as_time(events[i+1][0]) - tend)
        QtGui.QApplication.restoreOverrideCursor()
        
    @QtCore.pyqtSlot(int)
    def on_RemoveWidget_clicked(self, index):
        """
        Called when a power spectrum widget sends a remove signal.
        Removes a condition from the list.
        Parameters:
        index - Index given for the PowerSpectrumWidget.
        """
        widget = self.widgets.pop(index)
        self.ui.verticalLayoutConditions.removeWidget(widget)
        widget.deleteLater()
        widget = None
        # Restore order of indices:
        for i in xrange(len(self.widgets)):
            self.widgets[i].index = i
            self.widgets[i].ui.pushButtonRemove.setVisible(True)
            
    @QtCore.pyqtSlot(int)
    def copyChannels(self, index):
        """
        """
        channels = self.widgets[index].getChannels()
        for widget in self.conditions:
            widget.on_ChannelsChanged(channels)
            
    def accept(self, *args, **kwargs):
        self.timeSeriesChanged.emit(self.widgets)
        return QtGui.QDialog.accept(self, *args, **kwargs)
            