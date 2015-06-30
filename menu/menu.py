import settingsManager
import pygame
import os
from pygame.locals import *
import main
import random
import spriteManager

def main():
    settings = settingsManager.getSetting().setting
    
    pygame.init()
    screen = pygame.display.set_mode((settings['windowSize'][0], settings['windowSize'][1]))
    pygame.display.set_caption(settings['windowName'])
    
    StartScreen().executeMenu(screen)    
        

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
        self.logo = spriteManager.ImageSprite(settingsManager.createPath('sprites/logo-wip.png'))
        
        self.status = 0
        self.rgb = [89,56,255]
        
    def update(self):
        pass
    
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        while self.status == 0:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    print "keydown"
                if event.type == QUIT:
                    self.status = -1
            
            color = random.randint(0,2)
            self.rgb[color] += (random.randint(0,2) - 1)
            if self.rgb[color] > 255: self.rgb[color] = 255
            elif self.rgb[color] < 0: self.rgb[color] = 0
                                               
            screen.fill(self.rgb)
            self.logo.draw(screen, (0,0), 1.0)
            
            clock.tick(60)    
            pygame.display.flip()
            
class MainMenu(SubMenu):
    def __init__(self):
        SubMenu.__init__(self)
        self.submenus = [PlayGameMenu(), OptionsMenu(), ModulesMenu()]
    def update(self):
        SubMenu.update(self)
        
class PlayGameMenu(SubMenu):
    pass

""" Options Screen and related Submenus """
class OptionsMenu(SubMenu):
    pass

class ControlsMenu(SubMenu):
    pass

class GraphicsMenu(SubMenu):
    pass

class SoundMenu(SubMenu):
    pass

class GameSettingsMenu(SubMenu):
    pass

""" Modules and related Submenus """
class ModulesMenu(SubMenu):
    pass

class FighterModules(SubMenu):
    pass

class StageModules(SubMenu):
    pass

class MusicModules(SubMenu):
    pass


class MenuButton():
    def __init__(self,root,destination,text,prevItem = None, nextItem = None):
        self.root = root
        self.destination = destination
        self.inactiveSprite = None
        self.activeSprite = None
        self.nextItem = nextItem
        self.prevItem = prevItem
        
    def onClick(self):
        self.root.changeSubmenu(self.destination)
    
class MenuButtonSprite(spriteManager.ImageSprite):
    def __init__(self, image, topleft, colorKey=[255, 255, 255], generateAlpha=True, filepath=__file__):
        spriteManager.ImageSprite.__init__(self, filepath)
        
        
if __name__  == '__main__': main()