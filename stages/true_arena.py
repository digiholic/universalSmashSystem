import stages.stage as stage
import pygame
import spriteManager
import os

def getStage():
    return TrueArena()

class TrueArena(stage.Stage):
    def __init__(self):
        stage.Stage.__init__(self)
        
        self.size = pygame.Rect(0,0,2160,1440)
        self.camera_maximum = pygame.Rect(48,32,2064,1376)
        self.blast_line = pygame.Rect(0,0,2160,1440)
        
        #self.platform_list = [spriteObject.RectSprite([552,824],[798,342])]
        self.platform_list = [stage.Platform([552,824], [1350,824],(True,True)),
                              stage.Platform([552,824], [552,1166]),
                              stage.Platform([1350,824],[1350,1166])]
                            #stage.PassthroughPlatform([552,624],[752,624])]
        
        
        self.spawnLocations = [[680,824],
                               [1222,824],
                               [860,824],
                               [1024,824]]
        
        bgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__),"sprites/fd.png"))
        bgSprite.rect.topleft = [494,790]
        self.backgroundSprites.append(bgSprite)
        
        self.getLedges()