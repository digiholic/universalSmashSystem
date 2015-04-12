import pygame
import spriteObject

class Article():
    def __init__(self, owner,origin,length=1):
        self.frame = 0
        self.lastFrame = length
        
    def update(self):
        pass
    
class ShieldArticle(Article):
    def __init__(self,image,owner):
        self.sprite = spriteObject.ImageSprite(image,owner.topleft)
        self.owner = owner
        self.sprite.rect.center = owner.rect.center
    
    def update(self):
        self.sprite.rect.center = self.owner.rect.center
        if self.owner.shield == False:
            self.kill()
           
    def draw(self,screen,offset,zoom):
        scale = zoom*float(self.owner.shieldIntegrity/100)
        h = int(round(self.rect.height * scale))
        w = int(round(self.rect.width * scale))
        newOff = (int(offset[0] * scale), int(offset[1] * scale))
        blitSprite = pygame.transform.smoothscale(self.image, (w,h))
        screen.blit(blitSprite,pygame.Rect(newOff,(w,h)))