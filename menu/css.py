import settingsManager
import spriteManager
import os
import imp
import pygame
import menu

class CSSScreen():
    def __init__(self):
        settings = settingsManager.getSetting().setting
        
        self.height = settings['windowHeight']
        self.width = settings['windowWidth']
        
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(settings['windowName'])
        
        background = pygame.Surface(screen.get_size())
        background = background.convert()
    
        clock = pygame.time.Clock()
        self.playerControls = []
        self.playerPanels = []
        
        for i in range(0,4):
            self.playerControls.append(settingsManager.getControls(i))
            self.playerPanels.append(PlayerPanel(i))
        
        while 1:
            #Start event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
                    
                    for i,bindings in enumerate(self.playerControls):
                        if event.key == bindings['left']:
                            self.playerPanels[i].keyPressed('left')    
                        elif event.key == bindings['right']:
                            self.playerPanels[i].keyPressed('right')
                        elif event.key == bindings['attack']:
                            self.playerPanels[i].keyPressed('confirm')
                        #TODO: Fix this when special button is added
                        elif event.key == bindings['shield']:
                            self.playerPanels[i].keyPressed('cancel')
                            
                elif event.type == pygame.KEYUP:
                    for i,bindings in enumerate(self.playerControls):
                        if event.key == bindings['left']:
                            self.playerPanels[i].keyReleased('left')
                        elif event.key == bindings['right']:
                            self.playerPanels[i].keyReleased('right')             
            #End event loop
            
            screen.fill((128, 128, 128))
            for panel in self.playerPanels:
                panel.update()
                panel.draw(screen)
                
            pygame.display.flip()
            clock.tick(60)
        
class FighterWheel():
    def __init__(self):
        self.fighters = []
        
        # Load all files.
        directory = os.path.join(os.path.dirname(settingsManager.__file__),"fighters")
        fightercount = 0
        for subdir in next(os.walk(directory))[1]:
            fighter = settingsManager.importFromURI(directory, os.path.join(directory,subdir,"fighter.py"),suffix=str(fightercount))
            fightercount += 1
            self.fighters.append(fighter)      
        
        self.currentIndex = 0
        self.currentFighter = self.fighters[0]
        self.wheelSize = 9
        self.visibleSprites = [None for _ in range(self.wheelSize)]
        self.animateWheel()
        self.wheelShadow = spriteManager.ImageSprite(os.path.join(os.path.dirname(settingsManager.__file__),"sprites/cssbar_shadow.png"))
        
    def changeSelected(self,increment):
        self.currentIndex = self.currentIndex + increment
        self.currentFighter = self.fighters[self.currentIndex % len(self.fighters)]
        self.animateWheel()
        
    def fighterAt(self,offset):
        return self.fighters[(self.currentIndex + offset) % len(self.fighters)]
    
    def animateWheel(self):
        self.visibleSprites[0] = self.getFighterPortrait(self.fighterAt(0))
        for i in range(1,(self.wheelSize/2)+1):
            self.visibleSprites[2*i-1] = self.getFighterPortrait(self.fighterAt(i))
            self.visibleSprites[2*i] = self.getFighterPortrait(self.fighterAt(-1 * i))
                        
        [spriteManager.ImageSprite.alpha(sprite, 128) for sprite in self.visibleSprites]
        self.visibleSprites[0].alpha(255)
        
    def draw(self, screen, location):
        center = 112
        blankImage = pygame.Surface([256,32], pygame.SRCALPHA, 32).convert_alpha()
        blankImage.blit(self.visibleSprites[0].image, [center,0])
        for i in range(1,(self.wheelSize/2)+1):
            blankImage.blit(self.visibleSprites[2*i-1].image, [center + (32*i),0])
            blankImage.blit(self.visibleSprites[2*i].image, [center - (32*i),0])
        
        blankImage.blit(self.wheelShadow.image,[0,0])
        screen.blit(blankImage, location)
                     
    def getFighterPortrait(self,fighter):
        portrait = fighter.cssIcon()
        if portrait == None:
            portrait = spriteManager.ImageSprite(os.path.join(os.path.dirname(settingsManager.__file__),"sprites","icon_unknown.png"))
        return portrait

class PlayerPanel(pygame.Surface):
    def __init__(self,playerNum):
        pygame.Surface.__init__(self,(settingsManager.getSetting('windowWidth')/2,
                                settingsManager.getSetting('windowHeight')/2))
        
        print self.get_size()
        self.keys = settingsManager.getControls(playerNum)
        self.playerNum = playerNum
        self.wheel = FighterWheel()
        self.active = False
        
        self.wheelIncrement = 0
        self.holdtime = 0
        self.holdDistance = 0
        self.wheelOffset = [(self.get_width() - 256) / 2,
                            (self.get_height() - 32)]
    
    def update(self):
        if self.wheelIncrement != 0:
            if self.holdtime > self.holdDistance:
                if self.holdDistance == 0:
                    self.holdDistance = 30
                elif self.holdDistance == 30:
                    self.holdDistance = 20
                elif self.holdDistance == 20:
                    self.holdDistance = 10
                settingsManager.getSfx().playSound('selectL')
                self.wheel.changeSelected(self.wheelIncrement)
                self.holdtime = 0
            else:
                self.holdtime += 1
                
    def keyPressed(self,key):
        if key != 'cancel' and self.active == False:
            self.active = True
            return
        if key == 'cancel' and self.active == True:
            self.active = False
            return
        #TODO: Add more sound effects and shutter sprite
        
        if key == 'left':      self.wheelIncrement = -1
        elif key == 'right':   self.wheelIncrement = 1
        elif key == 'confirm': print self.wheel.fighterAt(0)
                
    def keyReleased(self,key):
        if key == 'right' or key == 'left':
            self.wheelIncrement = 0
            self.holdDistance = 0
            self.holdtime = 0
    
    def draw(self,screen):
        if self.active:
            self.fill((0,0,0))
            self.wheel.draw(self,self.wheelOffset)
        else:
            self.fill(pygame.Color(settingsManager.getSetting('playerColor' + str(self.playerNum))))
            #draw closed shutter
        offset = [0,0]
        if self.playerNum == 1 or self.playerNum == 3: offset[0] = self.get_width()
        if self.playerNum == 2 or self.playerNum == 3: offset[1] = self.get_height()
        screen.blit(self,offset)
        
if __name__  == '__main__': CSSScreen()