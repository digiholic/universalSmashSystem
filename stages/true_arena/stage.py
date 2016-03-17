import engine.stage as stage
import pygame
import spriteManager
import os
import settingsManager

def getStage():
    return TrueArena()

def getStageName():
    return "True Arena"

def getStageIcon():
    return spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","icon_true_arena.png"))

def getStagePreview():
    return None

def getMusicList():
    return [(os.path.join(os.path.dirname(__file__).replace('main.exe',''),'music','Laszlo - Fall To Light.ogg'),1,"Laszlo - Fall To Light (NCS Release)"),
            (os.path.join(os.path.dirname(__file__).replace('main.exe',''),'music','Autumn Warriors.ogg'),1,"Autumn Warriors")]

class TrueArena(stage.Stage):
    def __init__(self):
        stage.Stage.__init__(self)
        
        self.size = pygame.Rect(0,0,2160,1440)
        self.camera_maximum = pygame.Rect(48,32,2064,1376)
        self.blast_line = pygame.Rect(0,0,2160,1440)
        
        #self.platform_list = [stage.Platform([700,680], [1460,680],(True,True)),
        #                      stage.Platform([700,680], [700,750]),
        #                      stage.Platform([1460,680],[1460,750])]
        
        self.platform_list = [stage.Platform([self.size.centerx - 337,self.size.centery], [self.size.centerx + 337,self.size.centery+102],(True,True))]
        
        self.spawnLocations = [[self.size.centerx - 337 + (134 * 1),self.size.centery-1],
                               [self.size.centerx - 337 + (134 * 4),self.size.centery-1],
                               [self.size.centerx - 337 + (134 * 2),self.size.centery-1],
                               [self.size.centerx - 337 + (134 * 3),self.size.centery-1],
                               ]
        
        fgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TrueArenaFront.png"))
        fgSprite.rect.topleft = [self.size.centerx - 383,self.size.centery]
        self.foregroundSprites.append(fgSprite)
        
        backdropa = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll4.png"))
        backdropa.rect.left = 0
        backdropa.rect.centery = self.size.centery - 64
        self.addToBackground(backdropa,0.1)
        backdropb = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll4.png"))
        backdropb.rect.left = backdropa.rect.right
        backdropb.rect.centery = self.size.centery - 64
        self.addToBackground(backdropb,0.1)
        
        rockline0a = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll3.png"))
        rockline0a.rect.left = 0
        rockline0a.rect.centery = self.size.centery - 112
        self.addToBackground(rockline0a,0.2)
        rockline0b = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll3.png"))
        rockline0b.rect.left = rockline0b.rect.right
        rockline0b.rect.centery = self.size.centery - 112
        self.addToBackground(rockline0b,0.2)
        
        rockline1a = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll2.png"))
        rockline1a.rect.left = 0
        rockline1a.rect.centery = self.size.centery - 80
        self.addToBackground(rockline1a,0.5)
        rockline1b = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll2.png"))
        rockline1b.rect.left = rockline1a.rect.right
        rockline1b.rect.centery = self.size.centery - 80
        self.addToBackground(rockline1b,0.5)
        
        rockline2a = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll1.png"))
        rockline2a.rect.left = 0
        rockline2a.rect.centery = self.size.centery - 48
        self.addToBackground(rockline2a,0.8)
        rockline2b = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll1.png"))
        rockline2b.rect.left = rockline2a.rect.right
        rockline2b.rect.centery = self.size.centery - 48
        self.addToBackground(rockline2b,0.8)
        
        bgSprite0 = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TrueArenaBack.png"))
        bgSprite0.rect.topleft = [self.size.centerx - 383,self.size.centery-44]
        self.addToBackground(bgSprite0)
        
        
        self.backgroundColor = [0,0,0]
        self.getLedges()
