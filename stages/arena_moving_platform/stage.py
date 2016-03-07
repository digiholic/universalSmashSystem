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
    return [(os.path.join(os.path.dirname(__file__).replace('main.exe',''),'music','Autumn Warriors.ogg'),1,"Autumn Warriors")]

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
        
        self.platform_list = [stage.Platform([self.size.centerx - 314,self.size.centery+140], [self.size.centerx + 314,self.size.centery+140],(True,True)),
                              #stage.Platform([754,714], [754,1166]),
                              #stage.Platform([1406,714], [1406,1166]),
                              stage.PassthroughPlatform([self.size.centerx - 314 + 56,self.size.centery],[self.size.centerx - 314 + 56 + 172,self.size.centery]),
                              #stage.PassthroughPlatform([self.size.centerx - 314 + 56 + 172,self.size.centery-140],[self.size.centerx - 314 + 56 + 172 + 172,self.size.centery-140]),
                              stage.PassthroughPlatform([self.size.centerx - 314 + 56 + 172 + 172,self.size.centery],[self.size.centerx - 314 + 56 + 172 + 172 + 172,self.size.centery])]
        
        
        self.movingPlat = MovingPlatform([self.size.centerx - 314 + 56 + 172,self.size.centery-140],[self.size.centerx - 314 + 56 + 172 + 172,self.size.centery-140], self.size.centery-140, self.size.centery+140)
        self.entity_list.append(self.movingPlat)
        self.platform_list.append(self.movingPlat)
        
        self.spawnLocations = [[879,573],
                               [1279,573],
                               [1079,453],
                               [1079,713]]
        
        bgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaBack.png"))
        bgSprite.rect.topleft = [self.size.centerx - 351,self.size.centery+140-125]
        self.backgroundSprites.append(bgSprite)
        
        fgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaFront.png"))
        fgSprite.rect.topleft = [self.size.centerx - 351,self.size.centery+140-6]
        self.foregroundSprites.append(fgSprite)
        
        plat0front = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatFrontL.png"))
        plat0front.rect.topleft = [self.size.centerx - 314 - 9 + 56,self.size.centery]
        self.plat1front = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatFrontM.png"))
        self.plat1front.rect.topleft = [self.size.centerx - 314 - 9 + 56 + 172,self.size.centery-140]
        plat2front = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatFrontR.png"))
        plat2front.rect.topleft = [self.size.centerx - 314 - 9 + 56 + 172 + 172,self.size.centery]
        
        self.foregroundSprites.extend([plat0front, self.plat1front, plat2front])
        
        plat0back = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatBackL.png"))
        plat0back.rect.topleft = [self.size.centerx - 314 - 9 + 56,self.size.centery-3]
        self.plat1back = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatBackM.png"))
        self.plat1back.rect.topleft = [self.size.centerx - 314 - 9 + 56 + 172,self.size.centery-3-140]
        plat2back = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatBackR.png"))
        plat2back.rect.topleft = [self.size.centerx - 314 - 9 + 56 + 172 + 172,self.size.centery-3]
        
        self.backgroundSprites.extend([plat0back, self.plat1back, plat2back])
        
        self.getLedges()
        
    def update(self):
        stage.Stage.update(self)
        self.plat1back.rect.topleft = [self.movingPlat.rect.left-9,self.movingPlat.rect.top-3]
        self.plat1front.rect.topleft = [self.movingPlat.rect.left-9,self.movingPlat.rect.top]
        
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
