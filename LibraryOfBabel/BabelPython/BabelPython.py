from __future__ import division
import scipy as sp
import scipy.io as sio
import numpy as np
import git as git
import tables as tables


class Database():

    def __init__(self):
        self = None

    def CreateGroup(self, GroupName):
        
        self.group = self.file.createGroup("/", GroupName,'Neuron')


    def CreateDatabase(self, FileName):
        
        self.file = tables.openFile(FileName, mode = "w", title = 'NeuronData')

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

    def AddMetaData(self, metadata):
        
        self.file.attrs.content_type = 'text/plain; charset=us-ascii'
        
    def ImportDataFromMatlab(self, Database, FileName, Directory):

        NeuronData = sio.loadmat(Directory + FileName)

        self.OpenDatabase(Database + '.h5')

        ## Get meta data.
        #Database.CreateGroup('Info')

        DBase.AddData2Database('binRate', NeuronData['data']['binRate'][0][0][0]        , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['ouputClass'][0][0][0]     , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['stimulusType'][0][0][0]   , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['numSegments'][0][0][0]    , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['si'][0][0][0]             , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['clockstep'][0][0][0]      , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['sampleInterval'][0][0][0] , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['sampleRate'][0][0][0]     , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['ampMode'][0][0][0]        , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['ampGain'][0][0][0]        , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['rawData'][0][0][0]        , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['params'][0][0][0]         , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['monitorData'][0][0][0]    , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['frameRate'][0][0][0]      , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['preSamples'][0][0][0]     , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['postSampoles'][0][0][0]   , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['stimSamples'][0][0][0]    , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['time'][0][0][0]           , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['epochSize'][0][0][0]      , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['recordingMode'][0][0][0]  , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['subThreshold'][0][0][0]   , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['spikes'][0][0][0]         , 'DataFromMatlab')
        DBase.AddData2Database('binRate', NeuronData['data']['spikeTimes'][0][0][0]     , 'DataFromMatlab')

        ## Finally add 'epochComment' to meta data.

    def CloseDatabase(self):
        
        self.file.close()
        print "database closed"