# -*- coding: utf-8 -*-
import dbase as db
import numpy as np
import os 
import unittest

# make sure old test database is not present:
try:
    os.unlink('tests/tester.h5')
    
except (WindowsError, IOError):
    print 'no tests/tester.h5 file found'
h = db.Database()
h.CreateDatabase('tests/tester')
h.CloseDatabase()    

class TestDBwrapper(unittest.TestCase):

    def setUp(self):

        self.dbase = db.Database()
        #self.dbase.CreateDatabase('tests/tester')
        self.dbase.OpenDatabase('tests/tester.h5', 1)

    def test_AddGit(self):
        
        self.dbase.AddGitVersion('firstData', 'added some data')
        self.assertTrue(self.dbase.Exists('added some data',['git/firstData']))
        
    def test_DataEnter(self):
        
        dat = np.arange(0, 1000)
        self.dbase.CreateGroup('firstLayer')
        self.dbase.AddData2Database('firstData', dat, ['firstLayer'], 
                                    True)
        self.assertTrue(np.all(dat ==
                            self.dbase.file['firstLayer']['firstData'].value))

    def test_HDF5Import(self):
        
        self.dbase.ImportAllData('symphTest', 'tests')
        self.assertTrue(self.dbase.Exists('symphTest'))
        
        
    def test_RiekeImport(self):

        self.dbase.ImportAllData('RiekeTest', 'tests/TestData')
        self.assertEqual(8000, self.dbase.QueryDatabase('sampleRate',
                                            ['RiekeTest', 
                                             'epoch004']))
                                             
    def test_RiekeTestDelete(self):
        
        self.dbase.DeleteData('RiekeTest', option=1)
        self.assertFalse(self.dbase.Exists('RiekeTest'))
                                                               
    def tearDown(self):
        self.dbase.CloseDatabase(PRINT=1)
        
        
if __name__ == '__main__':
    unittest.main()