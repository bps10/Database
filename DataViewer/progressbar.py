from PyQt4.QtCore import pyqtSignal, QThread, Qt
from PyQt4.QtGui import QProgressBar
import time

class BusyBar(QThread):        
    """
    Adapted from: http://stackoverflow.com/questions/8007602/
    looping-qprogressbar-gives-error-qobjectinstalleventfilter-cannot-filter-e  
           
    Looping progress bar
    create the signal that the thread will emit
    
    .. note::
       This function creates a busy bar but I have not figured out how to \
       attach it to a process. Therefore, it is currently functionally \
       useless.
    """
    changeValue = pyqtSignal(int)
    def __init__(self, text = "" ):
        QThread.__init__(self, parent = None)
        self.text = text
        self.stop = False
        self.proBar = QProgressBar()
        self.proBar.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.SplashScreen )
        self.proBar.setRange( 0, 100 )
        self.proBar.setTextVisible( True )
        self.proBar.setFormat( self.text )
        self.proBar.setValue( 0 )
        self.proBar.setFixedSize( 300 , 40 )
        self.proBar.setAlignment(Qt.AlignCenter)
        self.proBar.show()

        #self.changeValue.connect(self.proBar.setValue, Qt.QueuedConnection)
        # Make the Busybar delete itself and the QProgressBar when done        
        self.finished.connect(self.onFinished)

    def run(self):
        """
        """
        while not self.stop:                
            # keep looping while self is visible
            # Loop sending mail 
            for i in range(100):
                # emit the signal instead of calling setValue
                # also we can't read the progress bar value from the thread
                self.changeValue.emit( i )
                time.sleep(0.01)
            self.changeValue.emit( 0 )

    def onFinished(self):
        """
        """
        self.proBar.deleteLater()
        self.deleteLater()

    def Kill(self):
        """
        """
        self.stop = True
