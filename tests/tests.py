# -*- coding: utf-8 -*-
import dbase as db
import numpy as np
import os 
import unittest

# make sure old test database is not present:
try:
    os.unlink('tester.h5')
except (WindowsError, IOError):
    print 'no tester.h5 file found'
    
class TestH5pyDBase(unittest.TestCase):

    def setUp(self):

        self.dbase = db.Database()
        self.dbase.CreateDatabase('tester')
        #self.dbase.CloseDatabase()        
        #self.dbase.OpenDatabase('tester.h5')

    def test_Group(self):

        self.dbase.CreateGroup('firstLayer')

    def test_DataEnter(self):
        
        dat = np.arange(0, 1000)
        self.dbase.AddData2Database('firstData', dat, ['firstLayer'], 
                                    True)
        self.assertTrue(np.all(dat ==
                            self.dbase.file['firstLayer']['firstData'].value))

    def test_AddGit(self):
        
        self.dbase.AddGitVersion('firstData', 'added some data')
        self.assertTrue(self.dbase.Exists('added some data',['git/firstData']))

    def test_RiekeImport(self):
        
        self.dbase.OpenMatlabData('epoch000', 'tests/TestData')
        self.assertTrue(len(self.dbase.NeuronData.keys()) > 0)
        
        self.dbase.getAllFiles('tests/TestData')
        self.assertTrue(len(self.dbase.DirFiles) == 5)

        self.dbase.ImportDataFromRiekeLab('epoch000', 'tests/TestNeuron')
        self.assertEquals(8000, self.dbase.QueryDatabase('sampleRate', 
                                            ['tests', 'TestNeuron', 
                                             'epoch000']))
        
        self.dbase.ImportAllData('SecondTest', 'tests/TestData')
        self.assertEqual(8000, self.dbase.QueryDatabase('sampleRate',
                                            ['SecondTest', 
                                             'epoch004']))

    def test_DeleteData(self):
        
        self.dbase.ImportAllData('ThirdTest', 'tests/TestData')
        self.assertTrue(self.dbase.Exists('ThirdTest'))       
        #self.dbase.DeleteData('ThirdTest', option=1)
        #print 'delete', self.dbase.Exists('ThirdTest')
        self.assertTrue(self.dbase.Exists('ThirdTest'))
        
                                                               
    def tearDown(self):
        self.dbase.CloseDatabase(PRINT=1)
        
if __name__ == '__main__':
    unittest.main()