import engine.action as action
import engine.baseActions as baseActions
import engine.hitbox as hitbox
import engine.article as article
import engine.abstractFighter as abstractFighter
import math
import pygame

class ForwardSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self, 100)
        self.sprite_image = 0
        self.sprite_rate = 0
        self.should_continue = True

    def setUp(self, _actor):
        #TODO Attribute checking
        variables = {'center': [0,0],
                     'size': [80,80],
                     'damage': 1,
                     'hitstun_multiplier': 2,
                     'x_bias': 0,
                     'y_bias': .25,
                     'shield_multiplier': 1,
                     'velocity_multiplier': 1,
                     'transcendence': -1,
                     'priority': -7
                     }
        self.chain_hitbox = hitbox.AutolinkHitbox(_actor, hitbox.HitboxLock(), variables)
        self.fling_hitbox = self.sideSpecialHitbox(_actor)
        self.num_frames = 0
        self.ecb_offset = [0,7]
        self.ecb_size = [64, 78]
        if _actor.sideSpecialUses == 1:
            _actor.sideSpecialUses = 0
        else:
            self.should_continue = False
            return
        _actor.change_x = 0
        _actor.preferred_xspeed = 0
        _actor.flinch_knockback_threshold = 4
        _actor.changeSprite("nair",0)
    
    def onClank(self,_actor):
        self.chain_hitbox.damage = 0
        self.chain_hitbox.base_knockback = 0
        self.chain_hitbox.knockback_growth = 0
        self.fling_hitbox.priority = -9999
        self.chain_hitbox.base_hitstun = 0
        self.fling_hitbox.damage = 0
        self.fling_hitbox.base_knockback = 0
        self.fling_hitbox.knockback_growth = 0
        self.fling_hitbox.priority = -9999
        self.fling_hitbox.base_hitstun = 0

        _actor.landing_lag = 60
    
    class sideSpecialHitbox(hitbox.DamageHitbox):
        def __init__(self,_actor):
            variables = {'center':[0,0],
                         'size':[80,80],
                         'damage':6,
                         'base_knockback':4,
                         'knockback_growth':0.1,
                         'trajectory':300,
                         'shield_multiplier':10,
                         'hitlag_multiplier':2
                         }
            hitbox.DamageHitbox.__init__(self, _actor, hitbox.HitboxLock(), variables)
            
        def onCollision(self, _other):
            hitbox.Hitbox.onCollision(self, _other)
            if 'AbstractFighter' in list(map(lambda x:x.__name__,_other.__class__.__bases__)) + [_other.__class__.__name__]:
                if _other.lockHitbox(self):
                    if self.article is None:
                        self.owner.applyPushback(self.base_knockback/5.0, self.trajectory+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier)
                    if _other.grounded:
                        _other.applyKnockback(self.damage, 0, 0, 0, 1, 1)
                        _other.doAction('Prone')
                        _other.current_action.last_frame = 50
                    else:
                        _other.applyKnockback(self.damage, self.base_knockback, self.knockback_growth, self.trajectory, self.weight_influence, self.hitstun_multiplier)
                            
    def stateTransitions(self, _actor):
        if not self.should_continue:
            _actor.doAction('Fall')
        if _actor.grounded == False and self.frame >= 17:
            baseActions.grabLedges(_actor)

    def tearDown(self, _actor, _newAction):
        self.chain_hitbox.kill()
        self.fling_hitbox.kill()
        _actor.flinch_knockback_threshold = 0
        _actor.preferred_xspeed = 0

    def update(self, _actor):
        if not self.should_continue:
            return
        if _actor.grounded:
            _actor.sideSpecialUses = 1
        _actor.changeSpriteImage(self.sprite_image%16)
        _actor.hurtbox.rect.width = 64
        _actor.hurtbox.rect.height = 64
        _actor.hurtbox.rect.center = _actor.sprite.bounding_rect.center
        _actor.accel(_actor.var['air_control'])
        if self.frame <= self.last_frame-2:
            self.sprite_image += 1
            if self.frame <= 16:
                _actor.preferred_xspeed = 0
                _actor.change_x = 0
                if _actor.change_y > 2:
                    _actor.change_y = 2
                _actor.preferred_yspeed = 2
                if _actor.keysContain('special') and self.frame == 16 and self.last_frame < 240:
                    self.last_frame += 1
                    self.frame -= 1
            else: #Actually launch forwards
                _actor.preferred_yspeed = _actor.var['max_fall_speed']
                self.num_frames += 1
                self.chain_hitbox.update()
                _actor.active_hitboxes.add(self.chain_hitbox)
                (key, invkey) = _actor.getForwardBackwardKeys()
                if self.frame == 17:
                    _actor.setSpeed(_actor.var['run_speed'], _actor.getForwardWithOffset(0))
                    _actor.change_y = -12
                if self.sprite_image%6 == 0:
                    self.chain_hitbox.hitbox_lock = hitbox.HitboxLock()
                if _actor.keysContain(invkey):
                    _actor.preferred_xspeed = _actor.var['run_speed']//2*_actor.facing
                    self.frame += 2
                    if (self.frame > self.last_frame-2):
                        self.frame = self.last_frame-2
                elif _actor.keysContain(key):
                    _actor.preferred_xspeed = _actor.var['run_speed']*_actor.facing
                    if (self.frame > self.last_frame-2):
                        self.frame = self.last_frame-2
                else:
                    _actor.preferred_xspeed = _actor.var['run_speed']*3//4*_actor.facing
                    self.frame += 1
                    if (self.frame > self.last_frame-2):
                        self.frame = self.last_frame-2
                
        else:
            if self.frame == self.last_frame-1:
                self.fling_hitbox.damage += int(float(self.num_frames)/float(24))
                self.fling_hitbox.priority += int(float(self.num_frames)/float(24))
                self.fling_hitbox.base_knockback += float(self.num_frames)/float(24)
                self.fling_hitbox.update()
                _actor.active_hitboxes.add(self.fling_hitbox)
            else:
                self.fling_hitbox.kill()
            self.chain_hitbox.kill()
            if self.frame >= self.last_frame:
                if _actor.grounded:
                    _actor.landing_lag = 25
                    _actor.doAction('Land')
                else:
                    _actor.landing_lag = 25
                    _actor.doAction('Fall')

        self.frame += 1
            
class UpSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self, 70)
        self.angle = 90
        self.sprite_rate = 0
        
    def setUp(self, _actor):
        action.Action.setUp(self,_actor)
        shared_lock = hitbox.HitboxLock()
        self.launchHitbox = hitbox.DamageHitbox(_actor,shared_lock,
                                                {'center':[0,0],
                                                 'size':[64,64],
                                                 'damage':14,
                                                 'base_knockback':12,
                                                 'knockback_growth':0.1,
                                                 'trajectory': 90,
                                                 'hitstun_multiplier':2.8                                                 
                                                 })
        self.flyingHitbox = hitbox.DamageHitbox(_actor,shared_lock,
                                                {'center':[0,0],
                                                 'size':[64,64],
                                                 'damage':8,
                                                 'base_knockback':10,
                                                 'knockback_growth':0.05,
                                                 'trajectory': 90,
                                                 'hitstun_multiplier':2                                                
                                                 })
        _actor.changeSprite('dtilt')
        _actor.changeSpriteImage(4)
        
        
    def tearDown(self, _actor, _newAction):
        action.Action.tearDown(self,_actor,_newAction)
        self.launchHitbox.kill()
        self.flyingHitbox.kill()
        _actor.unRotate()
        _actor.preferred_yspeed = _actor.var['max_fall_speed']
    
    def stateTransitions(self,_actor):
        if self.frame < 19:
            _actor.change_y = 0
            _actor.preferred_yspeed = 0
        if self.frame > 19:
            baseActions.grabLedges(_actor)
        if self.frame >= 45:
            _actor.preferred_yspeed = _actor.var['max_fall_speed']
            baseActions.airControl(_actor)
    
    def update(self,_actor):
        _actor.landing_lag = 10
        if _actor.grounded:
            _actor.accel(_actor.var['static_grip'])
        else:
            _actor.accel(_actor.var['air_control'])
        if self.frame <= 19:
            _actor.unRotate()
            _actor.change_x = 0
            _actor.change_y = 0
            if (_actor.getSmoothedInput() == [0, 0]):
                self.angle = 90
            else:
                self.angle = math.atan2(-_actor.getSmoothedInput()[1], _actor.getSmoothedInput()[0])*180.0/math.pi
            direction = abstractFighter.getXYFromDM(self.angle, 1.0)
            _actor.rotateSprite(self.angle)
        if self.frame == 2:
            _actor.changeSpriteImage(5)
        if self.frame == 4:
            _actor.changeSpriteImage(6)
        if self.frame == 6:
            _actor.changeSpriteImage(7)
        if self.frame == 8:
            _actor.changeSpriteImage(8)
        if self.frame == 11:
            _actor.changeSpriteImage(9)
        if self.frame == 19:
            self.launchHitbox.trajectory = self.angle
            self.flyingHitbox.trajectory = self.angle
            _actor.active_hitboxes.add(self.launchHitbox)
            _actor.changeSprite('airjump')
            self.ecb_size = [92, 92]
            _actor.preferred_yspeed = _actor.var['max_fall_speed']
            _actor.change_x = direction[0] * 20
            _actor.preferred_xspeed = _actor.var['max_air_speed'] * direction[0]
            _actor.change_y = direction[1] * 20
        if self.frame == 20:
            self.launchHitbox.kill()
            _actor.active_hitboxes.add(self.flyingHitbox)
        if self.frame == 45:
            self.flyingHitbox.kill()
        if self.frame > 20:
            if self.frame % 2 == 0:
                _actor.changeSpriteImage((self.frame - 15) // 2,_loop=True)
            self.flyingHitbox.update()
        if self.frame == self.last_frame:
            _actor.doAction('Helpless')
        self.frame += 1
        
class NeutralAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,17)
        self.sprite_rate = 0
    
    def setUp(self, _actor):
        _actor.preferred_xspeed = 0
        _actor.changeSprite("neutral",0)
        self.jab_hitbox = self.outwardHitbox(_actor)
        
    def tearDown(self, _actor, _newAction):
        self.jab_hitbox.kill()

    def onClank(self,_actor):
        _actor.doAction('NeutralAction')
    
    def stateTransitions(self, _actor):
        if not _actor.grounded:
            _actor.doAction('Fall')
        elif self.frame == self.last_frame:
            if _actor.keysContain('attack') and not _actor.keysContain('left') and not _actor.keysContain('right') and not _actor.keysContain('up') and not _actor.keysContain('down'):
                self.jab_hitbox.hitbox_lock = hitbox.HitboxLock()
                self.frame = 0
                
    # Here's an example of creating an anonymous hitbox class.
    # This one calculates its trajectory based off of the angle between the two fighters.
    # Since this hitbox if specifically for this attack, we can hard code in the values.
    class outwardHitbox(hitbox.DamageHitbox):
        def __init__(self,_actor):
            variables = {'center': [0,0],
                         'size': [80,80],
                         'damage': 3,
                         'base_knockback':8,
                         'knockback_growth':0.02,
                         'trajectory':20
                         }
            hitbox.DamageHitbox.__init__(self, _actor, hitbox.HitboxLock(), variables)
            
        def onCollision(self,_other):
            hitbox.Hitbox.onCollision(self, _other)
            self.trajectory = abstractFighter.getDirectionBetweenPoints(self.owner.rect.midbottom, _other.rect.center)
            hitbox.DamageHitbox.onCollision(self, _other)
            
    def update(self, _actor):
        if self.frame < 4:
            _actor.changeSpriteImage(self.frame)
        elif self.frame == 4:
            self.jab_hitbox.update()
            _actor.active_hitboxes.add(self.jab_hitbox)
        elif self.frame >= 5 and self.frame <= 8:
            self.jab_hitbox.update()
            _actor.changeSpriteImage(9)
        elif self.frame >= 9 and self.frame <= 10:
            self.jab_hitbox.kill()
            _actor.changeSpriteImage(10)
        elif self.frame > 10:
            self.jab_hitbox.kill()
            if not self.frame > 14:
                _actor.changeSpriteImage(self.frame)
        _actor.hurtbox.rect.width -= 16
        _actor.hurtbox.rect.height -= 16
        _actor.hurtbox.rect.midbottom = _actor.sprite.bounding_rect.midbottom
        if self.frame == self.last_frame:
            _actor.doAction('NeutralAction')
        self.frame += 1

