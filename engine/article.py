import pygame
import spriteManager
import math
import random
import settingsManager
import engine.hitbox as hitbox

"""
Articles are generated sprites that have their own behavior. For example, projectiles, shields,
particles, and all sorts of other sprites.

spritePath - the path to the image that the article uses.
owner - the fighter that "owns" the article. Can be None.
origin - where the article starts. This sets the center of the article, not the corner.
length - if this article has logic or animation, you can set this to be used in the update() method,
         just like a fighter's action.
"""
#Add method to get its own bounding rect
class DynamicArticle(spriteManager.SheetSprite):
    def __init__(self,_owner,_sheet,_imgWidth=0,_originPoint=(0,0),_length=1,_spriteRate=0,_startingDirection=0,_draw_depth=1,_tags = []):
        self.owner = _owner
        spriteManager.SheetSprite.__init__(self, _sheet, _imgWidth)
        
        self.frame = 0
        self.last_frame = _length
        self.change_x = 0
        self.change_y = 0
        self.sprite_rate = _spriteRate
        self.draw_depth = _draw_depth
        self.origin_point = _originPoint
        self.starting_direction = _startingDirection
        self.facing = _startingDirection
        self.tags = _tags
        
        self.hitboxes = {}
        self.hitbox_locks = {}
        
        self.actions_at_frame = [[]]
        self.actions_before_frame = []
        self.actions_after_frame = []
        self.actions_at_last_frame = []
        self.actions_on_prevail = []
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

    def changeOwner(self, _newOwner):
        self.owner = _newOwner
        for hitbox in self.hitboxes.values():
            hitbox.owner = _newOwner

    def onPrevail(self,_actor,_hitbox,_other):
        for act in self.actions_on_prevail:
            act.execute(self,_actor,_hitbox,_other)

    def onClank(self,_actor,_hitbox,_other):
        for act in self.actions_on_clank:
            act.execute(self,_actor,_hitbox,_other)
    
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
    
    def activateHitbox(self,_hitbox):
        self.active_hitboxes.add(_hitbox)
        _hitbox.activate()
    
    def playSound(self,_sound):
        self.owner.playSound(_sound)
          
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
    
    def activate(self):
        self.owner.articles.add(self)
    
    def deactivate(self):
        self.kill()
                
