'''
Created on 19.12.2014

@author: Jaakko Leppakangas
'''
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignal

import numpy as np
import matplotlib.pyplot as plt
from threading import Event
from multiprocessing.pool import ThreadPool
from time import sleep

from ui_ProjectionDialog import Ui_ProjectionDialog
from general.caller import Caller
from reportlab.lib.utils import prev_this_next

class ProjectionDialog(QtGui.QDialog):
    """
    """
    badsChanged = pyqtSignal(list)
    eventsChanged = pyqtSignal(int)
    e = Event()
    caller = Caller.Instance()
    
    def __init__(self, events, event_id, parent):
        """
        """
        QtGui.QDialog.__init__(self)

        self.ui = Ui_ProjectionDialog()
        self.ui.setupUi(self)
        self.installEventFilters()
        self.parent = parent
        
        self.event_id = int(event_id)
        self.ui.tableWidgetEvents.setSortingEnabled(False)
        self.ui.labelUsingEvents.setText("Using {!s} events for projections."\
                                         .format(len(events)))
        
        self.ui.tableWidgetEvents.clear()
        self.ui.tableWidgetEvents.setSelectionBehavior(1)        
        self.ui.tableWidgetEvents.setRowCount(0)
        self.ui.tableWidgetEvents.setColumnCount(4)
        #self.ui.tableWidgetEvents.setHorizontalHeaderLabels(["Time (s)", "Prev. id", "Current id"])
        self.updateProjectionList()
              
        for i in range(0, len(events)):
            self.ui.tableWidgetEvents.insertRow(i)
            self.ui.tableWidgetEvents.setItem(i,0,
                                    QtGui.QTableWidgetItem(str(self.caller.raw.index_as_time(events[i][0])[0])))
            self.ui.tableWidgetEvents.setItem(i,1,
                                    QtGui.QTableWidgetItem(str(events[i][0])))
            self.ui.tableWidgetEvents.setItem(i,2,
                                    QtGui.QTableWidgetItem(str(events[i][1])))
            self.ui.tableWidgetEvents.setItem(i,3,
                                    QtGui.QTableWidgetItem(str(events[i][2])))
        self.ui.tableWidgetEvents.setHorizontalHeaderLabels(["Time (s)",
                                                             "Sample",
                                                             "Prev. state",
                                                             "Event id"])
        
        self.ui.pushButtonDelEvent.setEnabled(False)
        self.ui.tableWidgetEvents.currentItemChanged.\
            connect(self.on_currentChanged)
        self.ui.listWidgetProjs.currentItemChanged.\
            connect(self.on_ProjChanged)
        
    def updateProjectionList(self):
        """
        Updates the projection list widget.
        """
        self.ui.listWidgetProjs.clear()
        for proj in self.caller.raw.info['projs']:
            self.ui.listWidgetProjs.addItem(str(proj))
        
    def getEvents(self):
        """
        A convenience function for fetching all the events from
        the tableWidgetEvents as a numpy array.
        returns:
        eog_events as numpy array
        """
        events = []
        rowCount = self.ui.tableWidgetEvents.rowCount()
        for i in xrange(0, rowCount):
            time, _ = self.ui.tableWidgetEvents.item(i, 1).text().toFloat()
            prev, _ = self.ui.tableWidgetEvents.item(i, 2).text().toFloat()
            curr, _ = self.ui.tableWidgetEvents.item(i, 3).text().toFloat()
            events.append([time, int(prev), int(curr)])
        #events = self.caller.raw.time_as_index(events)
        return np.array(events)
            
        
    def on_pushButtonPlotEpochs_clicked(self, checked=None):
        """
        Plots the averaged epochs.
        """
        if checked is None: return
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        events = self.getEvents()
        print events
        tmin = self.ui.doubleSpinBoxStart.value()
        tmax = self.ui.doubleSpinBoxEnd.value()

        self.caller.plotAverageEpochs(events, tmin, tmax, self.event_id)
        QtGui.QApplication.restoreOverrideCursor()
        
    def on_pushButtonShowEvents_clicked(self, checked=None):
        """
        Plots the events on mne_browse_raw.
        """
        if checked is None: return
        events = self.getEvents()
        self.caller.plotEvents(events)
        
    def on_pushButtonClose_clicked(self, checked=None):
        """
        Slot for closing the dialog.
        """
        if checked is None: return
        self.close()
        
    def on_pushButtonAddProj_clicked(self, checked=None):
        """
        Called when add SSP button is clicked.
        """
        if checked is None: return
        QtGui.QApplication.setOverrideCursor(QtGui.\
                                             QCursor(QtCore.Qt.WaitCursor))
        self.ui.pushButtonAddProj.setEnabled(False)
        self.events = self.getEvents()
        self.e.clear()
        pool = ThreadPool(processes=1)

        async_result = pool.apply_async(self.callSSP)
        
        #self.thread = Thread(target = self.callSSP, args=(events,))
        #self.thread.start()
        #while (self.thread.is_alive()):
        #    time.sleep(1)
        #self.e.wait()
        return_val = async_result.get()
        while not (self.e.is_set()):
            sleep(0.5)
            self.parent.updateUi()
            if self.e.is_set(): break
        
        print return_val

        self.caller.raw.plot(events=self.events, scalings=dict(eeg=40e-6),
                         show_options=True)
        plt.show()
        self.updateProjectionList()
        QtGui.QApplication.restoreOverrideCursor()
        print "Finished\n"
        reply = QtGui.QMessageBox.question(self,
                                        'Projection items deactivated.',
                                        'Do you want to keep the added' + 
                                        ' projection vectors?',
                                        QtGui.QMessageBox.Yes,
                                        QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.parent.ui.pushButtonSave.setEnabled(True)
        if reply == QtGui.QMessageBox.No:
            print "Action cancelled. Deleting projections from raw object...\n"
            # Find the indices of added projections.
            indices = []
            for i in xrange(len(self.caller.raw.info['projs'])):
                for returned in return_val:
                    if str(returned) == str(self.caller.raw.info['projs'][i]):
                        indices.append(i)
            # Remove projections starting from last index.
            for i in reversed(indices):
                self.caller.raw.del_proj(i)
            self.updateProjectionList()
            print "Finished"
        bads = self.caller.raw.info['bads']
        self.badsChanged.emit(bads)
        self.ui.pushButtonAddProj.setEnabled(True)
    
    def callSSP(self):
        """
        Calls the function that adds projection vectors to the data.
        Performed in a worker thread.
        """
        tmin = self.ui.doubleSpinBoxStart.value()
        tmax = self.ui.doubleSpinBoxEnd.value()
        n_eeg = self.ui.spinBoxVectors.value()
        
        proj = self.caller.computeSspProj(self.events, tmin, tmax,
                                             self.event_id, n_eeg)
        print "Launching mne_browse_raw...\n"
        self.e.set()
        return proj
        
    @QtCore.pyqtSlot()
    def on_currentChanged(self):
        """
        Called when tableWidgetEvent row selection is changed.
        """
        #if checked is None: return
        index = self.ui.tableWidgetEvents.currentIndex()
        if index is None:
            self.ui.pushButtonDelEvent.setEnabled(False)
        else:
            self.ui.pushButtonDelEvent.setEnabled(True)
            
    @QtCore.pyqtSlot()
    def on_ProjChanged(self):
        """
        Called when listWidgetProjs row selection is changed.
        """
        index = self.ui.listWidgetProjs.currentIndex()
        if index is None:
            self.ui.pushButtonDelProj.setEnabled(False)
        else:
            self.ui.pushButtonDelProj.setEnabled(True)
            
    def on_pushButtonDelEvent_clicked(self, checked=None):
        """
        Function for deleting an event from the list.
        """
        if checked is None: return
        index = self.ui.tableWidgetEvents.currentRow()
        if index < 0: return
        self.ui.tableWidgetEvents.removeRow(index)
        rows = self.ui.tableWidgetEvents.rowCount()
        self.ui.labelUsingEvents.setText("Using {!s} events for projections."\
                                         .format(rows))
        self.eventsChanged.emit(index)
        if self.ui.tableWidgetEvents.currentRow() < 0:
            self.ui.pushButtonDelEvent.setEnabled(False)
        
    def on_pushButtonDelProj_clicked(self, checked=None):
        """
        Function for deleting an added projection.
        """
        if checked is None: return
        index = self.ui.listWidgetProjs.currentRow()
        reply = 0
        if index == 0:
            reply = QtGui.QMessageBox.question(self,
                            'Delete projection.',
                            'Are you sure?' + 
                            ' EEG average reference cannot be added later.',
                            QtGui.QMessageBox.Yes,
                            QtGui.QMessageBox.No)
        else:
            reply = QtGui.QMessageBox.question(self,
                                        'Delete projection.',
                                        'Are you sure?',
                                        QtGui.QMessageBox.Yes,
                                        QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.No:
            return
        if reply == QtGui.QMessageBox.Yes:
            try:
                self.caller.raw.del_proj(index)
            except Exception as e:
                print "Projection not deleted."
                print str(e)
                return
            self.ui.listWidgetProjs.takeItem(index)
            print "Projection vector deleted."
            self.parent.ui.pushButtonSave.setEnabled(True)
            if self.ui.listWidgetProjs.currentRow() < 0:
                self.ui.pushButtonDelProj.setEnabled(False)
                
    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Delete:
            self.on_pushButtonDelEvent_clicked(1)
                
    def installEventFilters(self):
        """
        Helper method for disabling wheel events on all widgets.
        """
        self.ui.doubleSpinBoxStart.installEventFilter(self)
        self.ui.doubleSpinBoxEnd.installEventFilter(self)
        self.ui.spinBoxVectors.installEventFilter(self)
    
    def eventFilter(self, source, event):
        """
        Event filter for disabling wheel events on spin boxes and such.
        """
        if (event.type() == QtCore.QEvent.Wheel):
            return True
        return QtGui.QWidget.eventFilter(self, source, event)
      