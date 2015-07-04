import pygame
import random

"""
The Music Manager is an object that is meant to store the list of music
for a stage or menu with the chances and display name, as well as
rolling for those chances.
"""

class musicManager():
    def __init__(self,musicList=[],repeat=True):
        self.musicList = musicList
        self.repeat = repeat
        self.currentMusic = None
        
    def getTotalChance(self):
        totalChance = 0
        for path, chance, name in self.musicList:
            totalChance += chance
        return totalChance
    
    def rollMusic(self):
        roll = random.randint(0,self.getTotalChance())
        print roll, self.getTotalChance()
        for path, chance, name in self.musicList:
            roll -= chance
            if roll <= 0:
                self.currentMusic = (path,chance,name)
                pygame.mixer.music.load(path)
                pygame.mixer.music.play(-1)
                return