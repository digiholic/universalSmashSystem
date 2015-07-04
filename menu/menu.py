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
import css

import spriteManager

def main():
    Menu()
    
class Menu():
    def __init__(self):
        self.settings = settingsManager.getSetting().setting
        pygame.init()
        screen = pygame.display.set_mode((self.settings['windowSize'][0], self.settings['windowSize'][1]))
        pygame.display.set_caption(self.settings['windowName'])
            
        self.currentScreen = StartScreen(self)
        
        self.music = musicManager.musicManager([(settingsManager.createPath('music/Laszlo - Imaginary Friends.ogg'),9,"Laszlo - Imaginary Friends (NCS Release)"),
                                                (settingsManager.createPath('music/The Void - Lost Language (Original Edit).ogg'),1,"The Void - Lost Language (Original Edit) (NCS Release)")])
        
        self.bg = bgSpace()
        
        self.currentScreen.executeMenu(screen)
        
class SubMenu():
    def __init__(self,parent):
        self.submenus = []
        self.menuOptions = None
        self.status = 0
        self.parent = parent
        
    def update(self,screen):
        pass
    
    def executeMenu(self,screen):
        pass
    
class StartScreen(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        self.logo = spriteManager.ImageSprite(settingsManager.createPath('sprites/logo-wip.png'))
        
        self.start = spriteManager.TextSprite('PRESS START','full Pack 2025',18)
        self.start.rect.midbottom = (settingsManager.getSetting('windowSize')[0] / 2, 360)
        self.startAlpha = 144
        self.alphaRad = 0
        
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
                        menu = MainMenu(self.parent)
                        self.parent.music.rollMusic()
                        menu.starColor = self.hsv
                        retValue = menu.executeMenu(screen)
                        if retValue == -1: return -1
                    
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
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('TUSSLE','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Settings','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Modules','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Quit','full Pack 2025',24,[255,255,255])]
        
        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 100 + i*100
                
        self.selectedOption = 0
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        
        controls = settingsManager.getControls('menu')
        print controls.keyBindings
        
        while self.status == 0:
            self.update(screen)
            
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel':
                        pygame.mixer.music.fadeout(1000)
                        self.status = 1
                    if controls.get(event.key) == 'down':
                        self.selectedOption += 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    if controls.get(event.key) == 'up':
                        self.selectedOption -= 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    if controls.get(event.key) == 'confirm':
                        if self.selectedOption == 0: #play game
                            css.CSSScreen()
                        if self.selectedOption == 1: #options
                            self.state = OptionsMenu(self.parent).executeMenu(screen)
                            if self.state == -1: return -1
                        if self.selectedOption == 2: #modules
                            pass
                        if self.selectedOption == 3: #quit
                            return -1
                        
                if event.type == QUIT:
                    self.status = -1
            
            self.parent.bg.update(screen)
            self.parent.bg.draw(screen,(0,0),1.0)
            
            for m in self.menuText:
                m.draw(screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            rgb = self.parent.bg.hsvtorgb(self.parent.bg.starColor)
            self.menuText[self.selectedOption].changeColor(rgb)
                
            #self.menuText.draw(screen, (128,128), 1.0)
            clock.tick(60)    
            pygame.display.flip()
            
        return self.status
    
class PlayGameMenu(SubMenu):
    pass

""" Options Screen and related Submenus """
class OptionsMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('Controls','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Graphics','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Sound','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Game','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Back','full Pack 2025',24,[255,255,255])]
        
        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 90 + i*80
                
        self.selectedOption = 0
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        
        controls = settingsManager.getControls('menu')
        
        while self.status == 0:
            self.update(screen)
            
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel':
                        self.status = 1
                    if controls.get(event.key) == 'down':
                        self.selectedOption += 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    if controls.get(event.key) == 'up':
                        self.selectedOption -= 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    if controls.get(event.key) == 'confirm':
                        if self.selectedOption == 0: #controls
                            pass
                        if self.selectedOption == 1: #graphics
                            pass
                        if self.selectedOption == 2: #sound
                            pass
                        if self.selectedOption == 3: #game
                            self.state = GameSettingsMenu(self.parent).executeMenu(screen)
                            if self.state == -1: return -1
                        if self.selectedOption == 4: #quit
                            self.status = 1
                if event.type == QUIT:
                    self.status = -1
            
            self.parent.bg.update(screen)
            self.parent.bg.draw(screen,(0,0),1.0)
            
            for m in self.menuText:
                m.draw(screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            rgb = self.parent.bg.hsvtorgb(self.parent.bg.starColor)
            self.menuText[self.selectedOption].changeColor(rgb)
                
            #self.menuText.draw(screen, (128,128), 1.0)
            clock.tick(60)    
            pygame.display.flip()
            
        return self.status
    

class ControlsMenu(SubMenu):
    pass

class GraphicsMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        
        self.categoryList = ['Window', 'Debug']
        self.currentCategory = 0
        
        self.leftColumn = {'Window': ['Resolution'],
                           'Debug': ['Display Hitboxes','Display Hurtboxes', 'Display Sprite Bounds', 'Display Platform Lines']
                           }
        
        self.rightColumn = {'Resolution': ['640 x 480','1024 x 768'],
                            'Display Hitboxes': ['On','Off'],
                            'Display Hurtboxes': ['On','Off'],
                            'Display Sprite Bounds': ['On','Off'],
                            'Display Platform Lines': ['On','Off'],
                            }
        self.selected = 0
        
        self.categoryText = spriteManager.TextSprite('Window','full Pack 2025',24,[255,255,255])
        
        
        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 90 + i*80
                
        self.selectedOption = 0
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        controls = settingsManager.getControls('menu')
        
        while self.status == 0:
            self.update(screen)
            
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel':
                        self.status = 1
                    if controls.get(event.key) == 'down':
                        self.selectedOption += 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    if controls.get(event.key) == 'up':
                        self.selectedOption -= 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    if controls.get(event.key) == 'confirm':
                        if self.selectedOption == 0: #controls
                            pass
                        if self.selectedOption == 1: #graphics
                            pass
                        if self.selectedOption == 2: #sound
                            pass
                        if self.selectedOption == 3: #game
                            pass
                        if self.selectedOption == 4: #quit
                            self.status = 1
                if event.type == QUIT:
                    self.status = -1
            
            self.parent.bg.update(screen)
            self.parent.bg.draw(screen,(0,0),1.0)
            
            for m in self.menuText:
                m.draw(screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            rgb = self.parent.bg.hsvtorgb(self.parent.bg.starColor)
            self.menuText[self.selectedOption].changeColor(rgb)
                
            #self.menuText.draw(screen, (128,128), 1.0)
            clock.tick(60)    
            pygame.display.flip()
            
        return self.status

class SoundMenu(SubMenu):
    pass

class GameSettingsMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self, parent)
        
        self.settings = settingsManager.getSetting().setting
        self.presets = self.settings['presetLists']
        
        self.current_preset = 0
        self.selectionSlice = (1,10)
        
        self.selectedOption = 0
        self.menuText = [spriteManager.TextSprite(self.presets[self.current_preset], 'full Pack 2025', 24, [255,255,255]),
                         spriteManager.TextSprite('Gravity Multiplier','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Weight Multiplier','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Friction Multiplier','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Air Mobility Multiplier','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Hit Stun Multiplier','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Hit Lag Multiplier','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Shield Stun Multiplier','rexlia rg',18,[255,255,255]),
                         
                         spriteManager.TextSprite('Ledge Conflict Type','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Ledge Sweetspot Size','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Ledge Grab Forward Facing Only','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Team Ledge Conflict','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Ledge Invincibility Time','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Regrab Invincibility','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Slow Ledge Getup Damage Threshold','rexlia rg',18,[255,255,255]),
                         
                         ]
        
        self.updateMenuText()
        
        vertOff = 80
        for menu in self.menuText:
            menu.rect.left = 20
            menu.rect.top = vertOff
            vertOff += 25    
            
        self.menuText[0].rect.centerx = self.settings['windowSize'][0] / 2
        self.menuText[0].rect.top = 50
    
    def updateMenuText(self):
        settingsManager.getSetting().loadGameSettings(self.presets[self.current_preset])
        
        self.menuValues = [spriteManager.TextSprite('','rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['gravity']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['weight']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['friction']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['airControl']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['hitstun']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['hitlag']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['shieldStun']),'rexlia rg', 18, [255,255,255]),
                           
                           spriteManager.TextSprite(str(self.settings['ledgeConflict']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['ledgeSweetspotSize']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['ledgeSweetspotForwardOnly']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['teamLedgeConflict']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['ledgeInvincibilityTime']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['regrabInvincibility']),'rexlia rg', 18, [255,255,255]),
                           spriteManager.TextSprite(str(self.settings['slowLedgeWakeupThreshold']),'rexlia rg', 18, [255,255,255]),
                           
                           ]
        
        vertOff = 80
        for val in self.menuValues:
            val.rect.right = self.settings['windowSize'][0] - 20
            val.rect.top = vertOff
            vertOff += 25
        
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        controls = settingsManager.getControls('menu')
        
        while self.status == 0:
            self.update(screen)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel':
                        self.status = 1
                    
                    if controls.get(event.key) == 'left':
                        if self.selectedOption == 0: #currently selecting preset switcher
                            self.current_preset -= 1
                            self.current_preset = self.current_preset % len(self.presets)
                            self.menuText[0].changeText(self.presets[self.current_preset])
                            self.updateMenuText()
                            
                            
                    if controls.get(event.key) == 'right':
                        if self.selectedOption == 0: #currently selecting preset switcher
                            self.current_preset += 1
                            self.current_preset = self.current_preset % len(self.presets)
                            self.menuText[0].changeText(self.presets[self.current_preset])
                            self.updateMenuText()
        
                            
                    if controls.get(event.key) == 'down':
                        self.selectedOption += 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                        if self.selectedOption < len(self.menuText):
                            if self.selectedOption > self.selectionSlice[1] - 1:
                                self.selectionSlice = (self.selectionSlice[0]+1,self.selectionSlice[1]+1)
                                
                                for i in range(1,len(self.menuText)):
                                    self.menuText[i].rect.y -= 25
                                    self.menuValues[i].rect.y -= 25
                                    
                    if controls.get(event.key) == 'up':
                        self.selectedOption -= 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                        if self.selectedOption > 0:
                            if self.selectedOption < self.selectionSlice[0]:
                                self.selectionSlice = (self.selectionSlice[0]-1,self.selectionSlice[1]-1)
                                
                                for i in range(1,len(self.menuText)):
                                    self.menuText[i].rect.y += 25
                                    self.menuValues[i].rect.y += 25
                                    
                    if controls.get(event.key) == 'confirm':
                        if self.selectedOption == 0: #controls
                            pass
                        if self.selectedOption == 1: #graphics
                            pass
                        if self.selectedOption == 2: #sound
                            pass
                        if self.selectedOption == 3: #game
                            pass
                        if self.selectedOption == 4: #quit
                            self.status = 1
                
                if event.type == QUIT:
                    self.status = -1
            
            self.parent.bg.update(screen)
            self.parent.bg.draw(screen,(0,0),1.0)
            
            
            self.menuText[0].draw(screen,self.menuText[0].rect.topleft,1.0)
            self.menuText[0].changeColor([255,255,255])
            
            for m in self.menuText[self.selectionSlice[0]:self.selectionSlice[1]]:
                m.draw(screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            for m in self.menuValues[self.selectionSlice[0]:self.selectionSlice[1]]:
                m.draw(screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            
            
            rgb = self.parent.bg.hsvtorgb(self.parent.bg.starColor)
            self.menuText[self.selectedOption].changeColor(rgb)
            self.menuValues[self.selectedOption].changeColor(rgb)
            
            
                
            #self.menuText.draw(screen, (128,128), 1.0)
            clock.tick(60)    
            pygame.display.flip()
            
        return self.status

        
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
        

class bgSpace(spriteManager.ImageSprite):
    def __init__(self):
        spriteManager.Sprite.__init__(self)
        self.image = pygame.surface.Surface(tuple(settingsManager.getSetting('windowSize')))
        self.rect = pygame.rect.Rect((0,0),self.image.get_size())
        
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
        
        self.image.fill([0,0,0])
    
    def hsvtorgb(self,hsv):
        return tuple(i * 255 for i in colorsys.hsv_to_rgb(hsv[0],hsv[1],hsv[2]))
        
    def draw(self, screen, offset, scale):
        screen.blit(self.image,self.rect.topleft)
        self.stars.draw(screen)
        
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
    
    def hsvtorgb(self,hsv):
        return tuple(i * 255 for i in colorsys.hsv_to_rgb(hsv[0],hsv[1],hsv[2]))
    
    def changeColor(self,toColor):
        fromColor = self.hsvtorgb(self.color)
        trueColor = self.hsvtorgb(toColor)
        
        self.recolor(self.image, fromColor, trueColor)
        self.color = [toColor[0],toColor[1],toColor[2]]
        
        
if __name__  == '__main__': main()