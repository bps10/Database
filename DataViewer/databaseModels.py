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
        return self.Data.QueryDatabase(DataName, Parents)
        
    def AddData(self, DataName, Directory):
        """Add data to an open Database.
        
        :param DataName:
        """
        self.Data.ImportAllData(DataName, Directory)   

                
class treeList(Dbase, qg.QTreeWidget):
    """
    """
    def __init__(self, DBaseName = None):
        qg.QTreeWidget.__init__(self)
        self.DataBasesOpen = []
        self.DataBasesOpenPath = []

        Rieke = True
        if Rieke == True:
            header = qg.QTreeWidgetItem(["Database", "Neuron", "Epoch","Data1", 
                                      "Data2", "Data3", "Data4", "Data5"])
                                      
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
            self.tree[0].setText(0,os.path.basename(DBname))
            #self.treeList = {}            
            
            DB = Db.Database()
            DB.OpenDatabase(DBname, PRINT=True)
            DB.file.visititems(self._createTree)
            DB.CloseDatabase()

    def _createTree(self, name, obj):
        """
        """
        n = name.split('/')
        
        if n[0] != '':
            level = int(len(n))
        else: 
            level = 1
        if level > 1:
            self.tree[level] = qg.QTreeWidgetItem(self.tree[level - 1]) 
            self.tree[level].setText(level, n[-1])
        else:
            self.tree[level] = qg.QTreeWidgetItem(self.tree[0]) 
            self.tree[1].setText(level, n[-1])
            
        if len(n) > 1:
            par = n[:-1]
            if par[0] == '':
                par.pop('')
            if par[0] != '/' and n[-1] != '/':
                par.insert(0, '/')
        else:
            par = ''
        #self.treeList[n[-1]] = {'name': n[-1], 'parents': par}
        
    def refreshTree(self): 
        """
        """
        self.clear()
        for DB in self.DataBasesOpen:
            self.constructTree(DB)        
        self.update()

    def GetDtype(self, DBname, dataName, parents):
        '''
        '''
        print DBname, dataName, parents
        DB = Db.Database()
        DB.OpenDatabase(DBname, PRINT=0)
        dtype_ = DB.getDType(dataName, parents)
        DB.CloseDatabase()
        return dtype_
        
    def GetData(self, DBname, dataName, parents):
        '''
        '''
        DB = Db.Database()
        DB.OpenDatabase(DBname, PRINT=True)
        dat = DB.Query(dataName, parents)
        DB.CloseDatabase()
        return dat
        
        
    def AppendDatabasesOpen(self, DBname):
        """
        """
        self.DataBasesOpenPath.append(DBname)
        self.DataBasesOpen.append(os.path.basename(DBname))

    def OpenDatabases(self, DBaseName):
        """
        """
        self.constructTree(DBaseName)
        self.AppendDatabasesOpen(DBaseName)
        
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
    """No longer in use.  Eventually want to use tabs at the top to open
    multiple database as once.  However, not able to make it work currently.
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
