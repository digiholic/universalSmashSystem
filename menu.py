import settingsManager
import pygame
from pygame.locals import *
import main
import spriteObject

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
    
class MenuButtonSprite(spriteObject.ImageSprite):
    def __init__(self, image, topleft, colorKey=[255, 255, 255], generateAlpha=True, filepath=__file__):
        spriteObject.ImageSprite.__init__(self, image, topleft, colorKey=colorKey, generateAlpha=generateAlpha, filepath=filepath)
        
          
if __name__  == '__main__': main()