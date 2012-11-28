# -*- coding: utf-8 -*-
"""
Created on Fri Oct 26 13:30:48 2012

@author: Brian
"""
# guidata imports
from guidata.qt.QtGui import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                              QMainWindow, QLineEdit, QTreeWidget, QTreeWidgetItem, 
                              QCheckBox, QSpacerItem, QLabel, QFont, QDockWidget,
                              QMessageBox, QGroupBox, QDialog, QComboBox,
                              QFileDialog)
from guidata.qt.QtCore import (SIGNAL, Qt, QRect)
from guidata.qthelpers import create_action, add_actions, get_std_icon

# user defined imports
import Database as Db
import Preprocessing as pp
from ProgressBar import BusyBar

# general
import numpy as np
import os

#---Import plot widget base class
from guiqwt.curve import CurvePlot
from guiqwt.plot import PlotManager
from guiqwt.builder import make
from guidata.configtools import get_icon
#---
from spyderlib.widgets.internalshell import InternalShell

    
class FilterTestWidget(QWidget):
    """
    Filter testing widget
    parent: parent widget (QWidget)
    x, y: NumPy arrays
    func: function object (the signal filter to be tested)
    
    .. todo::
       Write documentation!
    """
    def __init__(self, parent):
        """
        """
        QWidget.__init__(self, parent)
        
        self.data = Dbase(DBaseName = None)
        self.y1Data = np.arange(0,100) #self.data.Query()
        self.y2Data = np.arange(0,100)
        self.xData = np.arange(0,100) #np.arange(0, len(self.yData))
        self.setMinimumSize(700, 600)
        #---guiqwt related attributes:
        self.plot = None
        self.curve_item = None
        #---
        
    def setup_widget(self, title):
        """
        """
        #---Create the plot widget:
        self.plot = CurvePlot(self)
        self.curve_item = (make.curve([], [], color='b'))
        self.second_curve_item = (make.curve([], [], color='g'))

        self.plot.add_item(self.curve_item)
        self.plot.add_item(self.second_curve_item)
        self.plot.set_antialiasing(True)

        self.databaseScroll = databaseListModel(DBaseName = None)

        spacer = QSpacerItem(30,40)
        
        preprocessData = QGroupBox(u"preprocess data")
        # create buttons
        listButton = QPushButton(u"Refresh list")
        processButton = QPushButton(u"       run preprocessing       ")
        addwaveletButton = QPushButton(u"  add wavelet spikes to DB  ")
        
        self.checkAddData = QMessageBox()
        
        self.wavelet = QCheckBox(u"wavelet filter      ")
        label1 = QLabel("enter threshold value: ")
        self.waveletThreshold = QLineEdit(u"10")

        

        # connect user actions with methods:
        self.connect(listButton, SIGNAL('clicked()'), self.but_clicked)
        #self.connect(queryButton, SIGNAL('clicked()'), self.query_database)
        self.connect(processButton, SIGNAL('clicked()'), self.run_preprocess)
        self.connect(self.databaseScroll, SIGNAL("doubleClicked(QModelIndex)"), 
                     self.double_clicked)
        self.connect(addwaveletButton, SIGNAL('clicked()'), self.add_data_to_DBase)
        
        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()

        
        vlayout.addWidget(self.databaseScroll)
        vlayout.addWidget(listButton)

        vlayout.addWidget(self.plot)
        vlayout.addSpacerItem(spacer)
        
        
        hlayout.addWidget(self.wavelet)
        hlayout.addWidget(label1)
        hlayout.addWidget(self.waveletThreshold)

        hlayout.addWidget(processButton)        
        hlayout.addWidget(addwaveletButton)
        preprocessData.setLayout(hlayout)
        vlayout.addWidget(preprocessData)
        
        self.setLayout(vlayout)
        
        self.update_curve()

                                             
    def run_preprocess(self):
        """
        """        
        if self.wavelet.isChecked():
            try:
                yData = self.y1Data
                waveletFilt = pp.wavefilter(yData)
                self.y1Data = waveletFilt
                
                thresh = float(self.waveletThreshold.displayText())
                foo = self.y1Data > thresh
                self.y2Data = self.spikes = pp.spikeThreshold(foo)
                self.y2Data = self.y2Data * max(self.y1Data)
                
                index = self.databaseScroll.currentIndex()
                root = index.parent().parent().row()
                neuron = index.parent().row()
                epoch = index.row()  
                
                r = self.databaseScroll.DataBasesOpen[root]
                self.data = Dbase(r, PRINT = 1)               
                n = self.databaseScroll.neuronName[neuron]
                epochs = self.data.GetTree(n)
                e = epochs[epoch]
                
                self.spikeOverwriteLoc = [r, n + '.' + e + '.spikes', n + '.' + e, 
                                          n, n + '_' + e + '_spikes']
                self.data.Data.CloseDatabase(PRINT=1)
                print 'spike handle: ', self.spikeOverwriteLoc[0:2]
                self.update_curve()
                
            except ValueError:
                print 'ValueError. Could not compute wave filter'
                pass


    def add_data_to_DBase(self):
        """
        """
        self.checkAddData.setText("Are you sure you want to add filtered spikes (green trace) to the DB?")
        self.checkAddData.setInformativeText("This will overwrite the existing spike data.")
        self.checkAddData.setStandardButtons(QMessageBox.Yes | QMessageBox.No )
        self.checkAddData.setDefaultButton(QMessageBox.Yes)
        choice = self.checkAddData.exec_() == QMessageBox.Yes
        if choice:

            self.data = Dbase(self.spikeOverwriteLoc[0], PRINT = 1)
            self.data.Data.RemoveChild(self.spikeOverwriteLoc[1], option=1)
            self.data.Data.AddData2Database('spikes', self.spikes,
                                            self.spikeOverwriteLoc[2])
            self.data.Data.AddGitVersion(self.spikeOverwriteLoc[3],
                                         Action = 'updated_{0}'.format(
                                         self.spikeOverwriteLoc[4]))
                                         
            self.data.Data.CloseDatabase(PRINT=1)
            
            """ add git version here """
            print 'spike data successfully overwritten.'

    
    def update_curve(self):
        """
        """
        #---Update curve
        
        self.curve_item.set_data(self.xData, self.y1Data)
        self.second_curve_item.set_data(self.xData, self.y2Data)
        self.plot.replot()
        self.plot.do_autoscale()
        
    def but_clicked(self):
        '''
        when refresh button is clicked, the tree is refreshed
        '''
        self.databaseScroll.refreshTree()
    
    def double_clicked(self):
        '''
        when a name button is clicked, iterate over the model, 
        find the neuron with this name, and set the treeviews current item
        '''
        
        index = self.databaseScroll.currentIndex()

        if index.column() == 2:
            root = index.parent().parent().row()
            neuron = index.parent().row()
            epoch = index.row()

            r = self.databaseScroll.DataBasesOpen[root]
            self.data = Dbase(r, PRINT = 1)
            
            n = self.databaseScroll.neuronName[neuron]
                
            epochs = self.data.GetTree(n)
            e = epochs[epoch]
            
            if e != 'git':
            
                rawDataquery = self.data.Query(NeuronName = n, Epoch = e, DataName = 'rawData')
                try:
                    self.spikesDataquery = self.data.Query(NeuronName = n, Epoch = e, DataName = 'spikes')   
                    self.y1Data = rawDataquery
                    if max(self.y1Data) < 0:
                        self.y2Data = min(self.y1Data) * self.spikesDataquery
                    else:
                        self.y2Data = max(self.y1Data) * self.spikesDataquery
                except (TypeError, ValueError):
                    
                    print 'spike data not available.'
                    self.y2Data = self.y1Data
    
                self.xData = np.arange(0, len(self.y1Data))
                self.update_curve()
                self.data.Data.CloseDatabase(PRINT=1)
            
        if index.column() == 3:
            
            root = index.parent().parent().parent().row()
            neuron = index.parent().parent().row()
            epoch = index.parent().row()
            data = index.row()

            try:
                r = self.databaseScroll.DataBasesOpen[root]
                self.data = Dbase(r, PRINT = 1)
                
                n = self.databaseScroll.neuronName[neuron]

                epochs = self.data.GetTree(n)
                e = epochs[epoch]
                
                if e != 'git':
                    d = self.databaseScroll.dataName[data] # account for git dataName
                    
                    if d != 'params':
    
                        query = self.data.Query( NeuronName = n, Epoch = e, DataName = d)
                    
                        if query.shape[0] > 1:
                            
                            self.y1Data = query
                            
                            try:
                                if max(self.y1Data) < 0:
                                    self.y2Data = min(self.y1Data) * self.spikesDataquery
                                else:
                                    self.y2Data = max(self.y1Data) * self.spikesDataquery
                            except TypeError:
                                    self.y2Data = self.y1Data
                             
                                
                            self.xData = np.arange(0, len(self.y1Data))
                            self.update_curve()
                        
                        if query.shape[0] == 1:
                            print ' '
                            print d, ': ', query[0]
                            
                    self.data.Data.CloseDatabase(PRINT=1)
                    
            except ValueError:
                pass
        
        if index.column() == 4:
            
            root = index.parent().parent().parent().parent().row()
            neuron = index.parent().parent().parent().row()
            epoch = index.parent().parent().row()
            data = index.parent().row()
            param = index.row()

            r = self.databaseScroll.DataBasesOpen[root]
            self.data = Dbase(r, PRINT = 1)           
            n = self.databaseScroll.neuronName[neuron]
            
            epochs = self.data.GetTree(n)
            e = epochs[epoch]
            
            d = self.databaseScroll.dataName[data] # account for git dataName
            p = self.databaseScroll.paramName[param]
            query =  self.data.Query(NeuronName = n, Epoch = e, 
                                     DataName = d + '.' + p)[0]
            print ' '
            print p, ': ', query
            self.data.Data.CloseDatabase(PRINT=1)
            
            
