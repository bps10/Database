# -*- coding: utf-8 -*-

# PyQt4 imports
import PyQt4.QtGui as qg
import PyQt4.QtCore as qc

class Popup(qg.QDialog):
    """
    .. todo:: 
        1. break down styles into methods
    """
    def __init__(self, openDB, textMessage = " ", style = 0):
        qg.QDialog.__init__(self)
        self.style = style
        
        self.selection = None
        Num = 1
        if self.style < 3:
            text = qg.QLabel(textMessage)
            enterbutton = qg.QPushButton("Enter")
            cancelbutton = qg.QPushButton("Cancel")
    
            vlayout = qg.QVBoxLayout()
            vlayout.addWidget(text)
            
            if self.style < 2:
                self.openDB = openDB
        
                self.name = qg.QComboBox()
                self.name.clear()
                self.name.addItems(openDB)
                label = qg.QLabel('database')
                
                h0layout = qg.QHBoxLayout()
                h0layout.addWidget(label)
                h0layout.addWidget(self.name)
                vlayout.addLayout(h0layout)                
                
                vlayout.addWidget(self.name)

            if self.style == 1:
                self.NeuronName = qg.QLineEdit()
                label = qg.QLabel('neuron name')
                
                h1layout = qg.QHBoxLayout()
                h1layout.addWidget(label)
                h1layout.addWidget(self.NeuronName)
                vlayout.addLayout(h1layout)
                
            if self.style == 2:
                
                self.name = qg.QLineEdit()
                label = qg.QLabel('database name')
                
                h1layout = qg.QHBoxLayout()
                h1layout.addWidget(label)
                h1layout.addWidget(self.name)
                vlayout.addLayout(h1layout)
                

            self.connect(enterbutton, qc.SIGNAL('clicked()'), self.returnSelection)
            self.connect(cancelbutton, qc.SIGNAL('clicked()'), self.closePopup)
                
            hlayout = qg.QHBoxLayout()
            hlayout.addWidget(enterbutton)
            hlayout.addWidget(cancelbutton)
            vlayout.addLayout(hlayout)            
    
            self.setLayout(vlayout)
            self.setGeometry(qc.QRect(100, 100, 200, 100 * Num))
            self.raise_()
            self.exec_()

        if self.style == 3:
            
            self.dirName = qg.QFileDialog.getOpenFileName(self, 'Open H5 file',
                                                         '.',
                                                         "H5 file ( *.h5 )")
            self.returnSelection()
            
            
        if self.style == 4:
            text = qg.QLabel(textMessage)
            enterbutton = qg.QPushButton("Enter")
            cancelbutton = qg.QPushButton("Cancel")
    
            vlayout = qg.QVBoxLayout()
            vlayout.addWidget(text)
            self.openDB = openDB
            self.NeuronName = qg.QLineEdit()
            label1 = qg.QLabel('neuron name :')  
            
            self.name = qg.QComboBox()
            self.name.clear()
            self.name.addItems(openDB)
            label2 = qg.QLabel('database :')
            

            enterbutton = qg.QPushButton("Enter")
            cancelbutton = qg.QPushButton("Cancel")
            
            self.dirName = qg.QFileDialog()
            #self.selectedDirName = str(QFileDialog.getOpenFileName(options=QFileDialog.DontUseNativeDialog))
            self.dirName.setFileMode(qg.QFileDialog.Directory)
            self.dirName.setOptions(qg.QFileDialog.ShowDirsOnly)
            

            fileLayout = self.dirName.layout()
            
            items = (fileLayout.itemAt(i) for i in range(fileLayout.count())) 
            i = 0
            for w in items:
                i +=1
                if i == 5 or i == 6 or i == 4:
                    fileLayout.removeItem(w)

            fileLayout.addWidget( qg.QLabel(' ') )
            fileLayout.addWidget( qg.QLabel(' ') )
            fileLayout.addWidget( qg.QLabel(' ') )

            fileLayout.addWidget( qg.QLabel(' ') )
            fileLayout.addWidget( qg.QLabel(' please enter data below:  ') )
            fileLayout.addWidget( qg.QLabel(' ') )

            fileLayout.addWidget(label1)
            fileLayout.addWidget(self.NeuronName)
            fileLayout.addWidget( enterbutton ) 

            fileLayout.addWidget(label2)
            fileLayout.addWidget(self.name)
            fileLayout.addWidget( cancelbutton )
                       
            self.connect(enterbutton, qc.SIGNAL('clicked()'), self.returnSelection)
            self.connect(cancelbutton, qc.SIGNAL('clicked()'), self.closePopup)
            
            
            self.dirName.raise_()
            self.dirName.exec_()           


            
    def returnSelection(self):
        """
        """
        if self.style == 0:
            self.selection = self.openDB[self.name.currentIndex()]

        if self.style == 1:
            self.selection = (self.openDB[self.name.currentIndex()], 
                                          str(self.NeuronName.displayText()))
        if self.style == 2:
            self.selection = str(self.name.displayText())
            
        if self.style == 3:
            self.selection = str(self.dirName)
            
        if self.style == 4:
            self.selection = []
            self.selection.append( str(list(self.dirName.selectedFiles())[0]) )
            self.selection.append( self.openDB[self.name.currentIndex()] )
            self.selection.append( str(self.NeuronName.displayText()) )
        
        if self.style == 4:            
            self.dirName.close()
        else:
            self.close()    

    def closePopup(self):
        """
        """
        self.selection = None
        
        if self.style == 4:
            self.dirName.close()

        else:
            self.close()
