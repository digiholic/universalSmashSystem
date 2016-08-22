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
    return [(settingsManager.createPath('music/Laszlo - Fall To Light.ogg'),2,"Laszlo - Fall To Light (NCS Release)"),
            (settingsManager.createPath('music/No Turning Back.ogg'),2,"No Turning Back"),
            (settingsManager.createPath('music/True Arena.ogg'),1,"No Turning Back (Chiptune ver.)")]

class wrapArticle(article.Article):
    def __init__(self,spritePath, center, speed):
        article.Article.__init__(self,spritePath, None, center)
        self.speed = speed
        self.frame = 0
        
    def update(self):
        if self.frame % 2 == 0:
            rect = self.image.get_rect()
            
            self.image.set_clip(pygame.Rect(rect.right - self.speed,0,self.speed,rect.height))
            small_portion = self.image.subsurface(self.image.get_clip())
            
            self.image.set_clip(pygame.Rect(0,0,self.rect.width - self.speed,rect.height))
            big_portion = self.image.subsurface(self.image.get_clip())
            
            new_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA, 32).convert_alpha()
            new_surface.blit(small_portion,pygame.Rect(0,0,self.speed,rect.height))
            new_surface.blit(big_portion,pygame.Rect(self.speed,0,rect.width - self.speed,rect.height))
            
            self.image = new_surface
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
        
        fg_sprite = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TrueArenaFront.png"))
        fg_sprite.rect.topleft = [self.size.centerx - 383,self.size.centery]
        self.foreground_sprites.append(fg_sprite)
        
        backdrop_a = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll4.png"))
        backdrop_a.rect.left = 0
        backdrop_a.rect.centery = self.size.centery - 64
        self.addToBackground(backdrop_a,0.1)
        backdrop_b = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll4.png"))
        backdrop_b.rect.left = backdrop_a.rect.right
        backdrop_b.rect.centery = self.size.centery - 64
        self.addToBackground(backdrop_b,0.1)
        
        background_element_0_a = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll3.png"),
                                             (0,self.size.centery - 20),
                                             1)
        self.addToBackground(background_element_0_a, 0.2)
        background_element_0_b = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll3.png"),
                                             (background_element_0_a.image.get_rect().right,self.size.centery - 20),
                                             1)
        self.addToBackground(background_element_0_b, 0.2)
        
        background_element_1_a = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll2.png"),
                                             (0,self.size.centery),
                                             2)
        self.addToBackground(background_element_1_a, 0.5)
        background_element_1_b = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll2.png"),
                                             (background_element_1_a.image.get_rect().right,self.size.centery),
                                             2)
        self.addToBackground(background_element_1_b, 0.5)
        
        background_element_2_a = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll1.png"),
                                             (0,self.size.centery+32),
                                             4)
        self.addToBackground(background_element_2_a, 0.8)
        background_element_2_b = wrapArticle(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TAscroll1.png"),
                                             (background_element_2_a.image.get_rect().right,self.size.centery+32),
                                             4)
        self.addToBackground(background_element_2_b, 0.8)
        
        self.articles.extend([background_element_0_a,background_element_0_b,background_element_1_a,background_element_1_b,background_element_2_a,background_element_2_b])
        
        bg_sprite_0 = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","TrueArenaBack.png"))
        bg_sprite_0.rect.topleft = [self.size.centerx - 383,self.size.centery-44]
        self.addToBackground(bg_sprite_0)
        
        
        self.background_color = [0,0,0]
        self.getLedges()
    
    def update(self):
        stage.Stage.update(self)
        for art in self.articles:
            art.update()
