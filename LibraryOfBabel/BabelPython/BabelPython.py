#import scipy as sp
import scipy.io as sio
import numpy as np
import glob as glob
import git as git
import tables as tables


class Database():

    def __init__(self):
        self = None


    def CreateGroup(self, GroupName, Parent = None):
        
        if Parent == None:

            self.group = self.file.createGroup("/", GroupName, GroupName)
        
        else :
            self.group = self.file.createGroup( ("/" + Parent), GroupName, GroupName)



    def CreateDatabase(self, FileName):
        
        self.file = tables.openFile(FileName, mode = "w", title = 'NeuronAnalysis')


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
        
        self.file = tables.openFile(DatabaseName, mode = "a")
        print '{0} database opened'.format(DatabaseName)


    def QueryDatabase(self, GroupName, DataName):
        
        loc = 'self.file.root.' + GroupName + '.' + DataName + '.read()'
        return eval(loc)


    def RemoveGroup(self, GroupName):
        	
        decision = raw_input( 'Are you absolutely sure you want to delete this group permenently? (y/n): ')
        if decision.lower() == 'y' or decision.lower() == 'yes':
            eval('self.file.root.' + GroupName + '._f_remove()')
            print '{0} successfully deleted'.format(GroupName)
        else:
            print 'Ok, nothing changed.'


    def RemoveChild(self, GroupName, ChildName):
        	
        decision = raw_input( 'Are you absolutely sure you want to delete this child permenently? (y/n): ')
        if decision.lower() == 'y' or decision.lower() == 'yes':
            eval('self.file.root.' + GroupName + '.' + ChildName + '._f_remove()')
            print '{0} successfully deleted'.format(ChildName)
        
        else:

            print 'Ok, nothing changed.'
     

    def OpenMatlabData(self, FileName, Directory):

        self.NeuronData = sio.loadmat(Directory + '/' + FileName + '.mat' )


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



    def ImportAllData(self, Name, Directory = None):

        self.CreateDatabase(Name + '.h5')
        self.getAllFiles(Name)
        self.CreateGroup(Name)

        for i in range(0, self.DirFiles.shape[0] ):
            FileName = self.DirFiles[i][-12:-4] # select only 'epochXXX.mat'

            self.OpenMatlabData(FileName, Name)
            self.ImportDataFromMatlab(FileName, Name)

        self.AddGitVersion('InitialImport')
        self.CloseDatabase()



    def ImportDataFromMatlab(self, FileName, Directory):
        
        self.CreateGroup(FileName, Directory)

        

        ## Get meta data.

        self.AddData2Database('fileComment', np.array([self.NeuronData['fileComment'][0]],dtype=str), Directory + '.' + FileName)

        PARAMS = np.array(['binRate', 'numSegments', 'si', 'clockstep', 'sampleInterval', 'sampleRate', 'ampMode', 'ampGain',
                           'rawData', 'monitorData', 'frameRate', 'preSamples', 'postSamples', 'stimSamples', 'time', 'epochsize',
                           'subThreshold', 'spikes', 'spikeTimes', 'recordingMode', 'outputClass', 'stimulusType', 'epochComment'])

        STRINGS = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1])

        for i, name in enumerate(PARAMS):

            try:
                if name != 'spikeTimes':
                    Data = self.NeuronData['data'][name][0][0][0]
                else:
                    Data = self.NeuronData['data'][name][0][0][0][0][0]
                    if Data.shape[0] == 0:
                        Data = np.array(['none entered'], dtype = str)
                        STRINGS[i] = 0

            except:

                Data = np.array(['none entered'], dtype = str)
                STRINGS[i] = 0

            if STRINGS[i] == 0:
 
                self.AddData2Database(name, Data, Directory + '.' + FileName)

            if STRINGS[i] == 1:

                self.AddData2Database(name, np.array([ Data ], dtype=str), Directory + '.' + FileName)

        # now load the params:
        self.CreateGroup('params', Directory + '/' + FileName )

        PARAMS = np.array(['Xpos', 'Ypos', 'colorGammaTable', 'diameter', 'epochNumber', 'flipInterval', 'integratedIntensity', 'intensity',
                  'intensity_raw', 'rand_behavior', 'repositoryVersion', 'screenX', 'screenY', 'sequential', 'spatial_meanLevel',
                  'spatial_postpts', 'spatial_prepts', 'windowPtr', 'stimClass', 'MatlabCodeDir'], dtype = str)

        STRINGS = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1], dtype = int)
        for i, name in enumerate(PARAMS):

            try:
                Data = self.NeuronData['data']['params'][0][0][0][name][0][0]
            except:
                Data = np.array(['none entered'], dtype = str)
                STRINGS[i] = 0

            if STRINGS[i] == 0:

                    self.AddData2Database(name, Data, Directory + '.' + FileName + '.params')

            if STRINGS[i] == 1:

                    self.AddData2Database(name, np.array([ Data ], dtype=str), Directory + '.' + FileName + '.params')
 
                          
    def Exists(self, FILE):
        
        TF = self.file.__contains__('/' + FILE)
        return TF


    def GetGitRepo(self, WorkingDir = '/Users/Brian/Documents/Database'):

        self.GitRepo = git.Repo(WorkingDir)


    def AddGitVersion(self, Action):

        self.GetGitRepo
       
        if self.Exists('git') == False:

            self.CreateGroup('git')

        dat = np.array([], dtype = str)
        for i in range(0,5):

            dat = np.append(dat, str(GitRepo.head.log()[-1][:][i]) )

        self.AddData2Database(Action, dat, 'git')
        
                

    def CloseDatabase(self):
        
        self.file.close()
        print "database closed"

#Db = Database()
#Db.ImportAllData('Oct0212Bc8')