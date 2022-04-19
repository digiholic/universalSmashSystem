import settingsManager
import pygame
from pygame.locals import *
import random
import math
import musicManager
import colorsys
import engine.article
import engine.controller
import sys
import menu.css
import spriteManager
import battle
import updater
from menu import css

def main():
    Menu()
    
class Menu():
    def __init__(self):
        self.settings = settingsManager.getSetting().setting
        pygame.init()
        pygame.joystick.init()
        screen = pygame.display.set_mode((self.settings['windowSize'][0], self.settings['windowSize'][1]))
        pygame.display.set_caption(self.settings['windowName'])
            
        self.current_screen = StartScreen(self)
        
        self.music = musicManager.getMusicManager()
        self.music.createMusicSet('menu', [(settingsManager.createPath('music/Laszlo - Imaginary Friends.ogg'),4,"Laszlo - Imaginary Friends (NCS Release)"),
                                           (settingsManager.createPath('music/The Void - Lost Language (Original Edit).ogg'),1,"The Void - Lost Language (Original Edit) (NCS Release)"),
                                           ])
        self.music.createMusicSet('css', [(settingsManager.createPath('music/Character Lobby.ogg'),5,"Character Lobby")])
        
        self.bg = bgSpace()
        
        self.current_screen.executeMenu(screen)
        
class SubMenu():
    def __init__(self,_parent):
        self.menu_text = []
        self.status = 0
        self._parent = _parent
        
    def update(self,_screen):
        self._parent.bg.update(_screen)
        self._parent.bg.draw(_screen,(0,0),1.0)
               
        for m in self.menu_text:
            m.draw(_screen,m.rect.topleft,1.0)
            m.changeColor([255,255,255])
        
        rgb = self._parent.bg.hsvtorgb(self._parent.bg.star_color)
        self.menu_text[self.selected_option].changeColor(rgb)    
    
    def executeMenu(self,_screen):
        self.clock = pygame.time.Clock()
        self.screen = _screen
        
        self.controls = []
        for i in range(0,4):
            self.controls.append(settingsManager.getControls(i))
        
        while self.status == 0:
            music = musicManager.getMusicManager()
            music.doMusicEvent()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: #Quitting the game should close it out completely
                    self.status = -1
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: #Hitting escape always counts as a back button
                    self.status = 1
                for control in self.controls:
                    k = control.getInputs(event,False,False)
                    if k == 'up':
                        self.selected_option = (self.selected_option - 1) % len(self.menu_text)
                    elif k == 'down':
                        self.selected_option = (self.selected_option + 1) % len(self.menu_text)
                    elif k == 'left':
                        self.incrementOption(self.selected_option,-1)
                    elif k == 'right':
                        self.incrementOption(self.selected_option,1)
                    elif k == 'confirm' or k == 'attack':
                        self.confirmOption(self.selected_option)
                    elif k == 'cancel' or k == 'special':
                        self.status = 1
            self.update(_screen)
            self.clock.tick(60)    
            pygame.display.flip()    
        return self.status
    
    def confirmOption(self,_optionNum):
        pass
    
    def incrementOption(self,_optionNum,_direction):
        pass
    
class StartScreen(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self,_parent)
        self.logo = spriteManager.ImageSprite(settingsManager.createPath('sprites/logo.png'))
        
        self.start = spriteManager.TextSprite('PRESS START','full Pack 2025',18)
        self.start.rect.midbottom = (settingsManager.getSetting('windowSize')[0] / 2, 360)
        self.start_alpha = 144
        self.alpha_rad = 0
        
        #self.rgb = [89,56,255]
        self.hsv = [random.randint(0,100)/100.0,0.8,1.0]
        print(self.hsv)
        
    def update(self,_screen):
        self.hsv[0] += .001
        if self.hsv[0] >= 1: self.hsv[0] -= 1
            
        # Math is cool! Ease in, ease out fade done with a sin.
        self.start_alpha = 127 * math.sin(self.alpha_rad) + 128
        self.alpha_rad += 0.05
        self.start.alpha(self.start_alpha)
        
    def executeMenu(self,_screen):
        clock = pygame.time.Clock()
        while self.status == 0:
            self.update(_screen)
            music = musicManager.getMusicManager()
            music.doMusicEvent()
            
            for event in pygame.event.get():
                if event.type == KEYDOWN or event.type == pygame.JOYBUTTONDOWN:
                    if event.type == pygame.KEYDOWN and event.key == K_ESCAPE:
                        self.status = 1
                    else:
                        menu = MainMenu(self._parent)
                        self._parent.music.rollMusic('menu')
                        menu.star_color = self.hsv
                        ret_value = menu.executeMenu(_screen)
                        pygame.mixer.music.fadeout(1000)
                        if ret_value == -1: return -1

                if event.type == QUIT:
                    self.status = -1
                    sys.exit()
            
            
            rgb = tuple(i * 255 for i in colorsys.hsv_to_rgb(self.hsv[0],self.hsv[1],self.hsv[2]))
            _screen.fill(rgb)
            self.logo.draw(_screen, self.logo.rect.topleft, 1.0)
            self.start.draw(_screen, self.start.rect.topleft, 1.0)
            
            clock.tick(60)    
            pygame.display.flip()
        
        return self.status
        
