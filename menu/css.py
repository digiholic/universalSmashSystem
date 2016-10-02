import settingsManager
import spriteManager
import os
import imp
import pygame
import battle
import sys
import stages.true_arena as stage
import engine.cpuPlayer as cpuPlayer
import engine.abstractFighter as abstractFighter
import sss
import musicManager

class CSSScreen():
    def __init__(self,_rules=None):
        settings = settingsManager.getSetting().setting
        
        self.rules = _rules
        self.height = settings['windowHeight']
        self.width = settings['windowWidth']
        
        pygame.init()
        screen = pygame.display.get_surface()
        
        background = pygame.Surface(screen.get_size())
        background = background.convert()
    
        clock = pygame.time.Clock()
        self.player_controls = []
        self.player_panels = []
        
        for i in range(0,4):
            self.player_controls.append(settingsManager.getControls(i))
            self.player_panels.append(PlayerPanel(i))
            self.player_controls[i].fighter = self.player_panels[i] #So playerPanel will take the inputs
            self.player_controls[i].flushInputs()
        
        status = 0
        musicManager.getMusicManager().stopMusic(100)
        
        while status == 0:
            music = musicManager.getMusicManager()
            music.doMusicEvent()
            if not musicManager.getMusicManager().isPlaying():
                musicManager.getMusicManager().rollMusic('css')
            
            #Start event loop
            for bindings in self.player_controls:
                bindings.passInputs()
                
            for event in pygame.event.get():
                
                for bindings in self.player_controls:
                    k = bindings.getInputs(event)
                    if k == 'attack':
                        if self.checkForSelections():
                            sss.StageScreen(self.rules,self.getFightersFromPanels())
                            for panel in self.player_panels:
                                panel.active_object = panel.wheel
                                panel.chosen_fighter = None
                                panel.bg_surface = None                
                            for i in range(0,4):
                                self.player_controls[i].fighter = self.player_panels[i] #So playerPanel will take the inputs
                                self.player_controls[i].flushInputs()
                if event.type == pygame.QUIT:
                    status = -1
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        status = 1          
            #End event loop
            
            screen.fill((128, 128, 128))
            for panel in self.player_panels:
                panel.update()
                panel.draw(screen)
                
            pygame.display.flip()
            clock.tick(60)

    def checkForSelections(self):
        for panel in self.player_panels:
            if panel.active and panel.chosen_fighter == None:
                return False
        if not any([x.active for x in self.player_panels]):
            return False
        return True
    
    def getFightersFromPanels(self):
        fighter_list = []
        for panel in self.player_panels:
            if panel.active:
                fighter_list.append(panel.chosen_fighter)
        return fighter_list
    
class CSSWidget():
    def __init__(self,_panel,_displayList,_choicesList):
        self.previous_widget = None
        self.next_widget = None
        self.panel = _panel
        self.choices = []
        for i,key in _displayList:
            self.choices.append((key,_choicesList[i]))
        
    def onConfirm(self):
        pass
    
    def draw(self):
        pass
       
