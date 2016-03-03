import engine.stage as stage
import pygame
import spriteManager
import os

def getStage():
    return ArenaMovingPlatform()

def getStageName():
    return "ArenaMovingPlatform"

def getStageIcon():
    return spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","icon_arena.png"))

def getStagePreview():
    return None

def getMusicList():
    return [(os.path.join(os.path.dirname(__file__).replace('main.exe',''),'music','Laszlo - Fall To Light.ogg'),1,"Laszlo - Fall To Light (NCS Release)")]

class ArenaMovingPlatform(stage.Stage):
    def __init__(self):
        stage.Stage.__init__(self)
        
        self.size = pygame.Rect(0,0,2160,1440)
        self.camera_maximum = pygame.Rect(48,32,2064,1376)
        self.blast_line = pygame.Rect(0,0,2160,1440)
        
        #self.platform_list = [spriteObject.RectSprite([552,824],[798,342])]
        self.platform_list = [stage.Platform([754,713], [1406,713],(True,True)),
                              stage.Platform([754,714], [754,1166]),
                              stage.Platform([1406,714],[1406,1166]),
                              stage.PassthroughPlatform([779,573],[979,573]),
                              # stage.PassthroughPlatform([979,453],[1179,453]),
                              stage.PassthroughPlatform([1179,573],[1379,573])]
        
        m = MovingPlatform([979,453],[1179,453], 453, 713)
        self.entity_list.append(m)
        self.platform_list.append(m)
        
        self.spawnLocations = [[879,573],
                               [1279,573],
                               [1079,453],
                               [1079,713]]
        
        bgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","arena.png"))
        bgSprite.rect.topleft = [729,587]
        self.backgroundSprites.append(bgSprite)
        
        self.getLedges()
        
    def update(self):
        stage.Stage.update(self)
        
class MovingPlatform(stage.Platform):
    def __init__(self, leftPoint, rightPoint, minHeight, maxHeight, moveSpeed = 1, grabbable = (False,False), solid = False):
        stage.Platform.__init__(self, leftPoint, rightPoint, grabbable)
        self.solid = solid
        self.minHeight = minHeight
        self.maxHeight = maxHeight
        self.rising = False
        self.height = leftPoint[1]
        self.speed = moveSpeed
        
    def update(self):
        if self.rising:
            self.height -= self.speed
            self.change_y = self.speed
        else:
            self.height += self.speed
            self.change_y = self.speed
        if self.height < self.minHeight:
            self.rising = False
            self.height = self.minHeight
            self.change_y = 0
        if self.height > self.maxHeight:
            self.rising = True
            self.height = self.maxHeight
            self.change_y = 0
            
        self.leftPoint[1] = self.height
        self.rightPoint[1] = self.height
        
        self.xdist = max(1,self.rightPoint[0] - self.leftPoint[0])
        self.ydist = max(1,self.rightPoint[1] - self.leftPoint[1])

        self.rect = pygame.Rect([self.leftPoint[0],min(self.leftPoint[1],self.rightPoint[1])], [self.xdist,self.ydist])
