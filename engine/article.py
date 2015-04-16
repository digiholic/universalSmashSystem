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
    
class ShieldArticle(Article):
    def __init__(self,image,owner):
        Article.__init__(self,image, owner, owner.rect.center)
        
    def update(self):
        self.rect.center = self.owner.rect.center
        if self.owner.shield == False:
            self.kill()            
   
    def draw(self,screen,offset,zoom):
        # This is all the same as the base Draw method. We're overriding because we need to put some code in the middle of it.
        h = int(round(self.rect.height * zoom))
        w = int(round(self.rect.width * zoom))
        newOff = (int(offset[0] * zoom), int(offset[1] * zoom))
        
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