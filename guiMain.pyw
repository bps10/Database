# -*- coding: utf-8 -*-
# PyQt4 imports
import PyQt4.QtGui as qg
import DataViewer.mainWindow as mw
            
        
def main():
    """
    """
    app = qg.QApplication([])
    win = mw.MainWindow()

    #---Setup window
    win.setup_window()   
    win.show()
    return app.exec_()
        
        
if __name__ == '__main__':
    main()