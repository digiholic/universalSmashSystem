import engine.stage as stage
import pygame
import spriteManager
import os

def getStage():
    return Arena()

def getStageName():
    return "Arena"

def getStageIcon():
    return spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","icon_arena.png"))

def getStagePreview():
    return None

def getMusicList():
    return [(os.path.join(os.path.dirname(__file__).replace('main.exe',''),'music','Laszlo - Fall To Light.ogg'),1,"Laszlo - Fall To Light (NCS Release)")]

class Arena(stage.Stage):
    def __init__(self):
        stage.Stage.__init__(self)
        
        self.size = pygame.Rect(0,0,2160,1440)
        self.camera_maximum = pygame.Rect(48,32,2064,1376)
        self.blast_line = pygame.Rect(0,0,2160,1440)
        
        #self.platform_list = [spriteObject.RectSprite([552,824],[798,342])]
        self.platform_list = [stage.Platform([754,713], [1406,713],(True,True)),
                              stage.Platform([754,714], [754,1166]),
                              stage.Platform([1406,714], [1406,1166]),
                              stage.PassthroughPlatform([779,573],[979,573]),
                              stage.PassthroughPlatform([979,453],[1179,453]),
                              stage.PassthroughPlatform([1179,573],[1379,573])]
        
        
        self.spawnLocations = [[879,573],
                               [1279,573],
                               [1079,453],
                               [1079,713]]
        
        bgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","arena.png"))
        bgSprite.rect.topleft = [729,587]
        self.backgroundSprites.append(bgSprite)
        
        self.getLedges()
