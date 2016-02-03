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
import sys
import spriteManager
import battle
import stages.arena.stage as stage0
import stages.true_arena.stage as stage1
import fighters.hitboxie.fighter as fighter
import fighters.sandbag.fighter as sandbag

def main():
    Menu()
    
class Menu():
    def __init__(self):
        self.settings = settingsManager.getSetting().setting
        pygame.init()
        screen = pygame.display.set_mode((self.settings['windowSize'][0], self.settings['windowSize'][1]))
        pygame.display.set_caption(self.settings['windowName'])
            
        self.currentScreen = StartScreen(self)
        
        self.music = musicManager.getMusicManager()
        self.music.createMusicSet('menu', [(settingsManager.createPath('music/Laszlo - Imaginary Friends.ogg'),9,"Laszlo - Imaginary Friends (NCS Release)"),
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
                        self.parent.music.rollMusic('menu')
                        menu.starColor = self.hsv
                        retValue = menu.executeMenu(screen)
                        if retValue == -1: return -1

                if event.type == QUIT:
                    self.status = -1
                    sys.exit()
            
            
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
        print(controls.keyBindings)
        canPress = True
        holding = {'up': False,'down': False,'left': False,'right': False}
        
        while self.status == 0:
            self.update(screen)
            
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    holding[controls.get(event.key)] = True
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel':
                        pygame.mixer.music.fadeout(1000)
                        self.status = 1
                    '''if controls.get(event.key) == 'down':
                        self.selectedOption += 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    if controls.get(event.key) == 'up':
                        self.selectedOption -= 1
                        self.selectedOption = self.selectedOption % len(self.menuText)'''
                    if controls.get(event.key) == 'confirm':
                        if self.selectedOption == 0: #play game
                            self.status = RulesMenu(self.parent).executeMenu(screen)
                            if self.status == -1: return -1
                        if self.selectedOption == 1: #options
                            self.status = OptionsMenu(self.parent).executeMenu(screen)
                            if self.status == -1: return -1
                        if self.selectedOption == 2: #modules
                            self.status = ModulesMenu(self.parent).executeMenu(screen)
                            if self.status == -1: return -1
                        if self.selectedOption == 3: #quit
                            return -1

                if event.type == KEYUP:
                    holding[controls.get(event.key)] = False

                if event.type == USEREVENT+1:
                    canPress = True
                        
                if event.type == QUIT:
                    self.status = -1

            for keyName,keyValue in holding.items():
                if keyValue and canPress: 
                    canPress = False
                    pygame.time.set_timer(pygame.USEREVENT+1,150)
                    if keyName == 'down':
                        self.selectedOption += 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    if keyName == 'up':
                        self.selectedOption -= 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
            
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
        self.menuText = [spriteManager.TextSprite('Controls','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Graphics','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Sound','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Game','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Training','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Back','full Pack 2025',20,[255,255,255])]
        
        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 90 + i*60
                
        self.selectedOption = 0
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        controls = settingsManager.getControls('menu')
        canPress = True
        holding = {'up': False,'down': False,'left': False,'right': False}
        
        while self.status == 0:
            self.update(screen)
            
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    holding[controls.get(event.key)] = True
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel': #if the player cancels
                        self.status = 1
                    if controls.get(event.key) == 'confirm': #if enter (?) is pressed
                        if self.selectedOption == 0: #controls
                            self.status = ControlsMenu(self.parent).executeMenu(screen)
                            if self.status == -1: return -1
                        if self.selectedOption == 1: #graphics
                            self.status = RulesMenu(self.parent).executeMenu(screen)
                            if self.status == -1: return -1
                        if self.selectedOption == 2: #sound
                            self.status = SoundMenu(self.parent).executeMenu(screen)
                            if self.status == -1: return -1
                        if self.selectedOption == 3: #game
                            self.status = GameSettingsMenu(self.parent).executeMenu(screen)
                            if self.status == -1: return -1
                        if self.selectedOption == 4: #debug
                            self.status = DebugMenu(self.parent).executeMenu(screen)
                            if self.status == -1: return -1
                        if self.selectedOption == 5: #quit
                            self.status = 1

                if event.type == KEYUP:
                    holding[controls.get(event.key)] = False
                
                if event.type == QUIT:
                    self.status = -1

                if event.type == pygame.USEREVENT+1: #USEREVENT+1 goes off whenever you can press a key again
                    canPress = True;
                    
            for keyName,keyValue in holding.items():
                if keyValue and canPress: 
                    canPress = False
                    pygame.time.set_timer(pygame.USEREVENT+1,150)
                    if keyName == 'down':
                        self.selectedOption += 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    if keyName == 'up':
                        self.selectedOption -= 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    
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

class RulesMenu (SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('Play','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Stock','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('3 Stocks','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('8 Minutes','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Teams Enabled','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Team Attack On','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Cancel','full Pack 2025',24,[255,255,255])]

        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 90 + i*40
        
        self.selectedOption = 0
    
    def executeMenu(self, screen):
        clock = pygame.time.Clock()
        canPress = True
        controls = settingsManager.getControls('menu')
        holding = {'up': False,'down': False,'left': False,'right': False}
        rules = {'Type':0, 'Stocks':3,'Time':8,'Teams':False,'Team Attack':True}

        while self.status == 0:
            self.update(screen)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    holding[controls.get(event.key)] = True
                    if controls.get(event.key) == 'confirm':
                        if self.selectedOption == 0:
                            gameRules = battle.Rules(rules['Stocks'],rules['Time'],[])
                            status = css.CSSScreen(gameRules)
                            if status == -1: return -1
                        if self.selectedOption == 4:
                            rules['Teams'] = not rules['Teams']
                        if self.selectedOption == 5:
                            rules['Team Attack'] = not rules['Team Attack']
                        if self.selectedOption == 6:
                            self.status = 1
                    if event.key == pygame.K_ESCAPE:
                        self.status = 1       
                if event.type == KEYUP:
                    holding[controls.get(event.key)] = False
                if event.type == USEREVENT+1:
                    canPress = True
                if event.type == QUIT:
                    self.status = -1

            for button,buttonPressed in holding.items():
                if buttonPressed and canPress:
                    canPress = False
                    pygame.time.set_timer(pygame.USEREVENT+1,150)
                    if button == 'up':
                        self.selectedOption -= 1
                    if button == 'down':
                        self.selectedOption += 1
                    self.selectedOption = self.selectedOption % 7

                    if button == 'left':
                        if self.selectedOption == 1:
                            rules['Type'] -= 1
                        if self.selectedOption == 2:
                            rules['Stocks'] -= 1
                        if self.selectedOption == 3:
                            rules['Time'] -= 1
                        if self.selectedOption == 4:
                            rules['Teams'] = not rules['Teams']
                        if self.selectedOption == 5:
                            rules['Team Attack'] = not rules['Team Attack']
                    if button == 'right':
                        if self.selectedOption == 1:
                            rules['Type'] += 1
                        if self.selectedOption == 2:
                            rules['Stocks'] += 1
                        if self.selectedOption == 3:
                            rules['Time'] += 1
                        if self.selectedOption == 4:
                            rules['Teams'] = not rules['Teams']
                        if self.selectedOption == 5:
                            rules['Team Attack'] = not rules['Team Attack']
                    rules['Type'] = rules['Type'] % 2
                    rules['Stocks'] = rules['Stocks'] % 100
                    rules['Time'] = rules['Time'] % 100

            if rules['Type'] == 0:
                self.menuText[1].changeText('Stock')
            if rules['Type'] == 1:
                self.menuText[1].changeText('Time')

            self.menuText[2].changeText(str(rules['Stocks'])+' Stock Battle')
            self.menuText[3].changeText(str(rules['Time'])+' Minute Match')
            if rules['Teams']:
                self.menuText[4].changeText('Teams Enabled')
            else:
                self.menuText[4].changeText('Teams Disabled')

            if rules['Team Attack']:
                self.menuText[5].changeText('Team Attack Enabled')
            else:
                self.menuText[5].changeText('Team Attack Disabled')


            self.parent.bg.update(screen)
            self.parent.bg.draw(screen,(0,0),1.0)
            
            for m in self.menuText:
                m.draw(screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            rgb = self.parent.bg.hsvtorgb(self.parent.bg.starColor)
            self.menuText[self.selectedOption].changeColor(rgb)
            
            clock.tick(60)    
            pygame.display.flip()
            
        return self.status
        

class DebugMenu(SubMenu):
    def __init__(self,parent):
        self.stages = [('Arena',stage0),('True Arena',stage1)] # TODO: Automate this, needs a way to get the stage names though
        self.stage = 0
        self.directory = settingsManager.createPath("fighters")
        self.settings = settingsManager.getSetting().setting
        for s in self.settings:
            print(s)
        
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('showHitboxes - ','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('showHurtboxes - ','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('showSpriteArea - ','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('showPlatformLines - ','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Spawn Sandbag - ','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Stage - ','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Start','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Exit','full Pack 2025',24,[255,255,255])]
        
        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 40 + i*40
        self.menuText[len(self.menuText)-2].rect.centery = 420
        self.menuText[len(self.menuText)-1].rect.centery = 450
                
        self.selectedOption = 0
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        controls = settingsManager.getControls('menu')
        canPress = True
        holding = {'up': False,'down': False,'left': False,'right': False}
        fightercount = 0
        self.spawnSandbag = False
        
        while self.status == 0:
            self.update(screen)
            self.stageName, self.currentStage = self.stages[self.stage]
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    holding[controls.get(event.key)] = True
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel': #if the player cancels
                        self.status = 1
                    if controls.get(event.key) == 'right' or controls.get(event.key) == 'left':
                        if self.selectedOption == 5:
                            if controls.get(event.key) == 'right':
                                self.stage += 1
                            else:
                                self.stage -= 1
                                if self.stage < 0:
                                    self.stage = len(self.stages) - 1
                            self.stage = self.stage % len(self.stages)
                        if self.selectedOption == 0: 
                            self.settings['showHitboxes'] = not self.settings['showHitboxes']
                        if self.selectedOption == 1: 
                            self.settings['showHurtboxes'] = not self.settings['showHurtboxes']
                        if self.selectedOption == 2: 
                            self.settings['showSpriteArea'] = not self.settings['showSpriteArea']
                        if self.selectedOption == 3:
                            self.settings['showPlatformLines'] = not self.settings['showPlatformLines']
                        if self.selectedOption == 4:
                            self.spawnSandbag = not self.spawnSandbag
                    if controls.get(event.key) == 'confirm':
                        if self.selectedOption == 0: 
                            self.settings['showHitboxes'] = not self.settings['showHitboxes']
                        if self.selectedOption == 1: 
                            self.settings['showHurtboxes'] = not self.settings['showHurtboxes']
                        if self.selectedOption == 2: 
                            self.settings['showSpriteArea'] = not self.settings['showSpriteArea']
                        if self.selectedOption == 3:
                            self.settings['showPlatformLines'] = not self.settings['showPlatformLines']
                        if self.selectedOption == 4:
                            self.spawnSandbag = not self.spawnSandbag
                        if self.selectedOption == len(self.menuText)-2:
                            self.fighters = [fighter.getFighter(0,0)]
                            if self.spawnSandbag:
                                self.fighters.append(sandbag.getFighter(1,0))
                            currentBattle = battle.Battle(battle.Rules(),self.fighters,self.currentStage.getStage())
                            currentBattle.startBattle(screen)
                        if self.selectedOption == len(self.menuText)-1: #quit
                            self.status = 1

                if event.type == KEYUP:
                    holding[controls.get(event.key)] = False
                
                if event.type == QUIT:
                    self.status = -1

                if event.type == pygame.USEREVENT+1: #USEREVENT+1 goes off whenever you can press a key again
                    canPress = True;
                    
            for keyName,keyValue in holding.items():
                if keyValue and canPress: 
                    canPress = False
                    pygame.time.set_timer(pygame.USEREVENT+1,150)
                    if keyName == 'down':
                        self.selectedOption += 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    if keyName == 'up':
                        self.selectedOption -= 1
                        self.selectedOption = self.selectedOption % len(self.menuText)

            self.menuText[0].changeText('showHitboxes - '+str(self.settings['showHitboxes']))
            self.menuText[1].changeText('showHurtboxes - '+str(self.settings['showHurtboxes']))
            self.menuText[2].changeText('showSpriteArea - '+str(self.settings['showSpriteArea']))
            self.menuText[3].changeText('showPlatformLines - '+str(self.settings['showPlatformLines']))
            self.menuText[4].changeText('Spawn Sandbag - '+str(self.spawnSandbag))
            self.menuText[5].changeText('Stage - '+str(self.stageName))
            
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

'''settings.setting['controls_'+currentPlayer] = settingsManager.Keybindings({
                                                         'left': ---,
                                                         'right': ---,
                                                         'up': ---,
                                                         'down': ---,
                                                         'jump': ---,
                                                         'attack': ---,
                                                         'shield': ---
                                                         })'''

'''class ControlsMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('Player 1','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Bind All','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Bind Movement','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Bind Actions','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Bind Individual','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Back','full Pack 2025',20,[255,255,255])]
        
        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 90 + i*60
                
        self.selectedOption = 0
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        controls = settingsManager.getControls('menu')
        canPress = True
        bindingKey = 0 # What type of binding am I doing?
        curentlyBinding = 0 # Which input am I binding now?
        currentPlayer = 0 # Which Player am I setting controls for?
        holding = {'up': False,'down': False,'left': False,'right': False}
        labels = ('left','right','up','down','attack','special','jump','shield')
        newBindings = []
        
        while self.status == 0:
            self.update(screen)
            controls = settingsManager.getControls(currentPlayer)
            if bindingKey == 0:
                for event in pygame.event.get():
                    #Changing state of key
                    if event.type == KEYDOWN:
                        holding[controls.get(event.key)] = True
                    if event.type == KEYUP:
                        holding[controls.get(event.key)] = False
                        print 'released ' + str(controls.get(event.key))
                    #Using KEYDOWN and KEYUP for the actual event, just for organization
                    if event.type == KEYDOWN:
                        pass
                    if event.type == KEYUP:
                        pass
                    if event.type == QUIT:
                        self.status = -1
                    if event.type == USEREVENT+1:
                        canPress = True
                    
                for keyName,keyValue in holding.items():
                    if keyValue and canPress:
                        print holding
                        canPress = False
                        pygame.time.set_timer(pygame.USEREVENT+1,150)
                        if keyName == 'up':
                            self.selectedOption -= 1
                            if self.selectedOption < 0:
                                self.selectedOptiom = len(self.menuText)-1
                        if keyName == 'down':
                            self.selectedOption += 1
                            self.selectedOption = self.selectedOption % len(self.menuText)
                        if keyName == 'left':
                            currentPlayer += -1
                        if keyName == 'right':
                            currentPlayer += 1
                        
            self.menuText[0].changeText('Player '+str(currentPlayer+1))
            
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
            
        return self.status'''

'''class RebindMenu(SubMenu):
    def __init__(self,parent):
        self.KeyIdMap = {}
        self.KeyNameMap = {}
        for name, value in vars(pygame.constants).items():
            if name.startswith("K_"):
                self.KeyIdMap[value] = name
                self.KeyNameMap[name] = value
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('Bind ','full Pack 2025',30,[255,255,255]),
                         spriteManager.TextSprite('Hold multiple keys before releasing to add more than one'),'full Pack 2025',15,[255,255,255]]
        self.menuText[0].rect.centerx = self.parent.settings['windowSize'][0] / 2
        self.menuText[0].rect.centery = self.parent.settings['windowSize'][1] / 2
        self.menuText[1].rect.centerx = self.parent.settings['windowSize'][0] / 2
        self.menuText[1].rect.centery = 100
            
    def executeMenu(self,screen,thingsToBind):
        clock = pygame.time.Clock()
        newBindings = []
        pressedKeys = []
        canPress = True
        for control in thingsToBind:
            notSet = True
            
            if canPress:
                self.menuText[0].changeText('Press ' + control)
                
            while notSet:
                self.update(screen)
                
                for event in pygame.event.get():
                    if event.type == KEYDOWN:
                        keyToSet.append(event.key)
                        pressedKeys[str(event.key)] = True
                    if event.type == KEYUP and canPress:
                        notSet = False
                        pressedKeys[str(event.key)] = False
                        self.menuText[0].changeText('Release All Keys')

                nonePressed = True
                for key in pressedKeys:
                    if key:
                        nonePressed = False
                if nonePressed:
                    canPress = True

                self.parent.bg.update(screen)
                self.parent.bg.draw(screen,(0,0),1.0)
                self.menuText[0].draw(screen,self.menuText[0].rect.topleft,1.0)
                self.menuText[0].changeColor([255,255,255])
                self.menuText[1].draw(screen,self.menuText[1].rect.topleft,1.0)
                self.menuText[1].changeColor([255,255,255])
                rgb = self.parent.bg.hsvtorgb(self.parent.bg.starColor)
                self.menuText[0].changeColor(rgb)
                pygame.display.flip()
                clock.tick(60)
                
            for x in keyToSet:
                newBindings.append((x,control))
            
        return dict(newBindings)'''

class RebindMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('Bind ','full Pack 2025',30,[255,255,255]),
                         spriteManager.TextSprite('Hold multiple keys before releasing to add more than one'),'full Pack 2025',15,[255,255,255]]
        self.menuText[0].rect.centerx = self.parent.settings['windowSize'][0] / 2
        self.menuText[0].rect.centery = self.parent.settings['windowSize'][1] / 2
        self.menuText[1].rect.centerx = self.parent.settings['windowSize'][0] / 2
        self.menuText[1].rect.centery = 100
        
    def executeMenu(self,screen,toBind):
        clock = pygame.time.Clock()
        notBound = True
        
        #for currentControl in toBind:
            #while notBound:
                #TODO: Make it work
                

        
class ControlsMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('Player 1','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Rebind All','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Rebind Movement','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Rebind Actions','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Rebind Individual','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Exit','full Pack 2025',20,[255,255,255])]
        
        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 90 + i*60
                
        self.selectedOption = 0
        
    def executeMenu(self,screen):
        currentPlayer = 0
        settings = settingsManager.getSetting()
        clock = pygame.time.Clock()
        controls = settingsManager.getControls(0)
        canPress = True
        holding = {'up': False,'down': False,'left': False,'right': False}
        labels = ('left','right','up','down','attack','special','jump','shield')
        newBindings = []
        
        while self.status == 0:
            self.update(screen)
            controls = settingsManager.getControls(currentPlayer)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    holding[controls.get(event.key)] = True
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel' or controls.get(event.key) == 'special': #if the player cancels
                        self.status = 1
                    if controls.get(event.key) == 'confirm' or controls.get(event.key) == 'attack':
                        if self.selectedOption == 1: #Rebind All
                            newBindings = RebindMenu(self.parent).executeMenu(screen,labels)
                            settings.setting['controls_' + str(currentPlayer)] = settingsManager.Keybindings(newBindings)
                            settingsManager.saveSettings(settingsManager.getSetting().setting)
                        if self.selectedOption == 2: #Rebind Movement
                            pass
                        if self.selectedOption == 3: #Rebind Rebing Actions
                            pass
                        if self.selectedOption == 4: #Go to rebind individual menu
                            pass
                        if self.selectedOption == 5: #quit
                            self.status = 1

                if event.type == KEYUP:
                    holding[controls.get(event.key)] = False
                
                if event.type == QUIT:
                    self.status = -1

                if event.type == pygame.USEREVENT+1: #USEREVENT+1 goes off whenever you can press a key again
                    canPress = True;
                    
            for keyName,keyValue in holding.items():
                if keyValue and canPress: 
                    canPress = False
                    pygame.time.set_timer(pygame.USEREVENT+1,150)
                    if keyName == 'down':
                        self.selectedOption += 1
                        self.selectedOption = self.selectedOption % len(self.menuText)
                    if keyName == 'up':
                        self.selectedOption -= 1
                        self.selectedOption = self.selectedOption % len(self.menuText)

                    if keyName == 'left':
                        currentPlayer -= 1
                    if keyName == 'right':
                        currentPlayer += 1
                    currentPlayer = currentPlayer % 4

            self.menuText[0].changeText('Player ' + str(currentPlayer + 1))
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
    def __init__(self,parent):
        SubMenu.__init__(self, parent)
        
        self.settings = settingsManager.getSetting().setting
                
        self.selectedOption = 0
        volList = range(0,100)
        self.menuText = [OptionButton('Music Volume', volList, (self.settings['musicVolume'] * 100)),
                         OptionButton('SFX Volume', volList, (self.settings['sfxVolume'] * 100)),
                         spriteManager.TextSprite('Save', 'full Pack 2025', 24, [255,255,255]),
                         spriteManager.TextSprite('Cancel', 'full Pack 2025', 24, [255,255,255]),
                         ]
        
        self.menuText[0].setHeight(80)
        self.menuText[1].setHeight(180)
        self.menuText[2].rect.centery = self.settings['windowHeight'] - 64
        self.menuText[3].rect.centery = self.settings['windowHeight'] - 64
        
        self.menuText[2].rect.centerx = (self.settings['windowWidth'] / 3)
        self.menuText[3].rect.centerx = (self.settings['windowWidth'] / 3) * 2
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        controls = settingsManager.getControls('menu')
        canPress = True
        holding = {'up': False,'down': False,'left': False,'right': False}
        print('This is using jam1garners test version')
        while self.status == 0:
            self.update(screen)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    holding[controls.get(event.key)] = True #When the key is pressed down it changes the state to held down
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel':
                        if self.selectedBlock == 0:
                            self.status = 1

                    # Old Code for inputs
                    '''if controls.get(event.key) == 'left': 
                        if self.selectedOption == 2: #if you're not highlighting back
                            self.selectedOption = 3
                        elif self.selectedOption == 3:
                            self.selectedOption = 2
                        else:
                            self.menuText[self.selectedOption].incVal(-1)
                            
                    if controls.get(event.key) == 'right':
                        if self.selectedOption == 2: #if you're not highlighting back
                            self.selectedOption = 3
                        elif self.selectedOption == 3:
                            self.selectedOption = 2
                        else:
                            self.menuText[self.selectedOption].incVal(1)
                                
                    if controls.get(event.key) == 'down':
                        if self.selectedOption == 2 or self.selectedOption == 3:
                            self.selectedOption = 0
                        else:
                            self.selectedOption += 1
                            self.selectedOption = self.selectedOption % len(self.menuText)
                            
                    if controls.get(event.key) == 'up':
                        if self.selectedOption == 0:
                            self.selectedOption = 3
                        elif self.selectedOption == 3:
                            self.selectedOption = 2
                        else:
                            self.selectedOption -= 1
                            self.selectedOption = self.selectedOption % len(self.menuText)'''
                            
                    if controls.get(event.key) == 'confirm':
                        if self.selectedOption == 2: #save
                            self.settings['musicVolume'] = float(self.menuText[0].getValue()) / 100
                            self.settings['sfxVolume'] = float(self.menuText[1].getValue()) / 100
                            
                            pygame.mixer.music.set_volume(float(self.menuText[0].getValue()) / 100)
                            settingsManager.saveSettings(self.settings)
                            self.status = 1
                        if self.selectedOption > 2: #save or cancel
                            self.status = 1
                            
                if event.type == KEYUP:
                    holding[controls.get(event.key)] = False; #Changes the state of the key to unpressed upon release
                    
                if event.type == QUIT:
                    self.status = -1

                if event.type == pygame.USEREVENT+1: #USEREVENT+1 goes off whenever you can press a key again
                    canPress = True;
                    
            for keyName,keyValue in holding.items():
                if keyValue and canPress:
                    canPress = False
                    if keyName == 'left':
                        pygame.time.set_timer(pygame.USEREVENT+1,100) #100 is currently the sensitivity in milliseconds between presses while holding down the button
                        if self.selectedOption == 2: #if you're not highlighting back
                            self.selectedOption = 3
                        elif self.selectedOption == 3:
                            self.selectedOption = 2
                        else:
                            self.menuText[self.selectedOption].incVal(-1)
                            
                    if keyName == 'right':
                        pygame.time.set_timer(pygame.USEREVENT+1,100) #100 is currently the sensitivity in milliseconds between presses while holding down the button
                        if self.selectedOption == 2: #if you're not highlighting back
                            self.selectedOption = 3
                        elif self.selectedOption == 3:
                            self.selectedOption = 2
                        else:
                            self.menuText[self.selectedOption].incVal(1)
                            
                    if keyName == 'down':
                        pygame.time.set_timer(pygame.USEREVENT+1,150) #150 is currently the sensitivity in milliseconds between presses while holding down the button
                        if self.selectedOption == 2:
                            self.selectedOption = 3
                        elif self.selectedOption == 3:
                             self.selectedOption = 0
                        else:
                            self.selectedOption += 1
                            self.selectedOption = self.selectedOption % len(self.menuText)
                            
                    if keyName == 'up':
                        pygame.time.set_timer(pygame.USEREVENT+1,150) #150 is currently the sensitivity in milliseconds between presses while holding down the button
                        if self.selectedOption == 0:
                            self.selectedOption = 3
                        elif self.selectedOption == 3:
                            self.selectedOption = 2
                        else:
                            self.selectedOption -= 1
                            self.selectedOption = self.selectedOption % len(self.menuText)
            
            self.parent.bg.update(screen)
            self.parent.bg.draw(screen,(0,0),1.0)
            
            self.menuText[0].draw(screen,(0,0),1.0)
            self.menuText[1].draw(screen,(0,0),1.0)
            self.menuText[2].draw(screen,self.menuText[2].rect.topleft,1.0)
            self.menuText[3].draw(screen,self.menuText[3].rect.topleft,1.0)
            
            self.menuText[0].changeColor([255,255,255])
            self.menuText[1].changeColor([255,255,255])
            self.menuText[2].changeColor([255,255,255])
            self.menuText[3].changeColor([255,255,255])
                
            rgb = self.parent.bg.hsvtorgb(self.parent.bg.starColor)
            self.menuText[self.selectedOption].changeColor(rgb)
            
            #self.menuText.draw(screen, (128,128), 1.0)
            clock.tick(60)    
            pygame.display.flip()
            
        return self.status

class GameSettingsMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self, parent)
        
        self.settings = settingsManager.getSetting().setting
        self.presets = self.settings['presetLists']
        
        self.current_preset = self.presets.index(self.settings['current_preset'])
        print(self.current_preset)
        self.selectionSlice = (0,10)
        
        self.selectedOption = 0
        self.selectedBlock = 0
        self.menuText = [spriteManager.TextSprite(self.presets[self.current_preset], 'full Pack 2025', 24, [255,255,255])]
                         #spriteManager.TextSprite('Cancel','full Pack 2025', 22, [255,255,255]),
                         #spriteManager.TextSprite('Save','full Pack 2025', 22, [255,255,255]),
                         #]
        
        numList = [0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0]
        
        self.options = [OptionButton('Gravity Multiplier', numList, (self.settings['gravity'])),
                        OptionButton('Weight Multiplier', numList, (self.settings['weight'])),
                        OptionButton('Friction Multiplier', numList, (self.settings['friction'])),
                        OptionButton('Air Mobility Multiplier', numList, (self.settings['airControl'])),
                        OptionButton('Hit Stun Multiplier', numList, (self.settings['hitstun'])),
                        OptionButton('Hit Lag Multiplier', numList, (self.settings['hitlag'])),
                        OptionButton('Shield Stun Multiplier', numList, (self.settings['shieldStun'])),
                        
                        OptionButton('Ledge Conflict Type', ['hog','trump','share'], (self.settings['ledgeConflict'])),
                        OptionButton('Ledge Sweetspot Size', [[128,128],[64,64],[32,32]], (self.settings['ledgeSweetspotSize'])),
                        OptionButton('Ledge Grab Only When Facing', [True, False], (self.settings['ledgeSweetspotForwardOnly'])),
                        OptionButton('Team Ledge Conflict', [True, False], (self.settings['teamLedgeConflict'])),
                        OptionButton('Ledge Invincibility Time', range(0,300,5), (self.settings['ledgeInvincibilityTime'])),
                        OptionButton('Regrab Invincibility', [True, False], (self.settings['regrabInvincibility'])),
                        OptionButton('Slow Ledge Getup Damage Threshold', range(0,300,5), (self.settings['slowLedgeWakeupThreshold'])),
                        
                        ]
            
        self.menuText[0].rect.centerx = self.settings['windowSize'][0] / 2
        self.menuText[0].rect.top = 50
    
    def updateMenuText(self):
        settingsManager.getSetting().loadGameSettings(self.presets[self.current_preset])
        self.selectionSlice = (0,10)
        
        numList = [0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0]
        
        self.options = [OptionButton('Gravity Multiplier', numList, (self.settings['gravity'])),
                        OptionButton('Weight Multiplier', numList, (self.settings['weight'])),
                        OptionButton('Friction Multiplier', numList, (self.settings['friction'])),
                        OptionButton('Air Mobility Multiplier', numList, (self.settings['airControl'])),
                        OptionButton('Hit Stun Multiplier', numList, (self.settings['hitstun'])),
                        OptionButton('Hit Lag Multiplier', numList, (self.settings['hitlag'])),
                        OptionButton('Shield Stun Multiplier', numList, (self.settings['shieldStun'])),
                        
                        OptionButton('Ledge Conflict Type', ['hog','trump','share'], (self.settings['ledgeConflict'])),
                        OptionButton('Ledge Sweetspot Size', [[128,128],[64,64],[32,32]], (self.settings['ledgeSweetspotSize'])),
                        OptionButton('Ledge Grab Only When Facing', [True, False], (self.settings['ledgeSweetspotForwardOnly'])),
                        OptionButton('Team Ledge Conflict', [True, False], (self.settings['teamLedgeConflict'])),
                        OptionButton('Ledge Invincibility Time', range(0,300,5), (self.settings['ledgeInvincibilityTime'])),
                        OptionButton('Regrab Invincibility', [True, False], (self.settings['regrabInvincibility'])),
                        OptionButton('Slow Ledge Getup Damage Threshold', range(0,300,5), (self.settings['slowLedgeWakeupThreshold'])),
                        
                        ]
        
    def updateSlice(self):
        if self.selectedOption <= self.selectionSlice[0] and self.selectionSlice[0] > 0:
            diff = self.selectionSlice[0] - self.selectedOption
            self.selectionSlice = (self.selectionSlice[0]-diff, self.selectionSlice[1]-diff)
        if self.selectedOption >= (self.selectionSlice[1]-1) and self.selectionSlice[1] <= len(self.options):
            diff = self.selectedOption - (self.selectionSlice[1] -1)
            self.selectionSlice = (self.selectionSlice[0]+diff, self.selectionSlice[1]+diff)
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        controls = settingsManager.getControls('menu')
        canPress = True
        holding = {'up': False,'down': False,'left': False,'right': False}
        
        while self.status == 0:
            self.update(screen)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    holding[controls.get(event.key)] = True
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel':
                        if self.selectedBlock == 0:
                            self.status = 1
                        else:
                            self.selectedBlock = 0
                            self.selectionSlice = (0,10)
                            self.selectedOption = 0
                            for opt in self.options:
                                opt.changeColor([100,100,100])
                                
                    '''if controls.get(event.key) == 'left':
                        if self.selectedBlock == 0 and self.selectedOption == 0: #currently selecting preset switcher
                            self.current_preset -= 1
                            self.current_preset = self.current_preset % len(self.presets)
                            self.menuText[0].changeText(self.presets[self.current_preset])
                            self.updateMenuText()
                        if self.selectedBlock == 1:
                            self.options[self.selectedOption].incVal(-1)
                            
                            
                    if controls.get(event.key) == 'right':
                        if self.selectedBlock == 0 and self.selectedOption == 0: #currently selecting preset switcher
                            self.current_preset += 1
                            self.current_preset = self.current_preset % len(self.presets)
                            self.menuText[0].changeText(self.presets[self.current_preset])
                            self.updateMenuText()
                        if self.selectedBlock == 1:
                            self.options[self.selectedOption].incVal(1)
                            
                    if controls.get(event.key) == 'down':
                        if self.selectedBlock == 0:
                            self.selectedOption += 1
                            self.selectedOption = self.selectedOption % len(self.menuText)
                        else:
                            self.selectedOption += 1
                            self.selectedOption = self.selectedOption % len(self.options)
                            self.updateSlice()
                            
                    if controls.get(event.key) == 'up':
                        if self.selectedBlock == 0:
                            self.selectedOption -= 1
                            self.selectedOption = self.selectedOption % len(self.menuText)
                        else:
                            self.selectedOption -= 1
                            self.selectedOption = self.selectedOption % len(self.options)
                            self.updateSlice()'''
                                        
                    if controls.get(event.key) == 'confirm':
                        if self.selectedBlock == 0: #not editing a preset
                            if self.selectedOption == 0: #selecting a preset
                                self.selectedBlock = 1
                                self.selectedOption = 0
                                self.selectionSlice = (0,10)
                                for opt in self.options:
                                    opt.changeColor([255,255,255])

                if event.type == KEYUP:
                    holding[controls.get(event.key)] = False;

                if event.type == pygame.USEREVENT+1:
                    canPress = True;
                                    
                if event.type == QUIT:
                    self.status = -1

            for keyName,keyValue in holding.items():
                if keyValue and canPress: 
                    canPress = False
                    pygame.time.set_timer(pygame.USEREVENT+1,200)
                    if keyName == 'left':
                        if self.selectedBlock == 0 and self.selectedOption == 0: #currently selecting preset switcher
                            self.current_preset -= 1
                            self.current_preset = self.current_preset % len(self.presets)
                            self.menuText[0].changeText(self.presets[self.current_preset])
                            self.updateMenuText()
                        if self.selectedBlock == 1:
                            self.options[self.selectedOption].incVal(-1)
                    if keyName == 'right':
                        if self.selectedBlock == 0 and self.selectedOption == 0: #currently selecting preset switcher
                            self.current_preset += 1
                            self.current_preset = self.current_preset % len(self.presets)
                            self.menuText[0].changeText(self.presets[self.current_preset])
                            self.updateMenuText()
                        if self.selectedBlock == 1:
                            self.options[self.selectedOption].incVal(1)
                    if keyName == 'down':
                        if self.selectedBlock == 0:
                            self.selectedOption += 1
                            self.selectedOption = self.selectedOption % len(self.menuText)
                        else:
                            self.selectedOption += 1
                            self.selectedOption = self.selectedOption % len(self.options)
                            self.updateSlice()
                    if keyName == 'up':
                        if self.selectedBlock == 0:
                            self.selectedOption -= 1
                            self.selectedOption = self.selectedOption % len(self.menuText)
                        else:
                            self.selectedOption -= 1
                            self.selectedOption = self.selectedOption % len(self.options)
                            self.updateSlice()

            self.parent.bg.update(screen)
            self.parent.bg.draw(screen,(0,0),1.0)
            
            self.menuText[0].draw(screen,self.menuText[0].rect.topleft,1.0)
            
            for m in self.menuText:
                m.draw(screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            
            vertOff = 100
            for opt in self.options[self.selectionSlice[0]:self.selectionSlice[1]]:
                opt.setHeight(vertOff)
                opt.draw(screen,(0,0),1.0)
                if self.selectedBlock == 1:
                    opt.changeColor([255,255,255])
                vertOff += 25
                
            rgb = self.parent.bg.hsvtorgb(self.parent.bg.starColor)
            if self.selectedBlock == 0:
                self.menuText[self.selectedOption].changeColor(rgb)
            else:
                self.options[self.selectedOption].changeColor(rgb)
                
            #self.menuText.draw(screen, (128,128), 1.0)
            clock.tick(60)    
            pygame.display.flip()
            
        return self.status

        
""" Modules and related Submenus """
class ModulesMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self, parent)
        self.menuText = [spriteManager.TextSprite('Module Manager not yet available','rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Back','full Pack 2025',24,[255,255,255])
                         ]
        
        self.menuText[0].rect.centerx = settingsManager.getSetting('windowSize')[0] / 2
        self.menuText[1].rect.centerx = settingsManager.getSetting('windowSize')[0] / 2
        
        self.menuText[0].rect.top = 50
        self.menuText[1].rect.bottom = settingsManager.getSetting('windowSize')[1] - 100
        
        self.selectedOption = 1
        
    def executeMenu(self,screen):
        clock = pygame.time.Clock()
        controls = settingsManager.getControls('menu')
        
        while self.status == 0:
            self.update(screen)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel':
                        self.status = 1
                    if controls.get(event.key) == 'confirm':
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
    
class FighterModules(SubMenu):
    pass

class StageModules(SubMenu):
    pass

class MusicModules(SubMenu):
    pass


class OptionButton(spriteManager.TextSprite):
    def __init__(self, name, vals, startingVal):
        spriteManager.Sprite.__init__(self)
        
        self.possibleVals = vals
        if startingVal in vals:
            self.selectedValue = self.possibleVals.index(startingVal) 
        else:
            print("Not in list of options")
            self.selectedValue = 0
        
        self.nameText = spriteManager.TextSprite(name, 'rexlia rg',18,[100,100,100])
        self.nameText.rect.left = 20
        
        self.valText = spriteManager.TextSprite(str(self.possibleVals[self.selectedValue]), 'rexlia rg',18,[100,100,100])
        self.valText.rect.right = 620
        
    def changeColor(self,color):
        self.nameText.changeColor(color)
        self.valText.changeColor(color)
        
    def getValue(self):
        return self.possibleVals[self.selectedValue]
    
    def update(self):
        pass
    
    def incVal(self,inc):
        self.selectedValue += inc
        self.selectedValue = self.selectedValue % len(self.possibleVals)
        
    def changeVal(self,val):
        if val in self.possibleVals:
            self.selectedValue = self.possibleVals.index(val)
    
    def setHeight(self,top):
        self.nameText.rect.top = top
        self.valText.rect.top = top
        
    def draw(self,screen,offset,scale):
        self.valText.text = str(self.getValue())
        self.nameText.draw(screen, self.nameText.rect.topleft, scale)
        self.valText.draw(screen, self.valText.rect.topleft, scale)  

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