class MainMenu(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self,_parent)
        self.menu_text = [spriteManager.TextSprite('TUSSLE','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Settings','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Modules','full Pack 2025',24,[255,255,255]),
                         #spriteManager.TextSprite('Update','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Quit','full Pack 2025',24,[255,255,255])]
        
        for i in range(0,len(self.menu_text)):
            self.menu_text[i].rect.centerx = self._parent.settings['windowSize'][0] / 2
            self.menu_text[i].rect.centery = 100 + i*100
                
        self.selected_option = 0
    
    def update(self, _screen):
        SubMenu.update(self, _screen)    
    
    def confirmOption(self, _optionNum):
        SubMenu.confirmOption(self, _optionNum)
        if _optionNum == 0: #play game
            status = RulesMenu(self._parent).executeMenu(self.screen)
        elif _optionNum == 1: #settings menu
            status = OptionsMenu(self._parent).executeMenu(self.screen)
            self.controls = []
            for i in range(0,4):
                self.controls.append(settingsManager.getControls(i))
        elif _optionNum == 2: #module manager
            status = ModulesMenu(self._parent).executeMenu(self.screen)
        elif _optionNum == 3: #updates
            #status = UpdateMenu(self._parent).executeMenu(self.screen)
            self.status = 1
            return
        elif _optionNum == 4: #quit
            self.status = 1
            return
        if status == -1: self.status = -1
        
    def executeMenu(self,_screen):
        return SubMenu.executeMenu(self, _screen)
        
""" Options Screen and related Submenus """
class OptionsMenu(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self,_parent)
        self.menu_text = [spriteManager.TextSprite('Controls','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Graphics','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Sound','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Game','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Back','full Pack 2025',20,[255,255,255])]
        
        for i in range(0,len(self.menu_text)):
            self.menu_text[i].rect.centerx = self._parent.settings['windowSize'][0] / 2
            self.menu_text[i].rect.centery = 90 + i*60
                
        self.selected_option = 0
    
    def confirmOption(self, _optionNum):
        SubMenu.confirmOption(self, _optionNum)
        if _optionNum == 0: #controls
            status = ControlsMenu(self._parent).executeMenu(self.screen)
            self.controls = []
            for i in range(0,4):
                self.controls.append(settingsManager.getControls(i))
        elif _optionNum == 1: #graphics
            status = GraphicsMenu(self._parent).executeMenu(self.screen)
        elif _optionNum == 2: #sound
            status = SoundMenu(self._parent).executeMenu(self.screen)
        elif _optionNum == 3: #game
            status = GameSettingsMenu(self._parent).executeMenu(self.screen)
        elif _optionNum == 4: #quit
            self.status = 1
            return
        if status == -1: self.status = -1
        
    def executeMenu(self,_screen):
        return SubMenu.executeMenu(self, _screen)

class RulesMenu (SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self,_parent)
        self.menu_text = [spriteManager.TextSprite('Play','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('3 Stocks','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('8 Minutes','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Teams Enabled','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Team Attack On','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Cancel','full Pack 2025',24,[255,255,255])]

        for i in range(0,len(self.menu_text)):
            self.menu_text[i].rect.centerx = self._parent.settings['windowSize'][0] / 2
            self.menu_text[i].rect.centery = 90 + i*40
        
        self.selected_option = 0
        self.rules = {'Stocks':3,'Time':8,'Teams':False,'Team Attack':True}
        
    def confirmOption(self, _optionNum):
        SubMenu.confirmOption(self, _optionNum)
        if _optionNum == 0: #play
            game_rules = battle.Rules(self.rules['Stocks'],self.rules['Time'],[])
            status = css.CSSScreen(game_rules)
            if status == -1: self.status = -1
        elif _optionNum == 3: #teams
            self.rules['Teams'] = not self.rules['Teams']
        elif _optionNum == 4: #team attack
            self.rules['Team Attack'] = not self.rules['Team Attack']
        elif _optionNum == 5: #quit
            self.status = 1
            return
            
    def incrementOption(self, _optionNum, _direction):
        SubMenu.incrementOption(self, _optionNum, _direction)
        if _optionNum == 1:
            self.rules['Stocks'] += _direction
        elif _optionNum == 2:
            self.rules['Time'] += _direction
        elif _optionNum == 3:
            self.rules['Teams'] = not self.rules['Teams']
        elif _optionNum == 4:
            self.rules['Team Attack'] = not self.rules['Team Attack']
        self.rules['Stocks'] = self.rules['Stocks'] % 100
        self.rules['Time'] = self.rules['Time'] % 100
                
        
    def executeMenu(self, _screen):
        return SubMenu.executeMenu(self,_screen)
        
    def update(self,_screen):
        SubMenu.update(self,_screen)
        
        self.menu_text[1].changeText(str(self.rules['Stocks'])+' Stock Battle')
        self.menu_text[2].changeText(str(self.rules['Time'])+' Minute Match')
        
        if (self.rules['Stocks'] == 0):
            self.menu_text[1].changeText('Unlimited Stock Battle')
        if (self.rules['Time'] == 0):
            self.menu_text[2].changeText('Unlimited Time Match')
        
        if self.rules['Teams']:
            self.menu_text[3].changeText('Teams Enabled')
        else:
            self.menu_text[3].changeText('Teams Disabled')

        if self.rules['Team Attack']:
            self.menu_text[4].changeText('Team Attack Enabled')
        else:
            self.menu_text[4].changeText('Team Attack Disabled')

class ControlsMenu(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self,_parent)
        self.menu_text = [spriteManager.TextSprite('Player Controls','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Gamepad Settings','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Exit','full Pack 2025',20,[255,255,255])]
        
        for i in range(0,len(self.menu_text)):
            self.menu_text[i].rect.centerx = self._parent.settings['windowSize'][0] / 2
            self.menu_text[i].rect.centery = 90 + i*60
                
        self.selected_option = 0
    
    def confirmOption(self, _optionNum):
        SubMenu.confirmOption(self, _optionNum)
        if _optionNum == 0:
            status = PlayerControlsMenu(self._parent).executeMenu(self.screen)
            self.controls = []
            for i in range(0,4):
                self.controls.append(settingsManager.getControls(i))
        
        elif _optionNum == 1:
            status = GamepadMenu(self._parent).executeMenu(self.screen)
            self.controls = []
            for i in range(0,4):
                self.controls.append(settingsManager.getControls(i))
        elif _optionNum == 2:
            self.status = 1
            return
        if status == -1: self.status = -1
    def executeMenu(self, _screen):
        return SubMenu.executeMenu(self, _screen)
        
class GamepadMenu(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self, _parent)
        
        self.controller_list = []
        self.connected_controllers = []
        for i in range(0,pygame.joystick.get_count()):
            controller_name = pygame.joystick.Joystick(i).get_name()
            self.controller_list.append((controller_name,settingsManager.getSetting().loadGamepad(controller_name)))
            self.connected_controllers.append(pygame.joystick.Joystick(i).get_name())
        
        for controller_name in settingsManager.getSetting().getGamepadList():
            if not controller_name in [data[0] for data in self.controller_list]:
                self.controller_list.append((controller_name,settingsManager.getSetting().loadGamepad(controller_name)))
                
        if self.controller_list:
            self.current_controller = 0
        
        self.menu_text = [spriteManager.TextSprite(self.controller_list[self.current_controller][0],'Orbitron Medium',18,[255,255,255]),
                         spriteManager.TextSprite('Exit','full Pack 2025',20,[255,255,255])]
        
        self.status_text = spriteManager.TextSprite('Controller not connected','Orbitron Medium',16,[255,255,255])
        
        if self.controller_list[self.current_controller][0] in self.connected_controllers:
            self.status_text.changeText('Controller connected')
            self.status_text.changeColor([255,255,255])
        else:
            self.status_text.changeText('Controller not connected')
            self.status_text.changeColor([55,55,55])
                            
        self.action_column = [spriteManager.TextSprite('left','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('right','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('up','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('down','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('attack','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('special','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('jump','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('shield','Orbitron Medium',16,[55,55,55]),
                             ]
        
        self.key_column = [spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          ]
        
        
        for i in range(0,len(self.action_column)):
            self.action_column[i].rect.left = self._parent.settings['windowSize'][0] / 4
            self.key_column[i].rect.right = (self._parent.settings['windowSize'][0] / 4) * 3
            self.action_column[i].rect.centery = 76 + 16*i
            self.key_column[i].rect.centery = 76 + 16*i
            
        self.menu_text[0].rect.midtop = (self._parent.settings['windowSize'][0] / 2,20)
        self.menu_text[-1].rect.midbottom = (self._parent.settings['windowSize'][0] / 2,self._parent.settings['windowSize'][1] - 20)
        self.status_text.rect.midtop = self.menu_text[0].rect.midbottom
        
        self.selected_option = 0
    
    def confirmOption(self, _optionNum):
        SubMenu.confirmOption(self, _optionNum)    
        if _optionNum == 0:
            status = self.bindControls(self.screen,settingsManager.getSetting().getGamepadByName(self.controller_list[self.current_controller][0]))
            self.controls = []
            for i in range(0,4):
                self.controls.append(settingsManager.getControls(i))
        elif _optionNum == 1:
            self.status = 1
            return
        if status == -1: self.status = -1
        
    def incrementOption(self, _optionNum, _direction):
        SubMenu.incrementOption(self, _optionNum, _direction)
        if _optionNum == 0:
            self.current_controller = (self.current_controller + _direction) % len(self.controller_list)
            if self.controller_list[self.current_controller][0] in self.connected_controllers:
                self.status_text.changeText('Controller connected')
                self.status_text.changeColor([255,255,255])
            else:
                self.status_text.changeText('Controller not connected')
                self.status_text.changeColor([55,55,55])
    
    def update(self, _screen):
        SubMenu.update(self, _screen)
        
        for i,action in enumerate(self.action_column):
            pad_controls = settingsManager.getSetting(self.controller_list[self.current_controller][0]) 
            
            self.key_column[i].changeText('---')
            if pad_controls:
                k = pad_controls.getKeysForAction(action.text)
                if k:
                    self.key_column[i].changeText(str(k))
                
        for m in self.action_column:
            m.draw(_screen,m.rect.topleft,1.0)
            m.changeColor([55,55,55])
        for m in self.key_column:
            m.draw(_screen,m.rect.topleft,1.0)
            m.changeColor([55,55,55])
        
        self.status_text.draw(_screen, self.status_text.rect.topleft, 1.0)
        self.menu_text[0].changeText(self.controller_list[self.current_controller][0])
        
        
    def executeMenu(self, _screen):
        return SubMenu.executeMenu(self, _screen)
            
    def bindControls(self,_screen,_joystick):
        selected_suboption = 0
        new_axis_binding = {}
        new_button_binding = {}
        
        held_buttons = []
        held_axis = []
        working_axis = []
        working_button = []
        
        status = 0
        ready = False
        while status == 0:
            music = musicManager.getMusicManager()
            music.doMusicEvent()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return 0
                elif event.type == pygame.JOYBUTTONDOWN:
                    if event.joy == _joystick.get_id():
                        value = (self.action_column[selected_suboption].text,event.button)
                        if value not in working_button:
                            working_button.append(value)
                        held_buttons.append(event.button)
                elif event.type == pygame.JOYBUTTONUP:
                    if event.joy == _joystick.get_id():
                        if event.button in held_buttons:
                            held_buttons.remove(event.button)
                            if not held_axis and not held_buttons:
                                ready = True
                elif event.type == pygame.JOYAXISMOTION:
                    if event.joy == _joystick.get_id():
                        if abs(event.value) > 0.5: #joy motion
                            if event.value > 0: #positive
                                value = (self.action_column[selected_suboption].text,event.axis,1)
                            else:
                                value = (self.action_column[selected_suboption].text,event.axis,0)
                            if value not in working_axis:
                                working_axis.append(value)
                                held_axis.append(event.axis)
                            
                        else: #joy released
                            if event.axis in held_axis:
                                held_axis.remove(event.axis)
                                if not held_axis and not held_buttons:
                                    ready = True
                
                if ready:
                    button_list = []
                    for action,button in working_button:
                        new_button_binding[button] = action
                        button_list.append('Button '+str(button))
                    working_button = []
                    
                    for action,axis,direction in working_axis:
                        if axis in new_axis_binding: #if we already have one of the axis points set, we need to pull it
                            new_binding = list(new_axis_binding[axis])
                        else: #If it's fresh, we need to build it
                            new_binding = ['','']
                        new_binding[direction] = action
                        new_axis_binding[axis] = tuple(new_binding)
                        
                        #get the string value of the direction of the axis
                        if direction == 1: string = ' Positive'
                        else: string = ' Negative'
                        button_list.append('Axis '+str(axis)+string)
                    working_axis = []
                     
                    self.key_column[selected_suboption].changeText(str(button_list))
                    selected_suboption += 1
                    ready = False
                    if selected_suboption >= len(self.action_column):
                        name = self.controller_list[self.current_controller][0]
                        new_pad_bindings = engine.controller.PadBindings(name,_joystick.get_id(),new_axis_binding,new_button_binding)
                        new_controller = engine.controller.GamepadController(new_pad_bindings)
                        settingsManager.getSetting().new_gamepads.append(name)
                        settingsManager.getSetting().setting[name] = new_controller
                        settingsManager.saveSettings(settingsManager.getSetting().setting)
                        return 0
                        
            self._parent.bg.update(_screen)
            self._parent.bg.draw(_screen,(0,0),1.0)
            
            for m in self.menu_text:
                m.draw(_screen,m.rect.topleft,1.0)
                m.changeColor([55,55,55])
            for m in self.action_column:
                m.draw(_screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            for m in self.key_column:
                m.draw(_screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            
            rgb = self._parent.bg.hsvtorgb(self._parent.bg.star_color)
            self.action_column[selected_suboption].changeColor(rgb)
            self.key_column[selected_suboption].changeColor(rgb)
            
            self.clock.tick(60)    
            pygame.display.update()

class PlayerControlsMenu(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self, _parent)
        
        self.menu_text = [spriteManager.TextSprite('Player 1','Orbitron Medium',18,[255,255,255]),
                         spriteManager.TextSprite('Smash Timing Window: 4','Orbitron Medium',18,[255,255,255]),
                         spriteManager.TextSprite('Repeat Timing Window: 8','Orbitron Medium',18,[255,255,255]),
                         spriteManager.TextSprite('Buffer Window: 8','Orbitron Medium',18,[255,255,255]),
                         spriteManager.TextSprite('Smoothing Window: 64','Orbitron Medium',18,[255,255,255]),
                         spriteManager.TextSprite('Exit','full Pack 2025',20,[255,255,255])]
        
        self.action_column = [spriteManager.TextSprite('left','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('right','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('up','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('down','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('attack','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('special','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('jump','Orbitron Medium',16,[55,55,55]),
                             spriteManager.TextSprite('shield','Orbitron Medium',16,[55,55,55]),
                             ]
        
        self.key_column = [spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          spriteManager.TextSprite('---','Orbitron Medium',16,[55,55,55]),
                          ]
        
        self.smash_window = 4
        self.repeat_window = 8
        self.buffer_window = 8
        self.smoothing_window = 64
        
        self.status_text = spriteManager.TextSprite('','Orbitron Medium',16,[255,255,255])
        
        self.player_num = 0
        
        for i in range(0,len(self.action_column)):
            self.action_column[i].rect.left = self._parent.settings['windowSize'][0] / 4
            self.key_column[i].rect.right = (self._parent.settings['windowSize'][0] / 4) * 3
            self.action_column[i].rect.centery = 76 + 16*i
            self.key_column[i].rect.centery = 76 + 16*i
        
        key_bottom = self.key_column[-1].rect.bottom
            
        self.menu_text[0].rect.midtop = (self._parent.settings['windowSize'][0] / 2,20)
        
        for i in range(1,len(self.menu_text)):
            self.menu_text[i].rect.midtop = (self._parent.settings['windowSize'][0] /2, key_bottom + 18*i)
            
        self.menu_text[-1].rect.midbottom = (self._parent.settings['windowSize'][0] / 2,self._parent.settings['windowSize'][1] - 20)
        
        self.status_text.rect.midtop = self.menu_text[0].rect.midbottom
        self.selected_option = 0
    
    def confirmOption(self, _optionNum):
        SubMenu.confirmOption(self, _optionNum)
        status = 0    
        if _optionNum == 0:
            status = self.bindControls(self.screen)
            self.controls = []
            for i in range(0,4):
                self.controls.append(settingsManager.getControls(i))
        elif _optionNum == 5:
            self.status = 1
            settingsManager.saveSettings(settingsManager.getSetting().setting)
            return
        if status == -1: self.status = -1
        
    def incrementOption(self, _optionNum, _direction):
        SubMenu.incrementOption(self, _optionNum, _direction)
        if _optionNum == 0:
            self.player_num += _direction
            self.player_num = self.player_num % 4
        if _optionNum == 1:
            self.smash_window = max(1,self.smash_window + _direction)
            settingsManager.getControls(self.player_num).timing_window['smash_window'] = self.smash_window
        if _optionNum == 2:
            self.repeat_window = max(1,self.repeat_window + _direction)
            settingsManager.getControls(self.player_num).timing_window['repeat_window'] = self.repeat_window
        if _optionNum == 3:
            self.buffer_window = max(1,self.buffer_window + _direction)
            settingsManager.getControls(self.player_num).timing_window['buffer_window'] = self.buffer_window
        if _optionNum == 4:
            self.smoothing_window = max(1,self.smoothing_window + _direction)
            settingsManager.getControls(self.player_num).timing_window['smoothing_window'] = self.smoothing_window
            
    def update(self, _screen):
        SubMenu.update(self, _screen)
        
        for i,action in enumerate(self.action_column):
            key_controls = settingsManager.getSetting('controls_'+str(self.player_num)) 
            self.key_column[i].changeText('---')
            if key_controls:
                k = key_controls.getKeysForAction(action.text)
                if k:
                    self.key_column[i].changeText(str(k))
        
        timings = settingsManager.getControls(self.player_num).timing_window
        self.menu_text[1].changeText('Smash Window: ' + str(timings['smash_window']))
        self.menu_text[2].changeText('Repeat Window: ' + str(timings['repeat_window']))
        self.menu_text[3].changeText('Buffer Window: ' + str(timings['buffer_window']))
        self.menu_text[4].changeText('Smoothing Window: ' + str(timings['smoothing_window']))  
        for m in self.action_column:
            m.draw(_screen,m.rect.topleft,1.0)
            m.changeColor([55,55,55])
        for m in self.key_column:
            m.draw(_screen,m.rect.topleft,1.0)
            m.changeColor([55,55,55])
        
        self.status_text.draw(_screen, self.status_text.rect.topleft, 1.0)
        self.menu_text[0].changeText('Player '+str(self.player_num+1))
        
        
    def executeMenu(self, _screen):
        return SubMenu.executeMenu(self, _screen)
            
    def bindControls(self,_screen):
        key_id_map = {}
        for name, value in vars(pygame.constants).items():
            if name.startswith("K_"):
                key_id_map[value] = name
        
        self.status_text.changeText('To use a gamepad, press a button on that gamepad now')        
        selected_suboption = 0
        
        new_key_binding = {}
        
        held_keys = []
        working_keys = []
        
        status = 0
        ready = False
        while status == 0:
            music = musicManager.getMusicManager()
            music.doMusicEvent()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.status_text.changeText('')
                    return 0
                elif event.type == pygame.KEYDOWN:
                    value = (self.action_column[selected_suboption].text, event.key)
                    if value not in working_keys:
                        working_keys.append(value)
                    held_keys.append(event.key)
                elif event.type == pygame.KEYUP:
                    if event.key in held_keys:
                        held_keys.remove(event.key)
                        if not held_keys:
                            ready = True
                elif event.type == pygame.JOYBUTTONDOWN:
                    joystick = pygame.joystick.Joystick(event.joy)
                    
                    name = joystick.get_name()
                    settings = settingsManager.getSetting().setting
                    
                    if settingsManager.getSetting().loadGamepad(name):
                        settings['controlType_'+str(self.player_num)] = name
    
                    settingsManager.saveSettings(settings)
                    self.status_text.changeText('')
                    return 0
                
                if ready:
                    button_list = []
                    for action,key in working_keys:
                        new_key_binding[key] = action
                        button_list.append(key_id_map[key])
                    working_keys = []
                     
                    self.key_column[selected_suboption].changeText(str(button_list))
                    selected_suboption += 1
                    ready = False
                    
                    if selected_suboption >= len(self.action_column):
                        new_controller = engine.controller.Controller(new_key_binding)
                        settingsManager.getSetting().setting['controls_'+str(self.player_num)] = new_controller
                        settingsManager.getSetting().setting['control_type_'+str(self.player_num)] = 'Keyboard'
                        
                        settingsManager.getControls(self.player_num).timing_window['smash_window'] = self.smash_window
                        settingsManager.getControls(self.player_num).timing_window['repeat_window'] = self.repeat_window
                        settingsManager.getControls(self.player_num).timing_window['buffer_window'] = self.buffer_window
                        settingsManager.getControls(self.player_num).timing_window['smoothing_window'] = self.smoothing_window
            
                        settingsManager.saveSettings(settingsManager.getSetting().setting)
                        self.status_text.changeText('')
                        return 0
                        
            self._parent.bg.update(_screen)
            self._parent.bg.draw(_screen,(0,0),1.0)
            
            for m in self.menu_text:
                m.draw(_screen,m.rect.topleft,1.0)
                m.changeColor([55,55,55])
            for m in self.action_column:
                m.draw(_screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            for m in self.key_column:
                m.draw(_screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            
            self.status_text.draw(_screen, self.status_text.rect.topleft, 1.0)
        
            rgb = self._parent.bg.hsvtorgb(self._parent.bg.star_color)
            self.action_column[selected_suboption].changeColor(rgb)
            self.key_column[selected_suboption].changeColor(rgb)
            
            self.clock.tick(60)    
            pygame.display.update()

"""               
class PlayerControlsMenu(SubMenu):
    def __init__(self, _parent):
        SubMenu.__init__(self, _parent)
        self.menu_text = [spriteManager.TextSprite('Player 1','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Use Gamepad: None','full Pack 2025',20,[255,255,255]),
                         spriteManager.TextSprite('Exit','full Pack 2025',20,[255,255,255])]
        
        
        for i in range(0,len(self.menu_text)):
            self.menu_text[i].rect.centerx = self._parent.settings['windowSize'][0] / 2
            self.menu_text[i].rect.centery = 90 + i*60
                
        self.selected_option = 0
    
    def executeMenu(self, _screen):
        return SubMenu.executeMenu(self, _screen)
"""
 
class GraphicsMenu(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self,_parent)
        
        self.category_list = ['Window', 'Debug']
        self.current_category = 0
        
        self.left_column = {'Window': ['Resolution'],
                           'Debug': ['Display Hitboxes','Display Hurtboxes', 'Display Sprite Bounds', 'Display Platform Lines']
                           }
        
        self.right_column = {'Resolution': ['640 x 480','1024 x 768'],
                            'Display Hitboxes': ['On','Off'],
                            'Display Hurtboxes': ['On','Off'],
                            'Display Sprite Bounds': ['On','Off'],
                            'Display Platform Lines': ['On','Off'],
                            }
        self.selected = 0
        
        self.category_text = spriteManager.TextSprite('Window','full Pack 2025',24,[255,255,255])
        
        
        self.selected_option = 0
        
    def executeMenu(self,_screen):
        return 1
        

class SoundMenu(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self, _parent)
        
        self.settings = settingsManager.getSetting().setting
                
        self.selected_option = 0
        self.selected_block = 0
        
        self.music_vol = int(self.settings['music_volume'] * 10)
        self.sound_vol = int(self.settings['sfxVolume'] * 10)
        
        self.menu_text = [spriteManager.TextSprite('Music Volume: '+str(self.music_vol),'Orbitron Medium',16,[255,255,255]),
                         spriteManager.TextSprite('SFX Volume: '+str(self.sound_vol),'Orbitron Medium',16,[255,255,255]),
                         spriteManager.TextSprite('Save', 'full Pack 2025', 24, [255,255,255]),
                         spriteManager.TextSprite('Cancel', 'full Pack 2025', 24, [255,255,255]),
                         ]
        
        self.menu_text[0].rect.midtop = (self.settings['windowWidth'] / 2,80)
        self.menu_text[1].rect.midtop = (self.settings['windowWidth'] / 2,180)
        
        self.menu_text[2].rect.center = (self.settings['windowWidth'] / 3,self.settings['windowHeight'] - 64)
        self.menu_text[3].rect.center = ((self.settings['windowWidth'] / 3) * 2,self.settings['windowHeight'] - 64)
    
    def confirmOption(self, _optionNum):
        SubMenu.confirmOption(self, _optionNum)
        if _optionNum == 2:
            self.settings['music_volume'] = float(self.music_vol)/10
            self.settings['sfxVolume'] = float(self.sound_vol)/10
            pygame.mixer.music.set_volume(float(self.music_vol)/10)
            settingsManager.saveSettings(self.settings)
            self.status = 1
        elif _optionNum == 3:
            self.status = 1
    
    def incrementOption(self, _optionNum, _direction):
        SubMenu.incrementOption(self, _optionNum, _direction)
        if _optionNum == 0:
            self.music_vol += _direction
            if self.music_vol > 10: self.music_vol = 10
        elif _optionNum == 1:
            self.sound_vol += _direction
            if self.sound_vol > 10: self.sound_vol = 10
    
    def update(self, _screen):
        self.menu_text[0].changeText('Music Volume: '+str(self.music_vol))
        self.menu_text[1].changeText('SFX Volume: '+str(self.sound_vol))
        SubMenu.update(self, _screen)        
        
    def executeMenu(self,_screen):
        return SubMenu.executeMenu(self, _screen)

""" Modules and related Submenus """
class ModulesMenu(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self, _parent)
        self.menu_text = [
                         spriteManager.TextSprite('Back','full Pack 2025',24,[255,255,255])
                         ]
        self.status_text = spriteManager.TextSprite('Module Manager not yet available','Orbitron Medium',18,[255,255,255])
        
        self.menu_text[0].rect.centerx = settingsManager.getSetting('windowSize')[0] / 2
        self.menu_text[0].rect.bottom = settingsManager.getSetting('windowSize')[1] - 100
        
        self.status_text.rect.top = 50
        self.status_text.rect.centerx = settingsManager.getSetting('windowSize')[0] / 2
        
        self.selected_option = 0
    
    def update(self, _screen):
        SubMenu.update(self, _screen)
        self.status_text.draw(_screen,self.status_text.rect.topleft,1.0)
        
    def confirmOption(self, _optionNum):
        self.status = 1
        SubMenu.confirmOption(self, _optionNum)
        
    def executeMenu(self,_screen):
        return SubMenu.executeMenu(self, _screen)
        
class bgSpace(spriteManager.ImageSprite):
    def __init__(self):
        spriteManager.Sprite.__init__(self)
        self.image = pygame.surface.Surface(tuple(settingsManager.getSetting('windowSize')))
        self.rect = pygame.rect.Rect((0,0),self.image.get_size())
        
        self.stars = list()
        self.sprites = pygame.sprite.Group()
        self.star_color = [float(random.randint(0,100))/100,1.0,1.0]
        self.star_timer = 3
        
        for i in range(0,30):
            st = bgStar(random.randint(1,10))
            st.sprite.rect.x = random.randint(1,settingsManager.getSetting('windowSize')[0])
            st.changeColor(self.star_color)
            self.stars.append(st)
            self.sprites.add(st.sprite)
            
    def update(self,_screen):
        # create more stars
        self.star_timer -= 1
        if self.star_timer == 0:
            new_bg_star = bgStar(random.randint(1,10))
            self.stars.append(new_bg_star)
            self.sprites.add(new_bg_star.sprite)
            self.star_timer = 3
            
        # recolor stars
        self.star_color[0] += .001
        if self.star_color[0] > 1: self.star_color[0] -= 1
        
        for star in self.stars:
            star.changeColor(self.star_color)
            star.update()
            if star.sprite not in self.sprites:
                self.stars.remove(star)
        
        self.image.fill([0,0,0])
    
    def hsvtorgb(self,_hsv):
        return tuple(i * 255 for i in colorsys.hsv_to_rgb(_hsv[0],_hsv[1],_hsv[2]))
        
    def draw(self, _screen, _offset, _scale):
        _screen.blit(self.image,self.rect.topleft)
        self.sprites.draw(_screen)
        
class bgStar(engine.article.Article):
    def __init__(self,_dist):
        engine.article.Article.__init__(self, settingsManager.createPath("sprites/star.png"), None,
                                        (settingsManager.getSetting('windowSize')[0],random.randint(0,settingsManager.getSetting('windowSize')[1])), 1)
        self.dist = _dist
        self.color = [0,0,1]
        
        self.sprite.image = pygame.transform.scale(self.sprite.image, (9*(11-_dist)//10,9*(11-_dist)//10))
        
    def update(self):
        self.sprite.rect.x -= 11 - self.dist
        if self.sprite.rect.right <= 0: 
            self.sprite.kill()
    
    def hsvtorgb(self,_hsv):
        return tuple(i * 255 for i in colorsys.hsv_to_rgb(_hsv[0],_hsv[1],_hsv[2]))
    
    def changeColor(self,_toColor):
        from_color = self.hsvtorgb(self.color)
        true_color = self.hsvtorgb(_toColor)
        
        self.sprite.recolor(self.sprite.image, from_color, true_color)
        self.color = [_toColor[0],_toColor[1],_toColor[2]]
        

"""
Dirty, awful code that must be rewritten
"""
class GameSettingsMenu(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self, _parent)
        
        self.settings = settingsManager.getSetting().setting
        self.presets = self.settings['presetLists']
        
        self.current_preset = self.presets.index(self.settings['current_preset'])
        self.selection_slice = (0,10)
        
        self.selected_option = 0
        self.selected_block = 0
        self.menu_text = [spriteManager.TextSprite(self.presets[self.current_preset], 'full Pack 2025', 24, [255,255,255])]
                         #spriteManager.TextSprite('Cancel','full Pack 2025', 22, [255,255,255]),
                         #spriteManager.TextSprite('Save','full Pack 2025', 22, [255,255,255]),
                         #]
        
        num_list = [0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0]
        
        self.options = [OptionButton('Gravity Multiplier', num_list, (self.settings['gravity'])),
                        OptionButton('Weight Multiplier', num_list, (self.settings['weight'])),
                        OptionButton('Friction Multiplier', num_list, (self.settings['friction'])),
                        OptionButton('Air Mobility Multiplier', num_list, (self.settings['airControl'])),
                        OptionButton('Hit Stun Multiplier', num_list, (self.settings['hitstun'])),
                        OptionButton('Hit Lag Multiplier', num_list, (self.settings['hitlag'])),
                        OptionButton('Shield Stun Multiplier', num_list, (self.settings['shieldStun'])),
                        
                        OptionButton('Ledge Conflict Type', ['hog','trump','share'], (self.settings['ledgeConflict'])),
                        OptionButton('Ledge Sweetspot Size', [[128,128],[64,64],[32,32]], (self.settings['ledgeSweetspotSize'])),
                        OptionButton('Ledge Grab Only When Facing', [True, False], (self.settings['ledgeSweetspotForwardOnly'])),
                        OptionButton('Team Ledge Conflict', [True, False], (self.settings['teamLedgeConflict'])),
                        OptionButton('Ledge Invincibility Time', range(0,300,5), (self.settings['ledgeInvincibilityTime'])),
                        OptionButton('Regrab Invincibility', [True, False], (self.settings['regrabInvincibility'])),
                        OptionButton('Slow Ledge Getup Damage Threshold', range(0,300,5), (self.settings['slowLedgeWakeupThreshold'])),
                        
                        ]
            
        self.menu_text[0].rect.centerx = self.settings['windowSize'][0] / 2
        self.menu_text[0].rect.top = 50
    
    def updateMenuText(self):
        settingsManager.getSetting().loadGameSettings(self.presets[self.current_preset])
        self.selection_slice = (0,10)
        
        num_list = [0.5,0.6,0.7,0.8,0.9,1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.7,1.8,1.9,2.0]
        
        self.options = [OptionButton('Gravity Multiplier', num_list, (self.settings['gravity'])),
                        OptionButton('Weight Multiplier', num_list, (self.settings['weight'])),
                        OptionButton('Friction Multiplier', num_list, (self.settings['friction'])),
                        OptionButton('Air Mobility Multiplier', num_list, (self.settings['airControl'])),
                        OptionButton('Hit Stun Multiplier', num_list, (self.settings['hitstun'])),
                        OptionButton('Hit Lag Multiplier', num_list, (self.settings['hitlag'])),
                        OptionButton('Shield Stun Multiplier', num_list, (self.settings['shieldStun'])),
                        
                        OptionButton('Ledge Conflict Type', ['hog','trump','share'], (self.settings['ledgeConflict'])),
                        OptionButton('Ledge Sweetspot Size', [[128,128],[64,64],[32,32]], (self.settings['ledgeSweetspotSize'])),
                        OptionButton('Ledge Grab Only When Facing', [True, False], (self.settings['ledgeSweetspotForwardOnly'])),
                        OptionButton('Team Ledge Conflict', [True, False], (self.settings['teamLedgeConflict'])),
                        OptionButton('Ledge Invincibility Time', range(0,300,5), (self.settings['ledgeInvincibilityTime'])),
                        OptionButton('Regrab Invincibility', [True, False], (self.settings['regrabInvincibility'])),
                        OptionButton('Slow Ledge Getup Damage Threshold', range(0,300,5), (self.settings['slowLedgeWakeupThreshold'])),
                        
                        ]
        
    def updateSlice(self):
        if self.selected_option <= self.selection_slice[0] and self.selection_slice[0] > 0:
            diff = self.selection_slice[0] - self.selected_option
            self.selection_slice = (self.selection_slice[0]-diff, self.selection_slice[1]-diff)
        if self.selected_option >= (self.selection_slice[1]-1) and self.selection_slice[1] <= len(self.options):
            diff = self.selected_option - (self.selection_slice[1] -1)
            self.selection_slice = (self.selection_slice[0]+diff, self.selection_slice[1]+diff)
        
    def executeMenu(self,_screen):
        return 1 #this one needs a total overhaul
        clock = pygame.time.Clock()
        controls = settingsManager.getControls('menu')
        can_press = True
        holding = {'up': False,'down': False,'left': False,'right': False}
        
        while self.status == 0:
            self.update(_screen)
            music = musicManager.getMusicManager()
            music.doMusicEvent()
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    holding[controls.get(event.key)] = True
                    if event.key == K_ESCAPE or controls.get(event.key) == 'cancel':
                        if self.selected_block == 0:
                            self.status = 1
                        else:
                            self.selected_block = 0
                            self.selection_slice = (0,10)
                            self.selected_option = 0
                            for opt in self.options:
                                opt.changeColor([100,100,100])
                                
                    '''if controls.get(event.key) == 'left':
                        if self.selected_block == 0 and self.selected_option == 0: #currently selecting preset switcher
                            self.current_preset -= 1
                            self.current_preset = self.current_preset % len(self.presets)
                            self.menu_text[0].changeText(self.presets[self.current_preset])
                            self.updateMenuText()
                        if self.selected_block == 1:
                            self.options[self.selected_option].incVal(-1)
                            
                            
                    if controls.get(event.key) == 'right':
                        if self.selected_block == 0 and self.selected_option == 0: #currently selecting preset switcher
                            self.current_preset += 1
                            self.current_preset = self.current_preset % len(self.presets)
                            self.menu_text[0].changeText(self.presets[self.current_preset])
                            self.updateMenuText()
                        if self.selected_block == 1:
                            self.options[self.selected_option].incVal(1)
                            
                    if controls.get(event.key) == 'down':
                        if self.selected_block == 0:
                            self.selected_option += 1
                            self.selected_option = self.selected_option % len(self.menu_text)
                        else:
                            self.selected_option += 1
                            self.selected_option = self.selected_option % len(self.options)
                            self.updateSlice()
                            
                    if controls.get(event.key) == 'up':
                        if self.selected_block == 0:
                            self.selected_option -= 1
                            self.selected_option = self.selected_option % len(self.menu_text)
                        else:
                            self.selected_option -= 1
                            self.selected_option = self.selected_option % len(self.options)
                            self.updateSlice()'''
                                        
                    if controls.get(event.key) == 'confirm':
                        if self.selected_block == 0: #not editing a preset
                            if self.selected_option == 0: #selecting a preset
                                self.selected_block = 1
                                self.selected_option = 0
                                self.selection_slice = (0,10)
                                for opt in self.options:
                                    opt.changeColor([255,255,255])

                if event.type == KEYUP:
                    holding[controls.get(event.key)] = False;

                if event.type == pygame.USEREVENT+1:
                    can_press = True;
                                    
                if event.type == QUIT:
                    self.status = -1

            for key_name,key_value in holding.items():
                if key_value and can_press: 
                    can_press = False
                    pygame.time.set_timer(pygame.USEREVENT+1,200)
                    if key_name == 'left':
                        if self.selected_block == 0 and self.selected_option == 0: #currently selecting preset switcher
                            self.current_preset -= 1
                            self.current_preset = self.current_preset % len(self.presets)
                            self.menu_text[0].changeText(self.presets[self.current_preset])
                            self.updateMenuText()
                        if self.selected_block == 1:
                            self.options[self.selected_option].incVal(-1)
                    if key_name == 'right':
                        if self.selected_block == 0 and self.selected_option == 0: #currently selecting preset switcher
                            self.current_preset += 1
                            self.current_preset = self.current_preset % len(self.presets)
                            self.menu_text[0].changeText(self.presets[self.current_preset])
                            self.updateMenuText()
                        if self.selected_block == 1:
                            self.options[self.selected_option].incVal(1)
                    if key_name == 'down':
                        if self.selected_block == 0:
                            self.selected_option += 1
                            self.selected_option = self.selected_option % len(self.menu_text)
                        else:
                            self.selected_option += 1
                            self.selected_option = self.selected_option % len(self.options)
                            self.updateSlice()
                    if key_name == 'up':
                        if self.selected_block == 0:
                            self.selected_option -= 1
                            self.selected_option = self.selected_option % len(self.menu_text)
                        else:
                            self.selected_option -= 1
                            self.selected_option = self.selected_option % len(self.options)
                            self.updateSlice()

            self._parent.bg.update(_screen)
            self._parent.bg.draw(_screen,(0,0),1.0)
            
            self.menu_text[0].draw(_screen,self.menu_text[0].rect.topleft,1.0)
            
            for m in self.menu_text:
                m.draw(_screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            
            vert_off = 100
            for opt in self.options[self.selection_slice[0]:self.selection_slice[1]]:
                opt.setHeight(vert_off)
                opt.draw(_screen,(0,0),1.0)
                if self.selected_block == 1:
                    opt.changeColor([255,255,255])
                vert_off += 25
                
            rgb = self._parent.bg.hsvtorgb(self._parent.bg.star_color)
            if self.selected_block == 0:
                self.menu_text[self.selected_option].changeColor(rgb)
            else:
                self.options[self.selected_option].changeColor(rgb)
                
            #self.menu_text.draw(_screen, (128,128), 1.0)
            clock.tick(60)    
            pygame.display.flip()
            
        return self.status

        
class OptionButton(spriteManager.TextSprite):
    def __init__(self, _name, _vals, _startingVal):
        spriteManager.Sprite.__init__(self)
        
        self.possibleVals = _vals
        if _startingVal in _vals:
            self.selected_value = self.possibleVals.index(_startingVal) 
        else:
            print("Not in list of options")
            self.selected_value = 0
        
        self.name_text = spriteManager.TextSprite(_name, 'Orbitron Medium',18,[100,100,100])
        self.name_text.rect.left = 20
        
        self.val_text = spriteManager.TextSprite(str(self.possibleVals[self.selected_value]), 'Orbitron Medium',18,[100,100,100])
        self.val_text.rect.right = 620
        
    def changeColor(self,_color):
        self.name_text.changeColor(_color)
        self.val_text.changeColor(_color)
        
    def getValue(self):
        return self.possibleVals[self.selected_value]
    
    def update(self):
        pass
    
    def incVal(self,_inc):
        self.selected_value += _inc
        self.selected_value = self.selected_value % len(self.possibleVals)
        
    def changeVal(self,_val):
        if _val in self.possibleVals:
            self.selected_value = self.possibleVals.index(_val)
    
    def setHeight(self,_top):
        self.name_text.rect.top = _top
        self.val_text.rect.top = _top
        
    def draw(self,_screen,_offset,_scale):
        self.val_text.text = str(self.getValue())
        self.name_text.draw(_screen, self.name_text.rect.topleft, _scale)
        self.val_text.draw(_screen, self.val_text.rect.topleft, _scale)  

class RebindMenu(SubMenu):
    def __init__(self,_parent):
        self.key_id_map = {}
        self.key_name_map = {}
        for name, value in vars(pygame.constants).items():
            if name.startswith("K_"):
                self.key_id_map[value] = name
                self.key_name_map[name] = value
        SubMenu.__init__(self,_parent)
        self.menu_text = [spriteManager.TextSprite('','full Pack 2025',25,[255,255,255]),
                         spriteManager.TextSprite('Hold keys to bind multiple','full Pack 2025',15,[255,255,255]),
                         spriteManager.TextSprite('Press ','full Pack 2025',15,[255,255,255])]
        self.menu_text[0].rect.center = (self._parent.settings['windowSize'][0] / 2,self._parent.settings['windowSize'][1] / 2)
        self.menu_text[1].rect.center = (self._parent.settings['windowSize'][0] / 2,self._parent.settings['windowSize'][1] / 6) 
        self.menu_text[2].rect.center = (self._parent.settings['windowSize'][0] / 2,self._parent.settings['windowSize'][1] *  5 / 6)
        self.status = 0
        
    def executeMenu(self,_screen,_toBind):
        clock = pygame.time.Clock()
        not_bound = True
        bindings = []
        current_string = ''
        keys_down = 0
        self.menu_text[2].changeText('Press '+ _toBind)
        
        while self.status == 0:
            music = musicManager.getMusicManager()
            music.doMusicEvent()
            current_string = ''
            for i in range(0,len(bindings)):
                current_string += self.key_id_map[bindings[i]][2:]
                if i < len(bindings) - 1:
                    current_string += ' - '
            self.menu_text[0].changeText(current_string)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    bindings.append(event.key);
                    keys_down += 1
                if event.type == KEYUP:
                    keys_down -= 1
                    not_bound = False
            if keys_down < 0:
                not_bound = True
                keys_down = 0
            if keys_down == 0 and not not_bound:
                return bindings
            self._parent.bg.update(_screen)
            self._parent.bg.draw(_screen,(0,0),1.0)
            for text in self.menu_text:
                text.draw(_screen, text.rect.topleft, 1.0)
            
            rgb = self._parent.bg.hsvtorgb(self._parent.bg.star_color)
            self.menu_text[0].changeColor(rgb)
            pygame.display.flip()
            clock.tick(60)

class RebindIndividual(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self,_parent)
        self.menu_text = []
        self.labels = ('left','right','up','down','attack','special','jump','shield')
        for label in self.labels:
            self.menu_text.append(spriteManager.TextSprite(label + ' - ','full Pack 2025',20,[255,255,255]))
        self.menu_text.append(spriteManager.TextSprite('Save','full Pack 2025',20,[255,255,255]))
        self.menu_text.append(spriteManager.TextSprite('Cancel','full Pack 2025',20,[255,255,255]))
        for i in range(0,len(self.menu_text)):
            self.menu_text[i].rect.centerx = self._parent.settings['windowSize'][0] / 2
            self.menu_text[i].rect.centery = 60 + i*50
        self.menu_text[len(self.menu_text)-2].rect.centerx = self._parent.settings['windowSize'][0] / 3
        self.menu_text[len(self.menu_text)-1].rect.centerx = self._parent.settings['windowSize'][0] * 2 / 3
        self.menu_text[len(self.menu_text)-2].rect.centery = self._parent.settings['windowSize'][1] - 25 
        self.menu_text[len(self.menu_text)-1].rect.centery = self._parent.settings['windowSize'][1] - 25
        self.selected_option = 0

    def executeMenu(self,_screen):
        controls = settingsManager.getControls('menu')
        clock = pygame.time.Clock()
        holding = {'up': False,'down': False,'left': False,'right': False}
        
        while self.status == 0:
            self.update(_screen)
            music = musicManager.getMusicManager()
            music.doMusicEvent()
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
                    can_press = True;

            for key_name,key_value in holding.items():
                if key_value and can_press:
                    can_press = False
                    pygame.time.set_timer(pygame.USEREVENT+1,150)
                    if key_name == 'down':
                        self.selected_option += 1
                        self.selected_option = self.selected_option % len(self.menu_text)
                    if key_name == 'up':
                        self.selected_option -= 1
                        self.selected_option = self.selected_option % len(self.menu_text)
                    if key_name == 'left' or key_name == 'right':
                        if self.selected_option == 8:
                            self.selected_option = 9
                        elif self.selected_option == 9:
                            self.selected_option = 8
                    

            self._parent.bg.update(_screen)
            self._parent.bg.draw(_screen,(0,0),1.0)
            
            for m in self.menu_text:
                m.draw(_screen,m.rect.topleft,1.0)
                m.changeColor([255,255,255])
            rgb = self._parent.bg.hsvtorgb(self._parent.bg.star_color)
            self.menu_text[self.selected_option].changeColor(rgb)
                
            #self.menu_text.draw(_screen, (128,128), 1.0)
            clock.tick(60)    
            pygame.display.flip()
                    

        return self.status


"""
class UpdateMenu(SubMenu):
    def __init__(self,_parent):
        SubMenu.__init__(self, _parent)
        self.menu_text = [spriteManager.TextSprite('Check','full Pack 2025',24,[255,255,255]),
                         spriteManager.TextSprite('Cancel','full Pack 2025',24,[255,255,255])]
        
        self.status_text = spriteManager.TextSprite('','Orbitron Medium',24,[255,255,255])
        
        self.menu_text[0].rect.centerx = self._parent.settings['windowSize'][0] / 3
        self.menu_text[1].rect.centerx = (self._parent.settings['windowSize'][0] / 3)*2
        self.menu_text[0].rect.centery = self._parent.settings['windowSize'][1] - 100
        self.menu_text[1].rect.centery = self._parent.settings['windowSize'][1] - 100
        
        self.change_list = None
        self.checked_list = False
        self.confirm_enabled = True
        
        self.selected_option = 0
        
        self.update_thread = updater.UpdateThread(self)
        
    def executeMenu(self, _screen):
        SubMenu.executeMenu(self, _screen)
    
    def incrementOption(self,_option,_direction):
        if self.selected_option == 0:
            self.selected_option = 1
        elif self.selected_option == 1:
            self.selected_option = 0
    
    def confirmOption(self,_optionNum):
        if _optionNum == 0 and not self.update_thread.running:
            if not self.checked_list:
                self.update_thread.start()
                self.confirm_enabled = False
                self.menu_text[0].changeColor([55,55,55])
            else:
                if self.change_list:
                    self.update_thread.start()
           
        elif _optionNum == 1:
            self.update_thread
            self.status = 1
        
    def update(self, _screen):
        self._parent.bg.update(_screen)
        self._parent.bg.draw(_screen,(0,0),1.0)
        
        if not self.confirm_enabled:
            self.menu_text[0].changeColor([55,55,55])
            if self.selected_option == 0:
                self.selected_option = 1
        
        for m in self.menu_text:
            m.draw(_screen,m.rect.topleft,1.0)
            m.changeColor([255,255,255])
        
        rgb = self._parent.bg.hsvtorgb(self._parent.bg.star_color)
        self.menu_text[self.selected_option].changeColor(rgb)    
        
        if self.checked_list:
            if self.changed_list == False:
                self.status_text.changeText('Unable to update. Please try again later')
            elif self.change_list == []:
                self.status_text.changeText('No update available')
            else:
                self.status_text.changeText('Update is available')
                self.update_thread.mode = 1
                self.confirm_enabled = True
                self.menu_text[0].changeText('Update')
                self.menu_text[0].changeColor(rgb)
                self.selected_option = 0
                
            self.recenterStatus()
        self.status_text.draw(_screen, self.status_text.rect.topleft, 1.0)
     
    def recenterStatus(self):
        self.status_text.rect.centerx = self._parent.settings['windowSize'][0] / 2
"""

if __name__  == '__main__': main()
