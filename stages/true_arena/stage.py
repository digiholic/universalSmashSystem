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
        
        self.platform_list = [stage.Platform([725,668], [1435,668],(True,True)),
                             stage.Platform([725,668], [725,750]),
                             stage.Platform([1435,668],[1435,750])]
        
        self.spawnLocations = [[780,668],
                               [1320,668],
                               [860,668],
                               [1040,668]]
        
        bgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","true_arena.png"))
        bgSprite.rect.topleft = [700,618]
        self.backgroundSprites.append(bgSprite)
        
        self.getLedges()