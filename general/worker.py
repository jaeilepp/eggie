'''
Created on 7.1.2015

@author: Jaakko Leppakangas
'''
from PyQt4.QtCore import QThread

from caller import Caller

class Worker(QThread):

    def __init__(self, notchFreq, highCutOff, parent = None):
        
        QThread.__init__(self, parent)
        self.notchFreq = notchFreq
        self.highCutOff = highCutOff
        
    def callFilter(self):
        
        finished = QtCore.pyqtSignal()
        caller = Caller.Instance()

        caller.raw.filter(l_freq=None, h_freq=self.highCutOff, n_jobs=2)
        caller.raw.notch_filter(freqs=self.notchFreq)
        finished.emit()
        
        
        
from PyQt4 import Qt, QtCore, QtGui
import threading
import socket
import Queue
import time
from caller import Caller

# Object of this class has to be shared between
# the two threads (Python and Qt one).
# Qt thread calls 'connect',   
# Python thread calls 'emit'.
# The slot corresponding to the emitted signal
# will be called in Qt's thread.
class SafeConnector:
    def __init__(self, receiver):
        self._rsock, self._wsock = socket.socketpair()
        self._queue = Queue.Queue()
        self._qt_object = QtCore.QObject()
        self._notifier = QtCore.QSocketNotifier(self._rsock.fileno(),
                                                QtCore.QSocketNotifier.Read)
        self._notifier.activated.connect(self._recv)
        self.receiver = receiver

    def connect(self, signal, receiver):
        QtCore.QObject.connect(self._qt_object, signal, receiver)

    # should be called by Python thread
    def emit(self, signal, args):
        self._queue.put((signal, args))
        self._wsock.send('!')

    # happens in Qt's main thread
    def _recv(self):
        self._rsock.recv(1)
        signal, args = self._queue.get()
        self._qt_object.emit(signal, args)

class PythonThread(threading.Thread):
    def __init__(self, connector, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.connector = connector
        self.daemon = True

    def emit_filterFinished(self):
        self.connector.emit(QtCore.SIGNAL("test"))

    def run(self):
        caller = Caller.Instance()
        notchFreq = [50]
        highCutOff = 80
        caller.raw.filter(l_freq=None, h_freq=highCutOff, n_jobs=2)
        caller.raw.notch_filter(freqs=notchFreq)
        self.emit_filterFinished()
