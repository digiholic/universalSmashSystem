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
    def __init__(self,_owner,_sheet,_imgWidth=0,_originPoint=(0,0),_length=1,_spriteRate=0,_startingDirection=0,_draw_depth=1):
        self.owner = _owner
        spriteManager.SheetSprite.__init__(self, _sheet, _imgWidth)
        
        self.frame = 0
        self.last_frame = _length
        self.change_x = 0
        self.change_y = 0
        self.sprite_rate = _spriteRate
        self.draw_depth = _draw_depth
        self.facing = 1
        self.origin_point = _originPoint
        self.starting_direction = _startingDirection
        
        self.hitboxes = {}
        self.hitbox_locks = {}
        
        self.actions_at_frame = [[]]
        self.actions_before_frame = []
        self.actions_after_frame = []
        self.actions_at_last_frame = []
        self.actions_on_clank = []
        self.conditional_actions = dict()
        self.set_up_actions = []
        self.tear_down_actions = []
        self.collision_actions = dict()
        
        self.active_hitboxes = pygame.sprite.Group()
        
    def update(self):
        for hbox in self.active_hitboxes:
            hbox.owner = self.owner
            hbox.article = self
            if hbox not in self.owner.active_hitboxes:
                self.owner.active_hitboxes.add(hbox)
        
        #Animate the article
        if self.sprite_rate is not 0:
            if self.frame % self.sprite_rate == 0:
                if self.sprite_rate < 0:
                    self.getImageAtIndex((self.frame / self.sprite_rate)-1)
                else:
                    self.getImageAtIndex(self.frame / self.sprite_rate)
        
        #Do all of the subactions involving update
        for act in self.actions_before_frame:
            act.execute(self,self)
        if self.frame < len(self.actions_at_frame):
            for act in self.actions_at_frame[self.frame]:
                act.execute(self,self)
        if self.frame == self.last_frame:
            for act in self.actions_at_last_frame:
                act.execute(self,self)
        
        #Update stuff
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        for hitbox in self.hitboxes.values():
            hitbox.update()
            
        for act in self.actions_after_frame:
            act.execute(self,self)
        
        if self.frame == self.last_frame:
            self.deactivate()
        self.frame += 1 
    
    def activate(self):
        self.owner.articles.add(self)
        self.recenter()
        self.facing = self.owner.facing
        if not self.facing == 0 and not self.facing == self.starting_direction: 
            self.flipX()
        for act in self.set_up_actions:
            act.execute(self,self)
        
    def deactivate(self):
        for hitbox in self.hitboxes.values():
            hitbox.kill()
        for act in self.tear_down_actions:
            act.execute(self,self)
        self.kill()

    def onClank(self,_actor):
        for act in self.actions_on_clank:
            act.execute(self,_actor)
    
    def onCollision(self,_other):
        others_classes = list(map(lambda x :x.__name__,_other.__class__.__bases__)) + [_other.__class__.__name__]
        
        for classKey,subacts in self.collision_actions.iteritems():
            if (classKey in others_classes):
                for subact in subacts:
                    subact.execute(_other,self)
    
    """
    Articles need to know which way they're facing too.
    """
    def getForwardWithOffset(self,_offSet = 0):
        if self.facing == 1:
            return _offSet
        else:
            return 180 - _offSet
    
    """
    Recenter Self on origin point
    """
    def recenter(self):
        self.rect.centerx = self.owner.rect.centerx + (self.origin_point[0] * self.owner.facing)
        self.rect.centery = self.owner.rect.centery + self.origin_point[1]
        
    def changeSpriteImage(self,index):
        self.getImageAtIndex(index)
        
class Article(spriteManager.ImageSprite):
    def __init__(self, _spritePath, _owner, _origin, _length=1, _draw_depth = 1):
        spriteManager.ImageSprite.__init__(self,_spritePath)
        self.rect.center = _origin
        self.owner = _owner
        self.frame = 0
        self.last_frame = _length
        self.tags = []
        self.draw_depth = _draw_depth
        
    def update(self):
        pass
    
    def changeOwner(self, _newOwner):
        self.owner = _newOwner
        self.hitbox.owner = _newOwner
    
    def activate(self):
        self.owner.articles.add(self)
    
    def deactivate(self):
        self.kill()

         
class AnimatedArticle(spriteManager.SheetSprite):
    def __init__(self, _sprite, _owner, _origin, _imageWidth, _length=1, _draw_depth=1):
        spriteManager.SheetSprite.__init__(self, pygame.image.load(_sprite), _imageWidth)
        self.rect.center = _origin
        self.owner = _owner
        self.frame = 0
        self.last_frame = _length
        self.tags = []
        self.draw_depth = _draw_depth
    
    def update(self):
        self.getImageAtIndex(self.frame)
        self.frame += 1
        if self.frame == self.last_frame: self.kill()
    
    def changeOwner(self, _newOwner):
        self.owner = _newOwner
        self.hitbox.owner = _newOwner
    
    def activate(self):
        self.owner.articles.add(self)
    
    def deactivate(self):
        self.kill()
                
