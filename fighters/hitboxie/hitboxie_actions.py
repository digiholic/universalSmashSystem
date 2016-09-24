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
        ambience =  {'center': [0,0],
                     'size': [80,80],
                     'damage': 0,
                     'base_hitstun': 0,
                     'x_bias': 0,
                     'y_bias': 0,
                     'hitlag_multiplier': 0,
                     'transcendence': -1,
                     'priority': -6
                     }
        variables = {'center': [0,0],
                     'size': [80,80],
                     'damage': 1,
                     'hitstun_multiplier': 2,
                     'x_bias': 0,
                     'y_bias': .25,
                     'shield_multiplier': 1,
                     'velocity_multiplier': 1,
                     'transcendence': -1,
                     'priority': -7,
                     }
        self.ambient_hitbox = hitbox.Hitbox(_actor, hitbox.HitboxLock(), ambience)
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
        _actor.doAction('Helpless')
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
                    _actor.setSpeed(_actor.var['aerial_transition_speed'], _actor.getForwardWithOffset(0))
                    _actor.change_y = -12
                if self.sprite_image%6 == 0:
                    self.chain_hitbox.hitbox_lock = hitbox.HitboxLock()
                if _actor.keysContain(invkey):
                    _actor.preferred_xspeed = _actor.var['aerial_transition_speed']//2*_actor.facing
                    self.frame += 2
                    if (self.frame > self.last_frame-2):
                        self.frame = self.last_frame-2
                elif _actor.keysContain(key):
                    _actor.preferred_xspeed = _actor.var['aerial_transition_speed']*_actor.facing
                    if (self.frame > self.last_frame-2):
                        self.frame = self.last_frame-2
                else:
                    _actor.preferred_xspeed = _actor.var['aerial_transition_speed']*3//4*_actor.facing
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
        action.Action.__init__(self, 80)
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
        _actor.changeSprite('dsmash')
        _actor.changeSpriteImage(4)
        
        
    def tearDown(self, _actor, _newAction):
        action.Action.tearDown(self,_actor,_newAction)
        self.launchHitbox.kill()
        self.flyingHitbox.kill()
        _actor.unRotate()
        _actor.preferred_yspeed = _actor.var['max_fall_speed']
    
    def stateTransitions(self,_actor):
        if self.frame < 31:
            _actor.change_y = 0
            _actor.preferred_yspeed = 0
        if self.frame > 31:
            baseActions.grabLedges(_actor)
        if self.frame >= 56:
            _actor.preferred_yspeed = _actor.var['max_fall_speed']
            baseActions.airControl(_actor)
    
    def update(self,_actor):
        _actor.landing_lag = 10
        if _actor.grounded:
            _actor.accel(_actor.var['static_grip'])
        else:
            _actor.accel(_actor.var['air_control'])
        if self.frame <= 30:
            _actor.unRotate()
            _actor.change_x = 0
            _actor.change_y = 0
            if (_actor.getSmoothedInput() == [0, 0]):
                self.angle = 90
            else:
                self.angle = math.atan2(-_actor.getSmoothedInput()[1], _actor.getSmoothedInput()[0])*180.0/math.pi
            direction = abstractFighter.getXYFromDM(self.angle, 1.0)
            print('direction: ',direction)
            _actor.rotateSprite(self.angle)
        if self.frame == 0:
            _actor.playSound('slingsquare')
        if self.frame == 3:
            _actor.changeSpriteImage(5)
        if self.frame == 6:
            _actor.changeSpriteImage(6)
        if self.frame == 9:
            _actor.changeSpriteImage(7)
        if self.frame == 12:
            _actor.changeSpriteImage(8)
        if self.frame == 15:
            _actor.changeSpriteImage(9)
        if self.frame == 30:
            self.launchHitbox.trajectory = self.angle
            self.flyingHitbox.trajectory = self.angle
            _actor.active_hitboxes.add(self.launchHitbox)
            _actor.changeSprite('airjump')
            self.ecb_size = [92, 92]
            _actor.preferred_yspeed = _actor.var['max_fall_speed']
            _actor.change_x = direction[0] * 20
            _actor.preferred_xspeed = _actor.var['max_air_speed'] * direction[0]
            _actor.change_y = direction[1] * 20
        if self.frame == 31:
            self.launchHitbox.kill()
            _actor.active_hitboxes.add(self.flyingHitbox)
        if self.frame == 56:
            self.flyingHitbox.kill()
        if self.frame > 31:
            if self.frame % 2 == 0:
                _actor.changeSpriteImage((self.frame - 15) // 2,_loop=True)
            self.flyingHitbox.update()
        if self.frame == self.last_frame:
            _actor.doAction('Helpless')
        self.frame += 1

########################################################
#            BEGIN OVERRIDE CLASSES                    #
########################################################


########################################################
#             BEGIN HELPER METHODS                     #
########################################################
