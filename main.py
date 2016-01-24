import pygame
import stages.stage
import stages.true_arena as stage
import settingsManager
import imp
import os
from menu.menu import *
from pygame.locals import *

from engine import *
from builder import *
from fighters import *
from menu import *
from stages import *

def main(debug = False):
    Menu()
    
def importFromURI(file, uri, absl=False):
    if not absl:
        uri = os.path.normpath(os.path.join(os.path.dirname(file), uri))
    path, fname = os.path.split(uri)
    mname, ext = os.path.splitext(fname)
        
    no_ext = os.path.join(path, mname)
         
    #if os.path.exists(no_ext + '.pyc'):
        #try:
            #return imp.load_compiled(mname, no_ext + '.pyc')
        #except:
            #pass
    if os.path.exists(no_ext + '.py'):
        try:
            return imp.load_source(mname, no_ext + '.py')
        except Exception as e:
            print mname, e
        
    
if __name__  == '__main__': main(True)

