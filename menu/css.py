import settingsManager
import spriteManager
import os
import imp
import pygame
import menu
import battle
import sys
import stages.true_arena as stage
import engine.cpuPlayer as cpuPlayer
try:
    import sss
except ImportError:
    from menu import sss
import musicManager
class CSSScreen():
    def __init__(self,rules=None,botlist=[False,False,False,False]):
        settings = settingsManager.getSetting().setting
        
        self.rules = rules
        self.botList = botlist
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
            self.playerControls[i].fighter = self.playerPanels[i] #So playerPanel will take the inputs
            self.playerControls[i].flushInputs()
        
        status = 0
        musicManager.getMusicManager().stopMusic(100)
        
        while status == 0:
            if not musicManager.getMusicManager().isPlaying():
                musicManager.getMusicManager().rollMusic('css')
            
            #Start event loop
            for bindings in self.playerControls:
                bindings.passInputs()
                
            for event in pygame.event.get():
                for bindings in self.playerControls:
                    k = bindings.getInputs(event)
                    if k == 'attack':
                        if self.checkForSelections():
                            sss.StageScreen(self.rules,self.getFightersFromPanels(),self.getCPUPlayers())
                            for panel in self.playerPanels:
                                panel.activeObject = panel.wheel
                                panel.chosenFighter = None
                                panel.bgSurface = None                
                            for i in range(0,4):
                                self.playerControls[i].fighter = self.playerPanels[i] #So playerPanel will take the inputs
                                self.playerControls[i].flushInputs()
                if event.type == pygame.QUIT:
                    status = -1
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        status = 1          
            #End event loop
            
            screen.fill((128, 128, 128))
            for panel in self.playerPanels:
                panel.update()
                panel.draw(screen)
                
            pygame.display.flip()
            clock.tick(60)

    def checkForSelections(self):
        for panel in self.playerPanels:
            if panel.active and panel.chosenFighter == None:
                return False
        if not any([x.active for x in self.playerPanels]):
            return False
        return True
    
    def getFightersFromPanels(self):
        fighterList = []
        for num,panel in enumerate(self.playerPanels):
            if panel.active:
                fighterList.append(panel.chosenFighter.getFighter(num,num))
        return fighterList
    
    def getCPUPlayers(self):
        retlist = []
        for bot in self.botList:
            if bot:
                retlist.append(cpuPlayer.CPUplayer())
            else:
                retlist.append(None)
        return retlist
    
class CSSWidget():
    def __init__(self,panel,displayList,choicesList):
        self.previousWidget = None
        self.nextWidget = None
        self.panel = panel
        self.choices = []
        for i,key in displayList:
            self.choices.append((key,choicesList[i]))
        
    def onConfirm(self):
        pass
    
    def draw(self):
        pass
       
