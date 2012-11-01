# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 13:30:48 2012

@author: Brian
"""
# guidata imports
from guidata.dataset.qtwidgets import DataSetShowGroupBox
from guidata.qt.QtGui import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QMainWindow, QLineEdit, QTreeWidget, QTreeWidgetItem)
from guidata.qt.QtCore import (SIGNAL, QAbstractListModel, QModelIndex, QVariant, 
                               Qt)
from guidata.dataset.dataitems import StringItem, DirectoryItem
from guidata.dataset.datatypes import DataSet
from guidata.qthelpers import create_action, add_actions, get_std_icon

# user defined imports
import Database as Db
import PreProcessing as pp

# general
import numpy as np
import sys

#---Import plot widget base class
from guiqwt.curve import CurvePlot
from guiqwt.plot import PlotManager
from guiqwt.builder import make
from guidata.configtools import get_icon
#---


    
class FilterTestWidget(QWidget):
    """
    Filter testing widget
    parent: parent widget (QWidget)
    x, y: NumPy arrays
    func: function object (the signal filter to be tested)
    """
    def __init__(self, parent, func):
        QWidget.__init__(self, parent)
        self.data = Dbase()
        self.y = np.arange(0,100) #self.data.Query()
        self.x = np.arange(0,100) #np.arange(0, len(self.y))
        self.setMinimumSize(600, 650)
        self.func = func
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
        
        # create table
        self.databaseScroll = databaseListModel()
         
        listButton = QPushButton(u"Refresh list")
        button = QPushButton(u"New Query: %s" % title)
        #itemDoubleClicked
        self.connect(listButton, SIGNAL('clicked()'), self.but_clicked)
        self.connect(button, SIGNAL('clicked()'), self.query_database)
        self.connect(self.databaseScroll, SIGNAL("doubleClicked(QModelIndex)"), 
                     self.double_clicked)

        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        vlayout.addWidget(self.databaseScroll)
        vlayout.addWidget(listButton)
        hlayout.addWidget(self.Neuron)
        hlayout.addWidget(self.Epoch)
        hlayout.addWidget(self.QueryName)
        vlayout.addLayout(hlayout)
        
        vlayout.addWidget(button)
        vlayout.addWidget(self.plot)
        

        self.setLayout(vlayout)
        
        self.update_curve()
        
        
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
        #database = index.parent().parent().parent().row()
        neuron = index.parent().parent().row()
        epoch = index.parent().row()
        data = index.row()
        #print neuron, epoch, data
        if index.column() == 3:
            #self.query_database()
            try:
                #print 'here'
                n= self.databaseScroll.neuronName[neuron]
                e = self.databaseScroll.epochName[epoch]
                d = self.databaseScroll.dataName[data] # account for git dataName
                #print n, e, d
                self.y = self.data.Query(NeuronName = n, Epoch = e, DataName = d)
                self.x = np.arange(0, len(self.y))
                self.update_curve()
            except :
                pass
            
        

class databaseListModel(QTreeWidget):
    def __init__(self):
        QTreeWidget.__init__(self)
        #self.widget = QTreeWidget(self)
        header = QTreeWidgetItem(["Database","Neuron","Epoch","Data"])

        self.setHeaderItem(header)   
        #Another alternative is setHeaderLabels(["Tree","First",...])
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
        self.neurons = []
        self.singleEpoch = []
        self.singleData = []
        
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
        
    def refreshTree(self): 
        self.constructTree()
        self.update()
            
        '''
        print self.neuronName
        print self.epochName
        print self.dataName
        '''
        
class MyListModel(QAbstractListModel): 
    def __init__(self, datain, parent=None, *args): 
        """ datain: a list where each item is a row
        """
        QAbstractListModel.__init__(self, parent, *args) 
        self.listdata = datain
 
    def rowCount(self, parent=QModelIndex()): 
        return len(self.listdata) 
 
    def data(self, index, role): 
        if index.isValid() and role == Qt.DisplayRole:
            return QVariant(self.listdata[index.row()])
        else: 
            return QVariant()
            
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

    Directory = DirectoryItem("Directory")
    NeuronName = StringItem("NeuronName")
    
    
class Window(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Neuron Database")
        self.setWindowIcon(get_icon('guiqwt.png'))
        
        file_menu = self.menuBar().addMenu("File")
        quit_action = create_action(self, "Quit",
                                    shortcut="Ctrl+Q",
                                    icon=get_std_icon("DialogCloseButton"),
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

    def add_newData(self):
        if self.importData.dataset.edit():
            self.importData.get()
            print str(self.importData.dataset.NeuronName)
            print str(self.importData.dataset.Directory)
            addData = Dbase()
            addData.AddData(str(self.importData.dataset.NeuronName), 
                            str(self.importData.dataset.Directory))
                            
        
    def add_plot(self, func, title):
        widget = FilterTestWidget(self, func)
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
        

def main():
    """Testing this simple Qt/guiqwt example"""
    from guidata.qt.QtGui import QApplication
    
    app = QApplication([])
    win = Window()
    

    win.add_plot(None, "1")
    win.add_plot(None, "2")
    #---Setup window
    win.setup_window()
    #---
    
    win.show()
    sys.exit(app.exec_())
        
        
if __name__ == '__main__':
    main()
    