from __future__ import division
import scipy as sp
import scipy.io as sio
import numpy as np
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


    def AddData2Database(self, DataName, Data, GroupName):
        
        loc = 'self.file.root.' + GroupName 
        
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


    def AddMetaData(self, metadata):
        
        self.file.attrs.content_type = 'text/plain; charset=us-ascii'
     

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
                self.DirFiles = np.append(files,name)
        
        if subdirectories == 1:
            self.DirFiles = []
            for name in glob.glob(Directory + '*/' + suffix):
                self.DirFiles = np.append(files,name)

        if subdirectories == 2:
            self.DirFiles = []
            for name in glob.glob(Directory + '*/*/' + suffix):
                self.DirFiles = np.append(files,name)



    def ImportAllData(self, FileName, Directory):

        self.getAllFiles(Directory)
        self.CreateGroup(Directory)

        for i in range(0, len(self.getAllFiles)):

            self.ImportDataFromMatlab(FileName, Directory)


    def ImportDataFromMatlab(self, FileName, Directory):

        self.CreateGroup(FileName, Directory)

        ## Get meta data.

        #Database.CreateGroup('Info')
        self.AddData2Database('fileComment', np.array([self.NeuronData['fileComment'][0]],dtype=str), Directory)

        self.AddData2Database('binRate',            self.NeuronData['data']['binRate'][0][0][0]        , Directory + '.' + FileName)
        self.AddData2Database('ouputClass',         self.NeuronData['data']['outputClass'][0][0][0]    , Directory + '.' + FileName)
        self.AddData2Database('stimulusType',       self.NeuronData['data']['stimulusType'][0][0][0]   , Directory + '.' + FileName)
        self.AddData2Database('numSegments',        self.NeuronData['data']['numSegments'][0][0][0]    , Directory + '.' + FileName)
        self.AddData2Database('si',                 self.NeuronData['data']['si'][0][0][0]             , Directory + '.' + FileName)
        self.AddData2Database('clockstep',          self.NeuronData['data']['clockstep'][0][0][0]      , Directory + '.' + FileName)
        self.AddData2Database('sampleInterval',     self.NeuronData['data']['sampleInterval'][0][0][0] , Directory + '.' + FileName)
        self.AddData2Database('sampleRate',         self.NeuronData['data']['sampleRate'][0][0][0]     , Directory + '.' + FileName)
        self.AddData2Database('ampMode',            self.NeuronData['data']['ampMode'][0][0][0]        , Directory + '.' + FileName)
        self.AddData2Database('ampGain',            self.NeuronData['data']['ampGain'][0][0][0]        , Directory + '.' + FileName)
        self.AddData2Database('rawData',            self.NeuronData['data']['rawData'][0][0][0]        , Directory + '.' + FileName)
        self.AddData2Database('monitorData',        self.NeuronData['data']['monitorData'][0][0][0]    , Directory + '.' + FileName)
        self.AddData2Database('frameRate',          self.NeuronData['data']['frameRate'][0][0][0]      , Directory + '.' + FileName)
        self.AddData2Database('preSamples',         self.NeuronData['data']['preSamples'][0][0][0]     , Directory + '.' + FileName)
        self.AddData2Database('postSamples',        self.NeuronData['data']['postSamples'][0][0][0]    , Directory + '.' + FileName)
        self.AddData2Database('stimSamples',        self.NeuronData['data']['stimSamples'][0][0][0]    , Directory + '.' + FileName)
        self.AddData2Database('time',               self.NeuronData['data']['time'][0][0][0]           , Directory + '.' + FileName)
        self.AddData2Database('epochSize',          self.NeuronData['data']['epochSize'][0][0][0]      , Directory + '.' + FileName)
        self.AddData2Database('recordingMode',      self.NeuronData['data']['recordingMode'][0][0][0]  , Directory + '.' + FileName)
        self.AddData2Database('subThreshold',       self.NeuronData['data']['subThreshold'][0][0][0]   , Directory + '.' + FileName)
        self.AddData2Database('spikes',             self.NeuronData['data']['spikes'][0][0][0]         , Directory + '.' + FileName)
        self.AddData2Database('spikeTimes',         self.NeuronData['data']['spikeTimes'][0][0][0]     , Directory + '.' + FileName)

        self.AddData2Database('fileComment', np.array([self.NeuronData['data']['epochComment'][0][0][0] ],dtype=str), Directory)

        # now load the params:
        self.CreateGroup('params', Directory + '/' + FileName )
        self.AddData2Database('MatlabCodeDir',          np.array([self.NeuronData['data']['params'][0][0][0]['MatlabCodeDir'][0][0]],
                                                                 dtype=str), Directory + '.' + FileName + '.params')
        self.AddData2Database('Xpos',                   self.NeuronData['data']['params'][0][0][0]['Xpos'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('Ypos',                   self.NeuronData['data']['params'][0][0][0]['Ypos'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('colorGammaTable',        self.NeuronData['data']['params'][0][0][0]['colorGammaTable'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('diameter',               self.NeuronData['data']['params'][0][0][0]['diameter'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('epochNumber',            self.NeuronData['data']['params'][0][0][0]['epochNumber'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('flipInterval',           self.NeuronData['data']['params'][0][0][0]['flipInterval'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('integratedIntensity',    self.NeuronData['data']['params'][0][0][0]['integratedIntensity'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('intensity',              self.NeuronData['data']['params'][0][0][0]['intensity'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('intensity_raw',          self.NeuronData['data']['params'][0][0][0]['intensity_raw'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('rand_behavior',          self.NeuronData['data']['params'][0][0][0]['rand_behavior'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('repositoryVersion',      self.NeuronData['data']['params'][0][0][0]['repositoryVersion'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('screenX',                self.NeuronData['data']['params'][0][0][0]['screenX'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('screenY',                self.NeuronData['data']['params'][0][0][0]['screenY'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('sequential',             self.NeuronData['data']['params'][0][0][0]['sequential'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('spatial_meanLevel',      self.NeuronData['data']['params'][0][0][0]['spatial_meanLevel'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('spatial_postpts',        self.NeuronData['data']['params'][0][0][0]['spatial_postpts'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('spatial_prepts',         self.NeuronData['data']['params'][0][0][0]['spatial_prepts'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('spatial_stimpts',        self.NeuronData['data']['params'][0][0][0]['spatial_stimpts'][0][0], 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('stimClass',              np.array([self.NeuronData['data']['params'][0][0][0]['stimClass'][0][0]],dtype=str), 
                              Directory + '.' + FileName + '.params')
        self.AddData2Database('windowPtr',              self.NeuronData['data']['params'][0][0][0]['windowPtr'][0][0], 
                              Directory + '.' + FileName + '.params')


    def CloseDatabase(self):
        
        self.file.close()
        print "database closed"