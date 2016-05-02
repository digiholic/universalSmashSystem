import engine.stage as stage
import pygame
import spriteManager
import os

def getStage():
    return Arena()

def getStageName():
    return "Arena"

def getStageIcon():
    return spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","icon_treehouse.png"))

def getStagePreview():
    return None

def getMusicList():
    return [(os.path.join(os.path.dirname(__file__).replace('main.exe',''),'music','Laszlo - Fall To Light.ogg'),1,"Laszlo - Fall To Light (NCS Release)"),
            (os.path.join(os.path.dirname(__file__).replace('main.exe',''),'music','Autumn Warriors.ogg'),1,"Autumn Warriors")]

class Arena(stage.Stage):
    def __init__(self):
        stage.Stage.__init__(self)
        
        self.size = pygame.Rect(0,0,2160,1440)
        self.camera_maximum = pygame.Rect(48,32,2064,1376)
        self.blast_line = pygame.Rect(0,0,2160,1440)
        
        self.platform_list = [stage.Platform([self.size.centerx - 230,self.size.bottom-318], [self.size.centerx + 230,self.size.bottom-305],(True,True)),
                              stage.PassthroughPlatform([self.size.centerx - 540,self.size.bottom-434], [self.size.centerx - 348,self.size.bottom-434],(True,False)),
                              stage.PassthroughPlatform([self.size.centerx + 347,self.size.bottom-434], [self.size.centerx + 539,self.size.bottom-434],(False,True))
                              
                              ]
        
        
        self.spawnLocations = [[self.size.centerx - 77,1121],
                               [self.size.centerx + 153,1121],
                               [self.size.centerx - 445,1005],
                               [self.size.centerx + 445,1005]]
        
        
        bgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TreeHouseBack.png"))
        bgSprite.rect.midbottom = self.size.midbottom
        self.addToBackground(bgSprite)
        
        fgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TreeHouseFront.png"))
        fgSprite.rect.midbottom = self.size.midbottom
        self.foregroundSprites.append(fgSprite)
        
        
        self.getLedges()
