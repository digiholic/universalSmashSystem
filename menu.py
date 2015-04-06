import settingsManager
import pygame
from pygame.locals import *
import main

def main():
    settings = settingsManager.getSetting().setting
    
    pygame.init()
    screen = pygame.display.set_mode((settings['windowSize'][0], settings['windowSize'][1]))
    pygame.display.set_caption(settings['windowName'])
    
    clock = pygame.time.Clock()
    
    currentSubmenu = StartScreen()
    
    while 1:
        for event in pygame.event.get():
            pass
                               
        screen.fill([100, 100, 100])
              
        clock.tick(60)    
        pygame.display.flip()

class SubMenu():
    def __init__(self):
        self.submenus = []
        self.menuOptions = None
        
    def update(self):
        pass
    
    def changeSubmenu(self, new):
        pass
    
class StartScreen(SubMenu):
    def __init__(self):
        SubMenu.__init__(self)
        
    def update(self):
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                self.changeSubmenu(MainMenu())
                
class MainMenu(SubMenu):
    def update(self):
        SubMenu.update(self)
if __name__  == '__main__': main()