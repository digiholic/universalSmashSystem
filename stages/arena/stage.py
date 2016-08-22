import engine.stage as stage
import pygame
import spriteManager
import os
import settingsManager

def getStage():
    return Arena()

def getStageName():
    return "Arena"

def getStageIcon():
    return spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","icon_arena.png"))

def getStagePreview():
    return None

def getMusicList():
    return [(settingsManager.createPath('music/Laszlo - Fall To Light.ogg'),1,"Laszlo - Fall To Light (NCS Release)"),
            (settingsManager.createPath('music/Autumn Warriors.ogg'),1,"Autumn Warriors")]

class Arena(stage.Stage):
    def __init__(self):
        stage.Stage.__init__(self)
        
        self.size = pygame.Rect(0,0,2160,1440)
        self.camera_maximum = pygame.Rect(48,32,2064,1376)
        self.blast_line = pygame.Rect(0,0,2160,1440)
        
        self.platform_list = [stage.Platform([self.size.centerx - 314,self.size.centery+140], [self.size.centerx + 314,self.size.centery+190],(True,True)),
                              stage.PassthroughPlatform([self.size.centerx - 314 + 56,self.size.centery],[self.size.centerx - 314 + 56 + 172,self.size.centery]),
                              stage.PassthroughPlatform([self.size.centerx - 314 + 56 + 172,self.size.centery-140],[self.size.centerx - 314 + 56 + 172 + 172,self.size.centery-140]),
                              stage.PassthroughPlatform([self.size.centerx - 314 + 56 + 172 + 172,self.size.centery],[self.size.centerx - 314 + 56 + 172 + 172 + 172,self.size.centery])]
        
        
        self.spawn_locations = [[879,573],
                               [1279,573],
                               [1079,453],
                               [1079,713]]
        
        
        bg_sprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaBack.png"))
        bg_sprite.rect.topleft = [self.size.centerx - 351,self.size.centery+140-125]
        self.addToBackground(bg_sprite)
        
        fg_sprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaFront.png"))
        fg_sprite.rect.topleft = [self.size.centerx - 351,self.size.centery+140-6]
        self.foreground_sprites.append(fg_sprite)
        
        
        plat_0_front = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatFrontL.png"))
        plat_0_front.rect.topleft = [self.size.centerx - 314 - 9 + 56,self.size.centery]
        plat_1_front = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatFrontM.png"))
        plat_1_front.rect.topleft = [self.size.centerx - 314 - 9 + 56 + 172,self.size.centery-140]
        plat_2_front = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatFrontR.png"))
        plat_2_front.rect.topleft = [self.size.centerx - 314 - 9 + 56 + 172 + 172,self.size.centery]
        
        self.foreground_sprites.extend([plat_0_front, plat_1_front, plat_2_front])
        
        plat_0_back = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatBackL.png"))
        plat_0_back.rect.topleft = [self.size.centerx - 314 - 9 + 56,self.size.centery-3]
        plat_1_back = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatBackM.png"))
        plat_1_back.rect.topleft = [self.size.centerx - 314 - 9 + 56 + 172,self.size.centery-3-140]
        plat_2_back = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","ArenaPlatBackR.png"))
        plat_2_back.rect.topleft = [self.size.centerx - 314 - 9 + 56 + 172 + 172,self.size.centery-3]
        
        self.addToBackground(plat_0_back)
        self.addToBackground(plat_1_back)
        self.addToBackground(plat_2_back)
        self.getLedges()
