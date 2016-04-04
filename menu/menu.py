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
import engine.controller
import sys
from Tix import OptionName
try:
    import css
except ImportError:
    from menu import css
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
        pygame.joystick.init()
        screen = pygame.display.set_mode((self.settings['windowSize'][0], self.settings['windowSize'][1]))
        pygame.display.set_caption(self.settings['windowName'])
            
        self.currentScreen = StartScreen(self)
        
        self.music = musicManager.getMusicManager()
        self.music.createMusicSet('menu', [(settingsManager.createPath('music/Laszlo - Imaginary Friends.ogg'),4,"Laszlo - Imaginary Friends (NCS Release)"),
                                           (settingsManager.createPath('music/The Void - Lost Language (Original Edit).ogg'),1,"The Void - Lost Language (Original Edit) (NCS Release)"),
                                           ])
        self.music.createMusicSet('css', [(settingsManager.createPath('music/Character Lobby.ogg'),5,"Character Lobby")])
        
        self.bg = bgSpace()
        
        self.currentScreen.executeMenu(screen)
        
class SubMenu():
    def __init__(self,parent):
        self.menuText = []
        self.status = 0
        self.parent = parent
        
    def update(self,screen):
        self.parent.bg.update(screen)
        self.parent.bg.draw(screen,(0,0),1.0)
               
        for m in self.menuText:
            m.draw(screen,m.rect.topleft,1.0)
            m.changeColor([255,255,255])
        
        rgb = self.parent.bg.hsvtorgb(self.parent.bg.starColor)
        self.menuText[self.selectedOption].changeColor(rgb)    
    
    def executeMenu(self,screen):
        self.clock = pygame.time.Clock()
        self.screen = screen
        
        controls = []
        for i in range(0,4):
            controls.append(settingsManager.getControls(i))
        
        while self.status == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: #Quitting the game should close it out completely
                    self.status = -1
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: #Hitting escape always counts as a back button
                    self.status = 1
                for control in controls:
                    k = control.getInputs(event,False,False)
                    if k == 'up':
                        self.selectedOption = (self.selectedOption - 1) % len(self.menuText)
                    elif k == 'down':
                        self.selectedOption = (self.selectedOption + 1) % len(self.menuText)
                    elif k == 'left':
                        self.incrementOption(self.selectedOption,-1)
                    elif k == 'right':
                        self.incrementOption(self.selectedOption,1)
                    elif k == 'confirm' or k == 'attack':
                        self.confirmOption(self.selectedOption)
                    elif k == 'cancel' or k == 'special':
                        self.status = 1
            self.update(screen)
            self.clock.tick(60)    
            pygame.display.flip()    
        return self.status
    
    def confirmOption(self,optionNum):
        pass
    
    def incrementOption(self,optionNum,direction):
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
                if event.type == KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                    if event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                        self.status = 1
                    else:
                        menu = MainMenu(self.parent)
                        self.parent.music.rollMusic('menu')
                        menu.starColor = self.hsv
                        retValue = menu.executeMenu(screen)
                        pygame.mixer.music.fadeout(1000)
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
    
    def update(self, screen):
        SubMenu.update(self, screen)    
    
    def confirmOption(self, optionNum):
        SubMenu.confirmOption(self, optionNum)
        if optionNum == 0: #play game
            status = RulesMenu(self.parent).executeMenu(self.screen)
        elif optionNum == 1: #settings menu
            status = OptionsMenu(self.parent).executeMenu(self.screen)
        elif optionNum == 2: #module manager
            status = ModulesMenu(self.parent).executeMenu(self.screen)
        elif optionNum == 3: #quit
            self.status = 1
            return
        if status == -1: self.status = -1
        
    def executeMenu(self,screen):
        return SubMenu.executeMenu(self, screen)
        
