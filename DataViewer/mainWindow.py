# -*- coding: utf-8 -*-
# PyQt4 imports
import PyQt4.QtGui as qg
import PyQt4.QtCore as qc

# user defined imports
from databaseModels import Dbase
from popups import Popup
from plotQwt import PlotWidget

# guidata imports
from guidata.qthelpers import create_action, add_actions, get_std_icon
#---Import plot widget base class
from guiqwt.plot import PlotManager
from guidata.configtools import get_icon
#---
from spyderlib.widgets.internalshell import InternalShell
       
class MainWindow(qg.QMainWindow):
    """This one generates the main window and orchestrates all other widgets
    """
    def __init__(self):
        qg.QMainWindow.__init__(self)
        self.setWindowTitle("Neuron Database")
        self.setWindowIcon(get_icon('guiqwt.png'))
        self.setAttribute(qc.Qt.WA_DeleteOnClose,True)
        
        hlayout = qg.QHBoxLayout()
        central_widget = qg.QWidget(self)
        central_widget.setLayout(hlayout)
        self.setCentralWidget(central_widget)
        #---guiqwt plot manager
        self.manager = PlotManager(self)
        #---
        self.add_plot("1")
        
        self._constructFileMenu()
        self._constructEditMenu()
        self._constructConsoleWidget(central_widget)

    def _constructFileMenu(self):
        """
        """
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
        
    def _constructEditMenu(self):
        """
        """
        edit_menu = self.menuBar().addMenu("Edit")
        editparam1_action = create_action(self, "Import dataset",
                                          shortcut ="Ctrl+A",
                                          tip ="Import data from matlab structure",
                                          triggered=self.add_newData)
        deleteNode_action = create_action(self, "Delete neuron",
                                          tip ="Delete neuron from database",
                                          triggered=self.delete_Neuron)
        add_actions(edit_menu, (editparam1_action, deleteNode_action))
        

    def _constructConsoleWidget(self, central_widget):
        """
        """
        font = qg.QFont("Courier new")
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
        console_dock = qg.QDockWidget("Console", self)
        console_dock.setWidget(cons)
        
        # Add the console widget to window as a dockwidget
        self.addDockWidget(qc.Qt.BottomDockWidgetArea, console_dock)
        
            
    def add_plot(self, title):
        """
        """
        self.widget = PlotWidget(self)
        self.widget.setup_widget(title)
        self.centralWidget().layout().addWidget(self.widget)
        
        #---Register plot to manager    
        self.manager.add_plot(self.widget.plot)

        
    def setup_window(self):
        """Add toolbar and register manager tools
        """
        toolbar = self.addToolBar("tools")
        self.manager.add_toolbar(toolbar, id(toolbar))
        self.manager.register_all_curve_tools()
        
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
            self.widget.databaseScroll.OpenDatabases(loadedDBname)
            #self.widget.databaseScroll.refreshTree()
            #print '{0} database opened.'.format(loadedDBname)
            
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


