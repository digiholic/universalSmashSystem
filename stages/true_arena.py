import stages.stage as stage
import pygame
import settingsManager
import spriteManager

def getStage():
    return TrueArena()

class TrueArena(stage.Stage):
    def __init__(self):
        stage.Stage.__init__(self)
        
        self.size = pygame.Rect(0,0,2160,1440)
        self.camera_maximum = pygame.Rect(48,32,2064,1376)
        self.blast_line = pygame.Rect(0,0,2160,1440)
        
        self.camera_position.midtop = self.size.midtop
        self.camera_preferred_position.midtop = self.size.midtop
        
        self.deadZone = [64,32]
        
        self.platform_list = [spriteObject.RectSprite([552,824],[798,342])]
        
        self.sprite = spriteObject.ImageSprite("fd",[494,790],generateAlpha=False,filepath = __file__)
        
        self.preferred_zoomLevel = 1.0
        self.zoomLevel = 1.0