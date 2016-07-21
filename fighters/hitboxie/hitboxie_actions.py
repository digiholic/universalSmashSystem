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
        self.spriteImage = 0
        self.spriteRate = 0
        self.shouldContinue = True

    def setUp(self, actor):
        #TODO Attribute checking
        variables = {'center': [0,0],
                     'size': [80,80],
                     'damage': 1,
                     'hitstun': 5,
                     'x_bias': 0,
                     'y_bias': -1.5,
                     'shield_multiplier': 1,
                     'velocity_multiplier': 1,
                     'transcendence': -1,
                     'priority': -7
                     }
        self.chainHitbox = hitbox.AutolinkHitbox(actor, hitbox.HitboxLock(), variables)
        self.flingHitbox = self.sideSpecialHitbox(actor)
        self.numFrames = 0
        self.ecbCenter = [0,7]
        self.ecbSize = [64, 78]
        if actor.sideSpecialUses == 1:
            actor.sideSpecialUses = 0
        else:
            self.shouldContinue = False
            return
        actor.change_x = 0
        actor.preferred_xspeed = 0
        actor.flinch_knockback_threshold = 4
        actor.changeSprite("nair",0)
    
    def onClank(self,actor):
        actor.landingLag = 30
        actor.doAction('Fall')
    
    class sideSpecialHitbox(hitbox.DamageHitbox):
        def __init__(self,actor):
            variables = {'center':[0,0],
                         'size':[80,80],
                         'damage':6,
                         'baseKnockback':4,
                         'knockbackGrowth':0.1,
                         'trajectory':300,
                         'shield_multiplier':10,
                         'hitlag_multiplier':2
                         }
            hitbox.DamageHitbox.__init__(self, actor, hitbox.HitboxLock(), variables)
            
        def onCollision(self, other):
            hitbox.Hitbox.onCollision(self, other)
            if 'AbstractFighter' in list(map(lambda x:x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
                if other.lockHitbox(self):
                    if self.article is None:
                        self.owner.applyPushback(self.damage/4.0, self.trajectory+180, (self.damage / 4.0 + 2.0)*self.hitlag_multiplier)
                    if other.grounded:
                        other.applyKnockback(self.damage, 0, 0, 0, 1, 1)
                        (otherDirect,_) = other.getDirectionMagnitude()
                        other.doTrip(55, other.getForwardWithOffset(otherDirect))
                    else:
                        other.applyKnockback(self.damage, self.baseKnockback, self.knockbackGrowth, self.trajectory, self.weight_influence, self.hitstun)
                            
    def stateTransitions(self, actor):
        if not self.shouldContinue:
            actor.doAction('Fall')
        if actor.grounded == False and self.frame >= 17:
            baseActions.grabLedges(actor)

    def tearDown(self, actor, newAction):
        self.chainHitbox.kill()
        self.flingHitbox.kill()
        actor.flinch_knockback_threshold = 0
        actor.preferred_xspeed = 0

    def update(self, actor):
        if not self.shouldContinue:
            return
        if actor.grounded:
            actor.sideSpecialUses = 1
        actor.changeSpriteImage(self.spriteImage%16)
        actor.hurtbox.rect.width = 64
        actor.hurtbox.rect.height = 64
        actor.hurtbox.rect.center = actor.sprite.boundingRect.center
        if self.frame <= self.lastFrame-2:
            self.spriteImage += 1
            if self.frame <= 16:
                actor.preferred_xspeed = 0
                actor.change_x = 0
                if actor.change_y > 2:
                    actor.change_y = 2
                actor.preferred_yspeed = 2
                if actor.keysContain('special') and self.frame == 16 and self.lastFrame < 240:
                    self.lastFrame += 1
                    self.frame -= 1
            else: #Actually launch forwards
                actor.preferred_yspeed = actor.var['maxFallSpeed']
                self.numFrames += 1
                self.chainHitbox.update()
                actor.active_hitboxes.add(self.chainHitbox)
                (key, invkey) = actor.getForwardBackwardKeys()
                if self.frame == 17:
                    actor.setSpeed(actor.var['runSpeed'], actor.getForwardWithOffset(0))
                    actor.change_y = -12
                if self.spriteImage%6 == 0:
                    self.chainHitbox.hitbox_lock = hitbox.HitboxLock()
                if actor.keysContain(invkey):
                    actor.preferred_xspeed = actor.var['runSpeed']//2*actor.facing
                    self.frame += 2
                    if (self.frame > self.lastFrame-2):
                        self.frame = self.lastFrame-2
                elif actor.keysContain(key):
                    actor.preferred_xspeed = actor.var['runSpeed']*actor.facing
                    if (self.frame > self.lastFrame-2):
                        self.frame = self.lastFrame-2
                else:
                    actor.preferred_xspeed = actor.var['runSpeed']*3//4*actor.facing
                    self.frame += 1
                    if (self.frame > self.lastFrame-2):
                        self.frame = self.lastFrame-2
                
        else:
            if self.frame == self.lastFrame-1:
                self.flingHitbox.damage += int(float(self.numFrames)/float(24))
                self.flingHitbox.priority += int(float(self.numFrames)/float(24))
                self.flingHitbox.baseKnockback += float(self.numFrames)/float(24)
                self.flingHitbox.update()
                actor.active_hitboxes.add(self.flingHitbox)
            else:
                self.flingHitbox.kill()
            self.chainHitbox.kill()
            if self.frame >= self.lastFrame:
                if actor.grounded:
                    actor.landingLag = 30
                    actor.doAction('Land')
                else:
                    actor.landingLag = 30
                    actor.doAction('Fall')

        self.frame += 1
            
class UpSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self, 70)
        self.angle = 90
        self.spriteRate = 0
        
    def setUp(self, actor):
        action.Action.setUp(self,actor)
        sharedLock = hitbox.HitboxLock()
        self.launchHitbox = hitbox.DamageHitbox(actor,sharedLock,
                                                {'center':[0,0],
                                                 'size':[64,64],
                                                 'damage':14,
                                                 'baseKnockback':12,
                                                 'knockbackGrowth':0.1,
                                                 'trajectory': 90,
                                                 'hitstun':7                                                 
                                                 })
        self.flyingHitbox = hitbox.DamageHitbox(actor,sharedLock,
                                                {'center':[0,0],
                                                 'size':[64,64],
                                                 'damage':8,
                                                 'baseKnockback':10,
                                                 'knockbackGrowth':0.05,
                                                 'trajectory': 90,
                                                 'hitstun':5                                                
                                                 })
        actor.changeSprite('dtilt')
        actor.changeSpriteImage(4)
        
        
    def tearDown(self, actor, newAction):
        action.Action.tearDown(self,actor,newAction)
        self.launchHitbox.kill()
        self.flyingHitbox.kill()
        actor.unRotate()
        actor.preferred_yspeed = actor.var['maxFallSpeed']
    
    def stateTransitions(self,actor):
        if self.frame < 19:
            actor.change_y = 0
            actor.preferred_yspeed = 0
        if self.frame > 19:
            baseActions.grabLedges(actor)
        if self.frame >= 45:
            actor.preferred_yspeed = actor.var['maxFallSpeed']
            baseActions.airControl(actor)
    
    def update(self,actor):
        actor.landingLag = 20
        if actor.grounded:
            actor.accel(actor.var['staticGrip'])
        if self.frame <= 19:
            actor.unRotate()
            actor.change_x = 0
            actor.change_y = 0
            self.angle = math.atan2(-actor.getSmoothedInput()[1]+0.0001, actor.getSmoothedInput()[0])*180.0/math.pi
            direction = abstractFighter.getXYFromDM(self.angle, 1.0)
            actor.rotateSprite(self.angle)
        if self.frame == 2:
            actor.changeSpriteImage(5)
        if self.frame == 4:
            actor.changeSpriteImage(6)
        if self.frame == 6:
            actor.changeSpriteImage(7)
        if self.frame == 8:
            actor.changeSpriteImage(8)
        if self.frame == 11:
            actor.changeSpriteImage(9)
        if self.frame == 19:
            self.launchHitbox.trajectory = self.angle
            self.flyingHitbox.trajectory = self.angle
            actor.active_hitboxes.add(self.launchHitbox)
            actor.changeSprite('airjump')
            self.ecbSize = [92, 92]
            actor.preferred_yspeed = actor.var['maxFallSpeed']
            actor.change_x = direction[0] * 20
            actor.preferred_xspeed = actor.var['maxAirSpeed'] * direction[0]
            actor.change_y = direction[1] * 20
        if self.frame == 20:
            self.launchHitbox.kill()
            actor.active_hitboxes.add(self.flyingHitbox)
        if self.frame == 45:
            self.flyingHitbox.kill()
        if self.frame > 20:
            if self.frame % 2 == 0:
                actor.changeSpriteImage((self.frame - 15) // 2,loop=True)
            self.flyingHitbox.update()
        if self.frame == self.lastFrame:
            actor.doAction('Helpless')
        self.frame += 1
        
class NeutralAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,22)
        self.spriteRate = 0
    
    def setUp(self, actor):
        actor.preferred_xspeed = 0
        actor.changeSprite("neutral",0)
        self.jabHitbox = self.outwardHitbox(actor)
        
    def tearDown(self, actor, new):
        self.jabHitbox.kill()

    def onClank(self,actor):
        actor.doAction('NeutralAction')
    
    def stateTransitions(self, actor):
        if not actor.grounded:
            actor.doAction('Fall')
        elif self.frame == self.lastFrame:
            if actor.keysContain('attack') and not actor.keysContain('left') and not actor.keysContain('right') and not actor.keysContain('up') and not actor.keysContain('down'):
                self.jabHitbox.hitbox_lock = hitbox.HitboxLock()
                self.frame = 0
                
    # Here's an example of creating an anonymous hitbox class.
    # This one calculates its trajectory based off of the angle between the two fighters.
    # Since this hitbox if specifically for this attack, we can hard code in the values.
    class outwardHitbox(hitbox.DamageHitbox):
        def __init__(self,actor):
            variables = {'center': [0,0],
                         'size': [80,80],
                         'damage': 3,
                         'baseKnockback':8,
                         'knockbackGrowth':0.02,
                         'trajectory':20
                         }
            hitbox.DamageHitbox.__init__(self, actor, hitbox.HitboxLock(), variables)
            
        def onCollision(self,other):
            hitbox.Hitbox.onCollision(self, other)
            self.trajectory = abstractFighter.getDirectionBetweenPoints(self.owner.rect.midbottom, other.rect.center)
            hitbox.DamageHitbox.onCollision(self, other)
            
    def update(self, actor):
        if self.frame < 4:
            actor.changeSpriteImage(self.frame)
        elif self.frame == 4:
            self.jabHitbox.update()
            actor.active_hitboxes.add(self.jabHitbox)
        elif self.frame >= 5 and self.frame <= 8:
            self.jabHitbox.update()
            actor.changeSpriteImage(9)
        elif self.frame >= 9 and self.frame <= 10:
            self.jabHitbox.kill()
            actor.changeSpriteImage(10)
        elif self.frame > 10:
            self.jabHitbox.kill()
            if not self.frame > 14:
                actor.changeSpriteImage(self.frame)
        actor.hurtbox.rect.width -= 16
        actor.hurtbox.rect.height -= 16
        actor.hurtbox.rect.midbottom = actor.sprite.boundingRect.midbottom
        if self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        self.frame += 1

class GroundGrab(action.Action):
    def __init__(self):
        action.Action.__init__(self, 30)
        self.spriteRate = 0

    def setUp(self, actor):
        self.grabHitbox = hitbox.GrabHitbox([30,0], [30,30], actor, hitbox.HitboxLock(), 30)

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
        if self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        self.frame += 1

class DashGrab(action.Action):
    def __init__(self):
        action.Action.__init__(self, 35)
        self.spriteRate = 0

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
        if self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        self.frame += 1

class Pummel(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self,22)
        self.spriteRate = 0

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
        if self.frame == self.lastFrame:
            actor.doAction('Grabbing')
        self.frame += 1
        
class ForwardThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self,20)
        self.spriteRate = 0

    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,13,12.0,0.20,40,1,hitbox.HitboxLock())

    def tearDown(self, actor, other):
        self.fSmashHitbox.kill()
        baseActions.BaseGrabbing.tearDown(self, actor, other)

    def update(self, actor): 
        baseActions.BaseGrabbing.update(self, actor)
        if self.frame == 0:
            actor.preferred_xspeed = 0
            actor.changeSprite("fsmash",0)
        elif self.frame <= 12:
            actor.changeSpriteImage(self.frame//2)
        elif self.frame == 14:
            actor.changeSpriteImage(7)
            actor.active_hitboxes.add(self.fSmashHitbox)
        elif self.frame == 16:
            actor.changeSpriteImage(8)
            self.fSmashHitbox.kill()
        elif self.frame == 18:
            actor.changeSpriteImage(9)
        elif self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        
        self.frame += 1

class DownThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self, 32)
        self.spriteRate = 0

    def setUp(self, actor):
        actor.changeSprite("nair")
        self.bottomHitbox = hitbox.DamageHitbox([10, 40], [30, 30], actor, 1, 3, 0, 260, 1, hitbox.HitboxLock(), 0, 1)
        actor.active_hitboxes.add(self.bottomHitbox)
        self.ecbCenter = [0,7]
        self.ecbSize = [64, 78]

    def tearDown(self, actor, nextAction):
        self.bottomHitbox.kill()
        baseActions.BaseGrabbing.tearDown(self, actor, nextAction)

    def update(self, actor):
        baseActions.BaseGrabbing.update(self, actor)
        actor.changeSpriteImage(self.frame%16)
        actor.hurtbox.rect.width = 64
        actor.hurtbox.rect.height = 64
        actor.hurtbox.rect.center = actor.sprite.boundingRect.center
        self.bottomHitbox.update()
        if (self.frame%4 == 0):
            self.bottomHitbox.hitbox_lock = hitbox.HitboxLock()
        if (self.frame == self.lastFrame-4):
            self.bottomHitbox.baseKnockback = 10
            self.bottomHitbox.trajectory = actor.getForwardWithOffset(90)
            self.bottomHitbox.knockbackGrowth = 0.12
            self.weight_influence = 1
        if self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        self.frame += 1

class UpThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self, 100)
        self.spriteRate = 0

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
            actor.landingLag = 12
        elif self.frame > 10:
            actor.calc_grav(4)
            if actor.grounded and actor.change_y >= 0:
                if actor.isGrabbing():
                    actor.grabbing.applyKnockback(11, 12, 0.15, actor.getForwardWithOffset(70))
                actor.doAction('Fall')
        self.frame += 1

class BackThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self, 22)
        self.spriteRate = 0

    def setUp(self, actor):
        actor.changeSprite("bthrow")

    def tearDown(self, actor, nextAction):
        baseActions.BaseGrabbing.tearDown(self, actor, nextAction)

    def update(self, actor):
        baseActions.BaseGrabbing.update(self, actor)
        if self.frame == 0 and actor.isGrabbing():
            actor.grabbing.applyKnockback(7, 18, 0.05, actor.getForwardWithOffset(170), 0.5)
        if self.frame <= 16:
            actor.changeSpriteImage(self.frame//2)
        elif self.frame == self.lastFrame: 
            actor.flip()
            actor.doAction('NeutralAction')
        self.frame += 1

########################################################
#            BEGIN OVERRIDE CLASSES                    #
########################################################

class Move(baseActions.Move):
    def __init__(self,accel = True):
        baseActions.Move.__init__(self,15)
        self.spriteRate = 0
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
        if (self.frame == self.lastFrame):
            self.frame = 12

class Dash(baseActions.Dash):
    def __init__(self,accel = True):
        baseActions.Dash.__init__(self,15)
        self.spriteRate = 0
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
        self.spriteRate = 0
        
    def update(self, actor):
        actor.changeSprite("run",4)
                
        baseActions.Run.update(self, actor)
        if (self.frame == self.lastFrame):
            self.frame = 1
"""
                   
class Pivot(baseActions.Pivot):
    def __init__(self):
        baseActions.Pivot.__init__(self,10)
        self.spriteRate = 0
        
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
        self.spriteRate = 0
        
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
        self.spriteRate = 0

    def update(self, actor):
        baseActions.Grabbing.update(self, actor)
        actor.change_x = 0
        if self.frame == 0:
            actor.changeSprite('pivot', 4)
        self.frame += 1
        
class Stop(baseActions.Stop):
    def __init__(self):
        baseActions.Stop.__init__(self, 9)
        self.spriteRate = 0
    
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
        self.spriteRate = 0
    
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
        self.spriteRate = 0

    def setUp(self, actor):
        actor.changeSprite('land', 2)

    def update(self, actor):
        actor.changeSpriteImage(3-self.frame/3)
        baseActions.CrouchGetup.update(self, actor)
        
class HitStun(baseActions.HitStun):
    def __init__(self,hitstun=1,direction=0):
        baseActions.HitStun.__init__(self, hitstun, direction)
        self.spriteRate = 0

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
        self.spriteRate = 0
        
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
        self.spriteRate = 0
        
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
        self.spriteRate = 0

    def update(self, actor):
        actor.changeSprite("jump")
        baseActions.Helpless.update(self, actor)
            
class Land(baseActions.Land):
    def __init__(self):
        baseActions.Land.__init__(self)
        self.spriteRate = 0

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
        self.spriteRate = 0

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
        self.spriteRate = 0

    def setUp(self, actor):
        baseActions.Trip.setUp(self, actor)
        actor.sideSpecialUses = 1

    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("land", 3)
        baseActions.Trip.update(self, actor)

class Prone(baseActions.Prone):
    def __init__(self):
        baseActions.Prone.__init__(self, 360)
        self.spriteName = 'land'
        self.spriteRate = 2
        
    def update(self, actor):
        if self.frame == 6: actor.changeSpriteImage(3)

class Getup(baseActions.Getup):
    def __init__(self, direction=0):
        baseActions.Getup.__init__(self, direction, 12)
        self.spriteRate = 0

    def update(self, actor):
        if self.frame < 12:
            if self.frame % 3 == 0:
                actor.changeSprite("land", 3-self.frame//3)
        baseActions.Getup.update(self, actor)

class GetupAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,36)
        self.spriteRate = 0

    def setUp(self, actor):
        actor.preferred_xspeed = 0
        actor.changeSprite("nair")
        self.ecbCenter = [0,7]
        self.ecbSize = [64, 78]
        self.dashHitbox = hitbox.DamageHitbox(actor,hitbox.HitboxLock(),{
                                                                         'center': [0,0],
                                                                         'size': [70,70],
                                                                         'damage': 2,
                                                                         'baseKnockback': 5,
                                                                         'knockbackGrowth': 0.1,
                                                                         'trajectory': 20,
                                                                         'hitstun': 5
                                                                         })
        self.chainHitbox = hitbox.AutolinkHitbox(actor,hitbox.HitboxLock(),{
                                                                         'center': [0,0],
                                                                         'size': [70,70],
                                                                         'damage': 2,
                                                                         'hitstun' 5,
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

        if self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        self.frame += 1

class PlatformDrop(baseActions.PlatformDrop):
    def __init__(self):
        baseActions.PlatformDrop.__init__(self, 12, 6, 9)
        self.spriteRate = 0
        
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
    def __init__(self, newShield=True):
        baseActions.Shield.__init__(self, newShield)
        self.spriteRate = 0
    
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("jump")
        baseActions.Shield.update(self, actor)

class ShieldStun(baseActions.ShieldStun):
    def __init__(self, length=1):
        baseActions.ShieldStun.__init__(self, length)
        self.spriteRate = 0

    def update(self, actor):
        actor.createMask([191, 63, 191], self.lastFrame, False, 8)
        baseActions.ShieldStun.update(self, actor)

class Stunned(baseActions.Stunned):
    def __init__(self, length=1):
        baseActions.Stunned.__init__(self, length)
        self.spriteRate = 0

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
        self.spriteRate = 0
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",1)
        elif self.frame == self.endInvulnFrame:
            actor.changeSprite("land",0)
        baseActions.ForwardRoll.update(self, actor)
        
class BackwardRoll(baseActions.BackwardRoll):
    def __init__(self):
        baseActions.BackwardRoll.__init__(self)
        self.spriteRate = 0
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",1)
        elif self.frame == self.endInvulnFrame:
            actor.changeSprite("land",0)
        baseActions.BackwardRoll.update(self, actor)
        
class SpotDodge(baseActions.SpotDodge):
    def __init__(self):
        baseActions.SpotDodge.__init__(self)
        self.spriteRate = 0
        
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
        self.spriteRate = 0
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("nair",0)
        elif self.frame == self.startInvulnFrame:
            actor.changeSpriteImage(-round(abs(actor.change_x)))
        elif self.frame == self.endInvulnFrame:
            actor.changeSpriteImage(0)
        baseActions.AirDodge.update(self, actor)

class Trapped(baseActions.Trapped):
    def __init__(self, length=1):
        baseActions.Trapped.__init__(self, length)
        self.spriteRate = 0

    def setUp(self, actor):
        baseActions.Trapped.setUp(self, actor)
        actor.sideSpecialUses = 1

    def update(self, actor):
        actor.changeSprite("idle")
        baseActions.Trapped.update(self, actor)

class Grabbed(baseActions.Grabbed):
    def __init__(self,height=0):
        baseActions.Grabbed.__init__(self, height)
        self.spriteRate = 0

    def setUp(self, actor):
        baseActions.Grabbed.setUp(self, actor)
        actor.sideSpecialUses = 1

    def update(self,actor):
        actor.changeSprite("idle")
        baseActions.Grabbed.update(self, actor)

class Release(baseActions.Release):
    def __init__(self,height=0):
        baseActions.Release.__init__(self)
        self.spriteRate = 0

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
        self.spriteRate = 0

    def setUp(self, actor):
        baseActions.Released.setUp(self, actor)
        actor.changeSprite("jump")

class LedgeGrab(baseActions.LedgeGrab):
    def __init__(self,ledge=None):
        baseActions.LedgeGrab.__init__(self, ledge)
        self.spriteRate = 0

    def setUp(self, actor):
        baseActions.LedgeGrab.setUp(self, actor)
        actor.sideSpecialUses = 1
        
    def update(self,actor):
        actor.changeSprite('jump')
        baseActions.LedgeGrab.update(self, actor)

class LedgeGetup(baseActions.LedgeGetup):
    def __init__(self):
        baseActions.LedgeGetup.__init__(self,27)
        self.spriteRate = 0

    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("getup",0)
            actor.createMask([255,255,255], 24, True, 24)
        if (self.frame >= 0) and (self.frame <= 6):
            actor.changeSpriteImage(self.frame)
            self.ecbSize = [0, 100]
            if self.frame > 2:
                actor.change_y = -19
            actor.change_x = 0
        if (self.frame >= 8) and (self.frame <= 14):
            self.ecbSize = [0, 0]
            actor.change_y = 0
            actor.change_x = 11.5*actor.facing
            if (self.frame % 2 == 0):
                actor.changeSpriteImage(self.frame//2+4)
        if (self.frame > 15):
            if (self.frame % 3 == 2):
                actor.changeSpriteImage(self.frame//3+6)
            actor.change_x = actor.var['maxGroundSpeed']*actor.facing
        baseActions.LedgeGetup.update(self, actor)

class LedgeAttack(baseActions.LedgeGetup):
    def __init__(self):
        baseActions.LedgeGetup.__init__(self,36)
        self.spriteRate = 0

    def setUp(self,actor):
        baseActions.LedgeGetup.setUp(self, actor)
        actor.invincibility = 24
        actor.createMask([255,255,255], 24, True, 24)
        self.dashHitbox = hitbox.DamageHitbox(actor,hitbox.HitboxLock(),{
                                                                         'center': [0,0],
                                                                         'size': [70,70],
                                                                         'damage': 2,
                                                                         'baseKnockback': 8,
                                                                         'knockbackGrowth': 0.2,
                                                                         'trajectory': 20,
                                                                         'hitstun': 5
                                                                         })
        self.chainHitbox = hitbox.AutolinkHitbox(actor,hitbox.HitboxLock(),{
                                                                         'center': [0,0],
                                                                         'size': [70,70],
                                                                         'damage': 2,
                                                                         'hitstun': 5,
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
            self.ecbSize = [0, 100]
            if self.frame > 2:
                actor.change_y = -19
            actor.change_x = 0
        if (self.frame >= 8) and (self.frame <= 14):
            self.ecbSize = [0, 0]
            actor.change_y = 0
            actor.change_x = 11.5*actor.facing
            if (self.frame % 2 == 0):
                actor.changeSpriteImage(self.frame//2+4)
        if self.frame == 15:
            actor.change_x = actor.var['maxGroundSpeed']*actor.facing
            actor.preferred_xspeed = actor.var['maxGroundSpeed']*actor.facing
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
        self.spriteRate = 0

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
            self.ecbSize = [0, 100]
            if self.frame > 2:
                actor.change_y = -19
            actor.change_x = 0
        if (self.frame >= 8) and (self.frame <= 14):
            self.ecbSize = [0, 0]
            actor.change_y = 0
            actor.change_x = 11.5*actor.facing
            if (self.frame % 2 == 0):
                actor.changeSpriteImage(self.frame//2+4)
        if self.frame == 15:
            actor.change_x = actor.var['dodgeSpeed']*actor.facing
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
        self.spriteRate = 0
        
    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("idle")
            self.frame += 1
        
class Crouch(baseActions.Crouch):
    def __init__(self):
        baseActions.Crouch.__init__(self, 2)
        self.spriteRate = 0
    def setUp(self, actor):
        actor.changeSprite('land', 0)
    def update(self, actor):
        actor.changeSpriteImage(self.frame)
        if self.frame == self.lastFrame:
            self.frame -= 1
        baseActions.Crouch.update(self, actor)

class Fall(baseActions.Fall):
    def __init__(self):
        baseActions.Fall.__init__(self)
        self.spriteRate = 0
        
    def update(self,actor):
        actor.changeSprite("jump")
        baseActions.Fall.update(self, actor)


########################################################
#             BEGIN HELPER METHODS                     #
########################################################
