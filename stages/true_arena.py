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
        self.platform_list = [stage.Platform([552,824],[1350,824],(True,True))]
        for plat in self.platform_list:
            for ledge in plat.ledges:
                if ledge != None:
                    self.platform_ledges.append(ledge)
        
        bgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__),"sprites/fd.png"))
        bgSprite.rect.topleft = [494,790]
        self.backgroundSprites.append(bgSprite)
        
        self.initializeCamera()