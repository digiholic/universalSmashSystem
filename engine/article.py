import pygame
import spriteManager

"""
Articles are generated sprites that have their own behavior. For example, projectiles, shields,
particles, and all sorts of other sprites.

spritePath - the path to the image that the article uses.
owner - the fighter that "owns" the article. Can be None.
origin - where the article starts. This sets the center of the article, not the corner.
length - if this article has logic or animation, you can set this to be used in the update() method,
         just like a fighter's action.
"""
class Article(spriteManager.ImageSprite):
    def __init__(self, spritePath, owner, origin, length=1):
        spriteManager.ImageSprite.__init__(self,spritePath)
        self.rect.center = origin
        self.owner = owner
        self.frame = 0
        self.lastFrame = length
        
    def update(self):
        pass
    
class AnimatedArticle(spriteManager.SheetSprite):
    def __init__(self,sprite, owner, origin, imageWidth, length=1):
        spriteManager.SheetSprite.__init__(self, pygame.image.load(sprite), imageWidth)
        self.rect.center = origin
        self.owner = owner
        self.frame = 0
        self.lastFrame = length
    
    def update(self):
        self.getImageAtIndex(self.frame)
        self.frame += 1
        if self.frame == self.length: self.kill()
        
class ShieldArticle(Article):
    def __init__(self,image,owner):
        Article.__init__(self,image, owner, owner.rect.center)
        
    def update(self):
        self.rect.center = self.owner.rect.center
        if not self.owner.shield:
            self.kill()            
   
    def draw(self,screen,offset,zoom):
        # This is all the same as the base Draw method. We're overriding because we need to put some code in the middle of it.
        h = int(round(self.owner.rect.height * zoom))
        w = int(round(self.owner.rect.width * zoom))
        newOff = (int(offset[0] * zoom + self.rect.width/2 - self.owner.rect.width/2), int(offset[1] * zoom + self.rect.height/2 - self.owner.rect.height/2))
        
        # What this does:
        screenRect = pygame.Rect(newOff,(w,h)) # Store the rect that it WOULD have drawn to at full size
        w = int(w * float(self.owner.shieldIntegrity/100)) # Shrink based on shield integrity
        h = int(h * float(self.owner.shieldIntegrity/100))
        blitRect = pygame.Rect(newOff,(w,h)) # Make a new rect with the shrunk sizes
        blitRect.center = screenRect.center # Center it on the screen rect
        w = max(w,0) #We can't go negative
        h = max(h,0)
        blitSprite = pygame.transform.smoothscale(self.image, (w,h)) # Scale down the image
        
        screen.blit(blitSprite,blitRect)
