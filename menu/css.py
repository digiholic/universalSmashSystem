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
        self.playerPanels = [PlayerPanel(0)]
        self.wheel = FighterWheel()
        self.wheelIncrement = 0
        self.holdtime = 0
        self.holdDistance = 0
        
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.wheelIncrement = -1
                    elif event.key == pygame.K_RIGHT:
                        self.wheelIncrement = 1
                    elif event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_z:
                        print self.wheel.fighterAt(0)
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                        self.wheelIncrement = 0
                        self.holdDistance = 0
                        self.holdtime = 0
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
            screen.fill((128, 128, 128))
            self.wheel.draw(screen)
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
        
    def draw(self,screen):
        center = 224
        blankImage = pygame.Surface([512,64], pygame.SRCALPHA, 32).convert_alpha()
        blankImage.blit(self.visibleSprites[0].image, [center,0])
        for i in range(1,(self.wheelSize/2)+1):
            blankImage.blit(self.visibleSprites[2*i-1].image, [center + (64*i),0])
            blankImage.blit(self.visibleSprites[2*i].image, [center - (64*i),0])
        
        blankImage.blit(self.wheelShadow.image,[0,0])
        screen.blit(blankImage, [64,256])
                     
    def getFighterPortrait(self,fighter):
        portrait = fighter.cssIcon()
        if portrait == None:
            portrait = spriteManager.ImageSprite(os.path.join(os.path.dirname(settingsManager.__file__),"sprites","icon_unknown.png"))
        return portrait

class PlayerPanel(pygame.Surface):
    def __init__(self,playerNum):
        pygame.Surface.__init__(settingsManager.getSetting('windowWidth')/2,
                                settingsManager.getSetting('windowHeight')/2)
        self.playerNum = playerNum
        self.wheel = FighterWheel()
        self.active = False
        self.controls = settingsManager.getSetting('controls_' + str(playerNum))
        
    def draw(self,screen):
        self.wheel.draw(screen)
        
if __name__  == '__main__': CSSScreen()