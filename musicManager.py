import pygame
import random
import settingsManager

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

class musicManager():
    def __init__(self):
        self.musicDict = {}
        self.currentMusic = None
        
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
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1)
                return
            
    def stopMusic(self,time=0):
        if self.currentMusic != None:
            pygame.mixer.music.fadeout(time)
            self.currentMusic = None
    
    def isPlaying(self):
        return pygame.mixer.music.get_busy()