class ShieldArticle(Article):
    def __init__(self,_image,_owner):
        import engine.hitbox as hitbox
        Article.__init__(self,_image, _owner, _owner.rect.center)
        self.reflect_hitbox = hitbox.PerfectShieldHitbox([0,0], [_owner.shield_integrity*_owner.var['shield_size'], _owner.shield_integrity*_owner.var['shield_size']], _owner, hitbox.HitboxLock())
        self.reflect_hitbox.article = self
        self.main_hitbox = hitbox.ShieldHitbox([0,0], [_owner.shield_integrity*_owner.var['shield_size'], _owner.shield_integrity*_owner.var['shield_size']], _owner, hitbox.HitboxLock())
        self.main_hitbox.article = self
        
    def update(self):
        self.rect.center = [self.owner.rect.center[0]+50*self.owner.var['shield_size']*self.owner.getSmoothedInput(int(self.owner.key_bindings.timing_window['smoothing_window']), 0.5)[0], 
                            self.owner.rect.center[1]+50*self.owner.var['shield_size']*self.owner.getSmoothedInput(int(self.owner.key_bindings.timing_window['smoothing_window']), 0.5)[1]]
        if self.frame == 0:
            self.owner.active_hitboxes.add(self.reflect_hitbox)
        if self.frame == 2:
            self.reflect_hitbox.kill()
            self.owner.active_hitboxes.add(self.main_hitbox)
        if not self.owner.shield:
            self.reflect_hitbox.kill()
            self.main_hitbox.kill()
            self.kill()     
        self.reflect_hitbox.update()
        self.main_hitbox.update()
        self.owner.shieldDamage(0.7)
        self.frame += 1       
   
    def draw(self,_screen,_offset,_zoom):
        # This is all the same as the base Draw method. We're overriding because we need to put some code in the middle of it.
        h = int(round(self.owner.rect.height * _zoom))
        w = int(round(self.owner.rect.width * _zoom))
        new_off = (int(_offset[0] * _zoom + self.rect.width/2.0*_zoom - self.owner.rect.width/2.0*_zoom), int(_offset[1] * _zoom + self.rect.height/2.0*_zoom - self.owner.rect.height/2.0*_zoom))
        
        # What this does:
        screen_rect = pygame.Rect(new_off,(w,h)) # Store the rect that it WOULD have drawn to at full size
        w = int(w * float(self.owner.shield_integrity/100)*self.owner.var['shield_size']) # Shrink based on shield integrity
        h = int(h * float(self.owner.shield_integrity/100)*self.owner.var['shield_size'])
        blit_rect = pygame.Rect(new_off,(w,h)) # Make a new rect with the shrunk sizes
        blit_rect.center = screen_rect.center # Center it on the screen rect
        w = max(w,0) #We can't go negative
        h = max(h,0)
        blit_sprite = pygame.transform.smoothscale(self.image, (w,h)) # Scale down the image
        
        _screen.blit(blit_sprite,blit_rect)

class LandingArticle(AnimatedArticle):
    def __init__(self,_owner):
        width, height = (86, 22) #to edit these easier if (when) we change the sprite
        scaled_width = _owner.rect.width
        #self.scale_ratio = float(scaled_width) / float(width)
        self.scale_ratio = 1
        scaled_height = math.floor(height * self.scale_ratio)
        AnimatedArticle.__init__(self, settingsManager.createPath('sprites/halfcirclepuff.png'), _owner, _owner.rect.midbottom, 86, 6)
        self.rect.y -= scaled_height / 2
        
    def draw(self, _screen, _offset, _scale):
        return AnimatedArticle.draw(self, _screen, _offset, _scale * self.scale_ratio)

class HitArticle(Article):
    color_array = {
        (255, 102, 102),
        (170, 170, 0), 
        (0, 255, 0), 
        (0, 204, 204),
        (127, 127, 255),
        (255, 64, 255),
        (146, 146, 146),
        (234, 234, 0),
        (64, 255, 255),
        (255, 159, 255),
        (255, 255, 255)
    }

    def __init__(self, _owner, _origin, _scale, _angle, _speed, _resistance):
        self.scaled_size = math.floor(64*_scale)
        Article.__init__(self, settingsManager.createPath('sprites/hit_particle.png'), _owner, _origin, 64, -1)
        self.rect.center = _origin
        self.angle = _angle
        self.speed = _speed
        self.resistance = _resistance

class RespawnPlatformArticle(Article):
    def __init__(self,_owner):
        width, height = (256,69)
        scaled_width = _owner.rect.width * 1.5
        scale_ratio = float(scaled_width) / float(width)
        
        Article.__init__(self, settingsManager.createPath('sprites/platform.png'), _owner, _owner.rect.midbottom, 120, _draw_depth = -1)
        
        w,h = int(width * scale_ratio),int(height * scale_ratio)
        self.image = pygame.transform.smoothscale(self.image, (w,h))
        
        self.rect = self.image.get_rect()
        
        self.rect.center = _owner.rect.midbottom
        self.rect.bottom += self.rect.height / 4
    
    def draw(self, _screen, _offset, _scale):
        return Article.draw(self, _screen, _offset, _scale)
