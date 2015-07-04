import settingsManager
import pygame
import os
from pygame.locals import *
import main
import random
import math
import musicManager
import colorsys
import engine.article

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
        
        self.music = musicManager.musicManager([(settingsManager.createPath('music/Laszlo - Imaginary Friends.ogg'),9,"Laszlo - Imaginary Friends (NCS Release)"),
                                                (settingsManager.createPath('music/The Void - Lost Language (Original Edit).ogg'),1,"The Void - Lost Language (Original Edit) (NCS Release)")])
        
        self.music.rollMusic()
        #self.rgb = [89,56,255]
        self.hsv = [random.randint(0,100)/100,0.8,1.0]
        
    def update(self,screen):
        self.hsv[0] += .001
        if self.hsv[0] >= 1: self.hsv[0] -= 1
            
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
                        menu = MainMenu()
                        menu.starColor = self.hsv
                        retValue = menu.executeMenu(screen)
                        if retValue == -1: self.status = -1
                    
                if event.type == QUIT:
                    self.status = -1
            
            
            rgb = tuple(i * 255 for i in colorsys.hsv_to_rgb(self.hsv[0],self.hsv[1],self.hsv[2]))
            screen.fill(rgb)
            self.logo.draw(screen, self.logo.rect.topleft, 1.0)
            self.start.draw(screen, self.start.rect.topleft, 1.0)
            
            clock.tick(60)    
            pygame.display.flip()
        
        return self.status
            
class MainMenu(SubMenu):
    def __init__(self):
        SubMenu.__init__(self)
        #self.menuText = spriteManager.TextSprite('PRESS START','full Pack 2025',18,[255,255,255])
        
        self.stars = pygame.sprite.Group()
        self.starColor = [float(random.randint(0,100))/100,1.0,1.0]
        self.starTimer = 3
        
        
        for i in range(0,30):
            st = bgStar(random.randint(1,10))
            st.rect.x = random.randint(1,settingsManager.getSetting('windowSize')[0])
            st.changeColor(self.starColor)
            self.stars.add(st)
            
    def update(self,screen):
        # create more stars
        self.starTimer -= 1
        if self.starTimer == 0:
            self.stars.add(bgStar(random.randint(1,10)))
            self.starTimer = 3
            
        # recolor stars
        self.starColor[0] += .001
        if self.starColor[0] > 1: self.starColor[0] -= 1
        
        for star in self.stars:
            star.changeColor(self.starColor)
            star.update()
            
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
            
            
            
            screen.fill([0,0,0])
            self.stars.draw(screen)
            
            #self.menuText.draw(screen, (128,128), 1.0)
            clock.tick(60)    
            pygame.display.flip()
            
        return self.status
    
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
        

class bgStar(engine.article.Article):
    def __init__(self,dist):
        engine.article.Article.__init__(self, settingsManager.createPath("sprites/star.png"), None,
                                        (settingsManager.getSetting('windowSize')[0],random.randint(0,settingsManager.getSetting('windowSize')[1])), 1)
        self.dist = dist
        self.color = [0,0,1]
        
        self.image = pygame.transform.scale(self.image, (9*(11-dist)/10,9*(11-dist)/10))
        
    def update(self):
        self.rect.x -= 11 - self.dist
        if self.rect.right <= 0: self.kill()
        
    def changeColor(self,toColor):
        fromColor = tuple(i * 255 for i in colorsys.hsv_to_rgb(self.color[0],self.color[1],self.color[2]))
        trueColor = tuple(i * 255 for i in colorsys.hsv_to_rgb(toColor[0],toColor[1],toColor[2]))
        
        self.recolor(self.image, fromColor, trueColor)
        self.color = [toColor[0],toColor[1],toColor[2]]
        
        
if __name__  == '__main__': main()