class GroundGrab(action.Action):
    def __init__(self):
        action.Action.__init__(self, 30)
        self.sprite_rate = 0
        self.hold_point = (0,30)

    def setUp(self, _actor):
        self.grab_hitbox = hitbox.GrabHitbox(_actor,hitbox.HitboxLock(),{'center':[30,0],
                                                                       'size': [30,30],
                                                                       'height': 30
                                                                       })
    def tearDown(self, _actor, _nextAction):
        self.grab_hitbox.kill()

    def stateTransitions(self, _actor):
        if not _actor.grounded:
            _actor.doAction('Fall')

    def update(self,_actor):
        self.grab_hitbox.update()
        _actor.preferred_xspeed = 0
        if self.frame == 0:
            _actor.changeSprite("pivot", 0)
        elif self.frame == 2:
            _actor.changeSpriteImage(1)
        elif self.frame == 4:
            _actor.changeSpriteImage(2)
            _actor.active_hitboxes.add(self.grab_hitbox)
        elif self.frame == 6:
            _actor.changeSpriteImage(3)
        elif self.frame == 8:
            _actor.changeSpriteImage(4)
        elif self.frame == 11:
            _actor.changeSpriteImage(3)
            self.grab_hitbox.kill()
        elif self.frame == 15:
            _actor.changeSpriteImage(2)
        elif self.frame == 20:
            _actor.changeSpriteImage(1)
        elif self.frame == 26:
            _actor.changeSpriteImage(0)
        if self.frame == self.last_frame:
            _actor.doAction('NeutralAction')
        self.frame += 1

