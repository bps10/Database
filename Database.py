#import scipy as sp
from scipy.io import loadmat
import numpy as np
import glob as glob
import git as git
import tables as tables
import os
import datetime as dt
#from ProgressBar import BusyBar
#from guidata.qt.QtCore import Qt

class Database():
    """
    A class for working with an HDF5 database. Basically a wrapper around pytables.
    
    """
    def __init__(self):
        """
        
        .. note:: 
           Not currently doing anything
        
        """
        pass

    def CreateGroup(self, GroupName, Parent = None):
        """
        Create a group in an HDF5 database.
        
        :param GroupName: provide a name for the group.
        :type GroupName: str
        :param Parent: provide names of parent nodes if they exist.
        :type Parent: str
        
        :returns: updates HDF5 database with new group.
        
        """
        if Parent == None:

            self.group = self.file.createGroup("/", GroupName, GroupName)
        
        else :
            self.group = self.file.createGroup( ("/" + Parent), GroupName, GroupName)



    def CreateDatabase(self, FileName):
        """
        
        Create a new HDF5 database.
        
        :param FileName:    provide a name for a new HDF5 database. DO NOT include
                            .h5 at the end - h5 suffix is automatically appended.
        :type FileName: str
        
        :returns: creates a new HDF5 database.
        
        """
        self.file = tables.openFile(FileName + '.h5', mode = "w", title = 'NeuronAnalysis')


    def AddData2Database(self, DataName, Data, GroupName, Parents = None):
        """
        
        Add numpy data to current database.
        
        :param DataName: name of data being entered.
        :type DataName: str
        :param Data: data to be entered.
        :type Data: np.array
        :param GroupName: provide the location in the open database to store the new data.
        :type param: str
        :param Parents: provide name of parents if they exist. Not currently active.
        :type Parents: str
        
        .. note::
           Do not use Parent option right now. It is untested and likely to fail.
           
        
        
        """
        
        if Parents == None:
            loc = 'self.file.root.' + GroupName 

        else :
            loc = 'self.file.root.' + GroupName
            for name in Parents:
                loc += '.' + Parents
                
        filters = tables.Filters(complevel=1, complib='zlib', fletcher32=True)
        atom = tables.Atom.from_dtype(Data.dtype)
        ds = self.file.createCArray(eval(loc), DataName, atom, Data.shape, filters = filters)
        ds[:] = Data


    def OpenDatabase(self, DatabaseName, PRINT = 0):
        """
        
        Open a specific database.
        
        :param DatabaseName: name of the database to open
        :type DatabaseName: str
        :param PRINT: select whether to print message or not. \n
                        0 = Yes \n
                        1 = No \n
        :type PRINT: int
        
        """

        self.file = []
        try:
            test = tables.isHDF5File(DatabaseName)

            if test:
                self.file = tables.openFile(DatabaseName, mode = "a")
                if PRINT == 0:
                    print '{0} database opened'.format(DatabaseName)
                
        except IOError:
            
            print '{0} does not exist'.format(DatabaseName)
            raise DatabaseError('{0} database does not exist'.format(DatabaseName))

    def QueryDatabase(self, NeuronName, GroupName, DataName):
        """
        Query a database. 
        
        :param NeuroonName: name of node 1.
        :type NeuronName: str
        :param GroupName: name of node 2.
        :type GroupName: str
        :param DataName: name of data you wish to have returned.
        :type DataName: str

        :returns: result of query in a numpy.array()        
        
        .. note:: not currently working in a very powerful way
        
        .. todo::
           1. Write a better query system.
           2. Generalize- get rid of neuron nomen.
        """
        
        loc = 'self.file.root.' + NeuronName + '.' + GroupName + '.' + DataName + '.read()'
        return eval(loc)


    def RemoveNeuron(self, NeuronName, option = 0):
        """
        
        Remove a neuron from the database. Uses the recursive option to force
        the node and all of its children to be deleted.
        
        :param NeuronName: name of the neuron you would like to remove.
        :type NeuronName: str
        :param option:  choose whether to confirm deletion with user. \n
                        0 = yes\n
                        1 = no\n
        :type option: int        
        
        :returns: deletes neuron and all of its children from the database.
        
        .. todo::
           1. change the name - node rather than neuron - to generalize. 
        
        """
        
        if option == 0:
            decision = raw_input( 'Are you absolutely sure you want to delete this group permenently? (y/n): ')
            if decision.lower() == 'y' or decision.lower() == 'yes':
                deleteHandle = self.file.removeNode
                deleteHandle( '/' + NeuronName, recursive=1)
                self.file.flush()
                print '{0} successfully deleted'.format(NeuronName)
            else:
                print 'Ok, nothing changed.'

        if option == 1:

            deleteHandle = self.file.removeNode
            #print 'hang tight. deleting in process...'
            deleteHandle( '/' + NeuronName, recursive=1)        
            self.file.flush()

    def RemoveChild(self, ChildName, option = 0):
        """
        
        Remove child.
        
        :param ChildName: name of child to remove.
        :type ChildName: str
        :param option: choose whether to confirm deletion with user. \n
                        0 = yes\n
                        1 = no\n
        :type option: int
        
        :returns: deletes child. This is a less severe than RemoveNeuron. It will not delete all of the children.
        
        .. note:: 
           Not currently in use as far as I am aware. Consider removing or 
           incorporating into RemoveNeuron.
           
        """
        
        if option == 0:    
            decision = raw_input( 'Are you absolutely sure you want to delete this child permenently? (y/n): ')
            if decision.lower() == 'y' or decision.lower() == 'yes':
                eval('self.file.root.' + ChildName + '._f_remove()')
                self.file.flush()
                print '{0} successfully deleted'.format(ChildName)
            
            else:
    
                print 'Ok, nothing changed.'
                
        if option == 1:
            eval('self.file.root.' + ChildName + '._f_remove()')
            self.file.flush()
            

    def OpenMatlabData(self, FileName, Directory):
        """
        
        Open matlab data. Just a rapper around scipy.io.loadmat
        
        :param FileName: name of .mat file to open.
        :type FileName: str
        :param Directory: directory housing FileName.
        :type Directory: str

        .. note::
           This function is basically only used internally.
           It is called by ImportAllData.
           
        """

        if Directory == None:
            
            self.NeuronData = loadmat(Directory + '/' + FileName + '.mat' )
        
        else:
            
            self.NeuronData = loadmat(Directory + '/' + FileName + '.mat')

    def getAllFiles(self, Directory, suffix = None, subdirectories = 1):
        """
        
        Get a list of path names of all files in a directory.
        
        :param Directory: a directory.
        :type Directory: str
        :param suffix: find only files with a specific ending.
        :type suffix: str
        :param subdirectories: indicate how deep (# of directories) you would like to search; 0 - 2.
        :type subdirectories: int
        
        :returns: a list of path names.
        :rtype: list

        e.g. subdirectories = 1: Find all files within a directory and its 
        first layer of subdirectories.

        
        .. note::
           basically a duplicate from GeneralFunc
           
        """
        if suffix is None:
            suffix = '/*'
        
        if subdirectories == 0:
            self.DirFiles = []
            for name in glob.glob(Directory + suffix):
                self.DirFiles = np.append(self.DirFiles,name)
        
        if subdirectories == 1:
            self.DirFiles = []
            for name in glob.glob(Directory + '*/' + suffix):
                self.DirFiles = np.append(self.DirFiles,name)

        if subdirectories == 2:
            self.DirFiles = []
            for name in glob.glob(Directory + '*/*/' + suffix):
                self.DirFiles = np.append(self.DirFiles,name)



    def ImportAllData(self, NeuronName, Directory, GitDirectory = None, progBar = 0):
        """
        
        This one calls ImportDataFromMatlab to load a .mat file
        
        .. note:: 
           currently hard coded.
        
        .. todo::
           * Possibly incorporate Qt progress bar to throttle a Qt application.
        
        """
        
        if GitDirectory == None:
            GitDirectory = os.getcwd()
            
        print 'Importing data, please wait ... '    

        self.getAllFiles(Directory)
        self.CreateGroup(NeuronName)
        
        """
        if progBar == 1:
            self.busyBar = BusyBar( text = "Importing data" )
            self.busyBar.changeValue.connect(self.busyBar.proBar.setValue, Qt.QueuedConnection)
            self.busyBar.start()
        """
        for i in range(0, self.DirFiles.shape[0] ):

            FileName = self.DirFiles[i][-12:-4]  # select only 'epochXXX.mat'

            self.OpenMatlabData(FileName, Directory, NeuronName)
            self.ImportDataFromMatlab(FileName, NeuronName)

        self.AddGitVersion(NeuronName, NeuronName + '_InitialImport', GitDirectory)
        self.file.flush()
        self.CloseDatabase()
        
        """
        if progBar == 1:
            self.busyBar.Kill()
        """

    def ImportDataFromMatlab(self, FileName, NeuronName):
        """
        This is the big one for importing data.
        
        :param FileName: name of the file to import.
        :type FileName: str
        :param NeuronName: name of the neuron importing.
        :type NeuronName: str        
        
        :returns: updated HDF5 database.
        
        
        .. note:: still hard coded for the Rieke lab format.
        
        .. todo::
           * Generalize. NeuronName makes sense here for now, but eventually would like to import everything.
           
        """
        
        self.CreateGroup(FileName, NeuronName)

        ## Get meta data.
        
        try :
            self.AddData2Database('fileComment', np.array([self.NeuronData['fileComment'][0]],dtype=str), 
                                  NeuronName + '.' + FileName)
        except (IndexError, ValueError):
             self.AddData2Database('fileComment', np.array(['none entered'], dtype = str),
                                   NeuronName + '.' + FileName)           
                

        PARAMS = np.array(['binRate', 'numSegments', 'si', 'clockstep', 'sampleInterval', 'sampleRate', 'ampMode', 'ampGain',
                           'rawData', 'monitorData', 'frameRate', 'preSamples', 'postSamples', 'stimSamples', 'time', 'epochsize',
                           'subThreshold', 'spikes', 'spikeTimes', 'recordingMode', 'outputClass', 'stimulusType', 'epochComment'])

        STRINGS = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1])

        for i, name in enumerate(PARAMS):

            try:
                if name != 'spikeTimes':
                    
                    try:
                        
                        Data = self.NeuronData['data'][name][0][0][0]
                        
                    except ValueError:
                        
                        Data = np.array(['none entered'], dtype = str)
                        STRINGS[i] = 0
                        
                else:
                    
                    try:
                        
                        Data = self.NeuronData['data'][name][0][0][0][0][0]
                        
                    except ValueError:
                        Data = np.array(['none entered'], dtype = str)
                        STRINGS[i] = 0

            except IndexError:

                Data = np.array(['none entered'], dtype = str)
                STRINGS[i] = 0

            if STRINGS[i] == 0:
                
                try:
                    
                    self.AddData2Database(name, Data, NeuronName + '.' + FileName)
                    
                except ValueError: # for unicode cases.
                
                    Data = np.array(['none entered'], dtype = str)
                    STRINGS[i] = 1
                                              
            if STRINGS[i] == 1:

                self.AddData2Database(name, np.array([ Data ], dtype=str), NeuronName + '.' + FileName)

        # now load the params:
        self.CreateGroup('params', NeuronName + '/' + FileName )

        PARAMS = np.array(['Xpos', 'Ypos', 'colorGammaTable', 'diameter', 'epochNumber', 'flipInterval', 'integratedIntensity', 'intensity',
                  'intensity_raw', 'rand_behavior', 'repositoryVersion', 'screenX', 'screenY', 'sequential', 'spatial_meanLevel',
                  'spatial_postpts', 'spatial_prepts', 'windowPtr', 'stimClass', 'MatlabCodeDir'], dtype = str)

        STRINGS = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], dtype = int)
        for i, name in enumerate(PARAMS):

            try:
                
                Data = self.NeuronData['data']['params'][0][0][0][name][0][0]
                
            except ValueError:
                
                Data = np.array(['none entered'], dtype = str)
                STRINGS[i] = 0

            if STRINGS[i] == 0:
                
                try:
                    self.AddData2Database(name, Data, NeuronName + '.' + FileName + '.params')
                    
                except ValueError:
                    
                    Data = np.array(['none entered'], dtype = str)
                    STRINGS[i] = 1
                
            if STRINGS[i] == 1:

                    self.AddData2Database(name, np.array([ Data ], dtype=str), NeuronName + '.' + FileName + '.params')


    def GetChildList(self, FILE = None, parent = None):
        """
        
        Get a list of all children for a given node.
        
        :param FILE: file whose children you are interested in.
        :param parent: add a parent node before FILE node.
        
        :returns: list of children for FILE.
        :rtype: list
        
        .. note:: 
           * currently using eval function.
           * not an especially elegant function.
        
        .. todo::
           * make this function more flexible, closer to HDF5 syntax.
           
        """
        if FILE == None:
            ChildList = self.file.root.__members__
            
        if FILE != None and parent == None:
            foo = 'self.file.root.' + FILE
            ChildList = eval(foo + '.__members__')
        elif FILE != None and parent != None:
            foo = 'self.file.root.' + parent + '.' + FILE
            ChildList = eval(foo + '.__members__')
            
        return ChildList
        
                          
    def Exists(self, FILE, parent = None):
        """
        
        Check if a file exists.
        
        :param FILE: pass a file name to see if it exists.
        :type FILE: str
        :param parent: parent nodes.
        :type parent: str
        
        :returns: True or False
        :rtype: bool
        
        """

        if parent == None:
            TF = self.file.root.__contains__(FILE)
        
        else:
            foo = 'self.file.root.' + parent 
            TF = eval(foo + '.__contains__(FILE)')
        return TF


    def GetGitRepo(self, WorkingDir = '/Users/Brian/Documents/LN-Model'):
        """
        
        Find the git repo version info.
        
        .. note:: not currently in use.
        
        """
        
        self.GitRepo = git.Repo(WorkingDir)


    def AddGitVersion(self, NeuronName, Action, GitDir = './dist'):
        """
        
        Add git version ot the database.
        
        :param NeuronName: name of the neuron that is being altered.
        :type NeuronName: str
        :param Action: description of what is being done to the neuron.
        :type Action: str
        
        :returns: add a child to the git section of database for a given neuron.
        
        .. todo:: 
           * Generalize, change NeuronName to node.
           
        """
        
        GitDat = open(GitDir + '/gitInfo.txt', 'r')
       
        if self.Exists('git', NeuronName) == False:

            self.CreateGroup('git', NeuronName)

        dat = np.array([], dtype = str)
        for line in GitDat:

            dat = np.append(dat, str(line) )
            
        dat = np.append(dat, dt.datetime.utcnow().ctime() )
        
        self.AddData2Database(Action, dat, NeuronName + '.git')
        
                

    def CloseDatabase(self, PRINT = 0):
        """
        
        Close a database.
        
        :param PRINT: choose whether to print a message or not.
                     0 = Yes \n
                     1 = No \n
        :type PRINT: int
        
        """
        self.file.close()
        if PRINT == 0:
            print "database closed"

class DatabaseError(Exception):
    """
    A simple class for raising database specific errors.
    
    See here for more on errors: http://docs.python.org/2/tutorial/errors.html
    
    .. todo:: 
       * incorporate DatabaseError into more of Database class
       
    """
    def __init__(self, value):
        
        self.value = value
        
    def __str__(self):
        
        return repr(self.value)
        
        