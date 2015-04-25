import settingsManager
import spriteManager
import os
import imp
import pygame

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
        self.playerPanel = PlayerPanel(0)
        self.wheel = FighterWheel(self.playerPanel.fighters)
        
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.wheel.changeSelected(-1)
                    elif event.key == pygame.K_RIGHT:
                        self.wheel.changeSelected(1)
                    elif event.key == pygame.K_ESCAPE:
                        return
                    elif event.key == pygame.K_z:
                        print self.wheel.fighterAt(0)
                
                screen.fill((128, 128, 128))
                self.wheel.draw(screen)
                
                
                pygame.display.flip()
                clock.tick(60)
                
                
                
class PlayerPanel():
    def __init__(self,playerNum):
        self.playerNum = playerNum
        self.active = False
        self.fighters = []
        self.portraitList = []
        
        # Load all files.
        directory = os.path.join(os.path.dirname(settingsManager.__file__),"fighters")
        fightercount = 0
        for subdir in next(os.walk(directory))[1]:
            fighter = importFromURI(directory, os.path.join(directory,subdir,"fighter.py"),suffix=str(fightercount))
            fightercount += 1
            self.fighters.append(fighter)
            portrait = fighter.cssIcon()
            if portrait == None: portrait = spriteManager.ImageSprite(os.path.join(os.path.dirname(settingsManager.__file__),"sprites","icon_unknown.png"))
            self.portraitList.append(portrait)
            print self.portraitList
            
        
class FighterWheel():
    def __init__(self,fighters):
        self.fighters = fighters
        self.currentIndex = 0
        self.currentFighter = fighters[0]
        self.wheelSize = 7
        self.visibleSprites = [None for x in range(self.wheelSize)]
        self.animateWheel(0)
        self.wheelShadow = spriteManager.ImageSprite(os.path.join(os.path.dirname(settingsManager.__file__),"sprites/cssbar_shadow.png"))
        
        
        
            
    def append(self,fighter):
        self.fighters.append(fighter)
        
    def changeSelected(self,increment):
        self.currentIndex = self.currentIndex + increment
        self.currentFighter = self.fighters[self.currentIndex % len(self.fighters)]
        self.animateWheel(increment)
        
    def fighterAt(self,offset):
        return self.fighters[(self.currentIndex + offset) % len(self.fighters)]
    
    def animateWheel(self,increment):
        self.visibleSprites[0] = self.getFighterPortrait(self.fighterAt(0))
        for i in range(1,(self.wheelSize/2)+1):
            self.visibleSprites[2*i-1] = self.getFighterPortrait(self.fighterAt(i))
            self.visibleSprites[2*i] = self.getFighterPortrait(self.fighterAt(-1 * i))
                        
        #self.visibleSprites[0] = self.getFighterPortrait(self.fighterAt( 0))
        #self.visibleSprites[1] = self.getFighterPortrait(self.fighterAt( 1))
        #self.visibleSprites[2] = self.getFighterPortrait(self.fighterAt(-1))
        #self.visibleSprites[3] = self.getFighterPortrait(self.fighterAt( 2))
        #self.visibleSprites[4] = self.getFighterPortrait(self.fighterAt(-2))
        #self.visibleSprites[5] = self.getFighterPortrait(self.fighterAt( 3))
        #self.visibleSprites[6] = self.getFighterPortrait(self.fighterAt(-3))
        [spriteManager.ImageSprite.alpha(sprite, 128) for sprite in self.visibleSprites]
        self.visibleSprites[0].alpha(255)
        
    def draw(self,screen):
        center = 288
        self.visibleSprites[0].draw(screen, [center, 256], 1.0)
        for i in range(1,(self.wheelSize/2)+1):
            self.visibleSprites[2*i-1].draw(screen, [center + (64*i),256], 1.0)
            self.visibleSprites[2*i].draw(screen, [center - (64*i),256], 1.0)

        self.wheelShadow.draw(screen, [64,256], 1.0)
                
    def getFighterPortrait(self,fighter):
        portrait = fighter.cssIcon()
        if portrait == None:
            portrait = spriteManager.ImageSprite(os.path.join(os.path.dirname(settingsManager.__file__),"sprites","icon_unknown.png"))
        return portrait
    
def importFromURI(filePath, uri, absl=False, suffix=""):
    if not absl:
        uri = os.path.normpath(os.path.join(os.path.dirname(filePath), uri))
    path, fname = os.path.split(uri)
    mname, ext = os.path.splitext(fname)
    
    no_ext = os.path.join(path, mname)
         
    if os.path.exists(no_ext + '.py'):
        try:
            return imp.load_source((mname + suffix), no_ext + '.py')
        except Exception as e:
            print mname, e
        
        
if __name__  == '__main__': CSSScreen()