class DashGrab(action.Action):
    def __init__(self):
        action.Action.__init__(self, 35)
        self.sprite_rate = 0

    def setUp(self, _actor):
        self.grab_hitbox = hitbox.GrabHitbox(_actor,hitbox.HitboxLock(),{'center':[40,0],
                                                                       'size': [50,30],
                                                                       'height': 30
                                                                       })

    def tearDown(self, _actor, _nextAction):
        self.grab_hitbox.kill()

    def stateTransitions(self, _actor):
        if not _actor.grounded:
            _actor.doAction('Fall')

    def update(self,_actor):
        self.grab_hitbox.update()
        _actor.preferred_xspeed = 0
        if self.frame == 0:
            _actor.changeSprite("pivot", 0)
        elif self.frame == 3:
            _actor.changeSpriteImage(1)
        elif self.frame == 6:
            _actor.changeSpriteImage(2)
            _actor.active_hitboxes.add(self.grab_hitbox)
        elif self.frame == 9:
            _actor.changeSpriteImage(3)
        elif self.frame == 13:
            _actor.changeSpriteImage(4)
        elif self.frame == 18:
            _actor.changeSpriteImage(3)
            self.grab_hitbox.kill()
        elif self.frame == 22:
            _actor.changeSpriteImage(2)
        elif self.frame == 26:
            _actor.changeSpriteImage(1)
        elif self.frame == 30:
            _actor.changeSpriteImage(0)
        if self.frame == self.last_frame:
            _actor.doAction('NeutralAction')
        self.frame += 1

class Pummel(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self,17)
        self.sprite_rate = 0

    def update(self, _actor):
        baseActions.BaseGrabbing.update(self, _actor)
        if self.frame == 0:
            _actor.changeSprite("neutral", self.frame)
        elif self.frame < 4:
            _actor.changeSpriteImage(self.frame)
        elif _actor.isGrabbing() and self.frame == 4:
            _actor.grabbing.dealDamage(3)
        elif self.frame >= 5 and self.frame <= 8:
            _actor.changeSpriteImage(9)
        elif self.frame >= 9 and self.frame <= 10:
            _actor.changeSpriteImage(10)
        elif self.frame > 10:
            if not (self.frame) > 14:
                _actor.changeSpriteImage(self.frame)
        _actor.hurtbox.rect.width -= 16
        _actor.hurtbox.rect.height -= 16
        _actor.hurtbox.rect.midbottom = _actor.sprite.bounding_rect.midbottom
        if self.frame == self.last_frame:
            _actor.doAction('Grabbing')

class UpThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self, 100)
        self.sprite_rate = 0

    def setUp(self, _actor):
        _actor.changeSprite("land",3)
        _actor.flinch_knockback_threshold = 10000
        _actor.flinch_damage_threshold = 10000

    def tearDown(self, _actor, _nextAction):
        baseActions.BaseGrabbing.tearDown(self, _actor, _nextAction)
        _actor.flinch_knockback_threshold = 0
        _actor.flinch_damage_threshold = 0

    def update(self, _actor):
        baseActions.BaseGrabbing.update(self, _actor)
        if self.frame < 8:
            _actor.changeSpriteImage(3-self.frame//2)
        elif self.frame == 8:
            _actor.change_y -= 45
            _actor.landing_lag = 12
        elif self.frame > 10:
            _actor.calcGrav(4)
            if _actor.grounded and _actor.change_y >= 0:
                if _actor.isGrabbing():
                    _actor.grabbing.applyKnockback(11, 12, 0.15, _actor.getForwardWithOffset(70))
                _actor.doAction('Fall')

class BackThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self, 22)
        self.sprite_rate = 0

    def setUp(self, _actor):
        _actor.changeSprite("bthrow")

    def tearDown(self, _actor, _nextAction):
        baseActions.BaseGrabbing.tearDown(self, _actor, _nextAction)

    def update(self, _actor):
        baseActions.BaseGrabbing.update(self, _actor)
        if self.frame == 1 and _actor.isGrabbing():
            _actor.grabbing.applyKnockback(7, 15, 0.05, _actor.getForwardWithOffset(170), 0.5)
        if self.frame <= 16:
            _actor.changeSpriteImage(self.frame//2)
        elif self.frame == self.last_frame: 
            _actor.flip()
            _actor.doAction('NeutralAction')

########################################################
#            BEGIN OVERRIDE CLASSES                    #
########################################################
class LedgeGetup(baseActions.LedgeGetup):
    def __init__(self):
        baseActions.LedgeGetup.__init__(self,27)
        self.sprite_rate = 0

    def setUp(self, _actor):
        baseActions.LedgeGetup.setUp(self, _actor)
        _actor.invulnerable = 20
        if _actor.facing == 1:
            _actor.rect.left -= _actor.rect.width//2
        else:
            _actor.rect.right += _actor.rect.width//2
            
    def update(self,_actor):
        if self.frame == 0:
            _actor.changeSprite("getup",0)
            _actor.createMask([255,255,255], 20, True, 24)
        if (self.frame >= 0) and (self.frame <= 6):
            _actor.changeSpriteImage(self.frame)
            if self.frame > 2:
                _actor.change_y = -19
            _actor.change_x = 0
        if (self.frame >= 8) and (self.frame <= 14):
            _actor.change_y = 0
            _actor.change_x = 11.5*_actor.facing
            if (self.frame % 2 == 0):
                _actor.changeSpriteImage(self.frame//2+4)
        if (self.frame > 15):
            if (self.frame % 3 == 2):
                _actor.changeSpriteImage(self.frame//3+6)
            _actor.change_x = _actor.var['max_ground_speed']*_actor.facing
        baseActions.LedgeGetup.update(self, _actor)

class LedgeAttack(baseActions.LedgeGetup):
    def __init__(self):
        baseActions.LedgeGetup.__init__(self,38)
        self.sprite_rate = 0

    def setUp(self,_actor):
        baseActions.LedgeGetup.setUp(self, _actor)
        _actor.invulnerable = 24
        _actor.createMask([255,255,255], 24, True, 24)
        self.dash_hitbox = hitbox.DamageHitbox(_actor,hitbox.HitboxLock(),{
                                                                         'center': [0,0],
                                                                         'size': [70,70],
                                                                         'damage': 2,
                                                                         'base_knockback': 8,
                                                                         'knockback_growth': 0.2,
                                                                         'trajectory': 20,
                                                                         'hitstun_multiplier': 2
                                                                         })
        self.chain_hitbox = hitbox.AutolinkHitbox(_actor,hitbox.HitboxLock(),{
                                                                         'center': [0,0],
                                                                         'size': [70,70],
                                                                         'damage': 2,
                                                                         'hitstun_multiplier': 2,
                                                                         'x_bias': 0,
                                                                         'y_bias': -1,
                                                                         'velocity_multiplier': 1.5
                                                                         })
    def tearDown(self,_actor,_newAction):
        self.dash_hitbox.kill()
        self.chain_hitbox.kill()
        _actor.change_x = 0
        _actor.preferred_xspeed = 0

    def update(self, _actor):
        if self.frame == 0:
            _actor.changeSprite("getup",0)
        if (self.frame >= 0) and (self.frame <= 6):
            _actor.changeSpriteImage(self.frame)
            self.ecb_size = [0, 100]
            if self.frame > 2:
                _actor.change_y = -19
            _actor.change_x = 0
        if (self.frame >= 8) and (self.frame <= 14):
            self.ecb_size = [0, 0]
            _actor.change_y = 0
            _actor.change_x = 11.5*_actor.facing
            if (self.frame % 2 == 0):
                _actor.changeSpriteImage(self.frame//2+4)
        if self.frame == 15:
            self.ecb_offset = [0,7]
            self.ecb_size = [96, 78]
            _actor.change_x = _actor.var['max_ground_speed']*_actor.facing
            _actor.preferred_xspeed = _actor.var['max_ground_speed']*_actor.facing
            _actor.changeSprite("nair", 0)
            self.sprite_rate = 1
            self.loop = True
        if self.frame == 22:
            self.sprite_rate = 2
        self.dash_hitbox.update()
        self.chain_hitbox.update()
        if self.frame == 17:
            _actor.active_hitboxes.add(self.chain_hitbox)
        if self.frame == 21:
            self.chain_hitbox.hitbox_lock = hitbox.HitboxLock()
        if self.frame == 25:
            self.chain_hitbox.hitbox_lock = hitbox.HitboxLock()
        if self.frame == 29:
            self.chain_hitbox.kill()
            _actor.active_hitboxes.add(self.dash_hitbox)
        if self.frame == 33:
            self.dash_hitbox.kill()
            _actor.preferred_xspeed = 0
        baseActions.LedgeGetup.update(self, _actor)

"""
I couldn't quite get this one exactly right, so I'm leaving it up, commented out
until I can figure out a better way
"""

"""
class LedgeRoll(baseActions.LedgeGetup):
    def __init__(self):
        baseActions.LedgeGetup.__init__(self, 43)
        self.sprite_rate = 0

    def setUp(self, _actor):
        baseActions.LedgeGetup.setUp(self, _actor)

    def tearDown(self, _actor, _nextAction):
        _actor.change_x = 0
        _actor.preferred_xspeed = 0
        if _actor.invulnerable > 0:
            _actor.invulnerable = 0
        _actor.mask = None

    def update(self, _actor):
        if self.frame == 0:
            _actor.invulnerable = 37
            _actor.createMask([255,255,255], 32, True, 24)
            _actor.changeSprite("getup",0)
        if (self.frame >= 0) and (self.frame <= 6):
            _actor.changeSpriteImage(self.frame)
            self.ecb_size = [0, 100]
            if self.frame > 2:
                _actor.change_y = -19
            _actor.change_x = 0
        if (self.frame >= 8) and (self.frame <= 14):
            self.ecb_size = [0, 0]
            _actor.change_y = 0
            _actor.change_x = 11.5*_actor.facing
            if (self.frame % 2 == 0):
                _actor.changeSpriteImage(self.frame//2+4)
        if self.frame == 15:
            _actor.change_x = _actor.var['dodge_speed']*_actor.facing
        if self.frame == 17:
            _actor.changeSprite("land", 1)
            _actor.flip()
            _actor.preferred_xspeed = 0
        if self.frame == 33:
            _actor.changeSprite("land", 0)
        baseActions.LedgeGetup.update(self, _actor)
"""

########################################################
#             BEGIN HELPER METHODS                     #
########################################################
