import engine.stage as stage
import pygame
import spriteManager
import os

def getStage():
    return TrueArena()

def getStageName():
    return "True Arena"

def getStageIcon():
    return spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","icon_true_arena.png"))

def getStagePreview():
    return None

def getMusicList():
    return [(os.path.join(os.path.dirname(__file__).replace('main.exe',''),'music','Laszlo - Fall To Light.ogg'),1,"Laszlo - Fall To Light (NCS Release)")]

class TrueArena(stage.Stage):
    def __init__(self):
        stage.Stage.__init__(self)
        
        self.size = pygame.Rect(0,0,2160,1440)
        self.camera_maximum = pygame.Rect(48,32,2064,1376)
        self.blast_line = pygame.Rect(0,0,2160,1440)
        
        #self.platform_list = [stage.Platform([700,680], [1460,680],(True,True)),
        #                      stage.Platform([700,680], [700,750]),
        #                      stage.Platform([1460,680],[1460,750])]
        
        self.platform_list = [stage.Platform([self.size.centerx - 337,self.size.centery], [self.size.centerx + 337,self.size.centery],(True,True)),
                              stage.Platform([self.size.centerx - 337,self.size.centery+1], [self.size.centerx - 337,self.size.centery+102],(True,True)),
                              stage.Platform([self.size.centerx + 337,self.size.centery+1], [self.size.centerx + 337,self.size.centery+102],(True,True)),
                             ]
        
        self.spawnLocations = [[self.size.centerx - 337 + (134 * 1),self.size.centery],
                               [self.size.centerx - 337 + (134 * 4),self.size.centery],
                               [self.size.centerx - 337 + (134 * 2),self.size.centery],
                               [self.size.centerx - 337 + (134 * 3),self.size.centery],
                               ]
        
        fgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TrueArenaFront.png"))
        fgSprite.rect.topleft = [self.size.centerx - 383,self.size.centery]
        self.foregroundSprites.append(fgSprite)
        
        bgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TrueArenaBack.png"))
        bgSprite.rect.topleft = [self.size.centerx - 383,self.size.centery-44]
        self.backgroundSprites.append(bgSprite)
        
        self.getLedges()
