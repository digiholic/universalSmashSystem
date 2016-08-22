#!/usr/bin/env python
from __future__ import print_function
import pygame
import imp
import os
import sys
import traceback
from pygame.locals import *
from engine import *
from builder import *
from fighters import *
from menu import *
from stages import *
import menu.mainMenu


def main(debug = False):
    try:
        sys.stderr.write("\n")
        sys.stderr.flush()
    except IOError:
        class dummyStream:
            ''' dummyStream behaves like a stream but does nothing. '''
            def __init__(self): pass
            def write(self,data): pass
            def read(self,data): pass
            def flush(self): pass
            def close(self): pass
        # and now redirect all default streams to this dummyStream:
        sys.stdout = dummyStream()
        sys.stderr = open("errors.txt", "w", 0)
        sys.stdin = dummyStream()
        sys.__stdout__ = dummyStream()
        sys.__stderr__ = dummyStream()
        sys.__stdin__ = dummyStream()
    menu.mainMenu.Menu()
    
def importFromURI(filePath, uri, absl=False, _suffix=""):
    if not absl:
        uri = os.path.normpath(os.path.join(os.path.dirname(filePath).replace('main.exe',''), uri))
    path, fname = os.path.split(uri)
    mname, ext = os.path.splitext(fname)
    
    no_ext = os.path.join(path, mname)
         
    if os.path.exists(no_ext + '.py'):
        try:
            return imp.load_source((mname + suffix), no_ext + '.py')
        except Exception as e:
            print(mname, e)
        
    
if __name__  == '__main__': main(True)