class databaseListModel(QTreeWidget):
    """
    """
        
    def __init__(self, DBaseName = None):
        """
        """
        
        QTreeWidget.__init__(self)
        self.DataBasesOpen = []
        self.DataBasesOpenPath = []
        
        header = QTreeWidgetItem(["Database","Neuron","Epoch","Data", 
                                  "Parameters"])
        self.setHeaderItem(header)   

        self.constructTree(DBname = DBaseName)
    
    def constructTree(self, DBname):   
        """
        """
        
        if DBname == None:
            root = QTreeWidgetItem(self)
        
        else:
            root = QTreeWidgetItem(self)
            root.setText(0, DBname[:-3])
            
            self.busyBar = BusyBar( text = "Updating tree" )
            self.busyBar.start()
            
            self.neuronName = []
            self.dataName = []
            self.paramName = []
            self.update()
            
            self.Db = Dbase(DBname)
            top = self.Db.GetTree()      
            for countNeuro,neuron in enumerate(top):
                
                neurons = QTreeWidgetItem(root) 
                neurons.setText(1, neuron)
                
                self.neuronName.append(neuron)
    
                neuronTree = self.Db.GetTree(neuron)
                for countEpoch, epoch in enumerate(neuronTree):
                    
                    singleEpoch = QTreeWidgetItem(neurons) 
                    singleEpoch.setText(2, epoch)
                    
                    
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
                                    
            self.Db.Data.CloseDatabase(PRINT=1)
            self.busyBar.Kill()
            #QTimer.singleShot(10000, self.busyBar.Kill)
            
    def stopBar(self):
        """
        """
        
        self.busyBar.Kill()   
        
    def refreshTree(self): 
        """
        """
        
        self.clear()
        for DB in self.DataBasesOpen:
            self.constructTree(DB)        
        self.update()

        
    def AppendDatabasesOpen(self, DBname):
        """
        """
        
        self.DataBasesOpenPath.append(DBname)
        self.DataBasesOpen.append(os.path.basename(DBname))
        print 'databases open: ', self.DataBasesOpen   
    
    def CloseDatabase(self, DBname):
        """
        """
        
        self.DataBasesOpen.remove(DBname )
        #self.DataBasesOpenPath.remove(endswith(DBname + '.h5'))        
        
    def GetOpenDatabases(self):
        """
        """
        
        return self.DataBasesOpen

    def isOpen(self, DBname):
        """
        """
        
        truth = False
        for DB in self.DataBasesOpen:
            if DB == DBname:
                truth = True
                break
            else:
                pass
        return truth

        
