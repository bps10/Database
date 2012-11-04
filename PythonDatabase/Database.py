#import scipy as sp
from scipy.io import loadmat
import numpy as np
import glob as glob
import git as git
import tables as tables
import os

class Database():

    def __init__(self):
        pass

    def CreateGroup(self, GroupName, Parent = None):
        
        if Parent == None:

            self.group = self.file.createGroup("/", GroupName, GroupName)
        
        else :
            self.group = self.file.createGroup( ("/" + Parent), GroupName, GroupName)



    def CreateDatabase(self, FileName):
        
        self.file = tables.openFile(FileName + '.h5', mode = "w", title = 'NeuronAnalysis')


    def AddData2Database(self, DataName, Data, GroupName, Parents = None):
        
        if Parents == None:
            loc = 'self.file.root.' + GroupName 

        else :
            loc = 'self.file.root.' + GroupName
            for name in Parents:
                loc += '.' + Parents
        
        atom = tables.Atom.from_dtype(Data.dtype)
        ds = self.file.createCArray(eval(loc), DataName, atom, Data.shape)
        ds[:] = Data


    def OpenDatabase(self, DatabaseName):
        
        self.file = tables.openFile(DatabaseName + '.h5', mode = "a")
        print '{0} database opened'.format(DatabaseName)


    def QueryDatabase(self, NeuronName, GroupName, DataName):
        
        
        loc = 'self.file.root.' + NeuronName + '.' + GroupName + '.' + DataName + '.read()'
        return eval(loc)


    def RemoveNeuron(self, NeuronName):
        	
        decision = raw_input( 'Are you absolutely sure you want to delete this group permenently? (y/n): ')
        if decision.lower() == 'y' or decision.lower() == 'yes':
            deleteHandle = self.file.removeNode
            deleteHandle( '/' + NeuronName, recursive=1)
            print '{0} successfully deleted'.format(NeuronName)
        else:
            print 'Ok, nothing changed.'


    def RemoveChild(self, GroupName, ChildName):
        	
        decision = raw_input( 'Are you absolutely sure you want to delete this child permenently? (y/n): ')
        if decision.lower() == 'y' or decision.lower() == 'yes':
            eval('self.file.root.' + GroupName + '.' + ChildName + '._f_remove()')
            print '{0} successfully deleted'.format(ChildName)
        
        else:

            print 'Ok, nothing changed.'
     

    def OpenMatlabData(self, FileName, Directory, NeuronName):

        if Directory == None:
            
            self.NeuronData = loadmat(Directory + '/' + FileName + '.mat' )
        
        else:
            
            self.NeuronData = loadmat(Directory + '/' + FileName + '.mat')

    def getAllFiles(self, Directory, suffix = None, subdirectories = 1):
        """
        subdirectories = 1: Find all files within a directory and its first layer of subdirectories.
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



    def ImportAllData(self, NeuronName, Directory, GitDirectory = None):
        
        if GitDirectory == None:
            GitDirectory = os.getcwd()
            
        #self.OpenDatabase(Name + '.h5')
        self.getAllFiles(Directory)
        self.CreateGroup(NeuronName)

        for i in range(0, self.DirFiles.shape[0] ):
            
            print 'Importing data, please wait ... '

            FileName = self.DirFiles[i][-12:-4]  # select only 'epochXXX.mat'

            self.OpenMatlabData(FileName, Directory, NeuronName)
            self.ImportDataFromMatlab(FileName, NeuronName)

        self.AddGitVersion(NeuronName, NeuronName + '_InitialImport', GitDirectory)
        self.file.flush()
        self.CloseDatabase()



    def ImportDataFromMatlab(self, FileName, NeuronName):
        
        self.CreateGroup(FileName, NeuronName)

        ## Get meta data.
        
        try :
            self.AddData2Database('fileComment', np.array([self.NeuronData['fileComment'][0]],dtype=str), 
                                  NeuronName + '.' + FileName)
        except IndexError:
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
                
                    self.AddData2Database(name, np.array([ Data ], dtype=str), 
                                              NeuronName + '.' + FileName)
                                              
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

                    self.AddData2Database(name, Data, NeuronName + '.' + FileName + '.params')

            if STRINGS[i] == 1:

                    self.AddData2Database(name, np.array([ Data ], dtype=str), NeuronName + '.' + FileName + '.params')


    def GetChildList(self, FILE = None, parent = None):
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
        
        if parent == None:
            TF = self.file.root.__contains__(FILE)
        
        else:
            foo = 'self.file.root.' + parent 
            TF = foo.__contains__( FILE)
        return TF


    def GetGitRepo(self, WorkingDir = '/Users/Brian/Documents/LN-Model'):

        self.GitRepo = git.Repo(WorkingDir)


    def AddGitVersion(self, NeuronName, Action, GitDirectory):

        self.GetGitRepo(WorkingDir = GitDirectory)
       
        if self.Exists('git', NeuronName) == False:

            self.CreateGroup('git', NeuronName)

        dat = np.array([], dtype = str)
        for i in range(0,5):

            dat = np.append(dat, str(self.GitRepo.head.log()[-1][:][i]) )

        self.AddData2Database(Action, dat, NeuronName + '.git')
        
                

    def CloseDatabase(self):
        
        self.file.close()
        print "database closed"