""" Options Screen and related Submenus """
class OptionsMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('Controls','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Graphics','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Sound','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Game','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Back','full Pack 2025',20,[255,255,255])]
        
        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 90 + i*60
                
        self.selectedOption = 0
    
    def confirmOption(self, optionNum):
        SubMenu.confirmOption(self, optionNum)
        if optionNum == 0: #controls
            status = ControlsMenu(self.parent).executeMenu(self.screen)
        elif optionNum == 1: #graphics
            status = GraphicsMenu(self.parent).executeMenu(self.screen)
        elif optionNum == 2: #sound
            status = SoundMenu(self.parent).executeMenu(self.screen)
        elif optionNum == 3: #game
            status = GameSettingsMenu(self.parent).executeMenu(self.screen)
        elif optionNum == 4: #quit
            self.status = 1
            return
        if status == -1: self.status = -1
        
    def executeMenu(self,screen):
        return SubMenu.executeMenu(self, screen)

class RulesMenu (SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('Play','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('3 Stocks','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('8 Minutes','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Player Two Bot OFF','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Teams Enabled','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Team Attack On','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Cancel','full Pack 2025',24,[255,255,255])]

        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 90 + i*40
        
        self.selectedOption = 0
        self.rules = {'Stocks':3,'Time':8,'Teams':False,'Team Attack':True,'Bots':False}
        
    def confirmOption(self, optionNum):
        SubMenu.confirmOption(self, optionNum)
        if optionNum == 0: #play
            botlist = [False,False,False,False]
            if self.rules['Bots']: botlist = [False,True,False,False]
            gameRules = battle.Rules(self.rules['Stocks'],self.rules['Time'],[])
            status = css.CSSScreen(gameRules,botlist)
            if status == -1: self.status = -1
        elif optionNum == 3: #bots
            self.rules['Bots'] = not self.rules['Bots']
        elif optionNum == 4: #teams
            self.rules['Teams'] = not self.rules['Teams']
        elif optionNum == 5: #team attack
            self.rules['Team Attack'] = not self.rules['Team Attack']
        elif optionNum == 6: #quit
            self.status = 1
            return
            
    def incrementOption(self, optionNum, direction):
        SubMenu.incrementOption(self, optionNum, direction)
        if optionNum == 1:
            self.rules['Stocks'] += direction
        elif optionNum == 2:
            self.rules['Time'] += direction
        elif optionNum == 3:
            self.rules['Bots'] = not self.rules['Bots']
        elif optionNum == 4:
            self.rules['Teams'] = not self.rules['Teams']
        elif optionNum == 5:
            self.rules['Team Attack'] = not self.rules['Team Attack']
        self.rules['Stocks'] = self.rules['Stocks'] % 100
        self.rules['Time'] = self.rules['Time'] % 100
                
        
    def executeMenu(self, screen):
        return SubMenu.executeMenu(self,screen)
        
    def update(self,screen):
        SubMenu.update(self,screen)
        
        self.menuText[1].changeText(str(self.rules['Stocks'])+' Stock Battle')
        self.menuText[2].changeText(str(self.rules['Time'])+' Minute Match')
        
        if (self.rules['Stocks'] == 0):
            self.menuText[1].changeText('Unlimited Stock Battle')
        if (self.rules['Time'] == 0):
            self.menuText[2].changeText('Unlimited Time Match')
        
        if self.rules['Bots']:
            self.menuText[3].changeText('Player Two Bot ON')
        else:
            self.menuText[3].changeText('Player Two Bot OFF')
        
        if self.rules['Teams']:
            self.menuText[4].changeText('Teams Enabled')
        else:
            self.menuText[4].changeText('Teams Disabled')

        if self.rules['Team Attack']:
            self.menuText[5].changeText('Team Attack Enabled')
        else:
            self.menuText[5].changeText('Team Attack Disabled')

class ControlsMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('Player Controls','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Gamepad Settings','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Exit','full Pack 2025',20,[255,255,255])]
        
        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 90 + i*60
                
        self.selectedOption = 0
    
    def confirmOption(self, optionNum):
        SubMenu.confirmOption(self, optionNum)
        if optionNum == 0:
            status = 0
        elif optionNum == 1:
            status = GamepadMenu(self.parent).executeMenu(self.screen)
        elif optionNum == 2:
            self.status = 1
            return
        if status == -1: self.status = -1
    def executeMenu(self, screen):
        return SubMenu.executeMenu(self, screen)
        
class GamepadMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self, parent)
        
        self.controllerList = []
        self.connectedControllers = []
        for i in range(0,pygame.joystick.get_count()):
            controllerName = pygame.joystick.Joystick(i).get_name()
            self.controllerList.append((controllerName,settingsManager.getSetting().loadGamepad(controllerName)))
            self.connectedControllers.append(pygame.joystick.Joystick(i).get_name())
        
        for controllerName in settingsManager.getSetting().getGamepadList():
            if not controllerName in [data[0] for data in self.controllerList]:
                self.controllerList.append((controllerName,settingsManager.getSetting().loadGamepad(controllerName)))
                
        if self.controllerList:
            self.currentController = 0
        
        self.menuText = [spriteManager.TextSprite(self.controllerList[self.currentController][0],'rexlia rg',18,[255,255,255]),
                         spriteManager.TextSprite('Exit','full Pack 2025',20,[255,255,255])]
        
        self.statusText = spriteManager.TextSprite('Controller not connected','rexlia rg',16,[255,255,255])
        
        if self.controllerList[self.currentController][0] in self.connectedControllers:
            self.statusText.changeText('Controller connected')
            self.statusText.changeColor([255,255,255])
        else:
            self.statusText.changeText('Controller not connected')
            self.statusText.changeColor([55,55,55])
                            
        self.actionColumn = [spriteManager.TextSprite('left','rexlia rg',16,[55,55,55]),
                             spriteManager.TextSprite('right','rexlia rg',16,[55,55,55]),
                             spriteManager.TextSprite('up','rexlia rg',16,[55,55,55]),
                             spriteManager.TextSprite('down','rexlia rg',16,[55,55,55]),
                             spriteManager.TextSprite('attack','rexlia rg',16,[55,55,55]),
                             spriteManager.TextSprite('special','rexlia rg',16,[55,55,55]),
                             spriteManager.TextSprite('jump','rexlia rg',16,[55,55,55]),
                             spriteManager.TextSprite('shield','rexlia rg',16,[55,55,55]),
                             ]
        
        self.keyColumn = [spriteManager.TextSprite('---','rexlia rg',16,[55,55,55]),
                          spriteManager.TextSprite('---','rexlia rg',16,[55,55,55]),
                          spriteManager.TextSprite('---','rexlia rg',16,[55,55,55]),
                          spriteManager.TextSprite('---','rexlia rg',16,[55,55,55]),
                          spriteManager.TextSprite('---','rexlia rg',16,[55,55,55]),
                          spriteManager.TextSprite('---','rexlia rg',16,[55,55,55]),
                          spriteManager.TextSprite('---','rexlia rg',16,[55,55,55]),
                          spriteManager.TextSprite('---','rexlia rg',16,[55,55,55]),
                          ]
        
        
        for i in range(0,len(self.actionColumn)):
            self.actionColumn[i].rect.left = self.parent.settings['windowSize'][0] / 4
            self.keyColumn[i].rect.right = (self.parent.settings['windowSize'][0] / 4) * 3
            self.actionColumn[i].rect.centery = 76 + 16*i
            self.keyColumn[i].rect.centery = 76 + 16*i
            
        self.menuText[0].rect.midtop = (self.parent.settings['windowSize'][0] / 2,20)
        self.menuText[-1].rect.midbottom = (self.parent.settings['windowSize'][0] / 2,self.parent.settings['windowSize'][1] - 20)
        self.statusText.rect.midtop = self.menuText[0].rect.midbottom
        
        self.selectedOption = 0
    
    def confirmOption(self, optionNum):
        SubMenu.confirmOption(self, optionNum)    
        if optionNum == 0:
            status = self.bindControls(self.screen,settingsManager.getSetting().getGamepadByName(self.controllerList[self.currentController][0]))
        elif optionNum == 1:
            self.status = 1
            return
        if status == -1: self.status = -1
        
    def incrementOption(self, optionNum, direction):
        SubMenu.incrementOption(self, optionNum, direction)
        if optionNum == 0:
            self.currentController = (self.currentController + direction) % len(self.controllerList)
            if self.controllerList[self.currentController][0] in self.connectedControllers:
                self.statusText.changeText('Controller connected')
                self.statusText.changeColor([255,255,255])
            else:
                self.statusText.changeText('Controller not connected')
                self.statusText.changeColor([55,55,55])
    
    def update(self, screen):
        SubMenu.update(self, screen)
        
        for i,action in enumerate(self.actionColumn):
            padControls = self.controllerList[self.currentController][1]
            self.keyColumn[i].changeText('---')
            if padControls:
                k = padControls.getKeysForAction(action.text)
                if k:
                    self.keyColumn[i].changeText(str(k))
                
        for m in self.actionColumn:
            m.draw(screen,m.rect.topleft,1.0)
            m.changeColor([55,55,55])
        for m in self.keyColumn:
            m.draw(screen,m.rect.topleft,1.0)
            m.changeColor([55,55,55])
        
        self.statusText.draw(screen, self.statusText.rect.topleft, 1.0)
        self.menuText[0].changeText(self.controllerList[self.currentController][0])
        
        
    def executeMenu(self, screen):
        return SubMenu.executeMenu(self, screen)
            
    def bindControls(self,screen,joystick):
        selectedSubOption = 0
        newAxisBinding = {}
        newButtonBinding = {}
        
        heldButtons = []
        heldAxis = []
        workingAxis = []
        workingButton = []
        
        status = 0
        ready = False
        while status == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return 0
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.joy == joystick.get_id():
                        value = (self.actionColumn[selectedSubOption].text,event.button)
                        if value not in workingButton:
                            workingButton.append(value)
                        heldButtons.append(event.button)
                elif event.type == pygame.JOYBUTTONUP:
                    if event.joy == joystick.get_id():
                        if event.button in heldButtons:
                            heldButtons.remove(event.button)
                            if not heldAxis and not heldButtons:
                                ready = True
                elif event.type == pygame.JOYAXISMOTION:
                    if event.joy == joystick.get_id():
                        if abs(event.value) > 0.5: #joy motion
                            if event.value > 0: #positive
                                value = (self.actionColumn[selectedSubOption].text,event.axis,1)
                            else:
                                value = (self.actionColumn[selectedSubOption].text,event.axis,0)
                            if value not in workingAxis:
                                workingAxis.append(value)
                                heldAxis.append(event.axis)
                            
                        else: #joy released
                            if event.axis in heldAxis:
                                heldAxis.remove(event.axis)
                                if not heldAxis and not heldButtons:
                                    ready = True
                
                if ready:
                    buttonList = []
                    for action,button in workingButton:
                        newButtonBinding[button] = action
                        buttonList.append('Button '+str(button))
                    workingButton = []
                    
                    for action,axis,direction in workingAxis:
                        if axis in newAxisBinding: #if we already have one of the axis points set, we need to pull it
                            newBinding = list(newAxisBinding[axis])
                        else: #If it's fresh, we need to build it
                            newBinding = ['','']
                        newBinding[direction] = action
                        newAxisBinding[axis] = tuple(newBinding)
                        
                        #get the string value of the direction of the axis
                        if direction == 1: string = ' Positive'
                        else: string = ' Negative'
                        buttonList.append('Axis '+str(axis)+string)
                    workingAxis = []
                     
                    self.keyColumn[selectedSubOption].changeText(str(buttonList))
                    selectedSubOption += 1
                    ready = False
                    if selectedSubOption >= len(self.actionColumn):
                        newPadBindings = engine.controller.PadBindings(joystick.get_id(),newAxisBinding,newButtonBinding)
                        newController = engine.controller.GamepadController(newPadBindings)
                        settingsManager.getSetting().setting['controls_0'] = newController
                        return 0
                        
            self.parent.bg.update(screen)
            self.parent.bg.draw(screen,(0,0),1.0)
            
            for m in self.menuText:
                m.draw(screen,m.rect.topleft,1.0)
                m.changeColor([55,55,55])
            for m in self.actionColumn:
                m.draw(screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            for m in self.keyColumn:
                m.draw(screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            
            rgb = self.parent.bg.hsvtorgb(self.parent.bg.starColor)
            self.actionColumn[selectedSubOption].changeColor(rgb)
            self.keyColumn[selectedSubOption].changeColor(rgb)
            
            self.clock.tick(60)    
            pygame.display.update()
   
class PlayerControlsMenu(SubMenu):
    def __init__(self, parent):
        SubMenu.__init__(self, parent)
        self.menuText = [spriteManager.TextSprite('Player 1','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Use Gamepad: None','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Exit','full Pack 2025',20,[255,255,255])]
        
        
        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 90 + i*60
                
        self.selectedOption = 0
    
    def executeMenu(self, screen):
        return SubMenu.executeMenu(self, screen)
    
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
        
        
        self.selectedOption = 0
        
    def executeMenu(self,screen):
        return 1
        

class SoundMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self, parent)
        
        self.settings = settingsManager.getSetting().setting
                
        self.selectedOption = 0
        self.selectedBlock = 0
        
        self.musicVol = self.settings['musicVolume']
        self.soundVol = self.settings['sfxVolume']
        
        self.menuText = [spriteManager.TextSprite('Music Volume: '+str(self.musicVol),'rexlia rg',16,[255,255,255]),
                         spriteManager.TextSprite('SFX Volume: '+str(self.soundVol),'rexlia rg',16,[255,255,255]),
                         spriteManager.TextSprite('Save', 'full Pack 2025', 24, [255,255,255]),
                         spriteManager.TextSprite('Cancel', 'full Pack 2025', 24, [255,255,255]),
                         ]
        
        self.menuText[0].rect.midtop = (self.settings['windowWidth'] / 2,80)
        self.menuText[1].rect.midtop = (self.settings['windowWidth'] / 2,180)
        
        self.menuText[2].rect.center = (self.settings['windowWidth'] / 3,self.settings['windowHeight'] - 64)
        self.menuText[3].rect.center = ((self.settings['windowWidth'] / 3) * 2,self.settings['windowHeight'] - 64)
    
    def confirmOption(self, optionNum):
        SubMenu.confirmOption(self, optionNum)
        if optionNum == 2:
            self.settings['musicVolume'] = self.musicVol
            self.settings['sfxVolume'] = self.soundVol
            pygame.mixer.music.set_volume(self.musicVol)
            settingsManager.saveSettings(self.settings)
            self.status = 1
        elif optionNum == 3:
            self.status = 1
    
    def incrementOption(self, optionNum, direction):
        SubMenu.incrementOption(self, optionNum, direction)
        if optionNum == 0:
            self.musicVol += float(direction) / 10
            if self.musicVol > 1.0: self.musicVol = 1.0
        elif optionNum == 1:
            self.soundVol += float(direction) / 10
            if self.soundVol > 1.0: self.soundVol = 1.0
    
    def update(self, screen):
        self.menuText[0].changeText('Music Volume: '+str(self.musicVol))
        self.menuText[1].changeText('SFX Volume: '+str(self.soundVol))
        SubMenu.update(self, screen)        
        
    def executeMenu(self,screen):
        return SubMenu.executeMenu(self, screen)

""" Modules and related Submenus """
class ModulesMenu(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self, parent)
        self.menuText = [
                         spriteManager.TextSprite('Back','full Pack 2025',24,[255,255,255])
                         ]
        self.statusText = spriteManager.TextSprite('Module Manager not yet available','rexlia rg',18,[255,255,255])
        
        self.menuText[0].rect.centerx = settingsManager.getSetting('windowSize')[0] / 2
        self.menuText[0].rect.bottom = settingsManager.getSetting('windowSize')[1] - 100
        
        self.statusText.rect.top = 50
        self.statusText.rect.centerx = settingsManager.getSetting('windowSize')[0] / 2
        
        self.selectedOption = 0
    
    def update(self, screen):
        SubMenu.update(self, screen)
        self.statusText.draw(screen,self.statusText.rect.topleft,1.0)
        
        
    def confirmOption(self, optionNum):
        self.status = 1
        SubMenu.confirmOption(self, optionNum)
        
    def executeMenu(self,screen):
        return SubMenu.executeMenu(self, screen)
        
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
        
        self.image = pygame.transform.scale(self.image, (9*(11-dist)//10,9*(11-dist)//10))
        
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
        

"""
Dirty, awful code that must be rewritten
"""
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
        return 1 #this one needs a total overhaul
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

class RebindMenu(SubMenu):
    def __init__(self,parent):
        self.KeyIdMap = {}
        self.KeyNameMap = {}
        for name, value in vars(pygame.constants).items():
            if name.startswith("K_"):
                self.KeyIdMap[value] = name
                self.KeyNameMap[name] = value
        SubMenu.__init__(self,parent)
        self.menuText = [spriteManager.TextSprite('','full Pack 2025',25,[255,255,255]),
                         spriteManager.TextSprite('Hold keys to bind multiple','full Pack 2025',15,[255,255,255]),
                         spriteManager.TextSprite('Press ','full Pack 2025',15,[255,255,255])]
        self.menuText[0].rect.center = (self.parent.settings['windowSize'][0] / 2,self.parent.settings['windowSize'][1] / 2)
        self.menuText[1].rect.center = (self.parent.settings['windowSize'][0] / 2,self.parent.settings['windowSize'][1] / 6) 
        self.menuText[2].rect.center = (self.parent.settings['windowSize'][0] / 2,self.parent.settings['windowSize'][1] *  5 / 6)
        self.status = 0
        
    def executeMenu(self,screen,toBind):
        clock = pygame.time.Clock()
        notBound = True
        bindings = []
        currentString = ''
        keysDown = 0
        self.menuText[2].changeText('Press '+ toBind)
        
        while self.status == 0:
            currentString = ''
            for i in range(0,len(bindings)):
                currentString += self.KeyIdMap[bindings[i]][2:]
                if i < len(bindings) - 1:
                    currentString += ' - '
            self.menuText[0].changeText(currentString)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    bindings.append(event.key);
                    keysDown += 1
                if event.type == KEYUP:
                    keysDown -= 1
                    notBound = False
            if keysDown < 0:
                notBound = True
                keysDown = 0
            if keysDown == 0 and not notBound:
                return bindings
            self.parent.bg.update(screen)
            self.parent.bg.draw(screen,(0,0),1.0)
            for text in self.menuText:
                text.draw(screen, text.rect.topleft, 1.0)
            
            rgb = self.parent.bg.hsvtorgb(self.parent.bg.starColor)
            self.menuText[0].changeColor(rgb)
            pygame.display.flip()
            clock.tick(60)

class RebindIndividual(SubMenu):
    def __init__(self,parent):
        SubMenu.__init__(self,parent)
        self.menuText = []
        self.labels = ('left','right','up','down','attack','special','jump','shield')
        for label in self.labels:
            self.menuText.append(spriteManager.TextSprite(label + ' - ','full Pack 2025',20,[255,255,255]))
        self.menuText.append(spriteManager.TextSprite('Save','full Pack 2025',20,[255,255,255]))
        self.menuText.append(spriteManager.TextSprite('Cancel','full Pack 2025',20,[255,255,255]))
        for i in range(0,len(self.menuText)):
            self.menuText[i].rect.centerx = self.parent.settings['windowSize'][0] / 2
            self.menuText[i].rect.centery = 60 + i*50
        self.menuText[len(self.menuText)-2].rect.centerx = self.parent.settings['windowSize'][0] / 3
        self.menuText[len(self.menuText)-1].rect.centerx = self.parent.settings['windowSize'][0] * 2 / 3
        self.menuText[len(self.menuText)-2].rect.centery = self.parent.settings['windowSize'][1] - 25 
        self.menuText[len(self.menuText)-1].rect.centery = self.parent.settings['windowSize'][1] - 25
        self.selectedOption = 0

    def executeMenu(self,screen):
        controls = settingsManager.getControls('menu')
        clock = pygame.time.Clock()
        holding = {'up': False,'down': False,'left': False,'right': False}
        
        while self.status == 0:
            self.update(screen)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    holding[controls.get(event.key)] = True
                    if controls.get(event.key) == 'confirm':
                        pass
                        
                if event.type == KEYUP:
                    holding[controls.get(event.key)] = False
                if event.type == QUIT:
                    self.status = -1
                if event.type == pygame.USEREVENT+1: 
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
                    if keyName == 'left' or keyName == 'right':
                        if self.selectedOption == 8:
                            self.selectedOption = 9
                        elif self.selectedOption == 9:
                            self.selectedOption = 8
                    

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


if __name__  == '__main__': main()