# -*- coding: utf-8 -*-
"""
Created on Sat Oct 27 15:34:23 2012

@author: Brian
"""

from distutils.core import setup
import py2exe # Patching distutils setup
from guidata.disthelpers import (remove_build_dist, get_default_excludes,
                         get_default_dll_excludes, create_vs2008_data_files,
                         add_modules)

# Removing old build/dist folders
remove_build_dist()

# Including/excluding DLLs and Python modules
EXCLUDES = get_default_excludes()
INCLUDES = []
DLL_EXCLUDES = get_default_dll_excludes()
DATA_FILES = create_vs2008_data_files()

# Configuring/including Python modules
add_modules(('PyQt4', 'guidata', 'guiqwt', 'numpy','Database', 'sys'), DATA_FILES, INCLUDES, EXCLUDES)

setup(
      options={
               "py2exe": {"compressed": 2, "optimize": 2, 'bundle_files': 1,
                          "includes": INCLUDES, "excludes": EXCLUDES,
                          "dll_excludes": DLL_EXCLUDES,
                          "dist_dir": "dist",},
               },
      data_files=DATA_FILES,
      windows=[{
                "script": "simpledialog.pyw",
                "dest_base": "simpledialog",
                "version": "1.0.0",
                "company_name": u"CEA",
                "copyright": u"Copyright © 2012",
                "name": "Database",
                "description": "Simple GUI",
                },],
      zipfile = None,
      )