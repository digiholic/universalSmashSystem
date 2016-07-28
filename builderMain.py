#!/usr/bin/env python
import builder.builderWindow
import sys

def Main():
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
        
    builder.builderWindow.MainFrame()
    
if __name__=='__main__': Main()
