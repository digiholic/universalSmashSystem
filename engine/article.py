import pygame
import spriteManager
import math

"""
Articles are generated sprites that have their own behavior. For example, projectiles, shields,
particles, and all sorts of other sprites.

spritePath - the path to the image that the article uses.
owner - the fighter that "owns" the article. Can be None.
origin - where the article starts. This sets the center of the article, not the corner.
length - if this article has logic or animation, you can set this to be used in the update() method,
         just like a fighter's action.
"""
import settingsManager
class Article(spriteManager.ImageSprite):
    def __init__(self, spritePath, owner, origin, length=1, drawDepth = 1):
        spriteManager.ImageSprite.__init__(self,spritePath)
        self.rect.center = origin
        self.owner = owner
        self.frame = 0
        self.lastFrame = length
        self.tags = []
        self.drawDepth = drawDepth
        
    def update(self):
        pass
    
    def changeOwner(self, newOwner):
        self.owner = newOwner
        self.hitbox.owner = newOwner
    
    def activate(self):
        self.owner.articles.add(self)
    
    def deactivate(self):
        self.kill()
         
class AnimatedArticle(spriteManager.SheetSprite):
    def __init__(self, sprite, owner, origin, imageWidth, length=1):
        spriteManager.SheetSprite.__init__(self, pygame.image.load(sprite), imageWidth)
        self.rect.center = origin
        self.owner = owner
        self.frame = 0
        self.lastFrame = length
        self.tags = []
    
    def update(self):
        self.getImageAtIndex(self.frame)
        self.frame += 1
        if self.frame == self.lastFrame: self.kill()
    
    def changeOwner(self, newOwner):
        self.owner = newOwner
        self.hitbox.owner = newOwner
    
    def activate(self):
        self.owner.articles.add(self)
    
    def deactivate(self):
        self.kill()
                
class ShieldArticle(Article):
    def __init__(self,image,owner):
        import engine.hitbox as hitbox
        Article.__init__(self,image, owner, owner.rect.center)
        self.reflectHitbox = hitbox.PerfectShieldHitbox([0,0], [owner.shieldIntegrity*owner.var['shieldSize'], owner.shieldIntegrity*owner.var['shieldSize']], owner, hitbox.HitboxLock())
        self.reflectHitbox.article = self
        self.mainHitbox = hitbox.ShieldHitbox([0,0], [owner.shieldIntegrity*owner.var['shieldSize'], owner.shieldIntegrity*owner.var['shieldSize']], owner, hitbox.HitboxLock())
        self.mainHitbox.article = self
        
    def update(self):
        self.rect.center = [self.owner.rect.center[0]+50*self.owner.var['shieldSize']*self.owner.getSmoothedInput(64, 0.5)[0], 
                            self.owner.rect.center[1]+50*self.owner.var['shieldSize']*self.owner.getSmoothedInput(64, 0.5)[1]]
        if self.frame == 0:
            self.owner.active_hitboxes.add(self.reflectHitbox)
        if self.frame == 2:
            self.reflectHitbox.kill()
            self.owner.active_hitboxes.add(self.mainHitbox)
        if not self.owner.shield:
            self.reflectHitbox.kill()
            self.mainHitbox.kill()
            self.kill()     
        self.reflectHitbox.update()
        self.mainHitbox.update()
        self.owner.shieldDamage(1)
        self.frame += 1       
   
    def draw(self,screen,offset,zoom):
        # This is all the same as the base Draw method. We're overriding because we need to put some code in the middle of it.
        h = int(round(self.owner.rect.height * zoom))
        w = int(round(self.owner.rect.width * zoom))
        newOff = (int(offset[0] * zoom + self.rect.width/2.0*zoom - self.owner.rect.width/2.0*zoom), int(offset[1] * zoom + self.rect.height/2.0*zoom - self.owner.rect.height/2.0*zoom))
        
        # What this does:
        screenRect = pygame.Rect(newOff,(w,h)) # Store the rect that it WOULD have drawn to at full size
        w = int(w * float(self.owner.shieldIntegrity/100)*self.owner.var['shieldSize']) # Shrink based on shield integrity
        h = int(h * float(self.owner.shieldIntegrity/100)*self.owner.var['shieldSize'])
        blitRect = pygame.Rect(newOff,(w,h)) # Make a new rect with the shrunk sizes
        blitRect.center = screenRect.center # Center it on the screen rect
        w = max(w,0) #We can't go negative
        h = max(h,0)
        blitSprite = pygame.transform.smoothscale(self.image, (w,h)) # Scale down the image
        
        screen.blit(blitSprite,blitRect)

class LandingArticle(AnimatedArticle):
    def __init__(self,owner):
        width, height = (86, 22) #to edit these easier if (when) we change the sprite
        scaledWidth = owner.rect.width
        #self.scaleRatio = float(scaledWidth) / float(width)
        self.scaleRatio = 1
        scaledHeight = math.floor(height * self.scaleRatio)
        AnimatedArticle.__init__(self, settingsManager.createPath('sprites/halfcirclepuff.png'), owner, owner.rect.midbottom, 86, 6)
        self.rect.y -= scaledHeight / 2
        
    def draw(self, screen, offset, scale):
        return AnimatedArticle.draw(self, screen, offset, scale * self.scaleRatio)

class RespawnPlatformArticle(Article):
    def __init__(self,owner):
        width, height = (256,69)
        scaledWidth = owner.rect.width
        #self.scaleRatio = float(scaledWidth) / float(width)
        self.scaleRatio = 1
        Article.__init__(self, settingsManager.createPath('sprites/platform.png'), owner, owner.rect.midbottom, 120, drawDepth = -1)
        self.rect.bottom += self.rect.height / 4
    
    def draw(self, screen, offset, scale):
        return Article.draw(self, screen, offset, scale * self.scaleRatio)