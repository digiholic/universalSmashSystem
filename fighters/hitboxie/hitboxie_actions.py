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
                        self.owner.applyPushback(self.damage/4.0, self.trajectory+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier)
                    if _other.grounded:
                        _other.applyKnockback(self.damage, 0, 0, 0, 1, 1)
                        (otherDirect,_) = _other.getDirectionMagnitude()
                        _other.doTrip(50, _other.getForwardWithOffset(otherDirect))
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
        _actor.hurtbox.rect.center = _actor.sprite.boundingRect.center
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
            self.angle = math.atan2(-_actor.getSmoothedInput()[1]+0.0001, _actor.getSmoothedInput()[0])*180.0/math.pi
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
        action.Action.__init__(self,22)
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
        _actor.hurtbox.rect.midbottom = _actor.sprite.boundingRect.midbottom
        if self.frame == self.last_frame:
            _actor.doAction('NeutralAction')
        self.frame += 1

class GroundGrab(action.Action):
    def __init__(self):
        action.Action.__init__(self, 30)
        self.sprite_rate = 0

    def setUp(self, actor):
        self.grabHitbox = hitbox.GrabHitbox(actor,hitbox.HitboxLock(),{'center':[30,0],
                                                                       'size': [30,30],
                                                                       'height': 30
                                                                       })
    def tearDown(self, actor, other):
        self.grabHitbox.kill()

    def stateTransitions(self, actor):
        if not actor.grounded:
            actor.doAction('Fall')

    def update(self,actor):
        self.grabHitbox.update()
        actor.preferred_xspeed = 0
        if self.frame == 0:
            actor.changeSprite("pivot", 0)
        elif self.frame == 2:
            actor.changeSpriteImage(1)
        elif self.frame == 4:
            actor.changeSpriteImage(2)
            actor.active_hitboxes.add(self.grabHitbox)
        elif self.frame == 6:
            actor.changeSpriteImage(3)
        elif self.frame == 8:
            actor.changeSpriteImage(4)
        elif self.frame == 11:
            actor.changeSpriteImage(3)
            self.grabHitbox.kill()
        elif self.frame == 15:
            actor.changeSpriteImage(2)
        elif self.frame == 20:
            actor.changeSpriteImage(1)
        elif self.frame == 26:
            actor.changeSpriteImage(0)
        if self.frame == self.last_frame:
            actor.doAction('NeutralAction')
        self.frame += 1

class DashGrab(action.Action):
    def __init__(self):
        action.Action.__init__(self, 35)
        self.sprite_rate = 0

    def setUp(self, actor):
        self.grabHitbox = hitbox.GrabHitbox([40,0], [50,30], actor, hitbox.HitboxLock(), 30)

    def tearDown(self, actor, other):
        self.grabHitbox.kill()

    def stateTransitions(self, actor):
        if not actor.grounded:
            actor.doAction('Fall')

    def update(self,actor):
        self.grabHitbox.update()
        actor.preferred_xspeed = 0
        if self.frame == 0:
            actor.changeSprite("pivot", 0)
        elif self.frame == 3:
            actor.changeSpriteImage(1)
        elif self.frame == 6:
            actor.changeSpriteImage(2)
            actor.active_hitboxes.add(self.grabHitbox)
        elif self.frame == 9:
            actor.changeSpriteImage(3)
        elif self.frame == 13:
            actor.changeSpriteImage(4)
        elif self.frame == 18:
            actor.changeSpriteImage(3)
            self.grabHitbox.kill()
        elif self.frame == 22:
            actor.changeSpriteImage(2)
        elif self.frame == 26:
            actor.changeSpriteImage(1)
        elif self.frame == 30:
            actor.changeSpriteImage(0)
        if self.frame == self.last_frame:
            actor.doAction('NeutralAction')
        self.frame += 1

