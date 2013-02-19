# -*- coding: utf-8 -*-
from Database import dbase as db
import numpy as np
import os 
import unittest

class TestH5pyDBase(unittest.TestCase):

    def setUp(self):
        self.dat = np.arange(0, 1000)
        
    def runTest(self):
        try:
            os.unlink('well.h5')
        except (WindowsError, IOError):
            print 'no well.h5 file found'
        self.dbase = db.Database()
        
        self.dbase.CreateDatabase('well')
        self.dbase.CloseDatabase(PRINT=0)
        self.dbase.OpenDatabase('well.h5')

        self.dbase.CreateGroup('firstLayer')
        print 'created group firstLayer'

        self.dbase.AddData2Database('firstData', self.dat, ['firstLayer'], 
                                    True)
        self.assertTrue(np.all(self.dat ==
                            self.dbase.file['firstLayer']['firstData'].value))

    
        self.dbase.AddGitVersion('firstData', 'added some data')
        self.assertTrue(self.dbase.Exists('added some data',['git/firstData']))
        
if __name__ == '__main__':
    unittest.main()