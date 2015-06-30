import settingsManager
import pygame
import os
from pygame.locals import *
import main
import random
import math

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
        self.status = 0
        
        
    def update(self,screen):
        pass
    
    def executeMenu(self,screen):
        pass
    
class StartScreen(SubMenu):
    def __init__(self):
        SubMenu.__init__(self)
        self.logo = spriteManager.ImageSprite(settingsManager.createPath('sprites/logo-wip.png'))
        
        self.start = spriteManager.TextSprite('PRESS START','full Pack 2025',18)
        self.start.rect.midbottom = (settingsManager.getSetting('windowSize')[0] / 2, 360)
        self.startAlpha = 144
        self.alphaRad = 0
        
        self.rgb = [89,56,255]
        
    def update(self,screen):
        color = random.randint(0,2)
        self.rgb[color] += (random.randint(0,2) - 1)
        if self.rgb[color] > 255: self.rgb[color] = 255
        elif self.rgb[color] < 0: self.rgb[color] = 0
            
        # Math is cool! Ease in, ease out fade done with a sin.
        self.startAlpha = 127 * math.sin(self.alphaRad) + 128
        self.alphaRad += 0.05
        self.start.alpha(self.startAlpha)
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        while self.status == 0:
            self.update(screen)
            
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.status = 1
                    else:
                        retValue = MainMenu().executeMenu(screen)
                        if retValue == -1: self.status = -1
                    
                if event.type == QUIT:
                    self.status = -1
                                            
            screen.fill(self.rgb)
            self.logo.draw(screen, self.logo.rect.topleft, 1.0)
            self.start.draw(screen, self.start.rect.topleft, 1.0)
            
            clock.tick(60)    
            pygame.display.flip()
            
class MainMenu(SubMenu):
    def __init__(self):
        SubMenu.__init__(self)
        self.menuText = spriteManager.TextSprite('PRESS START','full Pack 2025',18,[255,255,255])
        
        self.rgb = [0,0,0]
        
        
    def update(self,screen):
        pass
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        while self.status == 0:
            self.update(screen)
            
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    print "keydown"
                    if event.key == K_ESCAPE:
                        self.status = 1
                if event.type == QUIT:
                    self.status = -1
            
            screen.fill(self.rgb)
            
            self.menuText.draw(screen, (128,128), 1.0)
            clock.tick(60)    
            pygame.display.flip()
            
    
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