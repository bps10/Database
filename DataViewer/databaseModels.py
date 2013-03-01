# -*- coding: utf-8 -*-
# PyQt4 imports
import PyQt4.QtGui as qg
import PyQt4.QtCore as qc

import os
# user defined imports
import DatabaseWrapper.dbase as Db


class Dbase(object):
    """An abstract class for manipulating databases.
    """
    def __init__(self, DBaseName, PRINT = 0):
        
        self.Data = Db.Database()
        self.OpenDB(DBaseName, PRINT)
        
    def OpenDB(self, DBaseName, PRINT):
        
        if DBaseName != None:
            self.Data.OpenDatabase(DBaseName, PRINT)
                
            if self.Data.file == []:
                
                if DBaseName[-3:] == '.h5':
                    DBaseName = DBaseName[:-3]
                
                if PRINT == 0:
                    print '{0} database created.'.format(DBaseName + '.h5')
                    
                self.Data.CreateDatabase(DBaseName)    
        
    def Query(self, DataName, Parents=None):
        """Retrieve data from the database.
        
        :param DataName: name of the data to retrieve
        :type DataName: str
        :param Parents: optional. A string or list of parents in the database
        tree.
        :type Parents: str or list
        
        :returns: data.
        """        
        return self.Data.QueryDatabase( DataName, Parents)
        
    def AddData(self, DataName, Directory):
        """Add data to an open Database.
        
        :param DataName:
        """
        self.Data.ImportAllData(DataName, Directory)   

    def GetTree(self, DataName=None, Parents=''):
        """Get a list of all children in the tree.
        
        :param DataName: optional. If no name give, will return root children.
        :type DataName: str
        :param Parents: optional. A string or list of parents in the database
        tree for the given node (DataName).
        :type Parents: str or list
        
        :returns: list of children (keys) for the given node.
        """
        if DataName == None:
            tree = self.Data.GetChildList('/', '')
        else:
            tree = self.Data.GetChildList(DataName, Parents)
        
        return tree
        
        
class treeList(Dbase, qg.QTreeWidget):
    """
    """
    def __init__(self, DBaseName = None):
        qg.QTreeWidget.__init__(self)
        self.DataBasesOpen = []
        self.DataBasesOpenPath = []
        
        Rieke = True
        if Rieke == True:
            header = qg.QTreeWidgetItem(["Neuron", "Epoch","Data", 
                                      "Parameters"])
        self.setHeaderItem(header)   

        self.constructTree(DBname = DBaseName)
    
    def constructTree(self, DBname):   
        """
        """
        if DBname == None:
            pass
        
        else:
            
            self.update()
            
            self.tree = {0: qg.QTreeWidgetItem(self)}
            self.treeList = {}            
            
            self.Db = Dbase(DBname)
            
            self.Db.Data.file.visititems(self._createTree)

    def _createTree(self, name, obj):
        """
        """
        n = name.split('/')
        level = int(len(n)) - 1
        print level
        if level > 0:
            self.tree[level] = qg.QTreeWidgetItem(self.tree[level - 1]) 
            self.tree[level].setText(level, n[-1])
        else:
            self.tree[0].setText(level, n[-1])
            
        if len(n) > 1:
            par = n[:-1]
            if par[0] == '':
                par.pop('')
            if par[0] != '/' and n[-1] != '/':
                par.insert(0, '/')
        else:
            par = ''
        self.treeList[n[-1]] = {'name': n[-1], 'parents': par}
        
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
    
    def CloseDatabase(self, DBname):
        """
        """
        self.DataBasesOpen.remove(DBname)
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

            
class databaseListModel(qg.QWidget):
    """
    """
    def __init__(self, DBaseName = None):
        qg.QWidget.__init__(self)
        self.TabWid = qg.QTabWidget(self)
        self.here = treeList(DBaseName)
        self.TabWid.addTab(self.here, 'Empty')
        
        self.TreeWid = self.TabWid.children()[0].currentWidget()
        print self.TreeWid
        
        self.DataBasesOpen = []
        self.DataBasesOpenPath = []
        self.TabWid.setTabsClosable(True)
        self.TabWid.currTab = self.GetCurrentTab()

        self.connect(self.TabWid, qc.SIGNAL("doubleClicked()"),
                     self.dud)
        self.connect(self.TabWid, qc.SIGNAL("currentChanged(int)"),
                     self.switchTab)
        self.connect(self.TabWid, qc.SIGNAL("tabCloseRequested(int)"),
                     self.closeTab)

    def dud(self):
        print 'here idiot'
        
    def switchTab(self, index):
        """
        """
        print 'on tab: ', self.DataBasesOpen[index]
        self.TreeWid = self.TabWid.children()[0].currentWidget()
        print 'enabled? ', self.TabWid.isEnabled()
        self.TabWid.activateWindow()
        #self.here = treeList(self.DataBasesOpen[index])
        
    def closeTab(self, index):
        """
        """
        print index
        print self.DataBasesOpen[index]
        self.TabWid.removeTab(index)
        self.TreeWid = self.TabWid.children()[0].currentWidget()
        self.CloseDatabase(self.DataBasesOpen[index])
        self.here = treeList(self.DataBasesOpen[index])
        
    def GetCurrentTab(self):
        """
        """
        return self.TabWid.currentIndex()
        
    def OpenDatabases(self, DBaseName):
        """
        """
        if self.TabWid.children()[1].tabText(0) == 'Empty':
            self.TabWid.removeTab(0)
        self.here = treeList(DBaseName)
        self.TabWid.addTab(self.here, os.path.basename(DBaseName)[:-3])
        self.TreeWid = self.TabWid.children()[0].currentWidget()
        
    def AppendDatabasesOpen(self, DBaseName):
        """
        """
        self.DataBasesOpenPath.append(DBaseName)
        self.DataBasesOpen.append(os.path.basename(DBaseName))        

    def refreshTree(self): 
        """
        """
        self.TreeWid = self.TabWid.children()[0].currentWidget()
        self.TreeWid.refreshTree()
        self.TabWid.update()

    def CloseDatabase(self, DBname):
        """
        """
        self.here.clear()
        self.DataBasesOpen.remove(DBname)
        #self.DataBasesOpenPath.remove(endswith(DBname + '.h5'))   
        self.TabWid.update()