class FighterWheel():
    def __init__(self,_playerNum):
        self.fighters = []
        
        # Load all files.
        directory = settingsManager.createPath("fighters")
        fighter_count = 0
        for subdir in next(os.walk(directory))[1]:
            if(subdir == '__pycache__'):
                continue
            fighter_py = settingsManager.importFromURI(directory, os.path.join(directory,subdir,"fighter.py"),_suffix=str(fighter_count))
            #try:
            if fighter_py:
                fighter = fighter_py.getFighter(os.path.join(directory,subdir),_playerNum)
            else:
                fighter = abstractFighter.AbstractFighter(os.path.join(directory,subdir),_playerNum)
            if (fighter == None):
                print("No fighter found at " + os.path.join(directory,subdir,"fighter.py"))
            else:
                fighter_count += 1
                self.fighters.append(fighter)      
        
        self.current_index = 0
        self.current_fighter = self.fighters[0]
        self.wheel_size = 9
        self.visible_sprites = [None for _ in range(self.wheel_size)]
        self.animateWheel()
        self.wheel_shadow = spriteManager.ImageSprite(settingsManager.createPath(os.path.join("sprites","cssbar_shadow.png")))
        
    def changeSelected(self,_increment):
        self.current_index = self.current_index + _increment
        self.current_fighter = self.fighters[self.current_index % len(self.fighters)]
        self.animateWheel()
        
    def fighterAt(self,_offset):
        return self.fighters[(self.current_index + _offset) % len(self.fighters)]
    
    def animateWheel(self):
        self.visible_sprites[0] = self.fighterAt(0).css_icon
        for i in range(1,(self.wheel_size//2)+1):
            self.visible_sprites[2*i-1] = self.fighterAt(i).css_icon
            self.visible_sprites[2*i] = self.fighterAt(-1 * i).css_icon
                        
        [spriteManager.ImageSprite.alpha(sprite, 128) for sprite in self.visible_sprites]
        self.visible_sprites[0].alpha(255)
        
    def draw(self, _screen, _location):
        center = 112
        blank_image = pygame.Surface([256,32], pygame.SRCALPHA, 32).convert_alpha()
        blank_image.blit(self.visible_sprites[0].image, [center,0])
        for i in range(1,(self.wheel_size//2)+1):
            blank_image.blit(self.visible_sprites[2*i-1].image, [center + (32*i),0])
            blank_image.blit(self.visible_sprites[2*i].image, [center - (32*i),0])
        
        blank_image.blit(self.wheel_shadow.image,[0,0])
        _screen.blit(blank_image, _location)
        
class PlayerPanel(pygame.Surface):
    def __init__(self,_playerNum):
        pygame.Surface.__init__(self,(settingsManager.getSetting('windowWidth')//2,
                                settingsManager.getSetting('windowHeight')//2))
        
        self.keys = settingsManager.getControls(_playerNum)
        self.player_num = _playerNum
        self.wheel = FighterWheel(_playerNum)
        self.active = False
        self.ready = False
        self.active_object = self.wheel
        self.chosen_fighter = None
        self.myBots = []
        
        self.wheel_increment = 0
        self.hold_time = 0
        self.hold_distance = 0
        self.wheel_offset = [(self.get_width() - 256) // 2,
                            (self.get_height() - 32)]
        self.bg_surface = None
        self.current_color = _playerNum
    
    def update(self):
        if self.wheel_increment != 0:
            if self.hold_time > self.hold_distance:
                if self.hold_distance == 0:
                    self.hold_distance = 30
                elif self.hold_distance == 30:
                    self.hold_distance = 20
                elif self.hold_distance == 20:
                    self.hold_distance = 10
                settingsManager.getSfx().playSound('selectL')
                self.wheel.changeSelected(self.wheel_increment)
                self.hold_time = 0
            else:
                self.hold_time += 1
                
        if self.bg_surface and self.bg_surface.get_alpha() > 128:
            self.bg_surface.set_alpha(self.bg_surface.get_alpha() - 10)
                
    def keyPressed(self,_key):
        if _key != 'special' and self.active == False:
            self.active = True
            return
        if _key == 'special' and self.active == True:
            if len(self.myBots) > 0:
                pass #will disable bots
            elif self.active_object == self.wheel:
                self.active = False
                return
            else:
                self.active_object = self.wheel
                self.chosen_fighter = None
                self.bg_surface = None
                return
        #TODO: Add more sound effects and shutter sprite
        
        if _key == 'left':
            if self.active_object == self.wheel:
                self.wheel_increment = -1
                self.current_color = self.player_num
                print('current color:',self.current_color)
        elif _key == 'right':
            if self.active_object == self.wheel:
                self.wheel_increment = 1
                self.current_color = self.player_num
                print('current color:',self.current_color)
        elif _key == 'attack':
            if self.active_object == self.wheel:
                self.bg_surface = self.copy()
                self.bg_surface.set_alpha(240)
                self.active_object = None
                self.chosen_fighter = self.wheel.fighterAt(0)
                self.chosen_fighter.current_color = self.current_color
        elif _key == 'jump':
            self.current_color += 1
            print('current color:',self.current_color)
        elif _key == 'shield':
            pass #add bot
        
    def keyReleased(self,_key):
        if _key == 'right' or _key == 'left':
            self.wheel_increment = 0
            self.hold_distance = 0
            self.hold_time = 0
    
    def draw(self,_screen):
        if self.active:
            self.fill((0,0,0))
            if self.bg_surface:
                self.blit(self.bg_surface,[0,0])
            else:
                self.wheel.draw(self,self.wheel_offset)
        else:
            self.fill(pygame.Color(settingsManager.getSetting('playerColor' + str(self.player_num))))
            #draw closed shutter
        offset = [0,0]
        if self.player_num == 1 or self.player_num == 3: offset[0] = self.get_width()
        if self.player_num == 2 or self.player_num == 3: offset[1] = self.get_height()
        _screen.blit(self,offset)