class Pummel(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self,22)
        self.sprite_rate = 0

    def update(self, actor):
        baseActions.BaseGrabbing.update(self, actor)
        if self.frame == 0:
            actor.changeSprite("neutral", self.frame)
        elif self.frame < 4:
            actor.changeSpriteImage(self.frame)
        elif actor.isGrabbing() and self.frame == 4:
            actor.grabbing.dealDamage(3)
        elif self.frame >= 5 and self.frame <= 8:
            actor.changeSpriteImage(9)
        elif self.frame >= 9 and self.frame <= 10:
            actor.changeSpriteImage(10)
        elif self.frame > 10:
            if not (self.frame) > 14:
                actor.changeSpriteImage(self.frame)
        actor.hurtbox.rect.width -= 16
        actor.hurtbox.rect.height -= 16
        actor.hurtbox.rect.midbottom = actor.sprite.boundingRect.midbottom
        if self.frame == self.last_frame:
            actor.doAction('Grabbing')

class UpThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self, 100)
        self.sprite_rate = 0

    def setUp(self, actor):
        actor.changeSprite("land",3)
        actor.flinch_knockback_threshold = 10000
        actor.flinch_damage_threshold = 10000

    def tearDown(self, actor, nextAction):
        baseActions.BaseGrabbing.tearDown(self, actor, nextAction)
        actor.flinch_knockback_threshold = 0
        actor.flinch_damage_threshold = 0

    def update(self, actor):
        baseActions.BaseGrabbing.update(self, actor)
        if self.frame < 8:
            actor.changeSpriteImage(3-self.frame//2)
        elif self.frame == 8:
            actor.change_y -= 45
            actor.landing_lag = 12
        elif self.frame > 10:
            actor.calcGrav(4)
            if actor.grounded and actor.change_y >= 0:
                if actor.isGrabbing():
                    actor.grabbing.applyKnockback(11, 12, 0.15, actor.getForwardWithOffset(70))
                actor.doAction('Fall')

class BackThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self, 22)
        self.sprite_rate = 0

    def setUp(self, actor):
        actor.changeSprite("bthrow")

    def tearDown(self, actor, nextAction):
        baseActions.BaseGrabbing.tearDown(self, actor, nextAction)

    def update(self, actor):
        baseActions.BaseGrabbing.update(self, actor)
        if self.frame == 1 and actor.isGrabbing():
            actor.grabbing.applyKnockback(7, 15, 0.05, actor.getForwardWithOffset(170), 0.5)
        if self.frame <= 16:
            actor.changeSpriteImage(self.frame//2)
        elif self.frame == self.last_frame: 
            actor.flip()
            actor.doAction('NeutralAction')

########################################################
#            BEGIN OVERRIDE CLASSES                    #
########################################################

class Move(baseActions.Move):
    def __init__(self,accel = True):
        baseActions.Move.__init__(self,15)
        self.sprite_rate = 0
        self.accel = accel
        
    def update(self, actor):
        if self.accel:
            if (self.frame == 0):
                actor.changeSprite("run",0)
            elif (self.frame == 3):
                actor.changeSpriteImage(1)
            elif (self.frame == 6):
                actor.changeSpriteImage(2)
            elif (self.frame == 9):
                actor.changeSpriteImage(3)
            elif (self.frame == 12):
                actor.changeSpriteImage(4)
        else:
            if (self.frame == 0):
                actor.changeSprite("run",4)
                
        baseActions.Move.update(self, actor)
        if (self.frame == self.last_frame):
            self.frame = 12

class Dash(baseActions.Dash):
    def __init__(self,accel = True):
        baseActions.Dash.__init__(self,15)
        self.sprite_rate = 0
        self.accel = accel
        
    def update(self, actor):
        if self.accel:
            if (self.frame == 0):
                actor.changeSprite("run",0)
            elif (self.frame == 2):
                actor.changeSpriteImage(1)
            elif (self.frame == 4):
                actor.changeSpriteImage(2)
            elif (self.frame == 6):
                actor.changeSpriteImage(3)
            elif (self.frame == 8):
                actor.changeSpriteImage(4)
        else:
            if (self.frame == 0):
                actor.changeSprite("run",4)
                
        
        baseActions.Dash.update(self, actor)
        
"""
class Run(baseActions.Run):
    def __init__(self):
        baseActions.Run.__init__(self,2)
        self.sprite_rate = 0
        
    def update(self, actor):
        actor.changeSprite("run",4)
                
        baseActions.Run.update(self, actor)
        if (self.frame == self.last_frame):
            self.frame = 1
"""
                   
class Pivot(baseActions.Pivot):
    def __init__(self):
        baseActions.Pivot.__init__(self,10)
        self.sprite_rate = 0
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("pivot",4)
        elif self.frame == 2:
            actor.changeSpriteImage(3)
        elif self.frame == 4:
            actor.changeSpriteImage(2)
        elif self.frame == 6:
            actor.changeSpriteImage(1)
        elif self.frame == 8:
            actor.changeSpriteImage(0)
        baseActions.Pivot.update(self, actor)
        
    def tearDown(self,actor,newAction):
        if isinstance(newAction, Move) or isinstance(newAction, Dash):
            newAction.accel = False

class RunPivot(baseActions.RunPivot):
    def __init__(self):
        baseActions.RunPivot.__init__(self,15)
        self.sprite_rate = 0
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("pivot",4)
        elif self.frame == 3:
            actor.changeSpriteImage(3)
        elif self.frame == 6:
            actor.changeSpriteImage(2)
        elif self.frame == 9:
            actor.changeSpriteImage(1)
        elif self.frame == 12:
            actor.changeSpriteImage(0)
        baseActions.RunPivot.update(self, actor)
        
    def tearDown(self,actor,newAction):
        if isinstance(newAction, Dash):
            newAction.accel = False

class Grabbing(baseActions.Grabbing):
    def __init__(self):
        baseActions.Grabbing.__init__(self,1)
        self.sprite_rate = 0

    def update(self, actor):
        baseActions.Grabbing.update(self, actor)
        actor.change_x = 0
        if self.frame == 0:
            actor.changeSprite('pivot', 4)
        self.frame += 1
        
class Stop(baseActions.Stop):
    def __init__(self):
        baseActions.Stop.__init__(self, 9)
        self.sprite_rate = 0
    
    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("pivot",0)
        elif self.frame == 3:
            actor.changeSpriteImage(1)
        elif self.frame == 6:
            actor.changeSpriteImage(2)
        baseActions.Stop.update(self, actor)

class RunStop(baseActions.RunStop):
    def __init__(self):
        baseActions.RunStop.__init__(self, 12)
        self.sprite_rate = 0
    
    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("pivot",0)
        elif self.frame == 4:
            actor.changeSpriteImage(1)
        elif self.frame == 8:
            actor.changeSpriteImage(2)
        baseActions.RunStop.update(self, actor)


class CrouchGetup(baseActions.CrouchGetup):
    def __init__(self):
        baseActions.CrouchGetup.__init__(self, 9)
        self.sprite_rate = 0

    def setUp(self, actor):
        actor.changeSprite('land', 2)

    def update(self, actor):
        actor.changeSpriteImage(3-self.frame/3)
        baseActions.CrouchGetup.update(self, actor)
        
class HitStun(baseActions.HitStun):
    def __init__(self,hitstun=1,direction=0):
        baseActions.HitStun.__init__(self, hitstun, direction)
        self.sprite_rate = 0

    def setUp(self, actor):
        baseActions.HitStun.setUp(self, actor)
        actor.sideSpecialUses = 1
    
    def update(self, actor):
        baseActions.HitStun.update(self, actor)
        if self.frame == 1:
            if actor.grounded:
                actor.changeSprite("land",1)
            else:
                actor.changeSprite("jump")
        
class Jump(baseActions.Jump):
    def __init__(self):
        baseActions.Jump.__init__(self,8,5)
        self.sprite_rate = 0
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",0)
        elif self.frame == 1:
            actor.changeSpriteImage(1)
        elif self.frame == 2:
            actor.changeSpriteImage(2)
        elif self.frame == 3:
            actor.changeSpriteImage(3)
        elif self.frame == 5:
            actor.changeSprite("jump")
        baseActions.Jump.update(self, actor)
        

class AirJump(baseActions.AirJump):
    def __init__(self):
        baseActions.AirJump.__init__(self,8,4)
        self.sprite_rate = 0
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("airjump",0)
        elif self.frame == 1:
            actor.changeSpriteImage(1)
        elif self.frame == 2:
            actor.changeSpriteImage(2)
        elif self.frame == 4:
            actor.changeSpriteImage(3)
        elif self.frame == 6:
            actor.changeSpriteImage(4)
        elif self.frame == 8:
            actor.changeSpriteImage(0)
        baseActions.AirJump.update(self, actor)

class Helpless(baseActions.Helpless):
    def __init__(self):
        baseActions.Helpless.__init__(self)
        self.sprite_rate = 0

    def update(self, actor):
        actor.changeSprite("jump")
        baseActions.Helpless.update(self, actor)
            
class Land(baseActions.Land):
    def __init__(self):
        baseActions.Land.__init__(self)
        self.sprite_rate = 0

    def setUp(self, actor):
        baseActions.Land.setUp(self, actor)
        actor.sideSpecialUses = 1
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",0)
        else:
            if self.frame < 12:
                if self.frame % 3 == 0:
                    actor.changeSpriteImage(self.frame // 3)
        
        baseActions.Land.update(self, actor)

class HelplessLand(baseActions.HelplessLand):
    def __init__(self):
        baseActions.HelplessLand.__init__(self)
        self.sprite_rate = 0

    def setUp(self, actor):
        baseActions.HelplessLand.setUp(self, actor)
        actor.sideSpecialUses = 1
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",0)
        else:
            if self.frame < 12:
                if self.frame % 3 == 0:
                    actor.changeSpriteImage(self.frame // 3)
        
        baseActions.HelplessLand.update(self, actor)

class Trip(baseActions.Trip):
    def __init__(self, length=1, direction=0):
        baseActions.Trip.__init__(self, length, direction)
        self.sprite_rate = 0

    def setUp(self, actor):
        baseActions.Trip.setUp(self, actor)
        actor.sideSpecialUses = 1

    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("land", 3)
        baseActions.Trip.update(self, actor)

class Prone(baseActions.Prone):
    def __init__(self):
        baseActions.Prone.__init__(self, 60)
        self.sprite_name = 'land'
        self.sprite_rate = 2
        
    def update(self, actor):
        if self.frame == 6: actor.changeSpriteImage(3)

class Getup(baseActions.Getup):
    def __init__(self, direction=0):
        baseActions.Getup.__init__(self, direction, 12)
        self.sprite_rate = 0

    def update(self, actor):
        if self.frame < 12:
            if self.frame % 3 == 0:
                actor.changeSprite("land", 3-self.frame//3)
        baseActions.Getup.update(self, actor)

class GetupAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,36)
        self.sprite_rate = 0

    def setUp(self, actor):
        actor.preferred_xspeed = 0
        actor.changeSprite("nair")
        self.ecb_offset = [0,7]
        self.ecb_size = [64, 78]
        self.dashHitbox = hitbox.DamageHitbox(actor,hitbox.HitboxLock(),{
                                                                         'center': [0,0],
                                                                         'size': [70,70],
                                                                         'damage': 2,
                                                                         'base_knockback': 5,
                                                                         'knockback_growth': 0.1,
                                                                         'trajectory': 20,
                                                                         'hitstun_multiplier': 2
                                                                         })
        self.chainHitbox = hitbox.AutolinkHitbox(actor,hitbox.HitboxLock(),{
                                                                         'center': [0,0],
                                                                         'size': [70,70],
                                                                         'damage': 2,
                                                                         'hitstun_multiplier': 2,
                                                                         'x_bias': 0,
                                                                         'y_bias': -1,
                                                                         'velocity_multiplier': 1.5
                                                                         })
    def onClank(self,actor):
        actor.doAction('NeutralAction')

    def tearDown(self,actor,other):
        self.dashHitbox.kill()
        self.chainHitbox.kill()
        actor.preferred_xspeed = 0

    def stateTransitions(self, actor):
        if not actor.grounded:
            actor.doAction('Fall')

    def update(self,actor):
        if self.frame%2 == 0 and self.frame <= 12:
            actor.changeSpriteImage(self.frame//2)
        elif self.frame <= 28:
            actor.changeSpriteImage((self.frame-4)%16)
        elif self.frame%2 == 0:
            actor.changeSpriteImage((self.frame//2-8)%16)

        self.dashHitbox.update()
        self.chainHitbox.update()

        if self.frame == 12:
            actor.active_hitboxes.add(self.chainHitbox)
        if self.frame == 16:
            self.chainHitbox.hitbox_lock = hitbox.HitboxLock()
        if self.frame == 20:
            self.chainHitbox.hitbox_lock = hitbox.HitboxLock()
        if self.frame == 24:
            self.chainHitbox.kill()
            actor.active_hitboxes.add(self.dashHitbox)
        if self.frame == 28:
            self.dashHitbox.kill()
            actor.preferred_xspeed = 0

        if self.frame == self.last_frame:
            actor.doAction('NeutralAction')
        self.frame += 1

class PlatformDrop(baseActions.PlatformDrop):
    def __init__(self):
        baseActions.PlatformDrop.__init__(self, 12, 6, 9)
        self.sprite_rate = 0
        
    def update(self,actor):
        if self.frame == 2:
            actor.changeSprite("airjump",4)
            actor.change_y = 3
        elif self.frame == 4:
            actor.changeSpriteImage(3)
        elif self.frame == 6:
            actor.changeSpriteImage(2)
        elif self.frame == 8:
            actor.changeSpriteImage(1)
        elif self.frame == 10:
            actor.changeSpriteImage(0)
        baseActions.PlatformDrop.update(self, actor)
        
class Shield(baseActions.Shield):
    def __init__(self, new_shield=True):
        baseActions.Shield.__init__(self, new_shield)
        self.sprite_rate = 0
    
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("jump")
        baseActions.Shield.update(self, actor)

class ShieldStun(baseActions.ShieldStun):
    def __init__(self, length=1):
        baseActions.ShieldStun.__init__(self, length)
        self.sprite_rate = 0

    def update(self, actor):
        actor.createMask([191, 63, 191], self.last_frame, False, 8)
        baseActions.ShieldStun.update(self, actor)

class Stunned(baseActions.Stunned):
    def __init__(self, length=1):
        baseActions.Stunned.__init__(self, length)
        self.sprite_rate = 0

    def setUp(self, actor):
        baseActions.Stunned.setUp(self, actor)
        actor.sideSpecialUses = 1

    def tearDown(self, actor, newAction):
        actor.mask = None

    def update(self, actor):
        if self.frame == 0:
            actor.createMask([255, 0, 255], 99999, True, 8)
        baseActions.Stunned.update(self, actor)
        
class ForwardRoll(baseActions.ForwardRoll):
    def __init__(self):
        baseActions.ForwardRoll.__init__(self)
        self.sprite_rate = 0
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",1)
        elif self.frame == self.end_invuln_frame:
            actor.changeSprite("land",0)
        baseActions.ForwardRoll.update(self, actor)
        
class BackwardRoll(baseActions.BackwardRoll):
    def __init__(self):
        baseActions.BackwardRoll.__init__(self)
        self.sprite_rate = 0
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",1)
        elif self.frame == self.end_invuln_frame:
            actor.changeSprite("land",0)
        baseActions.BackwardRoll.update(self, actor)
        
class SpotDodge(baseActions.SpotDodge):
    def __init__(self):
        baseActions.SpotDodge.__init__(self)
        self.sprite_rate = 0
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",0)
        if self.frame < 4:
            actor.changeSpriteImage(self.frame)
        elif self.frame == 21:
            actor.changeSpriteImage(2)
        elif self.frame == 22:
            actor.changeSpriteImage(1)
        elif self.frame == 23:
            actor.changeSpriteImage(0)
        baseActions.SpotDodge.update(self, actor)
        
class AirDodge(baseActions.AirDodge):
    def __init__(self):
        baseActions.AirDodge.__init__(self)
        self.sprite_rate = 0
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("nair",0)
        elif self.frame == self.start_invuln_frame:
            actor.changeSpriteImage(-round(abs(actor.change_x)))
        elif self.frame == self.end_invuln_frame:
            actor.changeSpriteImage(0)
        baseActions.AirDodge.update(self, actor)

class Trapped(baseActions.Trapped):
    def __init__(self, length=1):
        baseActions.Trapped.__init__(self, length)
        self.sprite_rate = 0

    def setUp(self, actor):
        baseActions.Trapped.setUp(self, actor)
        actor.sideSpecialUses = 1

    def update(self, actor):
        actor.changeSprite("idle")
        baseActions.Trapped.update(self, actor)

class Grabbed(baseActions.Grabbed):
    def __init__(self,height=0):
        baseActions.Grabbed.__init__(self, height)
        self.sprite_rate = 0

    def setUp(self, actor):
        baseActions.Grabbed.setUp(self, actor)
        actor.sideSpecialUses = 1

    def update(self,actor):
        actor.changeSprite("idle")
        baseActions.Grabbed.update(self, actor)

class Release(baseActions.Release):
    def __init__(self,height=0):
        baseActions.Release.__init__(self)
        self.sprite_rate = 0

    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("pivot",4)
        elif self.frame == 2:
            actor.changeSpriteImage(3)
        elif self.frame == 4:
            actor.changeSpriteImage(2)
        elif self.frame == 10:
            actor.changeSpriteImage(3)
        elif self.frame == 12:
            actor.changeSpriteImage(4)
        baseActions.Release.update(self, actor)

class Released(baseActions.Released):
    def __init__(self):
        baseActions.Released.__init__(self)
        self.sprite_rate = 0

    def setUp(self, actor):
        baseActions.Released.setUp(self, actor)
        actor.changeSprite("jump")

class LedgeGrab(baseActions.LedgeGrab):
    def __init__(self,ledge=None):
        baseActions.LedgeGrab.__init__(self, ledge)
        self.sprite_rate = 0

    def setUp(self, actor):
        baseActions.LedgeGrab.setUp(self, actor)
        actor.sideSpecialUses = 1
        
    def update(self,actor):
        actor.changeSprite('jump')
        baseActions.LedgeGrab.update(self, actor)

class LedgeGetup(baseActions.LedgeGetup):
    def __init__(self):
        baseActions.LedgeGetup.__init__(self,27)
        self.sprite_rate = 0

    def setUp(self, actor):
        baseActions.LedgeGetup.setUp(self, actor)
        if actor.facing == 1:
            actor.rect.left -= actor.rect.width//2
        else:
            actor.rect.right += actor.rect.width//2
            
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("getup",0)
            actor.createMask([255,255,255], 24, True, 24)
        if (self.frame >= 0) and (self.frame <= 6):
            actor.changeSpriteImage(self.frame)
            self.ecb_size = [0, 100]
            if self.frame > 2:
                actor.change_y = -19
            actor.change_x = 0
        if (self.frame >= 8) and (self.frame <= 14):
            self.ecb_size = [0, 0]
            actor.change_y = 0
            actor.change_x = 11.5*actor.facing
            if (self.frame % 2 == 0):
                actor.changeSpriteImage(self.frame//2+4)
        if (self.frame > 15):
            if (self.frame % 3 == 2):
                actor.changeSpriteImage(self.frame//3+6)
            actor.change_x = actor.var['max_ground_speed']*actor.facing
        baseActions.LedgeGetup.update(self, actor)

class LedgeAttack(baseActions.LedgeGetup):
    def __init__(self):
        baseActions.LedgeGetup.__init__(self,36)
        self.sprite_rate = 0

    def setUp(self,actor):
        baseActions.LedgeGetup.setUp(self, actor)
        actor.invincibility = 24
        actor.createMask([255,255,255], 24, True, 24)
        self.dashHitbox = hitbox.DamageHitbox(actor,hitbox.HitboxLock(),{
                                                                         'center': [0,0],
                                                                         'size': [70,70],
                                                                         'damage': 2,
                                                                         'base_knockback': 8,
                                                                         'knockback_growth': 0.2,
                                                                         'trajectory': 20,
                                                                         'hitstun_multiplier': 2
                                                                         })
        self.chainHitbox = hitbox.AutolinkHitbox(actor,hitbox.HitboxLock(),{
                                                                         'center': [0,0],
                                                                         'size': [70,70],
                                                                         'damage': 2,
                                                                         'hitstun_multiplier': 2,
                                                                         'x_bias': 0,
                                                                         'y_bias': -1,
                                                                         'velocity_multiplier': 1.5
                                                                         })
    def tearDown(self,actor,other):
        self.dashHitbox.kill()
        self.chainHitbox.kill()
        actor.change_x = 0
        actor.preferred_xspeed = 0

    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("getup",0)
        if (self.frame >= 0) and (self.frame <= 6):
            actor.changeSpriteImage(self.frame)
            self.ecb_size = [0, 100]
            if self.frame > 2:
                actor.change_y = -19
            actor.change_x = 0
        if (self.frame >= 8) and (self.frame <= 14):
            self.ecb_size = [0, 0]
            actor.change_y = 0
            actor.change_x = 11.5*actor.facing
            if (self.frame % 2 == 0):
                actor.changeSpriteImage(self.frame//2+4)
        if self.frame == 15:
            actor.change_x = actor.var['max_ground_speed']*actor.facing
            actor.preferred_xspeed = actor.var['max_ground_speed']*actor.facing
        if self.frame >= 15 and self.frame <= 22:
            actor.changeSprite("nair", (self.frame-15)%16)
        if self.frame%2 == 0 and self.frame > 22:
            actor.changeSprite("nair", (self.frame//2-11)%16)
        self.dashHitbox.update()
        self.chainHitbox.update()
        if self.frame == 17:
            actor.active_hitboxes.add(self.chainHitbox)
        if self.frame == 21:
            self.chainHitbox.hitbox_lock = hitbox.HitboxLock()
        if self.frame == 25:
            self.chainHitbox.hitbox_lock = hitbox.HitboxLock()
        if self.frame == 29:
            self.chainHitbox.kill()
            actor.active_hitboxes.add(self.dashHitbox)
        if self.frame == 33:
            self.dashHitbox.kill()
            actor.preferred_xspeed = 0
        baseActions.LedgeGetup.update(self, actor)

class LedgeRoll(baseActions.LedgeGetup):
    def __init__(self):
        baseActions.LedgeGetup.__init__(self, 43)
        self.sprite_rate = 0

    def setUp(self, actor):
        baseActions.LedgeGetup.setUp(self, actor)

    def tearDown(self, actor, nextAction):
        actor.change_x = 0
        actor.preferred_xspeed = 0
        if actor.invulnerable > 0:
            actor.invulnerable = 0
        actor.mask = None

    def update(self, actor):
        if self.frame == 0:
            actor.invulnerable = 37
            actor.createMask([255,255,255], 32, True, 24)
            actor.changeSprite("getup",0)
        if (self.frame >= 0) and (self.frame <= 6):
            actor.changeSpriteImage(self.frame)
            self.ecb_size = [0, 100]
            if self.frame > 2:
                actor.change_y = -19
            actor.change_x = 0
        if (self.frame >= 8) and (self.frame <= 14):
            self.ecb_size = [0, 0]
            actor.change_y = 0
            actor.change_x = 11.5*actor.facing
            if (self.frame % 2 == 0):
                actor.changeSpriteImage(self.frame//2+4)
        if self.frame == 15:
            actor.change_x = actor.var['dodge_speed']*actor.facing
        if self.frame == 17:
            actor.changeSprite("land", 1)
            actor.flip()
            actor.preferred_xspeed = 0
        if self.frame == 33:
            actor.changeSprite("land", 0)
        baseActions.LedgeGetup.update(self, actor)

class NeutralAction(baseActions.NeutralAction):
    def __init__(self):
        baseActions.NeutralAction.__init__(self,1)
        self.sprite_rate = 0
        
    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("idle")
            self.frame += 1
        
class Crouch(baseActions.Crouch):
    def __init__(self):
        baseActions.Crouch.__init__(self, 2)
        self.sprite_rate = 0
    def setUp(self, actor):
        actor.changeSprite('land', 0)
    def update(self, actor):
        actor.changeSpriteImage(self.frame)
        if self.frame == self.last_frame:
            self.frame -= 1
        baseActions.Crouch.update(self, actor)

class Fall(baseActions.Fall):
    def __init__(self):
        baseActions.Fall.__init__(self)
        self.sprite_rate = 0
        
    def update(self,actor):
        actor.changeSprite("jump")
        baseActions.Fall.update(self, actor)


########################################################
#             BEGIN HELPER METHODS                     #
########################################################
