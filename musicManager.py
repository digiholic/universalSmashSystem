import pygame
import random
import settingsManager
import thread

"""
The Music Manager is an object that is meant to store the list of music
for a stage or menu with the chances and display name, as well as
rolling for those chances.
"""
music = None

def getMusicManager():
    global music
    if music == None:
        music = musicManager()
    return music

SONG_ENDED = pygame.USEREVENT + 616
pygame.mixer.music.set_endevent(SONG_ENDED)

class musicManager():
    def __init__(self):
        self.musicDict = {}
        self.currentMusic = None
        self.pathIndex = -1
        
    def createMusicSet(self,setName,musicList):
        self.musicDict[setName] = musicList
    
    def getTotalChance(self,setName):
        musicList = self.musicDict[setName]
        totalChance = 0
        for path, chance, name in musicList:
            totalChance += chance
        return totalChance
    
    def rollMusic(self,setName):
        musicList = self.musicDict[setName]
        roll = random.randint(0,self.getTotalChance(setName))
        print(roll, self.getTotalChance(setName))
        for path, chance, name in musicList:
            roll -= chance
            if roll <= 0:
                pygame.mixer.music.set_volume(settingsManager.getSetting('musicVolume'))
                self.currentMusic = (path,chance,name)
                if isinstance(path, list):
                    self.pathIndex = 0
                    pygame.mixer.music.load(path[0])
                    pygame.mixer.music.play(0)
                else:
                    self.pathIndex = -1
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play(-1)
                return

    def doMusicEvent(self):
        if self.currentMusic != None and self.pathIndex > -1:
            path = self.currentMusic[0]
            if isinstance(path, list):
                if pygame.event.peek(SONG_ENDED):
                    self.advanceSong()

    def advanceSong(self):
        path = self.currentMusic[0]
        self.pathIndex = self.pathIndex + 1
        if self.pathIndex == len(path):
            if path[self.pathIndex] != None:
                pygame.mixer.music.load(path[self.pathIndex])
                pygame.mixer.music.play(-1)
            else:
                self.pathIndex = -1
        else:
            pygame.mixer.music.load(path[self.pathIndex])
            pygame.mixer.music.play()
                        
    def stopMusic(self,time=0):
        if self.currentMusic != None:
            pygame.mixer.music.fadeout(time)
            self.currentMusic = None
            self.pathIndex = -1
    
    def isPlaying(self):
        return pygame.mixer.music.get_busy() or (self.currentMusic != None and self.pathIndex > -1)