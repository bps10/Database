# -*- coding: utf-8 -*-
# PyQt4 imports
import PyQt4.QtGui as qg
import PyQt4.QtCore as qc

import os
# user defined imports
import DatabaseWrapper.dbase as Db

class treeList(qg.QTreeWidget):
    def __init__(self, DBaseName = None):
        qg.QTreeWidget.__init__(self)
        self.DataBasesOpen = []
        self.DataBasesOpenPath = []
        
        header = qg.QTreeWidgetItem(["Neuron","Epoch","Data", 
                                  "Parameters"])
        self.setHeaderItem(header)   

        self.constructTree(DBname = DBaseName)
    
    def constructTree(self, DBname):   
        if DBname == None:
            pass
        
        else:
            
            #self.busyBar = BusyBar( text = "Updating tree" ) 
            #self.busyBar.changeValue.connect(self.busyBar.proBar.setValue, 
            #                                 qc.Qt.QueuedConnection)
            #self.busyBar.start()
            
            self.neuronName = []
            self.dataName = []
            self.paramName = []
            self.update()
            
            self.Db = Dbase(DBname)
            top = self.Db.GetTree()      
            for countNeuron,neuron in enumerate(top):

                neurons = qg.QTreeWidgetItem(self) 
                neurons.setText(0, neuron)
                
                self.neuronName.append(neuron)
    
                neuronTree = self.Db.GetTree(neuron)
                for countEpoch, epoch in enumerate(neuronTree):
                    
                    singleEpoch = qg.QTreeWidgetItem(neurons) 
                    singleEpoch.setText(1, epoch)
                    
                    
                    epochTree = self.Db.GetTree( neuron + '/' + epoch)
                    for countData,data in enumerate(epochTree):
                        singleData = qg.QTreeWidgetItem(singleEpoch) 
                        singleData.setText(2, data)
                        
                        if countEpoch == 1:
                            self.dataName.append(data)
                            
                        if data == 'params':
                            paramTree = self.Db.GetTree( neuron + '/' + epoch + '/' + data)
                            for countParam,param in enumerate(paramTree):
                                singleParam = qg.QTreeWidgetItem(singleData)
                                singleParam.setText(3, param)
                                
                                if countEpoch == 1:
                                    self.paramName.append(param)
                                    
            self.Db.Data.CloseDatabase(PRINT=1)
            self.busyBar.Kill()
            #QTimer.singleShot(10000, self.busyBar.Kill)
            
    #def stopBar(self):
    #    self.busyBar.Kill()   
        
    def refreshTree(self): 
        self.clear()
        for DB in self.DataBasesOpen:
            self.constructTree(DB)        
        self.update()

        
    def AppendDatabasesOpen(self, DBname):
        self.DataBasesOpenPath.append(DBname)
        self.DataBasesOpen.append(os.path.basename(DBname))
    
    def CloseDatabase(self, DBname):

        self.DataBasesOpen.remove(DBname)
        #self.DataBasesOpenPath.remove(endswith(DBname + '.h5'))        
        
    def GetOpenDatabases(self):
        return self.DataBasesOpen

    def isOpen(self, DBname):
        truth = False
        for DB in self.DataBasesOpen:
            if DB == DBname:
                truth = True
                break
            else:
                pass
        return truth

            
class databaseListModel(qg.QWidget):
    def __init__(self, DBaseName = None):
        qg.QWidget.__init__(self)
        self.TabWid = qg.QTabWidget(self)
        self.here = treeList(DBaseName)
        self.TabWid.addTab(self.here, 'Empty')
        
        self.TreeWid = self.TabWid.children()[0].currentWidget()
        print self.TreeWid
        #for name in dir(self.TreeWid):
            #print name
        
        self.DataBasesOpen = []
        self.DataBasesOpenPath = []
        self.TabWid.setTabsClosable(True)
        self.TabWid.currTab = self.GetCurrentTab()

        self.connect(self.TreeWid, qc.SIGNAL("doubleClicked(QModelIndex)"),
                     self.dud)
        self.connect(self.TabWid, qc.SIGNAL("currentChanged(int)"),
                     self.switchTab)
        self.connect(self.TabWid, qc.SIGNAL("tabCloseRequested(int)"),
                     self.closeTab)

    def dud(self):
        print 'here idiot'
        
    def switchTab(self, index):
        print 'switching tabs!'
        print index
        print self.DataBasesOpen[index]
        self.TreeWid = self.TabWid.children()[0].currentWidget()
        #self.here = treeList(self.DataBasesOpen[index])
        
    def closeTab(self, index):
        print index
        print self.DataBasesOpen[index]
        self.TabWid.removeTab(index)
        self.TreeWid = self.TabWid.children()[0].currentWidget()
        self.CloseDatabase(self.DataBasesOpen[index])
        self.here = treeList(self.DataBasesOpen[index])
        
    def onTabClick(self, index):
        print 'woohoo!'
        
    def GetCurrentTab(self):
        return self.TabWid.currentIndex()
        
    def OpenDatabases(self, DBaseName):

        
        if self.TabWid.children()[1].tabText(0) == 'Empty':
            self.TabWid.removeTab(0)
        self.here = treeList(DBaseName)
        self.TabWid.addTab(self.here, os.path.basename(DBaseName)[:-3])
        self.TreeWid = self.TabWid.children()[0].currentWidget()
        
        print self.TreeWid.neuronName[0]  
        
    def AppendDatabasesOpen(self, DBaseName):
        self.DataBasesOpenPath.append(DBaseName)
        self.DataBasesOpen.append(os.path.basename(DBaseName))        

    def refreshTree(self): 
        
        self.TreeWid = self.TabWid.children()[0].currentWidget()
        self.TreeWid.refreshTree()
        self.TabWid.update()

    def CloseDatabase(self, DBname):
        self.here.clear()
        self.DataBasesOpen.remove(DBname)
        #self.DataBasesOpenPath.remove(endswith(DBname + '.h5'))   
        self.TabWid.update()


        
class Dbase():
    def __init__(self, DBaseName, PRINT = 0):
        
        self.Data = Db.Database()
        
        if DBaseName != None:
            self.Data.OpenDatabase(DBaseName, PRINT)
                
            if self.Data.file == []:
                
                if DBaseName[-3:] == '.h5':
                    DBaseName = DBaseName[:-3]
                
                if PRINT == 0:
                    print '{0} database created.'.format(DBaseName + '.h5')
                    
                self.Data.CreateDatabase(DBaseName)    
        
    def Query(self, NeuronName = 'Oct0212Bc8', Epoch = 'epoch040', DataName = 'rawData'):
        return self.Data.QueryDatabase( NeuronName, Epoch, DataName)
        
    def AddData(self, NeuronName, Directory):
        
        self.Data.ImportAllData(NeuronName, Directory, progBar = 0)   

    def GetTree(self, NeuronName = None):
        
        if NeuronName == None:
            tree = self.Data.GetChildList()
        else:
            tree = self.Data.GetChildList(NeuronName)
        
        return tree
        
