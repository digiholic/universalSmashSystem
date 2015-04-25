import pygame
import os
import cPickle as pickle
import settingsManager


class MusicManager:
    def __init__(self,directory):
        self.myMusic = []
        self.directory = settingsManager.createPath(directory)
    
    def createSongData(self,path,name,prob):
        song = SongData(path,name,prob)
        self.saveSongData(song)
        
    def saveSongData(self,music):
        f = open(os.path.join(self.directory,music.name+".tstm"),'wb')
        pickle.dump(music, f)
        
    def loadSongData(self,fname):
        f = open(os.path.join(self.directory,fname+".tstm"),'rb')
        ret = pickle.load(f)
        return ret
    
class SongData:
    def __init__(self,path,name, prob):
        self.music = path
        self.name = name
        self.probability = prob
        pygame.mixer.init()
        
    def play(self):
        pygame.mixer.music.load(self.music)
        pygame.mixer.music.play()
        
    def stop(self):
        pygame.mixer.music.stop()

def test():
    musicManager = MusicManager("music")
    musicManager.createSongData(settingsManager.createPath("music\\The Void - Lost Language (Original Edit).ogg"), "The Void - Lost Language (NCS Release)",100)
    song = musicManager.loadSongData("The Void - Lost Language (NCS Release)")
    pygame.init()
    pygame.mixer.init()
    
    song.play()
    
    screen = pygame.display.set_mode([640,480])
    pygame.display.set_caption("USS Sprite Viewer")
    
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: song.stop()
            
        screen.fill([100, 100, 100])
        pygame.display.flip()
        
if __name__  == '__main__': test()      