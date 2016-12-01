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
        action.Action.setUp(self, _actor)
        #TODO Attribute checking
        ambience =  {'center': [0,0],
                     'size': [80,80],
                     'damage': 0,
                     'base_hitstun': 0,
                     'x_bias': 0,
                     'y_bias': 0,
                     'hitlag_multiplier': 0,
                     'transcendence': -1,
                     'priority': 0,
                     'trajectory': 90
                     }
        variables = {'center': [0,0],
                     'size': [80,80],
                     'damage': 1,
                     'hitstun_multiplier': 2,
                     'base_hitstun': 10,
                     'x_bias': 0,
                     'y_bias': .25,
                     'base_hitstun': 7,
                     'shield_multiplier': 1,
                     'velocity_multiplier': 1,
                     'transcendence': -1,
                     'priority': 1,
                     }
        self.ambient_hitbox = hitbox.Hitbox(_actor, hitbox.HitboxLock(), ambience)
        self.chain_hitbox = hitbox.AutolinkHitbox(_actor, hitbox.HitboxLock(), variables)
        self.fling_hitbox = self.sideSpecialHitbox(_actor)
        self.ecb_offset = [0,7]
        self.ecb_size = [64, 78]
        self.charge = 0
        if _actor.variables['sideSpecialUses'] == 1:
            _actor.variables['sideSpecialUses'] = 0
        else:
            self.should_continue = False
            return
        _actor.change_x = 0
        _actor.preferred_xspeed = 0
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
                         'hitlag_multiplier':2,
                         'charge_damage':0.08333,
                         'charge_base_knockback':0.04167,
                         'charge_knockback_growth':0.001667
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
        _actor.preferred_xspeed = 0
        _actor.flinch_knockback_threshold = 0

    def update(self, _actor):
        if not self.should_continue:
            return
        _actor.changeSpriteImage(self.sprite_image%16)
        _actor.auto_hurtbox.rect.width = 64
        _actor.auto_hurtbox.rect.height = 64
        _actor.auto_hurtbox.rect.center = _actor.sprite.bounding_rect.center
        _actor.accel(_actor.stats['air_control'])
        if self.frame <= self.last_frame-2:
            self.sprite_image += 1
            if self.frame <= 16:
                _actor.flinch_knockback_threshold = 3
                _actor.preferred_xspeed = 0
                _actor.change_x = 0
                if _actor.change_y > 2:
                    _actor.change_y = 2
                _actor.preferred_yspeed = 2
                if _actor.keysContain('special') and self.frame == 16 and self.last_frame < 240:
                    self.last_frame += 1
                    self.frame -= 1
            else: #Actually launch forwards
                _actor.preferred_yspeed = _actor.stats['max_fall_speed']
                self.charge += 1
                self.chain_hitbox.update()
                _actor.active_hitboxes.add(self.chain_hitbox)
                (key, invkey) = _actor.getForwardBackwardKeys()
                if self.frame == 17:
                    _actor.setSpeed(_actor.stats['aerial_transition_speed'], _actor.getForwardWithOffset(0))
                    _actor.change_y = -12
                if self.sprite_image%6 == 0:
                    self.chain_hitbox.hitbox_lock = hitbox.HitboxLock()
                if _actor.keysContain(invkey):
                    _actor.preferred_xspeed = _actor.stats['aerial_transition_speed']//2*_actor.facing
                    self.frame += 2
                elif _actor.keysContain(key):
                    _actor.preferred_xspeed = _actor.stats['aerial_transition_speed']*_actor.facing
                else:
                    _actor.preferred_xspeed = _actor.stats['aerial_transition_speed']*3//4*_actor.facing
                    self.frame += 1
                if (self.frame > self.last_frame-2):
                    self.frame = self.last_frame-2
                
        else:
            if self.frame == self.last_frame-1:
                self.fling_hitbox.update()
                _actor.active_hitboxes.add(self.fling_hitbox)
                print(self.fling_hitbox.damage)
            else:
                self.fling_hitbox.kill()
            self.chain_hitbox.kill()
            if self.frame >= self.last_frame:
                _actor.landing_lag = 25
                _actor.doAction('Fall')

        self.frame += 1

########################################################
#            BEGIN OVERRIDE CLASSES                    #
########################################################


########################################################
#             BEGIN HELPER METHODS                     #
########################################################
