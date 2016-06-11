import engine.action as action
import engine.baseActions as baseActions
import engine.hitbox as hitbox
import engine.article as article
import engine.abstractFighter as abstractFighter
import math
import pygame

class NeutralGroundSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self,36)
                
    def setUp(self, actor):
        self.projectile = actor.loadArticle('SplatArticle')
        actor.preferred_xspeed = 0
        actor.changeSprite("nspecial",0)
        
    def update(self, actor):
        if self.frame <= 14:
            actor.changeSpriteImage(self.frame//2)
        elif self.frame > 24 and self.frame <= 36:
            actor.changeSpriteImage((self.frame+4)//4)
        if self.frame == 12:
            self.projectile.activate()
        if self.frame == 26:
            if actor.keysContain('special'):
                actor.changeAction(NeutralGroundSpecial())
        if self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        self.frame += 1

class NeutralAirSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self,36)
                
    def setUp(self, actor):
        self.projectile = actor.loadArticle('SplatArticle')
        actor.changeSprite("nspecial",0)

    def stateTransitions(self, actor):
        if actor.keysContain('down'):
            actor.platformPhase = 1
            actor.calc_grav(actor.var['fastfallMultiplier'])
        baseActions.airControl(actor)
               
    def update(self, actor):
        actor.landingLag = 18
        if self.frame <= 14:
            actor.changeSpriteImage(self.frame//2)
        elif self.frame > 24 and self.frame <= 36:
            actor.changeSpriteImage((self.frame+4)//4)
        if self.frame == 12:
            self.projectile.rect.center = (actor.sprite.boundingRect.centerx + (24 * actor.facing),actor.sprite.boundingRect.centery-8)
            actor.articles.add(self.projectile)
            actor.active_hitboxes.add(self.projectile.hitbox)
            print(actor.active_hitboxes)
        if self.frame == 15:
            if actor.keysContain('special'):
                actor.changeAction(NeutralAirSpecial())
        if self.frame == self.lastFrame:
            actor.landingLag = 11
            actor.doAction('Fall')
        self.frame += 1

class ForwardSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self, 100)
        self.spriteImage = 0

    def setUp(self, actor):
        actor.sideSpecialUses -= 1
        actor.change_x = 0
        actor.preferred_xspeed = 0
        actor.flinch_knockback_threshold = 4
        actor.changeSprite("nair",0)
        self.chainHitbox = hitbox.AutolinkHitbox([0,0], [80,80], actor, 1, 0, hitbox.HitboxLock(), 0, -1.5, 1, 1, -1, -7)
        self.flingHitbox = self.sideSpecialHitbox(actor)
        self.numFrames = 0
        self.ecbCenter = [0,7]
        self.ecbSize = [64, 78]
    
    def onClank(self,actor):
        actor.landingLag = 30
        actor.doAction('Fall')
    
    class sideSpecialHitbox(hitbox.DamageHitbox):
        def __init__(self,actor):
            hitbox.DamageHitbox.__init__(self, [0,0], [80,80], actor, 6, 4, .1, 300, 1, hitbox.HitboxLock(), 1, 10, 0, 0, 1, 2)

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
        if actor.change_x//actor.facing <= 0 and self.frame >= 17:
            baseActions.grabLedges(actor)

    def tearDown(self, actor, newAction):
        self.chainHitbox.kill()
        self.flingHitbox.kill()
        actor.flinch_knockback_threshold = 0
        actor.preferred_xspeed = 0

    def update(self, actor):
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
            
class DownSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self, 32)
    
    def setUp(self, actor):
        self.article = actor.loadArticle('ShineArticle')
        self.damageHitbox = hitbox.DamageHitbox([0,0], [64,64], actor, 4, 9, 0.1, 330, 1.5, hitbox.HitboxLock(), 1, 1, 2)
        self.reflectorHitbox = hitbox.ReflectorHitbox([0,0], [92,92], actor, hitbox.HitboxLock(), 1.3, 1.1, 100, 90)
        return action.Action.setUp(self, actor)           
    
    def tearDown(self, actor, newAction):
        actor.preferred_yspeed = actor.var['maxFallSpeed']
        self.article.kill()
        self.damageHitbox.kill()
        self.reflectorHitbox.kill()
        actor.mask = None
        return action.Action.tearDown(self, actor, newAction)
    
    def stateTransitions(self, actor):
        return action.Action.stateTransitions(self, actor)
    
    def update(self, actor):
        self.damageHitbox.update()
        self.reflectorHitbox.update()
        if self.frame == 0:
            actor.change_y = 0
            actor.preferred_yspeed = 2
            actor.changeSprite('getup',12)
            actor.articles.add(self.article)
            actor.createMask([0,255,255],32,True,8)
            actor.active_hitboxes.add(self.damageHitbox)
            actor.active_hitboxes.add(self.reflectorHitbox)
        elif self.frame == 1:
            self.damageHitbox.kill()
        elif self.frame == 12:
            actor.preferred_yspeed = actor.var['maxFallSpeed']
            if 'special' in actor.keysHeld:
                if actor.mask == None:
                    actor.createMask([0,255,255],32,True,8)
                self.frame -= 1
        elif self.frame == 18:
            self.article.kill()
            self.reflectorHitbox.kill()
            actor.mask = None
        elif self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        self.frame += 1
        return action.Action.update(self, actor)
    
class UpSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self, 70)
        self.angle = 90
        
    def setUp(self, actor):
        action.Action.setUp(self,actor)
        sharedLock = hitbox.HitboxLock()
        self.launchHitbox = hitbox.DamageHitbox([0,0], [64,64], actor, 14, 12, 0.1, 90, 1.5, sharedLock)
        self.flyingHitbox = hitbox.DamageHitbox([0,0],[64,64], actor, 8, 10, 0.05, 90, 1, sharedLock)
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
            hitbox.DamageHitbox.__init__(self, [0,0], [80,80], actor, 3, 8, 0.02, 0, 1, hitbox.HitboxLock())
            
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

class UpAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,28)

    def setUp(self, actor):
        actor.changeSprite("utilt")
        sharedLock = hitbox.HitboxLock()
        actor.preferred_xspeed = 0
        self.sweetHitbox = hitbox.DamageHitbox([30,-20], [6,10], actor, 7, 8, 0.08, 100, 1, sharedLock)
        self.tangyHitbox = hitbox.DamageHitbox([27,-29], [12,18], actor, 5, 7, 0.08, 110, 1, sharedLock)
        self.sourHitbox = hitbox.DamageHitbox([21,-32], [24,26], actor, 3, 6, 0.08, 120, 1, sharedLock)

    def onClank(self,actor):
        actor.doAction('NeutralAction')

    def tearDown(self, actor, newAction):
        self.sweetHitbox.kill()
        self.tangyHitbox.kill()
        self.sourHitbox.kill()

    def stateTransitions(self, actor):
        if not actor.grounded:
            actor.doAction('Fall')

    def update(self, actor):
        actor.changeSpriteImage(self.frame//4)
        self.sweetHitbox.update()
        self.tangyHitbox.update()
        self.sourHitbox.update()
        if self.frame == 4:
            actor.active_hitboxes.add(self.sweetHitbox)
        elif self.frame == 6:
            actor.active_hitboxes.add(self.tangyHitbox)
        elif self.frame == 8:
            actor.active_hitboxes.add(self.sourHitbox)
            self.sweetHitbox.kill()
        elif self.frame == 12:
            self.tangyHitbox.kill()
        elif self.frame == 16:
            self.sourHitbox.kill()
        if self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        if self.frame <= 8:
            actor.hurtbox.rect.height -= 32
            actor.hurtbox.rect.midbottom = actor.sprite.boundingRect.midbottom
        self.frame += 1

class UpSmash(action.Action):
    def __init__(self):
        action.Action.__init__(self, 45)
        self.chargeLevel = 0
        
    def setUp(self,actor):
        self.popupHBox = hitbox.DamageHitbox([0,0],[100,100],actor,0,20,0,90,0,hitbox.HitboxLock())
        self.weakHBoxL = hitbox.DamageHitbox([0,-80],[80,80],actor,2,5,0,150,0,hitbox.HitboxLock())
        self.weakHBoxR = hitbox.DamageHitbox([0,-80],[80,80],actor,2,5,0,30,0,hitbox.HitboxLock())
        self.uSmashHitbox = hitbox.DamageHitbox([0,-80],[120,120],actor,8,2.0,.25,80,1,hitbox.HitboxLock())
    
    def tearDown(self, actor, newAction):
        self.popupHBox.kill()
        self.weakHBoxL.kill()
        self.weakHBoxR.kill()
        self.uSmashHitbox.kill()

    def stateTransitions(self, actor):
        if not actor.grounded:
            actor.doAction('Fall')
        
    def update(self,actor):
        if self.frame == 8 and not actor.keysContain('attack') and self.chargeLevel > 0:
            actor.mask = None
            
        if self.frame == 0:
            actor.preferred_xspeed = 0
            actor.changeSprite("usmash",0)
        elif self.frame == 2:
            actor.changeSpriteImage(1)
        elif self.frame == 4:
            if actor.keysContain('attack') and self.chargeLevel == 0:
                actor.createMask([255,255,0],72,True,32)
            actor.changeSpriteImage(2)
        elif self.frame == 6:
            actor.changeSpriteImage(3)
        elif self.frame == 8:
            if actor.keysContain('attack') and self.chargeLevel <= 30:
                print("charging...")
                self.chargeLevel += 1
                self.uSmashHitbox.damage += .1
                self.weakHBoxL.damage += .027
                self.weakHBoxR.damage += .027
                self.uSmashHitbox.baseKnockback += 0.02
                self.frame -= 1
        elif self.frame == 10:
            actor.changeSpriteImage(4)
        elif self.frame == 12:
            actor.mask = None
            actor.changeSpriteImage(5)
            self.popupHBox.update()
            actor.active_hitboxes.add(self.popupHBox)
        elif self.frame == 15:
            actor.changeSpriteImage(6)
            self.popupHBox.kill()
            self.weakHBoxL.update()
            actor.active_hitboxes.add(self.weakHBoxL)
        elif self.frame == 18:
            actor.changeSpriteImage(7)
            self.weakHBoxL.kill()
            self.weakHBoxR.update()
            actor.active_hitboxes.add(self.weakHBoxR)
        elif self.frame == 21:
            actor.changeSpriteImage(8)
            self.weakHBoxR.kill()
            self.weakHBoxL.update()
            actor.active_hitboxes.add(self.weakHBoxL)
        elif self.frame == 24:
            actor.changeSpriteImage(9)
            self.weakHBoxL.kill()
            self.weakHBoxR.update()
            actor.active_hitboxes.add(self.weakHBoxR)
        elif self.frame == 27:
            actor.changeSpriteImage(10)
            self.weakHBoxR.kill()
            self.uSmashHitbox.update()
            actor.active_hitboxes.add(self.uSmashHitbox)
        elif self.frame == self.lastFrame:
            self.uSmashHitbox.kill()
            actor.doAction('NeutralAction')
        
        self.frame += 1 
       
class DashAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,32)

    def setUp(self, actor):
        actor.changeSprite("nair")
        self.ecbCenter = [0,7]
        self.ecbSize = [64, 78]
        self.dashHitbox = hitbox.DamageHitbox([0,0],[70,70],actor,2,8,0.2,20,1,hitbox.HitboxLock())
        self.chainHitbox = hitbox.AutolinkHitbox([0,0],[70,70],actor,2,0,hitbox.HitboxLock(),0,-1,1,1.5)

    def onClank(self,actor):
        actor.doAction('NeutralAction')

    def tearDown(self,actor,other):
        self.dashHitbox.kill()
        self.chainHitbox.kill()

    def stateTransitions(self, actor):
        if not actor.grounded:
            actor.doAction('Fall')

    def update(self,actor):
        if self.frame%2 == 0 and self.frame <= 8:
            actor.changeSpriteImage(self.frame//2)
        elif self.frame <= 24:
            actor.changeSpriteImage((self.frame-4)%16)
        elif self.frame%2 == 0:
            actor.changeSpriteImage((self.frame//2-8)%16)

        self.dashHitbox.update()
        self.chainHitbox.update()
        actor.hurtbox.rect.width = 64
        actor.hurtbox.rect.height = 64
        actor.hurtbox.rect.center = actor.sprite.boundingRect.center

        if self.frame == 8:
            actor.active_hitboxes.add(self.chainHitbox)
        if self.frame == 12:
            self.chainHitbox.hitbox_lock = hitbox.HitboxLock()
        if self.frame == 16:
            self.chainHitbox.hitbox_lock = hitbox.HitboxLock()
        if self.frame == 20:
            self.chainHitbox.kill()
            actor.active_hitboxes.add(self.dashHitbox)
        if self.frame == 24:
            self.dashHitbox.kill()

        if self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        self.frame += 1
        
class DownAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self, 36)
    
    def setUp(self, actor):
        actor.preferred_xspeed = 0
        actor.changeSprite("dtilt",0)
        hitbox_lock = hitbox.HitboxLock()
        self.dsmashHitbox1 = hitbox.SakuraiAngleHitbox([34,26],[24,52],actor,14,8,0.075,40,1,hitbox_lock)
        self.dsmashHitbox2 = hitbox.SakuraiAngleHitbox([-34,26],[24,52],actor,14,8,0.075,140,1,hitbox_lock)
    
    def tearDown(self,actor,other):
        self.dsmashHitbox1.kill()
        self.dsmashHitbox2.kill()

    def onClank(self,actor):
        actor.doAction('NeutralAction')

    def stateTransitions(self, actor):
        if not actor.grounded:
            actor.doAction('Fall')
        
    def update(self,actor):
        self.dsmashHitbox1.update()
        self.dsmashHitbox2.update()
        if self.frame <= 10:
            actor.changeSpriteImage(self.frame//2)
        elif self.frame == 11:
            actor.changeSpriteImage(6)
            actor.active_hitboxes.add(self.dsmashHitbox1)
            actor.active_hitboxes.add(self.dsmashHitbox2)
        elif self.frame == 12:
            actor.changeSpriteImage(7)
        elif self.frame == 14:
            actor.changeSpriteImage(8)
        elif self.frame == 15:
            actor.changeSpriteImage(9)
            #create sweetspot hitbox
        elif self.frame == 16:
            actor.changeSpriteImage(10)
        elif self.frame == 18:
            actor.changeSpriteImage(11)
        elif self.frame == 20:
            actor.changeSpriteImage(12)
        elif self.frame == 24:
            actor.changeSpriteImage(13)
        elif self.frame == 30:
            actor.changeSpriteImage(14)
        if self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        self.frame += 1

class DownSmash(action.Action):
    def __init__(self):
        action.Action.__init__(self, 52)
        self.chargeLevel = 0

    def setUp(self, actor):
        actor.preferred_xspeed = 0
        actor.changeSprite("dsmash", 0)
        hitbox_lock = hitbox.HitboxLock()
        self.spikeBox = hitbox.FunnelHitbox([0, 26], [90, 40], actor, 1, 2, 270, 2, hitbox.HitboxLock(), 0.05, -0.1)
        self.dsmashHitbox1 = hitbox.DamageHitbox([23,26],[46,40],actor,8,8,0.3,20,1,hitbox_lock)
        self.dsmashHitbox2 = hitbox.DamageHitbox([-23,26],[46,40],actor,8,8,0.3,160,1,hitbox_lock)

    def tearDown(self, actor, nextAction):
        self.spikeBox.kill()
        self.dsmashHitbox1.kill()
        self.dsmashHitbox2.kill()

    def stateTransitions(self, actor):
        if not actor.grounded:
            actor.doAction('Fall')

    def update(self, actor):
        self.spikeBox.update()
        self.dsmashHitbox1.update()
        self.dsmashHitbox2.update()
        if self.frame == 6 and not actor.keysContain('attack') and self.chargeLevel > 0:
            actor.mask = None
        if self.frame == 0: 
            if actor.keysContain('attack') and self.chargeLevel == 0:
                actor.createMask([255,255,0],72,True,32)
            actor.changeSpriteImage(0)
        elif self.frame == 6:
            actor.changeSpriteImage(0)
            if actor.keysContain('attack') and self.chargeLevel <= 30:
                print("charging...")
                self.chargeLevel += 1
                self.dsmashHitbox1.damage += .146
                self.dsmashHitbox2.damage += .146
                self.frame -= 1
        elif self.frame > 6 and self.frame < self.lastFrame:
            actor.hurtbox.rect.width = 44
            actor.hurtbox.rect.midbottom = actor.sprite.boundingRect.midbottom
            actor.changeSpriteImage((self.frame//2-3)%6)
            print((self.frame//2-3)%6)
            if self.frame == 14:
                actor.active_hitboxes.add(self.spikeBox)
                actor.mask = None
            elif self.frame == 20:
                self.spikeBox.hitbox_lock = hitbox.HitboxLock()
            elif self.frame == 26:
                self.spikeBox.hitbox_lock = hitbox.HitboxLock()
            elif self.frame == 32:
                self.spikeBox.hitbox_lock = hitbox.HitboxLock()
            elif self.frame == 38:
                actor.active_hitboxes.add(self.dsmashHitbox1)
                actor.active_hitboxes.add(self.dsmashHitbox2)
            elif self.frame == 42:
                self.dsmashHitbox1.kill()
                self.dsmashHitbox2.kill()
        elif self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        
        self.frame += 1 
        
class ForwardAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)

    def tearDown(self,actor,nextAction):
        self.fSmashHitbox.kill()

    def onClank(self,actor):
        actor.doAction('NeutralAction')
    
    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,10,2.0,0.2,40,1,hitbox.HitboxLock())

    def stateTransitions(self, actor):
        if self.frame < 14 and not actor.grounded:
            actor.doAction('Fall')
            
    def update(self,actor):
        if self.frame == 0:
            actor.preferred_xspeed = 0
            actor.changeSprite("fsmash",0)
        elif self.frame <= 12:
            actor.changeSpriteImage(self.frame//2)
        elif self.frame == 14:
            actor.changeSpriteImage(7)
            self.fSmashHitbox.update()
            actor.active_hitboxes.add(self.fSmashHitbox)
        elif self.frame == 16:
            actor.changeSpriteImage(8)
            self.fSmashHitbox.kill()
        elif self.frame == 18:
            actor.changeSpriteImage(9)
        elif self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        
        self.frame += 1   

class ForwardSmash(action.Action):
    def __init__(self):
        action.Action.__init__(self, 46)
        self.chargeLevel = 0
        
    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,16,0.8,.25,40,1,hitbox.HitboxLock())

    def tearDown(self,actor,nextAction):
        self.fSmashHitbox.kill()

    def stateTransitions(self, actor):
        if self.frame < 18 and not actor.grounded:
            actor.doAction('Fall')
            
    def update(self,actor):
        if self.frame == 6 and not actor.keysContain('attack') and self.chargeLevel > 0:
            actor.mask = None
        if self.frame == 0:
            actor.preferred_xspeed = 0
            actor.changeSprite("fsmash",0)
        elif self.frame == 2:
            if actor.keysContain('attack') and self.chargeLevel == 0:
                actor.createMask([255,255,0],72,True,32)
            actor.changeSpriteImage(1)
        elif self.frame == 4:
            actor.changeSpriteImage(2)
        elif self.frame == 6:
            if actor.keysContain('attack') and self.chargeLevel <= 30:
                print("charging...")
                self.chargeLevel += 1
                self.fSmashHitbox.damage += .213
                self.fSmashHitbox.baseKnockback += 0.02
                self.frame -= 1
        elif self.frame == 8:
            actor.changeSpriteImage(3)
        elif self.frame == 10:
            actor.changeSpriteImage(4)
        elif self.frame == 12:
            actor.mask = None
            actor.changeSpriteImage(5)
        elif self.frame == 14:
            actor.changeSpriteImage(6)
        elif self.frame == 18:
            actor.changeSpriteImage(7)
            self.fSmashHitbox.update()
            actor.active_hitboxes.add(self.fSmashHitbox)
        elif self.frame == 32:
            self.fSmashHitbox.kill()
        elif self.frame == 40:
            actor.changeSpriteImage(8)
            self.fSmashHitbox.kill()
        elif self.frame == 43:
            actor.changeSpriteImage(9)
        elif self.frame == self.lastFrame:
            actor.doAction('NeutralAction')
        
        self.frame += 1 

class NeutralAir(action.Action):
    def __init__(self):
        action.Action.__init__(self, 40)
        self.ecbCenter = [0,7]
        self.ecbSize = [64, 78]
    
    def setUp(self, actor):
        actor.preferred_xspeed = 0
        actor.changeSprite("nair",0)
        self.subImage = 0
        self.nairHitbox = hitbox.SakuraiAngleHitbox([0,0],[72,72],actor,10,4,0.1,40,1,hitbox.HitboxLock(),1,1,1,0)
    
    def stateTransitions(self, actor):
        baseActions.airControl(actor)
        if actor.keysContain('down'):
            actor.platformPhase = 1
            actor.calc_grav(actor.var['fastfallMultiplier'])
    
    def tearDown(self,actor,other):
        self.nairHitbox.kill()
    
    def update(self,actor):
        actor.changeSpriteImage(self.subImage % 16)
        actor.hurtbox.rect.width = 64
        actor.hurtbox.rect.height = 64
        actor.hurtbox.rect.center = actor.sprite.boundingRect.center
        self.subImage += 1
        if self.frame == 2:
            actor.landingLag = 20
            actor.active_hitboxes.add(self.nairHitbox)
        if self.frame > 2:
            self.nairHitbox.update()
        if self.frame == 6:
            self.nairHitbox.damage = 7
            self.nairHitbox.baseKnockback = 5
        elif self.frame == 12:
            self.nairHitbox.damage = 5
            self.nairHitbox.baseKnockback = 2
        elif self.frame == 18:
            self.nairHitbox.damage = 3
            self.nairHitbox.baseKnockback = 1
            self.nairHitbox.hitstun = 0.5
            self.nairHitbox.base_hitstun = 0
        elif self.frame == 24:
            self.nairHitbox.damage = 1
            self.nairHitbox.baseKnockback = 0
            self.nairHitbox.hitstun = 0
        elif self.frame == 30:
            actor.landingLag = 12
        if self.frame == self.lastFrame:
            actor.changeAction(Fall())
        self.frame += 1

class BackAir(action.Action):
    def __init__(self):
        action.Action.__init__(self, 35)
        
    def setUp(self, actor):
        actor.changeSprite('bair')
        self.sweetspotHitbox = hitbox.DamageHitbox([-14,0], [64,46], actor, 10, 10, 0.2, 180, 1, hitbox.HitboxLock())
        
    def tearDown(self, actor, newAction):
        self.sweetspotHitbox.kill()
    
    def stateTransitions(self, actor):
        if self.frame >= 15 and self.frame < 35:
            baseActions.airControl(actor)
        elif self.frame >= 35:
            baseActions.airState(actor)
    
    def update(self, actor):
        actor.landingLag = 18
        self.sweetspotHitbox.update()
        if self.frame == 0:
            actor.changeSpriteImage(0)
        elif self.frame == 1:
            actor.changeSpriteImage(1)
        elif self.frame == 2:
            actor.changeSpriteImage(2)
            actor.change_x = 0
        elif self.frame == 4:
            actor.changeSpriteImage(3)
        elif self.frame == 6:
            actor.changeSpriteImage(4)
        elif self.frame == 8:
            actor.changeSpriteImage(5)
            actor.active_hitboxes.add(self.sweetspotHitbox)
            actor.change_x = 10 * actor.facing
        elif self.frame == 12:
            self.sweetspotHitbox.kill()
            actor.changeSpriteImage(6)
        elif self.frame == 16:
            actor.changeSpriteImage(7)
        elif self.frame >= 20:
            actor.changeSprite('jump')
        elif self.frame == self.lastFrame:
            actor.doAction('Fall')
        self.frame += 1

class ForwardAir(action.Action):
    def __init__(self):
        action.Action.__init__(self, 44)
        
    def setUp(self, actor):
        actor.changeSprite('fair')
        sharedLock = hitbox.HitboxLock()
        self.sourSpotHitbox = hitbox.DamageHitbox([-30,-2], [40,40], actor, 10, 8, 0.2, 50, 1, sharedLock)
        self.sweetSpotHitbox = hitbox.DamageHitbox([30,10], [40,40], actor, 14, 12, 0.3, 270, 1, sharedLock)
        
    def tearDown(self, actor, newAction):
        self.sourSpotHitbox.kill()
        self.sweetSpotHitbox.kill()
    
    def stateTransitions(self, actor):
        baseActions.airControl(actor)
    
    def update(self, actor):
        actor.landingLag = 26
        self.sourSpotHitbox.update()
        self.sweetSpotHitbox.update()
        if self.frame == 0:
            actor.changeSpriteImage(0)
        elif self.frame == 2:
            actor.changeSpriteImage(1)
        elif self.frame == 4:
            actor.changeSpriteImage(2)
        elif self.frame == 6:
            actor.changeSpriteImage(3)
        elif self.frame == 10:
            actor.changeSpriteImage(4)
        elif self.frame == 12:
            actor.changeSpriteImage(5)
            actor.active_hitboxes.add(self.sourSpotHitbox)
        elif self.frame == 14:
            actor.changeSpriteImage(6)
            self.sourSpotHitbox.x_offset = -14
            self.sourSpotHitbox.y_offset = -20
        elif self.frame == 16:
            actor.changeSpriteImage(7)
            actor.active_hitboxes.add(self.sweetSpotHitbox)
            self.sourSpotHitbox.x_offset = 9
            self.sourSpotHitbox.y_offset = -26
        elif self.frame == 18:
            actor.changeSpriteImage(8)
            self.sourSpotHitbox.x_offset = 23
            self.sourSpotHitbox.y_offset = -12
            self.sweetSpotHitbox.kill()
        elif self.frame == 20:
            self.sourSpotHitbox.x_offset = 30
            self.sourSpotHitbox.y_offset = 10
            actor.changeSpriteImage(9)
        elif self.frame == 22:
            actor.changeSpriteImage(10)
            self.sourSpotHitbox.kill()
        elif self.frame == 24:
            actor.changeSpriteImage(11)
        elif self.frame == 26:
            actor.changeSprite('jump')
        elif self.frame == self.lastFrame:
            actor.doAction('Fall')
        actor.hurtbox.rect.width -= 8
        actor.hurtbox.rect.height -= 8
        actor.hurtbox.rect.center = actor.sprite.boundingRect.center
        self.frame += 1

class DownAir(action.Action):
    def __init__(self):
        action.Action.__init__(self,39)
        self.bottom = 0

    def setUp(self, actor):
        actor.setSpeed(0, actor.getFacingDirection())
        actor.changeSprite("dair", 0)
        allLock = hitbox.HitboxLock()
        self.downHitbox = hitbox.DamageHitbox([0,80], [10,50], actor, 9, 8, 0.08, 270, 1, allLock, 1, 1, 1, 0)
        self.leftDiagonalHitbox = hitbox.DamageHitbox([-10,70], [10,30], actor, 7, 7, 0.06, 225, 1, allLock, 1, 1, 1, 0)
        self.rightDiagonalHitbox = hitbox.DamageHitbox([10,70], [10,30], actor, 7, 7, 0.06, 315, 1, allLock, 1, 1, 1, 0)
        self.leftSourSpot = hitbox.DamageHitbox([-20,60], [10,10], actor, 5, 6, 0.04, 180, 1, allLock, 1, 1, 1, 0)
        self.rightSourSpot = hitbox.DamageHitbox([20,60], [10,10], actor, 5, 6, 0.04, 0, 1, allLock, 1, 1, 1, 0)

    def stateTransitions(self, actor):
        baseActions.airControl(actor)

    def tearDown(self, actor, nextAction):
        actor.rect.bottom += self.bottom
        self.downHitbox.kill()
        self.leftDiagonalHitbox.kill()
        self.rightDiagonalHitbox.kill()
        self.leftSourSpot.kill()
        self.rightSourSpot.kill()
        
    def update(self, actor):
        actor.preferred_xspeed = 0
        self.downHitbox.update()
        self.leftDiagonalHitbox.update()
        self.rightDiagonalHitbox.update()
        self.leftSourSpot.update()
        self.rightSourSpot.update()
        if self.frame < 3:
            actor.landingLag = 16
            actor.changeSpriteImage(0)
            actor.change_y = 0
        elif self.frame < 6:
            actor.changeSpriteImage(1)
            actor.change_y = 0
        elif self.frame < 9:
            actor.changeSpriteImage(2)
            actor.change_y = 0
        elif self.frame < 12:
            actor.changeSpriteImage(3)
            self.bottom = 14
            actor.change_y = 0
        elif self.frame < 15:
            self.bottom = 34
            actor.changeSpriteImage(4)
            actor.change_y = actor.var['maxFallSpeed']
            actor.active_hitboxes.add(self.downHitbox)
            actor.active_hitboxes.add(self.leftDiagonalHitbox)
            actor.active_hitboxes.add(self.rightDiagonalHitbox)
            actor.active_hitboxes.add(self.leftSourSpot)
            actor.active_hitboxes.add(self.rightSourSpot)
        elif self.frame == 30 and actor.keysContain('attack'):
            self.frame -= 1
        elif self.frame < 30:
            pass
        elif self.frame < 33:
            self.bottom = 14
            self.downHitbox.kill()
            self.leftDiagonalHitbox.kill()
            self.rightDiagonalHitbox.kill()
            self.leftSourSpot.kill()
            self.rightSourSpot.kill()
            actor.changeSpriteImage(3)
        elif self.frame < 36:
            self.bottom = 0
            actor.changeSpriteImage(2)
        elif self.frame < 39:
            actor.changeSpriteImage(1)
        else: 
            actor.changeSpriteImage(0)
            actor.landingLag = 8
            actor.changeAction(Fall())
        actor.hurtbox.rect.height -= 16
        actor.hurtbox.rect.midtop = actor.sprite.boundingRect.midtop
        self.frame += 1

class UpAir(action.Action):
    def __init__(self):
        action.Action.__init__(self, 34)
        
    def setUp(self, actor):
        sharedLock = hitbox.HitboxLock()
        self.sourspot = hitbox.DamageHitbox([0,18],[60,47], actor, 6, 8, 0.05, 60, 1, sharedLock, 1, 1, 1, 0)
        self.semisweet = hitbox.DamageHitbox([0,-27],[30,46], actor, 8, 6, 0.1, 75, 1, sharedLock, 1, 1, 1, 0)
        self.sweetspot = hitbox.DamageHitbox([0,-25],[20,42], actor, 12, 6, 0.2, 90, 1, sharedLock, 1, 1, 1, 0)
    
    def stateTransitions(self, actor):
        baseActions.airControl(actor)
        
    def tearDown(self, actor, newAction):
        self.sourspot.kill()
        self.semisweet.kill()
        self.sweetspot.kill()
    
    def update(self, actor):
        print(self.frame)
        actor.landingLag = 20
        self.sourspot.update()
        self.semisweet.update()
        self.sweetspot.update()
        if self.frame == 0:
            actor.changeSprite('uair',0)
        elif self.frame == 3:
            actor.changeSpriteImage(1)
        elif self.frame == 6:
            actor.changeSpriteImage(2)
            actor.active_hitboxes.add(self.sourspot)
            actor.active_hitboxes.add(self.sweetspot)
        elif self.frame == 9:
            self.sweetspot.kill()
            actor.active_hitboxes.add(self.semisweet)
        elif self.frame == 18:
            actor.changeSpriteImage(3)
            self.semisweet.kill()
        elif self.frame == 21:
            actor.landingLag = 12
            actor.changeSpriteImage(4)
            self.sourspot.kill()
        elif self.frame == self.lastFrame:
            actor.doAction('Fall')
        self.frame += 1

class GroundGrab(action.Action):
    def __init__(self):
        action.Action.__init__(self, 30)

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

    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,11,12.0,0.20,40,1,hitbox.HitboxLock())

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
                    actor.grabbing.applyKnockback(9, 12, 0.15, actor.getForwardWithOffset(70))
                actor.doAction('Fall')
        self.frame += 1

class BackThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self, 22)

    def setUp(self, actor):
        actor.changeSprite("bthrow")

    def tearDown(self, actor, nextAction):
        baseActions.BaseGrabbing.tearDown(self, actor, nextAction)

    def update(self, actor):
        baseActions.BaseGrabbing.update(self, actor)
        if self.frame == 0 and actor.isGrabbing():
            actor.grabbing.applyKnockback(7, 10, 0.1, actor.getForwardWithOffset(170), 0.5)
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
        
class Run(baseActions.Run):
    def __init__(self):
        baseActions.Run.__init__(self,2)
        
    def update(self, actor):
        actor.changeSprite("run",4)
                
        baseActions.Run.update(self, actor)
        if (self.frame == self.lastFrame):
            self.frame = 1
                   
class Pivot(baseActions.Pivot):
    def __init__(self):
        baseActions.Pivot.__init__(self,10)
        
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

    def update(self, actor):
        baseActions.Grabbing.update(self, actor)
        actor.change_x = 0
        if self.frame == 0:
            actor.changeSprite('pivot', 4)
        self.frame += 1
        
class Stop(baseActions.Stop):
    def __init__(self):
        baseActions.Stop.__init__(self, 9)
    
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

    def setUp(self, actor):
        actor.changeSprite('land', 2)

    def update(self, actor):
        actor.changeSpriteImage(3-self.frame/3)
        baseActions.CrouchGetup.update(self, actor)
        
class HitStun(baseActions.HitStun):
    def __init__(self,hitstun,direction):
        baseActions.HitStun.__init__(self, hitstun, direction)

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

    def update(self, actor):
        actor.changeSprite("jump")
        baseActions.Helpless.update(self, actor)
            
class Land(baseActions.Land):
    def __init__(self):
        baseActions.Land.__init__(self)

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
    def __init__(self, length, direction):
        baseActions.Trip.__init__(self, length, direction)

    def setUp(self, actor):
        baseActions.Trip.setUp(self, actor)
        actor.sideSpecialUses = 1

    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("land", 3)
        baseActions.Trip.update(self, actor)

class Getup(baseActions.Getup):
    def __init__(self, direction):
        baseActions.Getup.__init__(self, direction, 12)

    def update(self, actor):
        if self.frame < 12:
            if self.frame % 3 == 0:
                actor.changeSprite("land", 3-self.frame//3)
        baseActions.Getup.update(self, actor)

class GetupAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,36)

    def setUp(self, actor):
        actor.preferred_xspeed = 0
        actor.changeSprite("nair")
        self.ecbCenter = [0,7]
        self.ecbSize = [64, 78]
        self.dashHitbox = hitbox.DamageHitbox([0,0],[70,70],actor,2,5,0.1,20,1,hitbox.HitboxLock())
        self.chainHitbox = hitbox.AutolinkHitbox([0,0],[70,70],actor,2,1,hitbox.HitboxLock(),0,-1,1,1.5)

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
    def __init__(self, newShield):
        baseActions.Shield.__init__(self, newShield)
    
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("jump")
        baseActions.Shield.update(self, actor)

class ShieldStun(baseActions.ShieldStun):
    def __init__(self, length):
        baseActions.ShieldStun.__init__(self, length)

    def update(self, actor):
        actor.createMask([191, 63, 191], self.lastFrame, False, 8)
        baseActions.ShieldStun.update(self, actor)

class Stunned(baseActions.Stunned):
    def __init__(self, length):
        baseActions.Stunned.__init__(self, length)

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
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",1)
        elif self.frame == self.endInvulnFrame:
            actor.changeSprite("land",0)
        baseActions.ForwardRoll.update(self, actor)
        
class BackwardRoll(baseActions.BackwardRoll):
    def __init__(self):
        baseActions.BackwardRoll.__init__(self)
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",1)
        elif self.frame == self.endInvulnFrame:
            actor.changeSprite("land",0)
        baseActions.BackwardRoll.update(self, actor)
        
class SpotDodge(baseActions.SpotDodge):
    def __init__(self):
        baseActions.SpotDodge.__init__(self)
        
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
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("nair",0)
        elif self.frame == self.startInvulnFrame:
            actor.changeSpriteImage(-round(abs(actor.change_x)))
        elif self.frame == self.endInvulnFrame:
            actor.changeSpriteImage(0)
        baseActions.AirDodge.update(self, actor)

class Trapped(baseActions.Trapped):
    def __init__(self, length):
        baseActions.Trapped.__init__(self, length)

    def setUp(self, actor):
        baseActions.Trapped.setUp(self, actor)
        actor.sideSpecialUses = 1

    def update(self, actor):
        actor.changeSprite("idle")
        baseActions.Trapped.update(self, actor)

class Grabbed(baseActions.Grabbed):
    def __init__(self,height):
        baseActions.Grabbed.__init__(self, height)

    def setUp(self, actor):
        baseActions.Grabbed.setUp(self, actor)
        actor.sideSpecialUses = 1

    def update(self,actor):
        actor.changeSprite("idle")
        baseActions.Grabbed.update(self, actor)

class Release(baseActions.Release):
    def __init__(self,height):
        baseActions.Release.__init__(self)

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

    def setUp(self, actor):
        baseActions.Released.setUp(self, actor)
        actor.changeSprite("jump")

class LedgeGrab(baseActions.LedgeGrab):
    def __init__(self,ledge=None):
        baseActions.LedgeGrab.__init__(self, ledge)

    def setUp(self, actor):
        baseActions.LedgeGrab.setUp(self, actor)
        actor.sideSpecialUses = 1
        
    def update(self,actor):
        actor.changeSprite('jump')
        baseActions.LedgeGrab.update(self, actor)

class LedgeGetup(baseActions.LedgeGetup):
    def __init__(self):
        baseActions.LedgeGetup.__init__(self,27)

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

    def setUp(self,actor):
        baseActions.LedgeGetup.setUp(self, actor)
        actor.invincibility = 24
        actor.createMask([255,255,255], 24, True, 24)
        self.dashHitbox = hitbox.DamageHitbox([0,0],[70,70],actor,2,8,0.2,20,1,hitbox.HitboxLock())
        self.chainHitbox = hitbox.AutolinkHitbox([0,0],[70,70],actor,2,1,hitbox.HitboxLock(),0,-1,1,1.5)

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
        
    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("idle")
            self.frame += 1
        
class Crouch(baseActions.Crouch):
    def __init__(self):
        baseActions.Crouch.__init__(self, 2)
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
        
    def update(self,actor):
        actor.changeSprite("jump")
        baseActions.Fall.update(self, actor)


########################################################
#             BEGIN HELPER METHODS                     #
########################################################
