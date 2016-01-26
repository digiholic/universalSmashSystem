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
        
        #self.platform_list = [stage.Platform([700,680], [1460,680],(True,True)),
        #                      stage.Platform([700,680], [700,750]),
        #                      stage.Platform([1460,680],[1460,750])]
        
        self.platform_list = [stage.Platform([672,680], [1307,680],(True,True)),
                             stage.Platform([672,680], [672,750]),
                             stage.Platform([1307,680],[1307,750])]
        
        self.spawnLocations = [[780,680],
                               [1320,680],
                               [860,680],
                               [1040,680]]
        
        bgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites/fd_new.png"))
        bgSprite.rect.topleft = [652,555]
        self.backgroundSprites.append(bgSprite)
        
        self.getLedges()