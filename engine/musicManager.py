import pygame
import os
import cPickle as pickle
import settingsManager


class musicManager:
    def __init__(self):
        self.myMusic = []
        
    def createSongData(self,music):
        f = open(music.name+".tstm",'w')
        pickle.dump(music, f)
        
    def loadSongData(self,fname):
        f = open(fname + ".tstm",'r')
        ret = pickle.load(f)
        return ret
    
class songData:
    def __init__(self,path,name):
        self.music = pygame.mixer.music.load(path)
        self.name = name
        
    def play(self):
        self.music.play(-1)
        
    def stop(self):
        self.music.stop()