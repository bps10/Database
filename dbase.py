# -*- coding: utf-8 -*-
from scipy.io import loadmat
import numpy as np
import glob as glob
import h5py as h5
#import os
import datetime as dt

class Database():
    """
    A class for working with an HDF5 database.
    Utilizes the h5py library.

    """
    def __init__(self):
        """

        .. note::
           Not currently doing anything

        """
        pass

    def _formatParents(self, Parents):
        if not isinstance(Parents, basestring):
            loc = ''
            for parent in Parents:
                loc += '/' + parent
            parentTree = loc + '/'
            return parentTree
        else:
            raise DatabaseError('Parents must be a python list.')
                
    def AddData2Database(self, DataName, Data, Parents=None, 
                         comp=True):
        """

        Add numpy data to current database.

        :param DataName: name of data being entered.
        :type DataName: str
        :param Data: data to be entered.
        :type Data: np.array
        :param GroupName: provide the location in the open database to store \
        the new data.
        :type param: str
        :param Parents: provide name of parents if they exist. 
        :type Parents: list of strings


        """
        
        if Parents is None:
            name = '/' + DataName

        else:
            name = self._formatParents(Parents) + DataName
        
        if comp:
            self.file.create_dataset(name, data=Data, dtype=Data.dtype,
                                          fletcher32=True, compression='gzip', 
                                          compression_opts=4)
        if not comp:
            self.file.create_dataset(name, data=Data, dtype=float)  
        
        self.file.flush()

    def AddGitVersion(self, DataName, Action, GitDir=None):
        """

        Add git version to the database.

        :param DataName: name of the neuron that is being altered.
        :type DataName: str
        :param Action: description of what is being done to the data.
        :type Action: str

        :returns: add a child to the git section of database for a given
            neuron.

        .. todo::
           * Generalize, change NeuronName to node.

        """
        if GitDir == None:
            GitDat = open('.git/Logs/HEAD', 'r')
            
        if GitDat == []:        
            GitDat = open('dist/gitInfo.txt', 'r')
            
        if self.Exists('git') is False:
            
            self.CreateGroup('git')    

        if self.Exists(DataName, ['git']) is False:

            self.CreateGroup(DataName, ['git'])

        dat = np.array([], dtype=str)
        for line in GitDat:
                dat = np.append(dat, str(line))

        dat = np.append(dat, dt.datetime.utcnow().ctime())

        self.AddData2Database(Action, dat, ['git', DataName])

    def CloseDatabase(self, PRINT=0):
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
                      
    def CreateDatabase(self, FileName):
        """

        Create a new HDF5 database.

        :param FileName:    provide a name for a new HDF5 database. \
                            **DO NOT** \
                            include .h5 at the end - h5 suffix is \
                            automatically appended.
        :type FileName: str

        :returns: creates a new HDF5 database.

        """
        self.file = h5.File(FileName + '.h5', mode="w")                                               

    def CreateGroup(self, GroupName, Parent=None):
        """
        Create a group in an HDF5 database.

        :param GroupName: provide a name for the group.
        :type GroupName: str
        :param Parent: provide names of parent nodes if they exist.
        :type Parent: str

        :returns: updates HDF5 database with new group.

        """
        if Parent is None:

            self.file.create_group('/' + GroupName)

        else:
            parents = self._formatParents(Parent)
            self.file.create_group('/' + parents + GroupName)

    def Exists(self, FILE, Parents=None):
        """

        Check if a file exists.

        :param FILE: pass a file name to see if it exists.
        :type FILE: str
        :param parent: parent nodes.  Must be a list.
        :type parent: str

        :returns: True or False
        :rtype: bool

        """

        if Parents == None:
            TF = self.file.__contains__(FILE)

        else:
            parents = self._formatParents(Parents)
            TF = self.file[parents].__contains__(FILE)

        return TF
        
    def getAllFiles(self, Directory, suffix='.mat', subdirectories=0):
        self.DirFiles = getAllFiles(Directory, suffix, subdirectories)

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
        
    def ImportAllData(self, NeuronName, Directory, GitDirectory=None,
            progBar=0):
        """This one calls ImportDataFromRiekeLab to load a Rieke lab .mat file or
        ImportHDF5 to import data from another H5 file depending on the file
        ending.

        """

        #if GitDirectory is None:
        #    GitDirectory = os.getcwd()

        print 'Importing data, please wait ... '

        self.getAllFiles(Directory)
        self.CreateGroup(NeuronName)

        for i in range(0, self.DirFiles.shape[0]):

            FileName = self.DirFiles[i][-12:-4]

            self.OpenMatlabData(FileName, Directory)
            self.ImportDataFromRiekeLab(FileName, NeuronName)

        self.AddGitVersion(NeuronName, NeuronName + '_InitialImport',
                GitDirectory)
        self.file.flush()
        #self.CloseDatabase()

    def ImportDataFromRiekeLab(self, FileName, DataName):
        """
        This is the big one for importing data.

        :param FileName: name of the file to import.
        :type FileName: str
        :param NeuronName: name of the neuron importing.
        :type NeuronName: str

        :returns: updated HDF5 database.

        """

        self.CreateGroup(FileName, [DataName])

        ## Get meta data.
        
        try:
            self.AddData2Database('fileComment',
                np.array([self.NeuronData['fileComment'][0]], dtype=str),
                                  [DataName, FileName])
        except (IndexError, ValueError):
            self.AddData2Database('fileComment', np.array(['none entered'],
              dtype=str), [DataName, FileName])

        PARAMS = np.array(['binRate', 'numSegments', 'si', 'clockstep',
                'sampleInterval', 'sampleRate', 'ampMode', 'ampGain',
                'rawData', 'monitorData', 'frameRate', 'preSamples',
                'postSamples', 'stimSamples', 'time', 'epochsize',
                'subThreshold', 'spikes', 'spikeTimes', 'recordingMode',
                'outputClass', 'stimulusType', 'epochComment'])

        STRINGS = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 1, 1, 1, 1])

        for i, name in enumerate(PARAMS):

            try:
                if name != 'spikeTimes':

                    try:

                        Data = self.NeuronData['data'][name][0][0][0]

                    except ValueError:

                        Data = np.array(['none entered'], dtype=str)
                        STRINGS[i] = 0

                else:

                    try:

                        Data = self.NeuronData['data'][name][0][0][0][0][0]

                    except ValueError:
                        Data = np.array(['none entered'], dtype=str)
                        STRINGS[i] = 0

            except IndexError:

                Data = np.array(['none entered'], dtype=str)
                STRINGS[i] = 0

            if STRINGS[i] == 0:

                try:

                    self.AddData2Database(name, Data, [DataName, FileName])

                except ValueError: # for unicode cases.

                    Data = np.array(['none entered'], dtype = str)
                    STRINGS[i] = 1

            if STRINGS[i] == 1:

                self.AddData2Database(name, np.array([ Data ], dtype=str),
                                      [DataName, FileName])

        # now load the params:
        self.CreateGroup('params', [DataName, FileName] )

        PARAMS = np.array(['Xpos', 'Ypos', 'colorGammaTable', 'diameter', 
                           'epochNumber', 'flipInterval', 
                           'integratedIntensity', 'intensity',
                           'intensity_raw', 'rand_behavior', 
                           'repositoryVersion', 'screenX', 'screenY', 
                           'sequential', 'spatial_meanLevel',
                           'spatial_postpts', 'spatial_prepts', 'windowPtr', 
                           'stimClass', 'MatlabCodeDir'], dtype = str)

        STRINGS = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                            0, 0, 0, 0, 0, 0, 0, 0, 1, 1], dtype = int)
        for i, name in enumerate(PARAMS):

            try:

                Data = self.NeuronData['data']['params'][0][0][0][name][0][0]

            except ValueError:

                Data = np.array(['none entered'], dtype = str)
                STRINGS[i] = 0

            if STRINGS[i] == 0:

                try:
                    self.AddData2Database(name, Data, [DataName, FileName,
                                                       'params'])

                except ValueError:

                    Data = np.array(['none entered'], dtype = str)
                    STRINGS[i] = 1

            if STRINGS[i] == 1:

                    self.AddData2Database(name, np.array([ Data ], dtype=str),
                                    [DataName, FileName, 'params'])

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

        if Directory is None:

            self.NeuronData = loadmat(FileName + '.mat')

        else:

            self.NeuronData = loadmat(Directory + '/' + FileName + '.mat')
            
    def OpenDatabase(self, DatabaseName, PRINT=0):
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
            test = h5.is_hdf5(DatabaseName)

            if test:
                self.file = h5.File(DatabaseName, mode="a")
                if PRINT == 0:
                    print '{0} database opened'.format(DatabaseName)

            if not test:
                print '{0} does not exist'.format(DatabaseName)
                
        except IOError:
            raise DatabaseError('{0} database does not exist'.format(
                            DatabaseName))

    def QueryDatabase(self, DataName, Parent):
        """
        Query a database.

        :param DataName: name of data node
        :type DataName: str
        :param Parent: name of parent node(s)
        :type Parent: list of strings

        :returns: result of query in a numpy.array()

        """
        if Parent == None:
            parents = '/'
        else:
            parents = self._formatParents(Parent)
        return self.file[parents + DataName].value
                            
    def RemoveNeuron(self, NeuronName, option=0):
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
            decision = raw_input('Are you absolutely sure you want to \
            delete this group permenently? (y/n): ')
            if decision.lower() == 'y' or decision.lower() == 'yes':
                deleteHandle = self.file.removeNode
                deleteHandle('/' + NeuronName, recursive=1)
                self.file.flush()
                print '{0} successfully deleted'.format(NeuronName)
            else:
                print 'Ok, nothing changed.'

        if option == 1:

            deleteHandle = self.file.removeNode
            #print 'hang tight. deleting in process...'
            deleteHandle('/' + NeuronName, recursive=1)
            self.file.flush()
            
            
def getAllFiles(Directory, suffix = None, subdirectories=1):
    """

    Get a list of path names of all files in a directory.

    :param Directory: a directory.
    :type Directory: str
    :param suffix: find only files with a specific ending.
    :type suffix: str
    :param subdirectories: indicate how deep (# of directories) \
        you would like to search; 0 - 2.
    :type subdirectories: int

    :returns: a list of path names.
    :rtype: list

    e.g. subdirectories = 1: Find all files within a directory and its
    first layer of subdirectories.


    """
    if suffix is None:
        suffix = '/*'

    if subdirectories == 0:
        DirFiles = []
        for name in glob.glob(Directory + '/*' + suffix):
            DirFiles = np.append(DirFiles, name)

    if subdirectories == 1:
        DirFiles = []
        for name in glob.glob(Directory + '*/*' + suffix):
            DirFiles = np.append(DirFiles, name)

    if subdirectories == 2:
        DirFiles = []
        for name in glob.glob(Directory + '*/*/*' + suffix):
            DirFiles = np.append(DirFiles, name)  

    return DirFiles
          
          
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