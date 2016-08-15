import engine.stage as stage
import pygame
import spriteManager
import os
import settingsManager
import engine.article as article

def getStage():
    return TrueArena()

def getStageName():
    return "True Arena"

def getStageIcon():
    return spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","icon_true_arena.png"))

def getStagePreview():
    return None

def getMusicList():
    return [(settingsManager.createPath('music/Laszlo - Fall To Light.ogg'),1,"Laszlo - Fall To Light (NCS Release)"),
            (settingsManager.createPath('music/Autumn Warriors.ogg'),1,"Autumn Warriors")]

class wrapArticle(article.Article):
    def __init__(self,spritePath, center, speed):
        article.Article.__init__(self,spritePath, None, center)
        self.speed = speed
        self.frame = 0
        
    def update(self):
        if self.frame % 2 == 0:
            rect = self.image.get_rect()
            
            self.image.set_clip(pygame.Rect(rect.right - self.speed,0,self.speed,rect.height))
            smallPortion = self.image.subsurface(self.image.get_clip())
            
            self.image.set_clip(pygame.Rect(0,0,self.rect.width - self.speed,rect.height))
            bigPortion = self.image.subsurface(self.image.get_clip())
            
            newSurface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA, 32).convert_alpha()
            newSurface.blit(smallPortion,pygame.Rect(0,0,self.speed,rect.height))
            newSurface.blit(bigPortion,pygame.Rect(self.speed,0,rect.width - self.speed,rect.height))
            
            self.image = newSurface
            self.frame = 0
        self.frame += 1

class TrueArena(stage.Stage):
    def __init__(self):
        stage.Stage.__init__(self)
        
        self.size = pygame.Rect(0,0,2160,1440)
        self.camera_maximum = pygame.Rect(48,32,2064,1376)
        self.blast_line = pygame.Rect(0,0,2160,1440)
        
        self.articles = []
        #self.platform_list = [stage.Platform([700,680], [1460,680],(True,True)),
        #                      stage.Platform([700,680], [700,750]),
        #                      stage.Platform([1460,680],[1460,750])]
        
        self.platform_list = [stage.Platform([self.size.centerx - 337,self.size.centery], [self.size.centerx + 337,self.size.centery+102],(True,True))]
        
        self.spawn_locations = [[self.size.centerx - 337 + (134 * 1),self.size.centery-1],
                               [self.size.centerx - 337 + (134 * 4),self.size.centery-1],
                               [self.size.centerx - 337 + (134 * 2),self.size.centery-1],
                               [self.size.centerx - 337 + (134 * 3),self.size.centery-1],
                               ]
        
        fgSprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TrueArenaFront.png"))
        fgSprite.rect.topleft = [self.size.centerx - 383,self.size.centery]
        self.foreground_sprites.append(fgSprite)
        
        backdropa = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll4.png"))
        backdropa.rect.left = 0
        backdropa.rect.centery = self.size.centery - 64
        self.addToBackground(backdropa,0.1)
        backdropb = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll4.png"))
        backdropb.rect.left = backdropa.rect.right
        backdropb.rect.centery = self.size.centery - 64
        self.addToBackground(backdropb,0.1)
        
        backgroundElement0a = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll3.png"),
                                             (0,self.size.centery - 20),
                                             1)
        self.addToBackground(backgroundElement0a, 0.2)
        backgroundElement0b = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll3.png"),
                                             (backgroundElement0a.image.get_rect().right,self.size.centery - 20),
                                             1)
        self.addToBackground(backgroundElement0b, 0.2)
        
        backgroundElement1a = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll2.png"),
                                             (0,self.size.centery),
                                             2)
        self.addToBackground(backgroundElement1a, 0.5)
        backgroundElement1b = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll2.png"),
                                             (backgroundElement1a.image.get_rect().right,self.size.centery),
                                             2)
        self.addToBackground(backgroundElement1b, 0.5)
        
        backgroundElement2a = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll1.png"),
                                             (0,self.size.centery+32),
                                             4)
        self.addToBackground(backgroundElement2a, 0.8)
        backgroundElement2b = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll1.png"),
                                             (backgroundElement2a.image.get_rect().right,self.size.centery+32),
                                             4)
        self.addToBackground(backgroundElement2b, 0.8)
        
        self.articles.extend([backgroundElement0a,backgroundElement0b,backgroundElement1a,backgroundElement1b,backgroundElement2a,backgroundElement2b])
        
        bg_sprite0 = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TrueArenaBack.png"))
        bg_sprite0.rect.topleft = [self.size.centerx - 383,self.size.centery-44]
        self.addToBackground(bg_sprite0)
        
        
        self.background_color = [0,0,0]
        self.getLedges()
    
    def update(self):
        stage.Stage.update(self)
        for art in self.articles:
            art.update()