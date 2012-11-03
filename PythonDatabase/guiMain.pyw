# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 13:30:48 2012

@author: Brian
"""
# guidata imports
from guidata.dataset.qtwidgets import DataSetShowGroupBox
from guidata.qt.QtGui import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QMainWindow, QLineEdit, QTreeWidget, QTreeWidgetItem, 
                              QCheckBox, QSpacerItem, QLabel, QFont, QDockWidget )
from guidata.qt.QtCore import (SIGNAL, Qt)
from guidata.dataset.dataitems import StringItem, DirectoryItem
from guidata.dataset.datatypes import DataSet
from guidata.qthelpers import create_action, add_actions #, get_std_icon

# user defined imports
import Database as Db
import Preprocessing as pp

# general
import numpy as np


#---Import plot widget base class
from guiqwt.curve import CurvePlot
from guiqwt.plot import PlotManager
from guiqwt.builder import make
#from guidata.configtools import get_icon
#---
from spyderlib.widgets.internalshell import InternalShell

    
class FilterTestWidget(QWidget):
    """
    Filter testing widget
    parent: parent widget (QWidget)
    x, y: NumPy arrays
    func: function object (the signal filter to be tested)
    """
    def __init__(self, parent):
        QWidget.__init__(self, parent)
        
        self.data = Dbase()
        self.y = np.arange(0,100) #self.data.Query()
        self.x = np.arange(0,100) #np.arange(0, len(self.y))
        self.setMinimumSize(600, 650)
        #---guiqwt related attributes:
        self.plot = None
        self.curve_item = None
        #---
        
    def setup_widget(self, title):
        #---Create the plot widget:
        self.plot = CurvePlot(self)
        self.curve_item = make.curve([], [], color='b')
        self.plot.add_item(self.curve_item)
        self.plot.set_antialiasing(True)
        #---
        
        self.Neuron     = QLineEdit("Neuron name")
        self.Epoch      = QLineEdit("Epoch name")
        self.QueryName  = QLineEdit("Data selection")
        

        # create tree
        self.databaseScroll = databaseListModel()
        

        text = QLabel("Preprocess data")
        spacer = QSpacerItem(30,40)
        
        # create buttons
        listButton = QPushButton(u"Refresh list")
        queryButton = QPushButton(u"New Query: %s" % title)
        processButton = QPushButton(u"run preprocessing")
        
        self.wavelet = QCheckBox(u"Wavelet")
        self.noneyet = QCheckBox(u"None Yet")
        
        # connect user actions with methods:
        self.connect(listButton, SIGNAL('clicked()'), self.but_clicked)
        self.connect(queryButton, SIGNAL('clicked()'), self.query_database)
        self.connect(processButton, SIGNAL('clicked()'), self.run_preprocess)
        self.connect(self.databaseScroll, SIGNAL("doubleClicked(QModelIndex)"), 
                     self.double_clicked)

        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        h2layout = QHBoxLayout()
        v2layout = QVBoxLayout()
        
        vlayout.addWidget(self.databaseScroll)
        vlayout.addWidget(listButton)
        hlayout.addWidget(self.Neuron)
        hlayout.addWidget(self.Epoch)
        hlayout.addWidget(self.QueryName)
        vlayout.addLayout(hlayout)
        
        vlayout.addWidget(queryButton)
        vlayout.addWidget(self.plot)
        vlayout.addSpacerItem(spacer)
        vlayout.addWidget(text)
        
        v2layout.addWidget(self.wavelet)
        v2layout.addWidget(self.noneyet)
        h2layout.addLayout(v2layout)
        h2layout.addWidget(processButton)        
        
        vlayout.addLayout(h2layout)
        self.setLayout(vlayout)
        
        self.update_curve()
        
     
    def run_preprocess(self):
        
        if self.wavelet.isChecked():
            try:
                yData = self.y
                waveletSpikes = pp.wavefilter(yData)
                self.y = waveletSpikes
                self.update_curve()
            except:
                print 'Could not compute wave filter'
                pass

        
        
    def query_database(self):
        neuronname = str(self.Neuron.displayText())
        epochname = str(self.Epoch.displayText())
        dataname = str(self.QueryName.displayText())
        try:
            self.y = self.data.Query(NeuronName = neuronname, Epoch = epochname, DataName = dataname)
            self.x = np.arange(0, len(self.y))
            self.update_curve()
        except :
            pass
        
    def update_curve(self):
        #---Update curve

        self.curve_item.set_data(self.x, self.y)
        self.plot.replot()
        self.plot.do_autoscale()
        
    def but_clicked(self):
        '''
        when a name button is clicked, I iterate over the model, 
        find the neuron with this name, and set the treeviews current item
        '''
        self.databaseScroll.refreshTree()
    
    def double_clicked(self):
        '''
        when a name button is clicked, iterate over the model, 
        find the neuron with this name, and set the treeviews current item
        '''
        
        index = self.databaseScroll.currentIndex() 

        if index.column() == 3:
            neuron = index.parent().parent().row()
            epoch = index.parent().row()
            data = index.row()

            try:

                n= self.databaseScroll.neuronName[neuron]
                e = self.databaseScroll.epochName[epoch]
                d = self.databaseScroll.dataName[data] # account for git dataName

                self.y = self.data.Query(NeuronName = n, Epoch = e, DataName = d)
                
                if self.y.shape[0] > 1:
                    self.x = np.arange(0, len(self.y))
                    self.update_curve()
                
                if self.y.shape[0] == 1:
                    print d, ': ', self.y[0]
                    
            except :
                
                #if data < 0:
                #    print 'could not update plot'
                    
                pass
        
        if index.column() == 4:
            neuron = index.parent().parent().parent().row()
            epoch = index.parent().parent().row()
            data = index.parent().row()
            param = index.row()
            
            n= self.databaseScroll.neuronName[neuron]
            e = self.databaseScroll.epochName[epoch]
            d = self.databaseScroll.dataName[data] # account for git dataName
            p = self.databaseScroll.paramName[param]
            query =  self.data.Query(NeuronName = n, Epoch = e, 
                                     DataName = d + '.' + p)[0]
            print ' '
            print p, ': ', query

        

class databaseListModel(QTreeWidget):
    def __init__(self):
        QTreeWidget.__init__(self)
        #self.widget = QTreeWidget(self)
        header = QTreeWidgetItem(["Database","Neuron","Epoch","Data", 
                                  "Parameters"])
        self.setHeaderItem(header)   

        self.Db = Dbase()
        try :
            self.constructTree()
        except :
            pass
        
    def constructTree(self):        
        root = QTreeWidgetItem(self)
        root.setText(0, "Neuron Data")
        
        self.neuronName = []
        self.epochName = []
        self.dataName = []

        self.paramName = []
        
        '''        
        self.neurons = []
        singleEpoch = []
        singleData = []
        singleParam = []
        '''
        
        top = self.Db.GetTree()      
        for countNeuro,neuron in enumerate(top):
            
            neurons = QTreeWidgetItem(root) 
            neurons.setText(1, neuron)
            
            self.neuronName.append(neuron)

            neuronTree = self.Db.GetTree(neuron)
            for countEpoch, epoch in enumerate(neuronTree):
                
                singleEpoch = QTreeWidgetItem(neurons) 
                singleEpoch.setText(2, epoch)
                
                self.epochName.append(epoch)
                
                epochTree = self.Db.GetTree( neuron + '.' + epoch)
                for countData,data in enumerate(epochTree):
                    singleData = QTreeWidgetItem(singleEpoch) 
                    singleData.setText(3, data)
                    
                    if countEpoch == 1:
                        self.dataName.append(data)
                        
                    if data == 'params':
                        paramTree = self.Db.GetTree( neuron + '.' + epoch + '.' + data)
                        for countParam,param in enumerate(paramTree):
                            singleParam = QTreeWidgetItem(singleData)
                            singleParam.setText(4, param)
                            
                            if countEpoch == 1:
                                self.paramName.append(param)
        
    def refreshTree(self): 
        self.constructTree()
        self.update()
            

            
class Dbase():
    def __init__(self):
        
        self.Data = Db.Database()
        self.Data.OpenDatabase('NeuronData')
        
    def Query(self, NeuronName = 'Oct0212Bc8', Epoch = 'epoch040', DataName = 'rawData'):
        return self.Data.QueryDatabase( NeuronName, Epoch, DataName)
        
    def AddData(self, NeuronName, Directory):
        
        self.Data.ImportAllData(NeuronName, Directory)        
        
    def GetTree(self, NeuronName = None):
        
        if NeuronName == None:
            tree = self.Data.GetChildList()
        else:
            tree = self.Data.GetChildList(NeuronName)
        
        return tree
        

class FindFile(DataSet):

    Directory   = DirectoryItem("Directory")
    NeuronName  = StringItem("NeuronName")
    
    
class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Neuron Database")
        #self.setWindowIcon(get_icon('guiqwt.png'))
        self.setAttribute(Qt.WA_DeleteOnClose,True)
        
        file_menu = self.menuBar().addMenu("File")
        quit_action = create_action(self, "Quit",
                                    shortcut="Ctrl+Q",
                                    #icon=get_std_icon("DialogCloseButton"),
                                    tip="Quit application",
                                    triggered=self.close)
        add_actions(file_menu, (quit_action, ))
        
        # Edit menu
        self.importData = DataSetShowGroupBox("Neuron Data",
                                             FindFile, comment='')
        #self.x = np.arange(0, len(self.y))
        edit_menu = self.menuBar().addMenu("Edit")
        editparam1_action = create_action(self, "Add dataset",
                                          triggered=self.add_newData)
        add_actions(edit_menu, (editparam1_action, ))
        
        hlayout = QHBoxLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(hlayout)
        self.setCentralWidget(central_widget)
        #---guiqwt plot manager
        self.manager = PlotManager(self)
        #---
        
        
        # Create the console widget
        font = QFont("Courier new")
        font.setPointSize(12)
        ns = {'win': self, 'widget': central_widget}
        msg = "Try for example: widget.set_text('foobar') or win.close()"
        # Note: by default, the internal shell is multithreaded which is safer 
        # but not compatible with graphical user interface creation.
        # For example, if you need to plot data with Matplotlib, you will need 
        # to pass the option: multithreaded=False
        self.console = cons = InternalShell(self, namespace=ns, message=msg)
        
        # Setup the console widget
        cons.set_font(font)
        cons.set_codecompletion_auto(True)
        cons.set_calltips(True)
        cons.setup_calltips(size=600, font=font)
        cons.setup_completion(size=(300, 100), font=font)
        console_dock = QDockWidget("Console", self)
        console_dock.setWidget(cons)
        
        # Add the console widget to window as a dockwidget
        self.addDockWidget(Qt.BottomDockWidgetArea, console_dock)
        
    def add_newData(self):
        if self.importData.dataset.edit():
            self.importData.get()
            print str(self.importData.dataset.NeuronName)
            print str(self.importData.dataset.Directory)
            addData = Dbase()
            addData.AddData(str(self.importData.dataset.NeuronName), 
                            str(self.importData.dataset.Directory))
                            
        
    def add_plot(self, title):
        widget = FilterTestWidget(self)
        widget.setup_widget(title)
        self.centralWidget().layout().addWidget(widget)
        
        #---Register plot to manager
        
        self.manager.add_plot(widget.plot)
        #self.manager.add_panel(widget.databaseScroll)
        #self.manager.add_tool()        
        #---
                       
        
    def setup_window(self):
        #---Add toolbar and register manager tools
        toolbar = self.addToolBar("tools")
        self.manager.add_toolbar(toolbar, id(toolbar))
        self.manager.register_all_curve_tools()
        #---
        
    def closeEvent(self, event):
        self.console.exit_interpreter()
        event.accept()       

def main():
    """Testing this simple Qt/guiqwt example"""
    
    from guidata.qt.QtGui import QApplication
    
    app = QApplication([])
    win = Window()
    

    win.add_plot( "1")
    win.add_plot( "2")
    #---Setup window
    win.setup_window()
    #---
    
    win.show()
    return app.exec_()
        
        
if __name__ == '__main__':
    main()
    