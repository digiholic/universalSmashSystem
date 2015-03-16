import pygame
import os

class Sprite(pygame.sprite.Sprite):
    #Create with image
    def __init__(self, topleft):
        pygame.sprite.Sprite.__init__(self)
        
        #Set whether the object is visible
        self.visible = True
        
        #Set whether the object is solid
        self.solid = True
        
        self.topleft = topleft
        
    def draw(self,screen,offset,scale):
        h = int(round(self.rect.height * scale))
        w = int(round(self.rect.width * scale))
        newOff = (int(offset[0] * scale), int(offset[1] * scale))
        blitSprite = pygame.transform.smoothscale(self.image, (w,h))
        screen.blit(blitSprite,pygame.Rect(newOff,(w,h)))
        
class ImageSprite(Sprite):
    def __init__(self,image,topleft,colorKey = [255,255,255],generateAlpha = True):
        Sprite.__init__(self, topleft)
        
        self.index = 0
        self.imagePrefix = os.path.dirname(__file__) + "/fighters/hitboxie/sprites/" 
        self.imageText = image
        self.image = pygame.image.load(self.imagePrefix + self.imageText + ".png")
        self.alpha = generateAlpha
        if self.alpha:
            self.colorKey = colorKey
            self.image.set_colorkey(self.colorKey)
        
        self.flip = False
        self.angle = 0
        
        self.image.convert_alpha()
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.topleft
        
    def getImageAtIndex(self,index):
        self.index = index
        self.changeImage(self.imageText + str(self.index))
        
    def flipX(self):
        self.flip = not self.flip
        
    def changeImage(self,imageText):
        self.imageText = imageText
        self.image = pygame.image.load(self.imagePrefix + self.imageText + ".png")
        if self.flip: self.image = pygame.transform.flip(self.image,True,False)
        self.rect = self.image.get_rect(center=self.rect.center)
            
        
    def draw(self,screen,offset,scale):
        if self.alpha: self.image.set_colorkey(self.colorKey)
        self.image = self.image.convert_alpha()
        Sprite.draw(self, screen, offset, scale)

class SheetSprite(ImageSprite):
    def __init__(self,image,topleft,offset,colorKey = [255,255,255],generateAlpha = True):
        Sprite.__init__(self,topleft)
        
        self.index = 0
        self.offset = offset
        self.imagePrefix = os.path.dirname(__file__) + "/fighters/hitboxie/sprites/" 
        self.imageText = image
        
        self.sheet = pygame.image.load(self.imagePrefix + self.imageText + ".png")
        self.sheet.set_clip(pygame.Rect(self.index * self.offset, 0, self.offset,self.sheet.get_height()))
        
        self.image = self.sheet.subsurface(self.sheet.get_clip())
        
        self.alpha = generateAlpha
        if self.alpha:
            self.colorKey = colorKey
            self.image.set_colorkey(self.colorKey)
        
        self.flip = False
        self.angle = 0
        
        self.image.convert_alpha()
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.topleft
        
    def getImageAtIndex(self,index):
        self.index = index
        self.changeImage(self.imageText,False)
        
    def changeImage(self,imageText, reset = True):
        self.imageText = imageText
        if reset: self.index = 0
        
        self.sheet = pygame.image.load(self.imagePrefix + self.imageText + ".png")
        self.sheet.set_clip(pygame.Rect(self.index * self.offset, 0, self.offset,self.sheet.get_height()))
        
        self.image = self.sheet.subsurface(self.sheet.get_clip())
        
        if self.flip: self.image = pygame.transform.flip(self.image,True,False)
        self.rect = self.image.get_rect(center=self.rect.center)
        
class RectSprite(Sprite):
    def __init__(self,topleft,size,color=[0,0,0]):
        Sprite.__init__(self,topleft)
        
        self.topleft = topleft
        self.size = size
        self.color = color  
        
        self.image = pygame.Surface(self.size)
        self.image.fill(self.color)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.topleft    
        
        self.image.set_alpha(128)
class TextSprite(Sprite):
    def __init__(self,topleft,text,font = None,color=[255,255,255],background=None):
        Sprite.__init__(self,topleft)
        
        if (font is None):
            self.font = pygame.font.SysFont("monospace", 20)
        else:
            self.font = font
        
        self.text = text
        self.color = color
        self.background = background
        
        self.image = self.font.render(text,1,color)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = self.topleft
    
    def update(self):
        self.image = self.font.render(self.text,1,self.color)
        
    