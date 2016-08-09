import pygame
import spriteManager
import math
import settingsManager

"""
Articles are generated sprites that have their own behavior. For example, projectiles, shields,
particles, and all sorts of other sprites.

spritePath - the path to the image that the article uses.
owner - the fighter that "owns" the article. Can be None.
origin - where the article starts. This sets the center of the article, not the corner.
length - if this article has logic or animation, you can set this to be used in the update() method,
         just like a fighter's action.
"""
class DynamicArticle(spriteManager.SheetSprite):
    def __init__(self,owner,sheet,imgWidth=0,originPoint=(0,0),length=1,spriteRate=0,drawDepth=1):
        self.owner = owner
        spriteManager.SheetSprite.__init__(self, sheet, imgWidth)
        
        self.frame = 0
        self.lastFrame = length
        self.change_x = 0
        self.change_y = 0
        self.spriteRate = spriteRate
        self.drawDepth = drawDepth
        self.facing = 1
        self.originPoint = originPoint
        
        self.hitboxes = {}
        self.hitboxLocks = {}
        
        self.actionsAtFrame = [[]]
        self.actionsBeforeFrame = []
        self.actionsAfterFrame = []
        self.actionsAtLastFrame = []
        self.actionsOnClank = []
        self.conditionalActions = dict()
        self.setUpActions = []
        self.tearDownActions = []
        self.collisionActions = dict()
        
        self.active_hitboxes = pygame.sprite.Group()
        
    def update(self):
        for hbox in self.active_hitboxes:
            hbox.owner = self.owner
            hbox.article = self
            if hbox not in self.owner.active_hitboxes:
                self.owner.active_hitboxes.add(hbox)
        
        #Animate the article
        if self.spriteRate is not 0:
            if self.frame % self.spriteRate == 0:
                if self.spriteRate < 0:
                    self.getImageAtIndex((self.frame / self.spriteRate)-1)
                else:
                    self.getImageAtIndex(self.frame / self.spriteRate)
        
        #Do all of the subactions involving update
        for act in self.actionsBeforeFrame:
            act.execute(self,self)
        if self.frame < len(self.actionsAtFrame):
            for act in self.actionsAtFrame[self.frame]:
                act.execute(self,self)
        if self.frame == self.lastFrame:
            for act in self.actionsAtLastFrame:
                act.execute(self,self)
        
        #Update stuff
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        for hitbox in self.hitboxes.values():
            hitbox.update()
            
        for act in self.actionsAfterFrame:
            act.execute(self,self)
            
        self.frame += 1 
        
    def activate(self):
        self.owner.articles.add(self)
        self.rect.centerx = self.owner.rect.centerx + self.originPoint[0]
        self.rect.centery = self.owner.rect.centery + self.originPoint[1]
        for act in self.setUpActions:
            act.execute(self,self)
        
    def deactivate(self):
        for hitbox in self.hitboxes.values():
            hitbox.kill()
        for act in self.tearDownActions:
            act.execute(self,self)
        self.kill()

    def onClank(self,actor):
        for act in self.actionsOnClank:
            act.execute(self,actor)
    
    def onCollision(self,other):
        othersClasses = list(map(lambda x :x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]
        if ('AbstractFighter' in othersClasses or 'Platform' in othersClasses):
            self.deactivate()
            
        for classKey,subacts in self.collisionActions:
            if (classKey in othersClasses):
                for subact in subacts:
                    subact.execute(self,other)
    
    """
    Articles need to know which way they're facing too.
    """
    def getForwardWithOffset(self,offSet = 0):
        if self.facing == 1:
            return offSet
        else:
            return 180 - offSet
    
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
    def __init__(self, sprite, owner, origin, imageWidth, length=1, drawDepth=1):
        spriteManager.SheetSprite.__init__(self, pygame.image.load(sprite), imageWidth)
        self.rect.center = origin
        self.owner = owner
        self.frame = 0
        self.lastFrame = length
        self.tags = []
        self.drawDepth = drawDepth
    
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
        scaledWidth = owner.rect.width * 1.5
        scaleRatio = float(scaledWidth) / float(width)
        
        Article.__init__(self, settingsManager.createPath('sprites/platform.png'), owner, owner.rect.midbottom, 120, drawDepth = -1)
        
        w,h = int(width * scaleRatio),int(height * scaleRatio)
        self.image = pygame.transform.smoothscale(self.image, (w,h))
        
        self.rect = self.image.get_rect()
        
        self.rect.center = owner.rect.midbottom
        self.rect.bottom += self.rect.height / 4
    
    def draw(self, screen, offset, scale):
        return Article.draw(self, screen, offset, scale)