class ShieldArticle(Article):
    def __init__(self,_image,_owner):
        Article.__init__(self,_image, _owner, _owner.rect.center)
        self.reflect_hitbox = hitbox.ReflectorHitbox(_owner, hitbox.HitboxLock(),
                                                         {'center':[0,0],
                                                          'size':[_owner.shield_integrity*_owner.var['shield_size'], _owner.shield_integrity*_owner.var['shield_size']],
                                                          'transcendence':6,
                                                          'priority':float('inf'),
                                                          'hp':float('inf'),
                                                          'velocity_multiplier': 1,
                                                          'damage_multiplier': 0.5
                                                         })
        self.reflect_hitbox.article = self
        self.parry_reflect_hitbox = hitbox.ReflectorHitbox(_owner, hitbox.HitboxLock(),
                                                         {'center':[0,0],
                                                          'size':[_owner.shield_integrity*_owner.var['shield_size'], _owner.shield_integrity*_owner.var['shield_size']],
                                                          'transcendence':6,
                                                          'priority':float('inf'),
                                                          'hp':float('inf'),
                                                          'velocity_multiplier': 1,
                                                          'damage_multiplier': 1.5
                                                         })
        self.parry_reflect_hitbox.article = self
        self.main_hitbox = hitbox.ShieldHitbox(_owner, hitbox.HitboxLock(), 
                                               {'center':[0,0],
                                                'size':[_owner.shield_integrity*_owner.var['shield_size'], _owner.shield_integrity*_owner.var['shield_size']],
                                                'transcendence':-5,
                                                'priority':_owner.shield_integrity-8,
                                                'hp':_owner.shield_integrity,
                                               })
        self.main_hitbox.article = self
        self.parry_hitbox = hitbox.InvulnerableHitbox(_owner, hitbox.HitboxLock(),
                                                      {'center':[0,0],
                                                       'size':[_owner.shield_integrity*_owner.var['shield_size'], _owner.shield_integrity*_owner.var['shield_size']],
                                                       'transcendence':-5,
                                                       'priority':float('inf')
                                                      })
        self.parry_hitbox.article = self
        self.scale = (self.owner.shield_integrity*self.owner.var['shield_size']/100.0)

    def onPrevail(self, _actor, _hitbox, _other):
        if _hitbox == self.main_hitbox and self.frame > 2 and (isinstance(_other, hitbox.DamageHitbox) and not _other.ignore_shields):
            _actor.doAction('SheildStun')
            _actor.shield_integrity -= _other.damage*_other.shield_multiplier
            _actor.hitstop = math.floor((_other.damage / 4.0 + 2.0)*_other.hitlag_multiplier*settingsManager.getSetting('hitlag'))
            _actor.change_x = _other.base_knockback/5.0*math.cos(math.radians(_other.trajectory))
            _actor.current_action.last_frame = math.floor((_other.damage*_other.shield_multiplier*3/4.0+_other.base_hitstun//5)*settingsManager.getSetting('shieldStun'))
        elif _hitbox == self.parry_hitbox or _hitbox == self.reflect_hitbox and (isinstance(_other, hitbox.DamageHitbox) or isinstance(_other, hitbox.GrabHitbox)):
            print("Successful parry!")
            _actor.doAction('NeutralAction')
            _other.owner.doAction('SlowGetup')
        elif _hitbox == self.parry_reflect_hitbox and (isinstance(_other, hitbox.DamageHitbox) and not _other.ignore_shields):
            _actor.doAction('NeutralAction')

    def onClank(self, _actor, _hitbox, _other):
        self.owner.change_y = -15
        self.owner.invulnerable = 20
        self.owner.doStunned(400)
        
    def update(self):
        self.rect.center = [self.owner.rect.center[0]+50*self.owner.var['shield_size']*self.owner.getSmoothedInput(int(self.owner.key_bindings.timing_window['smoothing_window']), 0.5)[0], 
                            self.owner.rect.center[1]+50*self.owner.var['shield_size']*self.owner.getSmoothedInput(int(self.owner.key_bindings.timing_window['smoothing_window']), 0.5)[1]]
        self.scale = (self.owner.shield_integrity*self.owner.var['shield_size']/100.0)
        if self.frame == 0:
            import engine.baseActions as baseActions
            if isinstance(self.owner.current_action, baseActions.Parry):
                self.owner.active_hitboxes.add(self.parry_hitbox)
                self.owner.active_hitboxes.add(self.parry_reflect_hitbox)
            else:
                self.owner.active_hitboxes.add(self.main_hitbox)
                self.owner.active_hitboxes.add(self.reflect_hitbox)
        if self.frame == 1:
            self.parry_hitbox.kill()
            self.parry_reflect_hitbox.kill()
        if self.frame == 2:
            self.reflect_hitbox.kill()
        if not self.owner.shield:
            self.reflect_hitbox.kill()
            self.main_hitbox.kill()
            self.parry_hitbox.kill()
            self.parry_reflect_hitbox.kill()
            self.kill()     

        self.reflect_hitbox.rect.size = [self.owner.shield_integrity*self.owner.var['shield_size'], self.owner.shield_integrity*self.owner.var['shield_size']]
        self.main_hitbox.priority = self.owner.shield_integrity-8
        self.main_hitbox.hp = self.owner.shield_integrity
        self.main_hitbox.rect.size = [self.owner.shield_integrity*self.owner.var['shield_size'], self.owner.shield_integrity*self.owner.var['shield_size']]
        self.parry_hitbox.rect.size = [self.owner.shield_integrity*self.owner.var['shield_size'], self.owner.shield_integrity*self.owner.var['shield_size']]
        self.parry_reflect_hitbox.rect.size = [self.owner.shield_integrity*self.owner.var['shield_size'], self.owner.shield_integrity*self.owner.var['shield_size']]
        self.reflect_hitbox.update()
        self.main_hitbox.update()
        self.parry_hitbox.update() 
        self.parry_reflect_hitbox.update()
        self.owner.shield_integrity -= 1
        self.frame += 1       
   
    def draw(self,_screen,_offset,_scale):
        return Article.draw(self, _screen, _offset, _scale)

class LandingArticle(AnimatedArticle):
    def __init__(self,_owner):
        width, height = (86, 22) #to edit these easier if (when) we change the sprite
        scaled_width = _owner.rect.width
        #self.scale_ratio = float(scaled_width) / float(width)
        self.scale = 1
        scaled_height = math.floor(height * self.scale_ratio)
        AnimatedArticle.__init__(self, settingsManager.createPath('sprites/halfcirclepuff.png'), _owner, _owner.rect.midbottom, 86, 6)
        self.rect.y -= scaled_height / 2
        
    def draw(self, _screen, _offset, _scale):
        return AnimatedArticle.draw(self, _screen, _offset, _scale)

class HitArticle(Article):
    color_change_array = [
        (3, 0, 0),
        (0, 1, 0),
        (0, 0, 9),
        (-3, 0, 0),
        (0, -1, 0),
        (0, 0, -9)
    ]

    def __init__(self, _owner, _origin, _scale=1, _angle=0, _speed=0, _resistance=0, _colorBase = None):
        Article.__init__(self, settingsManager.createPath('sprites/hit_particle.png'), _owner, _origin, 256, -1)
        self.scale = _scale*.25
        self.rect.center = _origin
        self.angle = _angle
        self.speed = _speed
        self.resistance = _resistance

        if _colorBase is None:
            base_color = [127, 127, 127]
        else:
            print(_colorBase)
            base_color = pygame.Color(_colorBase)
        print(base_color)
        for i in range(0, 1):
            random_displacement = random.choice(self.color_change_array)
            if base_color[0] + random_displacement[0] < 0:
                base_color[0] = 0
            elif base_color[0] + random_displacement[0] > 255:
                base_color[0] = 255
            else:
                base_color[0] += random_displacement[0]
            if base_color[1] + random_displacement[1] < 0:
                base_color[1] = 0
            elif base_color[1] + random_displacement[1] > 255:
                base_color[1] = 255
            else:
                base_color[1] += random_displacement[1]
            if base_color[2] + random_displacement[2] < 0:
                base_color[2] = 0
            elif base_color[2] + random_displacement[2] > 255:
                base_color[2] = 255
            else:
                base_color[2] += random_displacement[2]
        
        self.recolor(self.image, (0,0,0), base_color)
        self.alpha(128)

    def update(self):
        self.rect.x += self.speed * math.cos(math.radians(self.angle))
        self.rect.y += -self.speed * math.sin(math.radians(self.angle))
        self.speed -= self.resistance
        if self.speed <= 0:
            self.kill()
   
    def draw(self,_screen,_offset,_scale):
        return Article.draw(self, _screen, _offset, _scale)
        

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
