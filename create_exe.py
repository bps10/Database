

# -*- coding: utf-8 -*-
#
# Copyright © 2011 Pierre Raybaut
# Licensed under the terms of the MIT License
# (see spyderlib/__init__.py for details)

"""Create a stand-alone executable"""

try:
    from guidata.disthelpers import Distribution
except ImportError:
    raise ImportError, "This script requires guidata 1.4+"

import spyderlib
import git as git

Info = git.Repo()

dat = []
for i in range(0,5):

    dat.append( Info.head.log()[-1][:][i] )

thefile = open('gitInfo.txt', 'w')
thelist = dat
for item in thelist:
    thefile.write('{0} \n'.format(item))
thefile.close()
    
def create_executable():
    """Build executable using ``guidata.disthelpers``"""
    dist = Distribution()
    dist.setup(name="Database", version="1.1",
               description=u"HDF5 database in a gui shell",
               script="guiMain.pyw", target_name="Database.exe")
               
    spyderlib.add_to_distribution(dist)
    dist.add_data_file('gitInfo.txt')
    dist.add_modules('guidata')
    dist.add_modules('guiqwt')
    dist.add_modules('scipy.io')
    dist.add_modules('spyderlib')
    dist.excludes += ['IPython']
    # Building executable
    dist.build('cx_Freeze')


if __name__ == '__main__':
    create_executable()