class Dbase():
    """
    """
        
    def __init__(self, DBaseName, PRINT = 0):
        """
        """
        
        self.Data = Db.Database()
        
        if DBaseName != None:
            self.Data.OpenDatabase(DBaseName, PRINT)
                
            if self.Data.file == []:
                
                if DBaseName[-3:] == '.h5':
                    DBaseName = DBaseName[:-3]
                
                if PRINT == 0:
                    print 'here creating {0} database.'.format(DBaseName + '.h5')
                    
                self.Data.CreateDatabase(DBaseName)    
        
    def Query(self, NeuronName = 'Oct0212Bc8', Epoch = 'epoch040', DataName = 'rawData'):
        """
        """
        
        return self.Data.QueryDatabase( NeuronName, Epoch, DataName)
        
    def AddData(self, NeuronName, Directory):
        """
        """
        
        self.Data.ImportAllData(NeuronName, Directory, progBar = 0)   

    def GetTree(self, NeuronName = None):
        """
        """
        
        if NeuronName == None:
            tree = self.Data.GetChildList()
        else:
            tree = self.Data.GetChildList(NeuronName)
        
        return tree
        


    
    
class Window(QMainWindow):
    """
    """
        
    def __init__(self):
        """
        """
        QMainWindow.__init__(self)
        self.setWindowTitle("Neuron Database")
        self.setWindowIcon(get_icon('guiqwt.png'))
        self.setAttribute(Qt.WA_DeleteOnClose,True)
        
        hlayout = QHBoxLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(hlayout)
        self.setCentralWidget(central_widget)
        #---guiqwt plot manager
        self.manager = PlotManager(self)
        #---
        self.add_plot("1")
        

        # file menu

        file_menu = self.menuBar().addMenu("File")
        quit_action = create_action(self, "Quit",
                                    shortcut="Ctrl+Q",
                                    icon=get_std_icon("DialogCloseButton"),
                                    tip="Quit application",
                                    triggered=self.close)
        openDB_action = create_action(self, "Open database",
                                     shortcut ="Ctrl+D",
                                     tip ="Open an existing database into scroll area",
                                     triggered=self.open_Database)
        createDB_action = create_action(self,"New database",
                                        shortcut ="Ctrl+N",
                                        tip ="Create a new database",
                                        triggered=self.create_Database)
        closeDB_action = create_action(self,"Close database",
                                       shortcut ="Ctrl+W",
                                       tip = "Close an open database",
                                       triggered=self.close_Database)
        
        add_actions(file_menu, (quit_action, openDB_action, createDB_action,
                                closeDB_action))
        
        # Edit menu


        edit_menu = self.menuBar().addMenu("Edit")
        editparam1_action = create_action(self, "Import dataset",
                                          shortcut ="Ctrl+A",
                                          tip ="Import data from matlab structure",
                                          triggered=self.add_newData)
        deleteNode_action = create_action(self, "Delete neuron",
                                          tip ="Delete neuron from database",
                                          triggered=self.delete_Neuron)
        add_actions(edit_menu, (editparam1_action, deleteNode_action))
        

        # Create the console widgetDBaseName
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
        
            
    def add_plot(self, title):
        """
        """
        
        self.widget = FilterTestWidget(self)
        self.widget.setup_widget(title)
        self.centralWidget().layout().addWidget(self.widget)
        
        #---Register plot to manager    
        self.manager.add_plot(self.widget.plot)

        
    def setup_window(self):
        """
        """
        
        #---Add toolbar and register manager tools
        toolbar = self.addToolBar("tools")
        self.manager.add_toolbar(toolbar, id(toolbar))
        self.manager.register_all_curve_tools()
        #---
        
    def closeEvent(self, event):
        """
        """
        
        self.console.exit_interpreter()
        event.accept()       

    def findOpenDBases(self):
        """
        """
        
        return self.widget.databaseScroll.DataBasesOpen
        
    ### popup actions: 
        
    def add_newData(self):
        """
        """
        
        DBname = Popup(self.findOpenDBases(), 
                       textMessage = "add data to a database:",
                       style = 4)
                       
        if DBname.selection != None and DBname.selection != []:
            
            name = DBname.selection[1]
            neuronName = DBname.selection[2]
            if self.widget.databaseScroll.isOpen(name):
                addData = Dbase(DBaseName = name)
                if not addData.Data.Exists(neuronName):
                    addData.AddData(neuronName, Directory = DBname.selection[0])
                
                    self.widget.databaseScroll.refreshTree()
                    print 'data import complete.'
                else :
                    print ' '
                    print 'database already has Neuron named {0}'.format(neuronName)
            else:
                print 'database not open.'
                

    def open_Database(self):
        """
        """
        
        DBname = Popup(self.findOpenDBases(), 
                       textMessage = "select database to open",
                       style = 3)
                       
        if DBname.selection != None and len(DBname.selection) > 1:
            print DBname.selection
            
            loadedDBname = DBname.selection
            self.widget.databaseScroll.AppendDatabasesOpen(loadedDBname)
            self.widget.databaseScroll.refreshTree()
            print '{0} database opened.'.format(loadedDBname)
            
        else:
            pass
         
                
    def create_Database(self):
        """
        """
        DBname = Popup(self.findOpenDBases(), 
                       textMessage = "enter name of new database",
                       style = 2)
                       
        if DBname.selection != None :
            newDBname = DBname.selection
            if newDBname[-3:] != '.h5':
                newDBname = newDBname + '.h5'
            self.widget.databaseScroll.AppendDatabasesOpen(newDBname)
            self.widget.databaseScroll.refreshTree()
            #print '{0} database created.'.format(newDBname)
        else:
            pass
            
        
    def delete_Neuron(self):
        """
        """
        
        DBname = Popup(self.findOpenDBases(), 
                       textMessage = "enter name of neuron to delete",
                       style = 1)
                       
        if DBname.selection != None :
            try: 
                name = DBname.selection[0]
                if self.widget.databaseScroll.isOpen(name):
                    rmData = Dbase(DBaseName = name)
                    neuron = DBname.selection[1]
                    rmData.Data.RemoveNeuron(neuron, option = 1)
                    rmData.Data.CloseDatabase()
                    self.widget.databaseScroll.refreshTree()
                    print 'successfully deleted', neuron
                else:
                    print 'database not open.'
            except (ValueError, TypeError):
                
                print 'sorry, could not delete. please make sure data exists.'
        else:
             pass
         
         
         
    def close_Database(self):
        """
        """
        
        DBname = Popup(self.findOpenDBases(), 
                       textMessage = "select database to close",
                       style = 0)
        
        if DBname.selection != None :

            self.widget.databaseScroll.CloseDatabase(DBname.selection)
            self.widget.databaseScroll.refreshTree()
            print '{0} closed.'.format(DBname.selection)        
        else:
            pass



