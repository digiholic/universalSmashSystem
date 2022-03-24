import pygame
import random
import settingsManager
import _thread as thread

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
        self.music_dict = {}
        self.current_music = None
        self.path_index = -1
        
    def createMusicSet(self,setName,music_list):
        self.music_dict[setName] = music_list
    
    def getTotalChance(self,setName):
        music_list = self.music_dict[setName]
        total_chance = 0
        for path, chance, name in music_list:
            total_chance += chance
        return total_chance
    
    def rollMusic(self,setName):
        music_list = self.music_dict[setName]
        roll = random.randint(0,self.getTotalChance(setName))
        print(roll, self.getTotalChance(setName))
        for path, chance, name in music_list:
            roll -= chance
            if roll <= 0:
                pygame.mixer.music.set_volume(settingsManager.getSetting('music_volume'))
                self.current_music = (path,chance,name)
                if isinstance(path, list):
                    self.path_index = 0
                    pygame.mixer.music.load(path[0])
                    pygame.mixer.music.play(0)
                else:
                    self.path_index = -1
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play(-1)
                return

    def doMusicEvent(self):
        if self.current_music != None and self.path_index > -1:
            path = self.current_music[0]
            if isinstance(path, list):
                if pygame.event.peek(SONG_ENDED):
                    self.advanceSong()

    def advanceSong(self):
        path = self.current_music[0]
        self.path_index = self.path_index + 1
        if self.path_index == len(path):
            if path[self.path_index] != None:
                pygame.mixer.music.load(path[self.path_index])
                pygame.mixer.music.play(-1)
            else:
                self.path_index = -1
        else:
            pygame.mixer.music.load(path[self.path_index])
            pygame.mixer.music.play()
                        
    def stopMusic(self,_time=0):
        if self.current_music != None:
            pygame.mixer.music.fadeout(_time)
            self.current_music = None
            self.path_index = -1
    
    def isPlaying(self):
        return pygame.mixer.music.get_busy() or (self.current_music != None and self.path_index > -1)
