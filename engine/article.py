import pygame
import spriteManager
import math
import random
import settingsManager
import engine.hitbox as hitbox
import engine.collisionBox as collisionBox
import engine.subaction
import numpy

"""
Articles are objects subordinate to a fighter that have their own behavior. For example, projectiles, shields,
particles, and all sorts of other objects. 

spritePath - the path to the image that the article uses.
owner - the fighter that "owns" the article. Can be None.
origin - where the article starts. This sets the center of the article, not the corner.
length - if this article has logic or animation, you can set this to be used in the update() method,
         just like a fighter's action.
"""
#Add method to get its own bounding rect
class DynamicArticle():
    def __init__(self,_owner,_sheet,_imgWidth=0,_originPoint=(0,0),_length=1,_spriteRate=0,_startingDirection=0,_draw_depth=1,_tags = []):
        self.owner = _owner
        self.game_state = self.owner.game_state

        self.sprite = spriteManager.SheetSprite(_sheet, _imgWidth)
        self.frame = 0
        self.last_frame = _length
        self.posx = 0
        self.posy = 0
        self.change_x = 0
        self.change_y = 0
        self.draw_depth = _draw_depth
        self.origin_point = _originPoint
        self.starting_direction = _startingDirection
        self.facing = _startingDirection
        self.tags = _tags

        #These determine the size and shape of the fighter's ECB
        #Keep these at 0 to make it fit the sprite
        self.ecb_size = [0,0]
        self.ecb_offset = [0,0]

        self.sprite_rate = _spriteRate
        self.base_sprite_rate = _spriteRate
        self.sprite_name = _sheet
        self.loop = True
        
        self.hitboxes = {}
        self.hitbox_locks = {}
        
        self.actions_at_frame = [[]]
        self.actions_before_frame = []
        self.actions_after_frame = []
        self.actions_at_last_frame = []
        self.actions_on_prevail = []
        self.actions_on_clank = []
        self.events = dict()
        self.set_up_actions = []
        self.tear_down_actions = []
        self.collision_actions = dict()
        
        self.active_hitboxes = pygame.sprite.Group()
        self.ecb = collisionBox.ECB(self)

        self.platform_phase = 0
        self.elasticity = 0
        self.ground_elasticity = 0
        
        self.default_vars = {}
        self.variables = {}

    ########################################################
    #                   UPDATE METHODS                     #
    ########################################################
        
    def update(self, *args): #Ignores actor
        self.ecb.normalize()
        self.ecb.store()
        
        for hbox in self.active_hitboxes:
            hbox.owner = self.owner
            hbox.article = self
            if hbox not in self.owner.active_hitboxes:
                self.owner.active_hitboxes.add(hbox)

        if self.sprite_rate is not 0:
            if self.sprite_rate < 0:
                self.sprite.getImageAtIndex((self.frame // self.sprite_rate)-1)
            else:
                self.sprite.getImageAtIndex(self.frame // self.sprite_rate)
        
        #Do all of the subactions involving update
        for act in self.actions_before_frame:
            act.execute(self,self)
        if self.frame < len(self.actions_at_frame):
            for act in self.actions_at_frame[self.frame]:
                act.execute(self,self)
        if self.frame == self.last_frame:
            for act in self.actions_at_last_frame:
                act.execute(self,self)
        
        self.updatePosition()
        self.ecb.normalize()
        
        if 'collides' in self.tags:
            self.collisionUpdate()
        else:
            self.posx += self.change_x
            self.posy += self.change_y

        for hitbox in self.hitboxes.values():
            hitbox.update()
            
        for act in self.actions_after_frame:
            act.execute(self,self)

        if self.frame == self.last_frame:
            self.deactivate()
        self.frame += 1 
        
    def updateAnimationOnly(self, *args): #Ignores actor
        from engine.subactions.sprite import changeSubimage,changeSprite,shiftSprite
        from engine.subactions.hitbox import activateHitbox, deactivateHitbox, modifyHitbox
        from engine.subactions.hurtbox import activateHurtbox, deactivateHurtbox, modifyHurtbox
        animation_actions = (changeSubimage.changeFighterSubimage, changeSprite.changeFighterSprite, shiftSprite.shiftSpritePosition,
                            activateHitbox.activateHitbox, deactivateHitbox.deactivateHitbox, modifyHitbox.modifyHitbox)
        
        for hbox in self.active_hitboxes:
            hbox.owner = self.owner
            hbox.article = self
            if hbox not in self.owner.active_hitboxes:
                self.owner.active_hitboxes.add(hbox)
        for act in self.actions_before_frame:
            if isinstance(act, animation_actions):
                act.execute(self,self)
        if self.frame < len(self.actions_at_frame):
            for act in self.actions_at_frame[self.frame]:
                if isinstance(act, animation_actions):
                    act.execute(self,self)
        if self.frame == self.last_frame:
            for act in self.actions_at_last_frame:
                if isinstance(act, animation_actions):
                    act.execute(self,self)
        for act in self.actions_after_frame:
            if isinstance(act, animation_actions):
                act.execute(self,self)
        
        if self.sprite_rate is not 0:
            if self.sprite_rate < 0:
                self.sprite.getImageAtIndex((self.frame // self.sprite_rate)-1)
            else:
                self.sprite.getImageAtIndex(self.frame // self.sprite_rate)
            
        for hitbox in self.hitboxes.values():
            hitbox.update()
                
        self.frame += 1      
    
    def activate(self):
        self.owner.articles.append(self)
        self.recenter()
        self.facing = self.owner.facing

        self.variables = self.default_vars.copy()
        print(self.variables)
    
        # Evironmental Collision Box
        self.ecb = collisionBox.ECB(self)

        # Hitboxes
        self.active_hitboxes = pygame.sprite.Group()
        
        self.change_x = 0
        self.change_y = 0
        
        if not self.facing == 0 and not self.facing == self.starting_direction: 
            self.sprite.flipX()
        for act in self.set_up_actions:
            act.execute(self,self)
        
    def deactivate(self):
        for hitbox in self.hitboxes.values():
            hitbox.kill()
        for act in self.tear_down_actions:
            act.execute(self,self)
        self.ecb = None
        if self.sprite: #This makes deactivating a deactive article safe
            self.sprite.kill()
        self.sprite = None
        if self in self.owner.articles:
            self.owner.articles.remove(self)

    def collisionUpdate(self):
        if 'platform_phase' in self.variables:
            self.platform_phase = self.variables['platform_phase']
        else:
            self.platform_phase = 0
        """ Execute movement and resolve collisions.
        This function is due for a huge overhaul.
        """
        
        loop_count = 0
        while loop_count < 2:
            self.updatePosition()
            self.ecb.normalize()
            bumped = False
            block_hit_list = collisionBox.getSizeCollisionsWith(self, self.game_state.platform_list)
            if not block_hit_list:
                break
            for block in block_hit_list:
                if block.solid or (self.platform_phase <= 0):
                    self.platform_phase = 0
                    if collisionBox.eject(self, block, self.platform_phase > 0):
                        bumped = True
                        break
            if not bumped:
                break
            loop_count += 1
        # TODO: Crush death if loopcount reaches the 10 resolution attempt ceiling

        self.updatePosition()
        self.ecb.normalize()

        t = 1

        to_bounce_block = None

        self.updatePosition()
        self.ecb.normalize()
        block_hit_list = collisionBox.getMovementCollisionsWith(self, self.game_state.platform_list)
        for block in block_hit_list:
            if self.ecb.pathRectIntersects(block.rect, self.change_x, self.change_y) > 0 and self.ecb.pathRectIntersects(block.rect, self.change_x, self.change_y) < t and collisionBox.catchMovement(self, block, self.platform_phase > 0): 
                t = self.ecb.pathRectIntersects(block.rect, self.change_x, self.change_y)
                to_bounce_block = block
                
        self.posy += self.change_y*t
        self.posx += self.change_x*t

        self.updatePosition()
        self.ecb.normalize()

        if to_bounce_block is not None and 'bounces' in self.tags:
            if 'elasticity' in self.variables:
                self.elasticity = self.variables['elasticity']
            else:
                self.elasticity = 0.0
            if 'ground_elasticity' in self.variables:
                self.ground_elasticity = self.variables['ground_elasticity']
            else:
                self.ground_elasticity = 0.0
            collisionBox.reflect(self, to_bounce_block)

    def draw(self,_screen,_offset,_scale):
        if settingsManager.getSetting('showECB'): 
            self.ecb.draw(_screen,_offset,_scale)
        return self.sprite.draw(_screen, _offset, _scale)

    """
    Recenter Self on origin point
    """
    def recenter(self):
        self.posx = self.owner.posx + (self.origin_point[0] * self.owner.facing)
        self.posy = self.owner.posy + self.origin_point[1]
        self.sprite.rect.center = [self.posx, self.posy]

    ########################################################
    #                  EVENT MANAGEMENT                    #
    ########################################################

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


    ########################################################
    #              COLLISIONS AND MOVEMENT                 #
    ########################################################


    def checkGround(self):
        self.updatePosition()
        return collisionBox.checkGround(self, self.game_state.platform_list, True)

    def checkLeftWall(self):
        self.updatePosition()
        return collisionBox.checkLeftWall(self, self.game_state.platform_list, True)

    def checkRightWall(self):
        self.updatePosition()
        return collisionBox.checkRightWall(self, self.game_state.platform_list, True)

    def checkBackWall(self):
        self.updatePosition()
        return collisionBox.checkBackWall(self, self.game_state.platform_list, True)

    def checkFrontWall(self):
        self.updatePosition()
        return collisionBox.checkFrontWall(self, self.game_state.platform_list, True)

    def checkCeiling(self):
        self.updatePosition()
        return collisionBox.checkCeiling(self, self.game_state.platform_list, True)

    def isGrounded(self):
        self.updatePosition()
        return collisionBox.isGrounded(self, self.game_state.platform_list, True)

    def isLeftWalled(self):
        self.updatePosition()
        return collisionBox.isLeftWalled(self, self.game_state.platform_list, True)

    def isRightWalled(self):
        self.updatePosition()
        return collisionBox.isRightWalled(self, self.game_state.platform_list, True)

    def isBackWalled(self):
        self.updatePosition()
        return collisionBox.isBackWalled(self, self.game_state.platform_list, True)

    def isFrontWalled(self):
        self.updatePosition()
        return collisionBox.isFrontWalled(self, self.game_state.platform_list, True)

    def isCeilinged(self):
        self.updatePosition()
        return collisionBox.isCeilinged(self, self.game_state.platform_list, True)

    def setSpeed(self,_speed,_direction):
        """ Set the article's speed. Instead of modifying the change_x and change_y values manually,
        this will calculate what they should be set at if you want to give a direction and
        magnitude instead.
        
        Parameters
        -----------
        _speed : float
            The total speed you want the fighter to move
        _direction : int
            The angle of the speed vector in degrees, 0 being right, 90 being up, 180 being left.
        """
        (x,y) = getXYFromDM(_direction,_speed)
        self.change_x = x
        self.change_y = y

    ########################################################
    #              ANIMATION FUNCTIONS                     #
    ########################################################

    def rotateSprite(self,_direction):
        """ Rotate's the fighter's sprite a given number of degrees
        
        Parameters
        -----------
        _direction : int
            The degrees to rotate towards. 0 being forward, 90 being up
        """
        self.sprite.rotate(-1 * (90 - _direction)) 
        
    def unRotate(self):
        """ Resets rotation to it's proper, straight upwards value """
        self.sprite.rotate()

    def changeSpriteImage(self,index,_loop=False):
        self.sprite.getImageAtIndex(index)

    def updatePosition(self):
        """ Passes the updatePosition call to the sprite.
        See documentation in SpriteLibrary.updatePosition
        """
        return self.sprite.updatePosition(self.posx, self.posy)
    
    ########################################################
    #                 COMBAT FUNCTIONS                     #
    ########################################################
    
    def applySubactions(self, _subacts):
        for subact in _subacts:
            subact.execute(self.current_action, self)
        return True # Our hit filter stuff expects this

    def changeOwner(self, _newOwner):
        self.owner = _newOwner
        for hitbox in self.hitboxes.values():
            hitbox.owner = _newOwner
        
    def activateHitbox(self,_hitbox):
        self.active_hitboxes.add(_hitbox)
        _hitbox.activate()

    ########################################################
    #                 HELPER FUNCTIONS                     #
    ########################################################
    
    """
    Articles need to know which way they're facing too.
    """
    def getForwardWithOffset(self,_offSet = 0):
        if self.facing == 1:
            return _offSet
        else:
            return 180 - _offSet

    
    def getDirectionMagnitude(self):
        """ Converts the fighter's current speed from XY components into
        a Direction and Magnitude. Angles are in degrees, with 0 being forward
        
        Return
        -----------
        (direction,magnitude) : Tuple (int,float)
            The direction in degrees, and the magnitude in map uints
        """
        if self.change_x == 0:
            magnitude = self.change_y
            direction = 90 if self.change_y < 0 else 270
            return (direction,magnitude)
        if self.change_y == 0:
            magnitude = self.change_x
            direction = 0 if self.change_x > 0 else 180
            return(direction,magnitude)
        
        direction = math.degrees(math.atan2(-self.change_y, self.change_x))
        direction = round(direction)
        magnitude = numpy.linalg.norm([self.change_x, self.change_y])
        
        return (direction,magnitude) 

    def getFacingDirection(self):
        """ A simple function that converts the facing variable into a direction in degrees.
        
        Return
        -----------
        The direction the fighter is facing in degrees, zero being right, 90 being up
        """
        if self.facing == 1: return 0
        else: return 180

    def flip(self):
        """ Flip the fighter so he is now facing the other way.
        Also flips the sprite for you.
        """
        self.facing = -self.facing
        self.sprite.flipX()

    def getForwardBackwardKeys(self):
        """ This returns a tuple of the key for forward, then backward
        Useful for checking if the fighter is pivoting, or doing a back air, or getting the
        proper key to dash-dance, etc.
        
        The best way to use this is something like
        (key,invkey) = actor.getForwardBackwardKeys()
        which will assign the variable "key" to the forward key, and "invkey" to the backward key.
        """
        if self.facing == 1: return ('right','left')
        else: return ('left','right')

    def playSound(self,_sound):
        self.owner.playSound(_sound)
          
class Article():
    def __init__(self, _spritePath, _owner, _origin, _length=1, _draw_depth = 1):
        self.sprite = spriteManager.ImageSprite(_spritePath)
        self.posx, self.posy = _origin
        self.sprite.rect.center = self.posx, self.posy
        self.owner = _owner
        self.frame = 0
        self.last_frame = _length
        self.tags = []
        self.draw_depth = _draw_depth

        self.sprite_rate = 0
        self.base_sprite_rate = 0
        self.sprite_name = _spritePath
        self.loop = False
        
    def update(self):
        self.sprite.updatePosition(self.posx, self.posy)

    def draw(self,_screen,_offset,_scale):
        return self.sprite.draw(_screen, _offset, _scale)
    
    def changeOwner(self, _newOwner):
        self.owner = _newOwner
        self.hitbox.owner = _newOwner
    
    def activate(self):
        self.owner.articles.append(self)
    
    def deactivate(self):
        self.sprite.kill()
        if self in self.owner.articles:
            self.owner.articles.remove(self)

         
class AnimatedArticle():
    def __init__(self, _sprite, _owner, _origin, _imageWidth, _length=1, _draw_depth=1):
        self.sprite = spriteManager.SheetSprite(pygame.image.load(_sprite), _imageWidth)
        self.posx, self.posy = _origin
        self.sprite.rect.center = _origin
        self.owner = _owner
        self.frame = 0

        self.sprite_rate = 1
        self.base_sprite_rate = 1
        self.sprite_name = _sprite
        self.loop = False

        self.last_frame = _length
        self.tags = []
        self.draw_depth = _draw_depth

    def draw(self,_screen,_offset,_scale):
        return self.sprite.draw(_screen, _offset, _scale)
    
    def update(self):
        self.sprite.updatePosition(self.posx, self.posy)
        if self.sprite_rate is not 0:
            if self.sprite_rate < 0:
                self.sprite.getImageAtIndex((self.frame // self.sprite_rate)-1)
            else:
                self.sprite.getImageAtIndex(self.frame // self.sprite_rate)
        self.frame += 1
        if self.frame == self.last_frame: self.deactivate()
    
    def changeOwner(self, _newOwner):
        self.owner = _newOwner
    
    def activate(self):
        self.owner.articles.append(self)
    
    def deactivate(self):
        self.sprite.kill()
        if self in self.owner.articles:
            self.owner.articles.remove(self)
                
class ShieldArticle(Article):
    def __init__(self,_image,_owner):
        Article.__init__(self,_image, _owner, (_owner.posx, _owner.posy))
        self.reflect_hitbox = hitbox.ReflectorHitbox(_owner, hitbox.HitboxLock(),
                                                         {'center':[0,0],
                                                          'size':[_owner.shield_integrity*_owner.stats['shield_size'], _owner.shield_integrity*_owner.stats['shield_size']],
                                                          'transcendence':6,
                                                          'priority':float('inf'),
                                                          'hp':float('inf'),
                                                          'velocity_multiplier': 0.75,
                                                          'damage_multiplier': 0.75
                                                         })
        self.reflect_hitbox.article = self
        self.main_hitbox = hitbox.ShieldHitbox(_owner, hitbox.HitboxLock(), 
                                               {'center':[0,0],
                                                'size':[_owner.shield_integrity*_owner.stats['shield_size'], _owner.shield_integrity*_owner.stats['shield_size']],
                                                'transcendence':-5,
                                                'priority':_owner.shield_integrity-8,
                                                'hp':_owner.shield_integrity,
                                               })
        self.main_hitbox.article = self
        self.sprite.scale = self.owner.shield_integrity*self.owner.stats['shield_size']/100.0

    def onPrevail(self, _actor, _hitbox, _other):
        if _hitbox == self.main_hitbox and self.frame > 2 and (isinstance(_other, hitbox.DamageHitbox) and not _other.ignore_shields):
            _actor.doAction('SheildStun')
            _actor.shield_integrity -= (_other.damage+_other.charge_damage*_other.charge)*_other.shield_multiplier
            _actor.hitstop = math.floor(((_other.damage+_other.charge_damage*_other.charge) / 3.0 + 3.0)*_other.hitlag_multiplier*settingsManager.getSetting('hitlag'))
            _actor.change_x = (_other.base_knockback+_other.charge_base_knockback*_other.charge)/5.0*math.cos(math.radians(_other.trajectory))
            _actor.current_action.last_frame = math.floor(((_other.damage+_other.charge_damage*_other.charge)*_other.shield_multiplier*0.375*_other.hitstun_multiplier+_other.base_hitstun/3.0)*settingsManager.getSetting('shieldStun'))

    def onClank(self, _actor, _hitbox, _other):
        self.owner.change_y = -15
        self.owner.doStunned(400)
        
    def update(self):
        self.sprite.rect.center = [self.owner.posx+50*self.owner.stats['shield_size']*self.owner.getSmoothedInput(int(self.owner.key_bindings.timing_window['smoothing_window']), 0.5)[0], 
                            self.owner.posy+50*self.owner.stats['shield_size']*self.owner.getSmoothedInput(int(self.owner.key_bindings.timing_window['smoothing_window']), 0.5)[1]]
        self.sprite.scale = (self.owner.shield_integrity*self.owner.stats['shield_size']/100.0)
        if self.frame == 0:
            self.owner.active_hitboxes.add(self.main_hitbox)
            self.owner.active_hitboxes.add(self.reflect_hitbox)
        if self.frame == 2:
            self.reflect_hitbox.kill()
        if not self.owner.shield:
            self.reflect_hitbox.kill()
            self.main_hitbox.kill()
            self.deactivate()     

        self.reflect_hitbox.rect.size = [self.owner.shield_integrity*self.owner.stats['shield_size'], self.owner.shield_integrity*self.owner.stats['shield_size']]
        self.main_hitbox.priority = self.owner.shield_integrity-8
        self.main_hitbox.hp = self.owner.shield_integrity
        self.main_hitbox.rect.size = [self.owner.shield_integrity*self.owner.stats['shield_size'], self.owner.shield_integrity*self.owner.stats['shield_size']]
        self.reflect_hitbox.update()
        self.main_hitbox.update()
        self.owner.shield_integrity -= .6
        self.frame += 1       
   
    def draw(self,_screen,_offset,_scale):
        print(self)
        return Article.draw(self, _screen, _offset, _scale)

class ParryArticle(Article):
    def __init__(self,_image,_owner):
        Article.__init__(self,_image, _owner, (_owner.posx, _owner.posy))
        self.reflect_hitbox = hitbox.ReflectorHitbox(_owner, hitbox.HitboxLock(),
                                                         {'center':[0,0],
                                                          'size':[_owner.shield_integrity*_owner.stats['shield_size']/2.0, _owner.shield_integrity*_owner.stats['shield_size']/2.0],
                                                          'transcendence':6,
                                                          'priority':float('inf'),
                                                          'hp':float('inf'),
                                                          'velocity_multiplier': 1.5,
                                                          'damage_multiplier': 1.5
                                                         })
        self.reflect_hitbox.article = self
        self.main_hitbox = hitbox.InvulnerableHitbox(_owner, hitbox.HitboxLock(),
                                                      {'center':[0,0],
                                                       'size':[_owner.shield_integrity*_owner.stats['shield_size']/2.0, _owner.shield_integrity*_owner.stats['shield_size']/2.0],
                                                       'transcendence':-5,
                                                       'priority':float('inf')
                                                      })
        self.main_hitbox.article = self
        self.sprite.scale = self.owner.shield_integrity*self.owner.stats['shield_size']/100.0*(.6-self.owner.current_action.frame*.1)

    def onPrevail(self, _actor, _hitbox, _other):
        if _hitbox == self.main_hitbox and (isinstance(_other, hitbox.DamageHitbox) or isinstance(_other, hitbox.GrabHitbox)):
            print("Successful parry!")
            from engine import hurtbox
            self.owner.grabbing = _other.owner
            _other.owner.grabbed_by = self.owner
            _actor.armor['parry_invuln'] = hurtbox.Intangibility(_actor)

    def onClank(self, _actor, _hitbox, _other):
        self.owner.change_y = -15
        self.owner.doStunned(400)
        
    def update(self):
        self.sprite.rect.center = [self.owner.posx+50*self.owner.stats['shield_size']*self.owner.getSmoothedInput(int(self.owner.key_bindings.timing_window['smoothing_window']), 0.5)[0], 
                            self.owner.posy+50*self.owner.stats['shield_size']*self.owner.getSmoothedInput(int(self.owner.key_bindings.timing_window['smoothing_window']), 0.5)[1]]
        self.sprite.scale = (self.owner.shield_integrity*self.owner.stats['shield_size']/100.0*(.6-self.owner.current_action.frame*.1))
        self.sprite.alpha = 0
        if self.frame == 0:
            self.owner.active_hitboxes.add(self.main_hitbox)
            self.owner.active_hitboxes.add(self.reflect_hitbox)
        if not self.owner.shield:
            self.reflect_hitbox.kill()
            self.main_hitbox.kill()
            self.deactivate()     
        self.main_hitbox.rect.size = [self.owner.shield_integrity*self.owner.stats['shield_size']*(.6-self.owner.current_action.frame*.1), self.owner.shield_integrity*self.owner.stats['shield_size']*(.6-self.owner.current_action.frame*.1)]
        self.reflect_hitbox.rect.size = [self.owner.shield_integrity*self.owner.stats['shield_size']*(.6-self.owner.current_action.frame*.1), self.owner.shield_integrity*self.owner.stats['shield_size']*(.6-self.owner.current_action.frame*.1)]
        self.reflect_hitbox.update()
        self.main_hitbox.update()
        self.owner.shield_integrity -= 5
        self.frame += 1       
   
    def draw(self,_screen,_offset,_scale):
        return Article.draw(self, _screen, _offset, _scale)

class LandingArticle(AnimatedArticle):
    def __init__(self,_owner):
        width, height = (86, 22) #to edit these easier if (when) we change the sprite
        scaled_width = _owner.sprite.rect.width
        #self.scale_ratio = float(scaled_width) / float(width)
        self.sprite.scale = 1
        scaled_height = math.floor(height * self.scale_ratio)
        AnimatedArticle.__init__(self, settingsManager.createPath('sprites/halfcirclepuff.png'), _owner, _owner.sprite.rect.midbottom, 86, 6)
        self.sprite.rect.y -= scaled_height / 2
        
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
        self.sprite.scale = _scale*.25
        self.posx, self.posy = _origin
        self.sprite.rect.center = _origin
        self.angle = _angle
        self.sprite.angle = _angle
        self.speed = _speed
        self.resistance = _resistance

        if _colorBase is None:
            base_color = [127, 127, 127]
        else:
            base_color = pygame.Color(_colorBase)
        for i in range(0, 31):
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
        
        self.sprite.recolor(self.sprite.image, (0,0,0), base_color)
        self.sprite.alpha(128)

    def update(self):
        self.posx += self.speed * math.cos(math.radians(self.angle))
        self.posy += -self.speed * math.sin(math.radians(self.angle))
        self.sprite.rect.centerx = self.posx
        self.sprite.rect.centery = self.posy
        self.speed -= self.resistance
        if self.speed <= 0:
            self.deactivate()
        

class RespawnPlatformArticle(Article):
    def __init__(self,_owner):
        width, height = (256,69)
        scaled_width = _owner.sprite.rect.width * 1.5
        scaled_height = _owner.sprite.rect.height * 1.5
        scale_ratio = float(scaled_width) / float(width)
        
        Article.__init__(self, settingsManager.createPath('sprites/platform.png'), _owner, _owner.sprite.rect.midbottom, 120, _draw_depth = -1)
        
        w,h = int(width * scale_ratio),int(height * scale_ratio)
        self.sprite.image = pygame.transform.smoothscale(self.sprite.image, (w,h))
        
        self.sprite.rect = self.sprite.image.get_rect()
        
        self.sprite.rect.center = _owner.sprite.rect.midbottom
        self.posx, self.posy = _owner.sprite.rect.midbottom
        self.sprite.rect.bottom += scaled_height // 4
        self.posy += scaled_height // 4