class Popup(QDialog):
    """
    """
    
    def __init__(self, openDB, textMessage = " ", style = 0):
        """
        """
        
        QDialog.__init__(self)
        self.style = style
        
        self.selection = None
        Num = 1
        if self.style < 3:
            text = QLabel(textMessage)
            enterbutton = QPushButton("Enter")
            cancelbutton = QPushButton("Cancel")
    
            vlayout = QVBoxLayout()
            vlayout.addWidget(text)
            
            if self.style < 2:
                self.openDB = openDB
        
                self.name = QComboBox()
                self.name.clear()
                self.name.addItems(openDB)
                label = QLabel('database')
                
                h0layout = QHBoxLayout()
                h0layout.addWidget(label)
                h0layout.addWidget(self.name)
                vlayout.addLayout(h0layout)                
                
                vlayout.addWidget(self.name)

            if self.style == 1:
                self.NeuronName = QLineEdit()
                label = QLabel('neuron name')
                
                h1layout = QHBoxLayout()
                h1layout.addWidget(label)
                h1layout.addWidget(self.NeuronName)
                vlayout.addLayout(h1layout)
                
            if self.style == 2:
                
                self.name = QLineEdit()
                label = QLabel('database name')
                
                h1layout = QHBoxLayout()
                h1layout.addWidget(label)
                h1layout.addWidget(self.name)
                vlayout.addLayout(h1layout)
                

            self.connect(enterbutton, SIGNAL('clicked()'), self.returnSelection)
            self.connect(cancelbutton, SIGNAL('clicked()'), self.closePopup)
                
            hlayout = QHBoxLayout()
            hlayout.addWidget(enterbutton)
            hlayout.addWidget(cancelbutton)
            vlayout.addLayout(hlayout)            
    
            self.setLayout(vlayout)
            self.setGeometry(QRect(100, 100, 200, 100 * Num))
            self.raise_()
            self.exec_()

        if self.style == 3:
            
            self.dirName = QFileDialog.getOpenFileName(self, 'Open H5 file',
                                                         '.',
                                                         "H5 file ( *.h5 )")
            self.returnSelection()
            
            
        if self.style == 4:
            text = QLabel(textMessage)
            enterbutton = QPushButton("Enter")
            cancelbutton = QPushButton("Cancel")
    
            vlayout = QVBoxLayout()
            vlayout.addWidget(text)
            self.openDB = openDB
            self.NeuronName = QLineEdit()
            label1 = QLabel('neuron name :')  
            
            self.name = QComboBox()
            self.name.clear()
            self.name.addItems(openDB)
            label2 = QLabel('database :')
            
            '''
            h0layout = QHBoxLayout()
            h0layout.addWidget(label)
            h0layout.addWidget(self.name)
            vlayout.addLayout(h0layout)                
            
            vlayout.addWidget(self.name)            
            '''
            enterbutton = QPushButton("Enter")
            cancelbutton = QPushButton("Cancel")
            
            self.dirName = QFileDialog()
            #self.selectedDirName = str(QFileDialog.getOpenFileName(options=QFileDialog.DontUseNativeDialog))
            self.dirName.setFileMode(QFileDialog.Directory)
            self.dirName.setOptions(QFileDialog.ShowDirsOnly)
            
            """
            for child in self.dirName.isWidgetType()():
                if child.objectName() == "qt_new_folder_action":
                    print 'here'
                    pass
                    #self.dirName.removeAction(child)
            """
            fileLayout = self.dirName.layout()
            
            items = (fileLayout.itemAt(i) for i in range(fileLayout.count())) 
            i = 0
            for w in items:
                i +=1
                if i == 5 or i == 6 or i == 4:
                    fileLayout.removeItem(w)

            fileLayout.addWidget( QLabel(' ') )
            fileLayout.addWidget( QLabel(' ') )
            fileLayout.addWidget( QLabel(' ') )

            fileLayout.addWidget( QLabel(' ') )
            fileLayout.addWidget( QLabel(' please enter data below:  ') )
            fileLayout.addWidget( QLabel(' ') )

            fileLayout.addWidget(label1)
            fileLayout.addWidget(self.NeuronName)
            fileLayout.addWidget( enterbutton ) 

            fileLayout.addWidget(label2)
            fileLayout.addWidget(self.name)
            fileLayout.addWidget( cancelbutton )
                       
            self.connect(enterbutton, SIGNAL('clicked()'), self.returnSelection)
            self.connect(cancelbutton, SIGNAL('clicked()'), self.closePopup)
            
            
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
        
def main():
    """
    
    Testing this simple Qt/guiqwt example
    
    """
    
    from guidata.qt.QtGui import QApplication
    
    app = QApplication([])
    win = Window()
    

    #win.add_plot("1")
    #win.add_plot("2")
    #---Setup window
    win.setup_window()
    #---
    
    win.show()
    return app.exec_()
        
        
if __name__ == '__main__':
    main()
    