class FighterWheel():
    def __init__(self):
        self.fighters = []
        
        # Load all files.
        directory = settingsManager.createPath("fighters")
        fightercount = 0
        for subdir in next(os.walk(directory))[1]:
            if(subdir == '__pycache__'):
                continue
            fighter = settingsManager.importFromURI(directory, os.path.join(directory,subdir,"fighter.py"),suffix=str(fightercount))
            print(fighter)
            if (fighter == None):
                raise ValueError("No fighter found at " + os.path.join(directory,subdir,"fighter.py"))
            fightercount += 1
            self.fighters.append(fighter)      
        
        self.currentIndex = 0
        self.currentFighter = self.fighters[0]
        self.wheelSize = 9
        self.visibleSprites = [None for _ in range(self.wheelSize)]
        self.animateWheel()
        self.wheelShadow = spriteManager.ImageSprite(settingsManager.createPath(os.path.join("sprites","cssbar_shadow.png")))
        
    def changeSelected(self,increment):
        self.currentIndex = self.currentIndex + increment
        self.currentFighter = self.fighters[self.currentIndex % len(self.fighters)]
        self.animateWheel()
        
    def fighterAt(self,offset):
        return self.fighters[(self.currentIndex + offset) % len(self.fighters)]
    
    def animateWheel(self):
        self.visibleSprites[0] = self.getFighterPortrait(self.fighterAt(0))
        for i in range(1,(self.wheelSize//2)+1):
            self.visibleSprites[2*i-1] = self.getFighterPortrait(self.fighterAt(i))
            self.visibleSprites[2*i] = self.getFighterPortrait(self.fighterAt(-1 * i))
                        
        [spriteManager.ImageSprite.alpha(sprite, 128) for sprite in self.visibleSprites]
        self.visibleSprites[0].alpha(255)
        
    def draw(self, screen, location):
        center = 112
        blankImage = pygame.Surface([256,32], pygame.SRCALPHA, 32).convert_alpha()
        blankImage.blit(self.visibleSprites[0].image, [center,0])
        for i in range(1,(self.wheelSize//2)+1):
            blankImage.blit(self.visibleSprites[2*i-1].image, [center + (32*i),0])
            blankImage.blit(self.visibleSprites[2*i].image, [center - (32*i),0])
        
        blankImage.blit(self.wheelShadow.image,[0,0])
        screen.blit(blankImage, location)
                     
    def getFighterPortrait(self,fighter):
        portrait = fighter.cssIcon()
        if portrait == None:
            portrait = spriteManager.ImageSprite(settingsManager.createPath(os.path.join("sprites","icon_unknown.png")))
        return portrait

class PlayerPanel(pygame.Surface):
    def __init__(self,playerNum):
        pygame.Surface.__init__(self,(settingsManager.getSetting('windowWidth')//2,
                                settingsManager.getSetting('windowHeight')//2))
        
        self.keys = settingsManager.getControls(playerNum)
        self.playerNum = playerNum
        self.wheel = FighterWheel()
        self.active = False
        self.activeObject = self.wheel
        self.chosenFighter = None
        
        self.wheelIncrement = 0
        self.holdtime = 0
        self.holdDistance = 0
        self.wheelOffset = [(self.get_width() - 256) // 2,
                            (self.get_height() - 32)]
        self.bgSurface = None
    
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
                
        if self.bgSurface and self.bgSurface.get_alpha() > 128:
            self.bgSurface.set_alpha(self.bgSurface.get_alpha() - 10)
                
    def keyPressed(self,key):
        if key != 'special' and self.active == False:
            self.active = True
            return
        if key == 'special' and self.active == True:
            if self.activeObject == self.wheel:
                self.active = False
                return
            else:
                self.activeObject = self.wheel
                self.chosenFighter = None
                self.bgSurface = None
                return
        #TODO: Add more sound effects and shutter sprite
        
        if key == 'left':
            if self.activeObject == self.wheel:
                self.wheelIncrement = -1
        elif key == 'right':
            if self.activeObject == self.wheel:
                self.wheelIncrement = 1
        elif key == 'attack':
            if self.activeObject == self.wheel:
                self.bgSurface = self.copy()
                self.bgSurface.set_alpha(240)
                self.activeObject = None
                self.chosenFighter = self.wheel.fighterAt(0)
                
    def keyReleased(self,key):
        if key == 'right' or key == 'left':
            self.wheelIncrement = 0
            self.holdDistance = 0
            self.holdtime = 0
    
    def draw(self,screen):
        if self.active:
            self.fill((0,0,0))
            if self.bgSurface:
                self.blit(self.bgSurface,[0,0])
            else:
                self.wheel.draw(self,self.wheelOffset)
        else:
            self.fill(pygame.Color(settingsManager.getSetting('playerColor' + str(self.playerNum))))
            #draw closed shutter
        offset = [0,0]
        if self.playerNum == 1 or self.playerNum == 3: offset[0] = self.get_width()
        if self.playerNum == 2 or self.playerNum == 3: offset[1] = self.get_height()
        screen.blit(self,offset)