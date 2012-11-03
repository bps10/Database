# -*- coding: utf-8 -*-
"""
Created on Fri Nov 02 14:17:32 2012

@author: Brian
"""

import os, os.path
import subprocess

from distutils.core import setup
from py2exe.build_exe import py2exe

NSIS_SCRIPT_TEMPLATE = r"""
!define py2exeOutputDirectory '{output_dir}\'
!define exe '{program_name}.exe'

; Uses solid LZMA compression. Can be slow, use discretion.
SetCompressor /SOLID lzma

; Sets the title bar text (although NSIS seems to append "Installer")
Caption "{program_desc}"

Name '{program_name}'
OutFile ${{exe}}
Icon '{icon_location}'
; Use XPs styles where appropriate
XPStyle on

; You can opt for a silent install, but if your packaged app takes a long time
; to extract, users might get confused. The method used here is to show a dialog
; box with a progress bar as the installer unpacks the data.
;SilentInstall silent
AutoCloseWindow true
ShowInstDetails nevershow

Section
    DetailPrint "Extracting application..."
    SetDetailsPrint none
    
    InitPluginsDir
    SetOutPath '$PLUGINSDIR'
    File /r '${{py2exeOutputDirectory}}\*'

    GetTempFileName $0
    ;DetailPrint $0
    Delete $0
    StrCpy $0 '$0.bat'
    FileOpen $1 $0 'w'
    FileWrite $1 '@echo off$\r$\n'
    StrCpy $2 $TEMP 2
    FileWrite $1 '$2$\r$\n'
    FileWrite $1 'cd $PLUGINSDIR$\r$\n'
    FileWrite $1 '${{exe}}$\r$\n'
    FileClose $1
    ; Hide the window just before the real app launches. Otherwise you have two
    ; programs with the same icon hanging around, and it's confusing.
    HideWindow
    nsExec::Exec $0
    Delete $0
SectionEnd
"""


class NSISScript(object):
    
    NSIS_COMPILE = "makensis"
    
    def __init__(self, program_name, program_desc, dist_dir, icon_loc):
        self.program_name = program_name
        self.program_desc =  program_desc
        self.dist_dir = dist_dir
        self.icon_loc = icon_loc
        self.pathname = "setup_%s.nsi" % self.program_name
    
    def create(self):
        contents = NSIS_SCRIPT_TEMPLATE.format(
                    program_name = self.program_name,
                    program_desc = self.program_desc,
                    output_dir = self.dist_dir,
                    icon_location = os.path.join(self.dist_dir, self.icon_loc))

        with open(self.pathname, "w") as outfile:
            outfile.write(contents)

    def compile(self):
        subproc = subprocess.Popen(
            # "/P5" uses realtime priority for the LZMA compression stage.
            # This can get annoying though.
            [self.NSIS_COMPILE, self.pathname, "/P5"], env=os.environ)
        subproc.communicate()
        
        retcode = subproc.returncode
        
        if retcode:
            raise RuntimeError("NSIS compilation return code: %d" % retcode)

class build_installer(py2exe):
    # This class first builds the exe file(s), then creates an NSIS installer
    # that runs your program from a temporary directory.
    def run(self):
        # First, let py2exe do it's work.
        py2exe.run(self)

        lib_dir = self.lib_dir
        dist_dir = self.dist_dir
        
        # Create the installer, using the files py2exe has created.
        script = NSISScript(PROGRAM_NAME,
                            PROGRAM_DESC,
                            dist_dir,
                            os.path.join('path', 'to, 'my_icon.ico'))
        print "*** creating the NSIS setup script***"
        script.create()
        print "*** compiling the NSIS setup script***"
        script.compile()

zipfile = r"lib\shardlib"

setup(
    name = 'MyApp',
    description = 'My Application',
    version = '1.0',

    window = [
                {
                    'script': os.path.join('path','to','my_app.py'),
                    'icon_resources': [(1, os.path.join('path', 'to', 'my_icon.ico'))],
                    'dest_base': PROGRAM_NAME,
                },
            ]

    options = {
                  'py2exe': {
                       # Py2exe options...
                  }
              },

    zipfile = zipfile,
    data_files = # etc...
    cmdclass = {"py2exe": build_installer},
           
)