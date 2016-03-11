import engine.action as action
import engine.baseActions as baseActions
import engine.hitbox as hitbox
import engine.article as article
import engine.abstractFighter as abstractFighter
import math

import settingsManager #TEMPORARY until I figure out article sprites

class SplatArticle(article.AnimatedArticle):
    def __init__(self, owner, origin, direction):
        article.AnimatedArticle.__init__(self, settingsManager.createPath('sprites/hitboxie_projectile.png'), owner, origin, imageWidth=16,length=120)
        self.direction = direction
        self.change_y = 0
        self.hitbox = hitbox.DamageHitbox(self.rect.center, [12,12], self.owner, 6, 2, 0, 0, 1, hitbox.HitboxLock())  
        self.hitbox.article = self
            
    # Override the onCollision of the hitbox
    def onCollision(self, other):
        othersClasses = map(lambda(x):x.__name__,other.__class__.__bases__) + [other.__class__.__name__]
        print othersClasses
        if 'AbstractFighter' in othersClasses or 'Platform' in othersClasses:
            self.hitbox.kill()
            self.kill()
        #TODO check for verticality of platform landing
            
            
    def update(self):
        self.rect.x += 24 * self.direction
        self.rect.y += self.change_y
        self.change_y += 0.5
        self.hitbox.rect.center = self.rect.center #update adjusts to the actor
        self.frame += 1
            
        if self.frame > 120:
            self.kill()
            self.hitbox.kill()

class NeutralGroundSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self,40)
                
    def setUp(self, actor):
        self.projectile = SplatArticle(actor,(actor.sprite.boundingRect.centerx + (32 * actor.facing), actor.sprite.boundingRect.centery), actor.facing)
        actor.change_x = 0
        actor.preferred_xspeed = 0
        actor.changeSprite("nspecial",0)
        
    def tearDown(self, actor, new):
        pass
    
    def stateTransitions(self, actor):
        pass
               
    def update(self, actor):
        actor.changeSpriteImage(math.floor(self.frame/4))
        if self.frame == 24:
            self.projectile.rect.center = (actor.sprite.boundingRect.centerx + (24 * actor.facing),actor.sprite.boundingRect.centery-8)
            actor.articles.add(self.projectile)
            actor.active_hitboxes.add(self.projectile.hitbox)
            print actor.active_hitboxes
            
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1

class NeutralAirSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self,40)
                
    def setUp(self, actor):
        self.projectile = SplatArticle(actor,(actor.sprite.boundingRect.centerx + (32 * actor.facing), actor.sprite.boundingRect.centery), actor.facing)
        actor.changeSprite("nspecial",0)


    def stateTransitions(self, actor):
        if actor.keysContain('down'):
            if actor.change_y >= 0:
                actor.change_y = actor.var['maxFallSpeed']
        baseActions.airControl(actor)
        
    def tearDown(self, actor, new):
        pass
               
    def update(self, actor):
        actor.landingLag = 25
        actor.changeSpriteImage(math.floor(self.frame/4))
        if self.frame == 24:
            self.projectile.rect.center = (actor.sprite.boundingRect.centerx + (24 * actor.facing),actor.sprite.boundingRect.centery-8)
            actor.articles.add(self.projectile)
            actor.active_hitboxes.add(self.projectile.hitbox)
            print actor.active_hitboxes
            if actor.bufferContains('special', 8):
                actor.changeAction(NeutralAirSpecial())
            
        if self.frame == self.lastFrame:
            actor.landingLag = 12
            actor.changeAction(Fall())
        self.frame += 1

class ForwardSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self, 32)
        self.spriteImage = 0

    def setUp(self, actor):
        actor.change_x = 0
        actor.preferred_xspeed = 0
        actor.flinch_knockback_threshold = 4
        actor.changeSprite("nair",0)
        self.chainHitbox = hitbox.AutolinkHitbox([0,0], [80,80], actor, 1, 1, hitbox.HitboxLock(), 5, 1)
        self.flingHitbox = self.sideSpecialHitbox(actor)

    class sideSpecialHitbox(hitbox.SakuraiAngleHitbox):
        def __init__(self,actor):
            hitbox.SakuraiAngleHitbox.__init__(self, [0,0], [80,80], actor, 8, 2, 0.04, 30, 1, hitbox.HitboxLock(), 1, 6)

        def onCollision(self, other):
            hitbox.Hitbox.onCollision(self, other)
            if 'AbstractFighter' in map(lambda(x):x.__name__,other.__class__.__bases__) + [other.__class__.__name__]:
                if other.lockHitbox(self):
                    if other.shield:
                        other.shieldDamage(math.floor(self.damage*self.shield_multiplier))
                    elif other.grounded:
                        other.dealDamage(self.damage)
                        (actorDirect,_) = self.owner.getDirectionMagnitude()
                        other.doTrip(40, other.getForwardWithOffset(actorDirect))
                    else:
                        other.applyKnockback(self.damage, self.baseKnockback, self.knockbackGrowth, self.trajectory, self.weight_influence, self.hitstun)
                            
    def stateTransitions(self, actor):
        if actor.change_x/actor.facing <= 0 and self.frame >= 2:
            baseActions.grabLedges(actor)

    def tearDown(self, actor, newAction):
        self.chainHitbox.kill()
        self.flingHitbox.kill()
        actor.flinch_knockback_threshold = 0

    def update(self, actor):
        actor.changeSpriteImage(self.spriteImage%16)
        if self.frame < self.lastFrame:
            self.spriteImage += 1
            if self.frame <= 1:
                actor.setSpeed(0, actor.getForwardWithOffset(0))
                actor.change_x = 0
                if actor.change_y > 2:
                    actor.change_y = 2
                if actor.keysContain('shield'):
                    actor.doShield()
                elif actor.keysContain('special') and self.lastFrame < 240:
                    self.lastFrame += 2
                    self.frame -= 1
            else: #Actually launch forwards
                self.chainHitbox.update()
                actor.active_hitboxes.add(self.chainHitbox)
                (key, invkey) = actor.getForwardBackwardKeys()
                if self.frame == 2:
                    actor.setSpeed(actor.var['runSpeed'], actor.getForwardWithOffset(0))
                    actor.change_y = -8
                if self.spriteImage%6 == 0:
                    self.chainHitbox.hitbox_lock = hitbox.HitboxLock()
                if actor.keysContain(invkey):
                    actor.setPreferredSpeed(actor.var['runSpeed']/2, actor.getForwardWithOffset(0))
                    self.frame += 2
                    if (self.frame > self.lastFrame):
                        self.frame = self.lastFrame
                elif actor.keysContain(key):
                    actor.setPreferredSpeed(actor.var['runSpeed'], actor.getForwardWithOffset(0))
                else:
                    actor.setPreferredSpeed(actor.var['runSpeed']*3/4, actor.getForwardWithOffset(0))
                    self.frame += 1
                    if (self.frame > self.lastFrame):
                        self.frame = self.lastFrame
                
        else:
            if self.frame == self.lastFrame:
                self.flingHitbox.update()
                actor.active_hitboxes.add(self.flingHitbox)
            else:
                self.flingHitbox.kill()
            self.chainHitbox.kill()
            # 32 frames of wind-down. Plenty to punish if it was expected.
            actor.setPreferredSpeed(0, actor.facing) 
            if self.frame % 2 == 0:
                self.spriteImage += 1
            if self.frame >= self.lastFrame+32:
                if actor.grounded:
                    actor.doIdle()
                else:
                    actor.landingLag = 5
                    actor.doFall()
        self.frame += 1
                    
           
class NeutralAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,22)
    
    def setUp(self, actor):
        actor.change_x = 0
        actor.preferred_xspeed = 0
        actor.changeSprite("neutral",0)
        self.jabHitbox = self.outwardHitbox(actor)
        
    def tearDown(self, actor, new):
        self.jabHitbox.kill()
    
    def stateTransitions(self, actor):
        if self.frame == self.lastFrame:
            if actor.keysContain('attack'):
                self.jabHitbox.hitbox_lock = hitbox.HitboxLock()
                self.frame = 0
                
    # Here's an example of creating an anonymous hitbox class.
    # This one calculates its trajectory based off of the angle between the two fighters.
    # Since this hitbox if specifically for this attack, we can hard code in the values.
    class outwardHitbox(hitbox.DamageHitbox):
        def __init__(self,actor):
            hitbox.DamageHitbox.__init__(self, [0,0], [80,80], actor, 2, 8, 0.02, 0, 1, hitbox.HitboxLock())
            
        def onCollision(self,other):
            hitbox.Hitbox.onCollision(self, other)
            self.trajectory = abstractFighter.getDirectionBetweenPoints(self.owner.rect.midbottom, other.rect.center)
            hitbox.DamageHitbox.onCollision(self, other)
            
    def update(self, actor):
        if self.frame < 9:
            actor.changeSpriteImage(self.frame)
        elif self.frame == 9:
            actor.active_hitboxes.add(self.jabHitbox)
        elif self.frame >= 10 and self.frame <= 13:
            actor.changeSpriteImage(9)
        elif self.frame > 13:
            self.jabHitbox.kill()
            if not (self.frame) > 18:
                actor.changeSpriteImage(self.frame - 4)
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1

class DashAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,32)

    def setUp(self, actor):
        actor.setPreferredSpeed(actor.change_x, actor.facing)
        actor.changeSprite("nair")

        self.dashHitbox = hitbox.DamageHitbox([0,0],[70,70],actor,2,10,0.07,20,1,hitbox.HitboxLock())
        self.chainHitbox = hitbox.AutolinkHitbox([0,0],[70,70],actor,2,1,hitbox.HitboxLock(),1,1.5)

    def tearDown(self,actor,other):
        self.dashHitbox.kill()
        self.chainHitbox.kill()
        actor.setPreferredSpeed(0, actor.facing)

    def update(self,actor):
        if self.frame%2 == 0 and self.frame <= 8:
            actor.changeSpriteImage(self.frame/2)
        elif self.frame <= 24:
            actor.changeSpriteImage((self.frame-4)%16)
        elif self.frame%2 == 0:
            actor.changeSpriteImage((self.frame/2-8)%16)

        self.dashHitbox.update()
        self.chainHitbox.update()

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
            actor.setPreferredSpeed(0, actor.facing)

        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1
        
class DownAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self, 34)
    
    def setUp(self, actor):
        actor.change_x = 0
        actor.preferred_xspeed = 0
        actor.changeSprite("dsmash",0)
        hitbox_lock = hitbox.HitboxLock()
        self.dsmashHitbox1 = hitbox.SakuraiAngleHitbox([34,26],[24,52],actor,12,8,0.075,40,1,hitbox_lock)
        self.dsmashHitbox2 = hitbox.SakuraiAngleHitbox([-34,26],[24,52],actor,12,8,0.075,140,1,hitbox_lock)
    
    def tearDown(self,actor,other):
        self.dsmashHitbox1.kill()
        self.dsmashHitbox2.kill()
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSpriteImage(0)
        elif self.frame == 2:
            actor.changeSpriteImage(1)
        elif self.frame == 4:
            actor.changeSpriteImage(2)
        elif self.frame == 6:
            actor.changeSpriteImage(3)
        elif self.frame == 8:
            actor.changeSpriteImage(4)
        elif self.frame == 12:
            actor.changeSpriteImage(5)
        elif self.frame == 14:
            actor.changeSpriteImage(6)
        elif self.frame == 15:
            actor.changeSpriteImage(7)
            actor.active_hitboxes.add(self.dsmashHitbox1)
            actor.active_hitboxes.add(self.dsmashHitbox2)
            #create hitbox
        elif self.frame == 17:
            actor.changeSpriteImage(8)
        elif self.frame == 19:
            actor.changeSpriteImage(9)
            #create sweetspot hitbox
        elif self.frame == 23:
            actor.changeSpriteImage(10)
        elif self.frame == 25:
            actor.changeSpriteImage(11)
        elif self.frame == 27:
            actor.changeSpriteImage(12)
        elif self.frame == 29:
            actor.changeSpriteImage(13)
        elif self.frame == 31:
            actor.changeSpriteImage(14)
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1
                       
class ForwardAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
    
    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,8,2.0,0.3,40,1,hitbox.HitboxLock())
            
    def update(self,actor):
        if self.frame == 0:
            actor.change_x = 0
            actor.preferred_xspeed = 0
            actor.changeSprite("fsmash",0)
        elif self.frame == 2:
            actor.changeSpriteImage(1)
        elif self.frame == 4:
            actor.changeSpriteImage(2)
        elif self.frame == 6:
            actor.changeSpriteImage(3)
        elif self.frame == 8:
            actor.changeSpriteImage(4)
        elif self.frame == 10:
            actor.changeSpriteImage(5)
        elif self.frame == 12:
            actor.changeSpriteImage(6)
        elif self.frame == 14:
            actor.changeSpriteImage(7)
            actor.active_hitboxes.add(self.fSmashHitbox)
        elif self.frame == 16:
            actor.changeSpriteImage(8)
            self.fSmashHitbox.kill()
        elif self.frame == 18:
            actor.changeSpriteImage(9)
        elif self.frame == self.lastFrame:
            actor.doIdle()
        
        self.frame += 1
        
        def stateTransitions(self,actor):
            if self.frame > 20:
                baseActions.neutralState(actor)    

class ForwardSmash(action.Action):
    def __init__(self):
        action.Action.__init__(self, 42)
        self.chargeLevel = 0
        
    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,12,0.8,.35,40,1,hitbox.HitboxLock())
            
    def update(self,actor):
        if self.frame >= 3 and self.frame <= 8 and not actor.keysContain('attack') and self.chargeLevel > 0:
            self.frame = 9
            actor.mask = None
            
        if self.frame == 0:
            actor.change_x = 0
            actor.preferred_xspeed = 0
            actor.changeSprite("fsmash",0)
        elif self.frame == 3:
            if actor.keysContain('attack') and self.chargeLevel == 0:
                actor.createMask([255,255,0],72,True,32)
            actor.changeSpriteImage(1)
        elif self.frame == 6:
            actor.changeSpriteImage(2)
        elif self.frame == 8:
            if actor.keysContain('attack') and self.chargeLevel <= 5:
                print("charging...")
                self.chargeLevel += 1
                self.fSmashHitbox.damage += 1
                self.fSmashHitbox.baseKnockback += 0.05
                self.frame = 3
        elif self.frame == 9:
            actor.changeSpriteImage(3)
        elif self.frame == 12:
            actor.changeSpriteImage(4)
        elif self.frame == 15:
            actor.mask = None
            actor.changeSpriteImage(5)
        elif self.frame == 18:
            actor.changeSpriteImage(6)
        elif self.frame == 21:
            actor.changeSpriteImage(7)
            actor.active_hitboxes.add(self.fSmashHitbox)
        elif self.frame == 36:
            actor.changeSpriteImage(8)
            self.fSmashHitbox.kill()
        elif self.frame == 39:
            actor.changeSpriteImage(9)
        elif self.frame == self.lastFrame:
            actor.doIdle()
        
        self.frame += 1 

class NeutralAir(action.Action):
    def __init__(self):
        action.Action.__init__(self, 34)
    
    def setUp(self, actor):
        actor.change_x = 0
        actor.preferred_xspeed = 0
        actor.changeSprite("nair",0)
        self.subImage = 0
        self.nairHitbox = hitbox.SakuraiAngleHitbox([0,0],[72,72],actor,10,4,0.06,40,1,hitbox.HitboxLock())
    
    def stateTransitions(self, actor):
        if actor.keysContain('down'):
            if actor.change_y >= 0:
                actor.change_y = actor.var['maxFallSpeed']
        baseActions.airControl(actor)
    
    def tearDown(self,actor,other):
        self.nairHitbox.kill()
    
    def update(self,actor):
        actor.landingLag = 28
        actor.changeSpriteImage(self.subImage % 16)
        self.subImage += 1
        if self.frame == 2:
            actor.active_hitboxes.add(self.nairHitbox)
        if self.frame > 2:
            self.nairHitbox.update()
        if self.frame == 6:
            self.nairHitbox.damage = 8
            self.nairHitbox.baseKnockback = 5
        elif self.frame == 18:
            self.nairHitbox.damage = 4
            self.nairHitbox.baseKnockback = 2
        if self.frame == self.lastFrame:
            self.nairHitbox.kill()
            actor.landingLag = 14
            actor.changeAction(Fall())
        self.frame += 1

class DownAir(action.Action):
    def __init__(self):
        action.Action.__init__(self,30)
        self.bottom = 0

    def setUp(self, actor):
        actor.setSpeed(0, actor.getFacingDirection())
        actor.changeSprite("dair", 0)
        allLock = hitbox.HitboxLock()
        self.downHitbox = hitbox.DamageHitbox([0,80], [10,50], actor, 9, 8, 0.08, 270, 1, allLock)
        self.leftDiagonalHitbox = hitbox.DamageHitbox([-10,70], [10,30], actor, 7, 7, 0.06, 225, 1, allLock)
        self.rightDiagonalHitbox = hitbox.DamageHitbox([10,70], [10,30], actor, 7, 7, 0.06, 315, 1, allLock)
        self.leftSourSpot = hitbox.DamageHitbox([-20,60], [10,10], actor, 5, 6, 0.04, 180, 1, allLock)
        self.rightSourSpot = hitbox.DamageHitbox([20,60], [10,10], actor, 5, 6, 0.04, 0, 1, allLock)

    def stateTransitions(self, actor):
        baseActions.airControl(actor)

    def tearDown(self, actor, nextAction):
        actor.rect.y += self.bottom
        self.downHitbox.kill()
        self.leftDiagonalHitbox.kill()
        self.rightDiagonalHitbox.kill()
        self.leftSourSpot.kill()
        self.rightSourSpot.kill()
        
    def update(self, actor):
        actor.landingLag = 30
        actor.change_x = 0
        actor.preferred_xspeed = 0
        self.downHitbox.update()
        self.leftDiagonalHitbox.update()
        self.rightDiagonalHitbox.update()
        self.leftSourSpot.update()
        self.rightSourSpot.update()
        if self.frame < 3:
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
        elif self.frame == self.lastFrame and actor.keysContain('attack'):
            self.frame -= 2
        elif self.frame < self.lastFrame:
            pass
        elif self.frame < self.lastFrame + 3:
            self.bottom = 14
            self.downHitbox.kill()
            self.leftDiagonalHitbox.kill()
            self.rightDiagonalHitbox.kill()
            self.leftSourSpot.kill()
            self.rightSourSpot.kill()
            actor.changeSpriteImage(3)
        elif self.frame < self.lastFrame + 6:
            self.bottom = 0
            actor.changeSpriteImage(2)
        elif self.frame < self.lastFrame + 9:
            actor.changeSpriteImage(1)
        else: 
            actor.changeSpriteImage(0)
            actor.landingLag = 18
            actor.changeAction(Fall())
        self.frame += 1

class GroundGrab(action.Action):
    def __init__(self):
        action.Action.__init__(self, 35)

    def setUp(self, actor):
        self.grabHitbox = hitbox.GrabHitbox([40,0], [40,40], actor, hitbox.HitboxLock(), 30)

    def tearDown(self, actor, other):
        self.grabHitbox.kill()

    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("pivot", 0)
        elif self.frame == 4:
            actor.changeSpriteImage(1)
        elif self.frame == 8:
            actor.changeSpriteImage(2)
        elif self.frame == 12:
            actor.changeSpriteImage(3)
            actor.active_hitboxes.add(self.grabHitbox)
        elif self.frame == 16:
            actor.changeSpriteImage(4)
        elif self.frame == 20:
            actor.changeSpriteImage(3)
            self.grabHitbox.kill()
        elif self.frame == 24:
            actor.changeSpriteImage(2)
        elif self.frame == 28:
            actor.changeSpriteImage(1)
        elif self.frame == 32:
            actor.changeSpriteImage(0)
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1

class Pummel(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self,22)

    def update(self, actor):
        baseActions.BaseGrabbing.update(self, actor)
        if self.frame == 0:
            actor.changeSprite("neutral", self.frame)
        elif self.frame < 9:
            actor.changeSpriteImage(self.frame)
        elif isinstance(actor.grabbing.current_action, baseActions.Grabbed) and self.frame == 9:
            actor.grabbing.dealDamage(2)
        elif self.frame >= 10 and self.frame <= 13:
            actor.changeSpriteImage(9)
        elif self.frame > 13:
            if not (self.frame) > 18:
                actor.changeSpriteImage(self.frame - 4)
        if self.frame == self.lastFrame:
            actor.doGrabbing()
        self.frame += 1
        
class ForwardThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self,20)

    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,10,12.0,0.20,40,1,hitbox.HitboxLock())

    def tearDown(self, actor, other):
        self.fSmashHitbox.kill()
        baseActions.BaseGrabbing.tearDown(self, actor, other)

    def update(self, actor): 
        baseActions.BaseGrabbing.update(self, actor)
        if self.frame == 0:
            actor.change_x = 0
            actor.preferred_xspeed = 0
            actor.changeSprite("fsmash",0)
        elif self.frame == 2:
            actor.changeSpriteImage(1)
        elif self.frame == 4:
            actor.changeSpriteImage(2)
        elif self.frame == 6:
            actor.changeSpriteImage(3)
        elif self.frame == 8:
            actor.changeSpriteImage(4)
        elif self.frame == 10:
            actor.changeSpriteImage(5)
        elif self.frame == 12:
            actor.changeSpriteImage(6)
        elif self.frame == 14:
            actor.changeSpriteImage(7)
            actor.active_hitboxes.add(self.fSmashHitbox)
        elif self.frame == 16:
            actor.changeSpriteImage(8)
            self.fSmashHitbox.kill()
        elif self.frame == 18:
            actor.changeSpriteImage(9)
        elif self.frame == self.lastFrame:
            actor.doIdle()
        
        self.frame += 1

class DownThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self, 32)

    def setUp(self, actor):
        actor.changeSprite("nair")
        self.bottomHitbox = hitbox.DamageHitbox([10, 40], [30, 30], actor, 1, 3, 0, 260, 1, hitbox.HitboxLock(), 0, 1)
        actor.active_hitboxes.add(self.bottomHitbox)

    def tearDown(self, actor, nextAction):
        self.bottomHitbox.kill()
        baseActions.BaseGrabbing.tearDown(self, actor, nextAction)

    def update(self, actor):
        baseActions.BaseGrabbing.update(self, actor)
        actor.changeSpriteImage(self.frame%16)
        if (self.frame%4 == 0):
            self.bottomHitbox.hitbox_lock = hitbox.HitboxLock()
        if (self.frame == self.lastFrame-4):
            self.bottomHitbox.baseKnockback = 10
            self.bottomHitbox.trajectory = actor.getForwardWithOffset(90)
            self.bottomHitbox.knockbackGrowth = 0.12
            self.weight_influence = 1
        if self.frame == self.lastFrame:
            actor.doIdle()
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
                
        if actor.grounded == False:
            actor.doFall()
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
                
        if actor.grounded == False:
            actor.doFall()
        baseActions.Dash.update(self, actor)
        
class Run(baseActions.Run):
    def __init__(self):
        baseActions.Run.__init__(self,2)
        
    def update(self, actor):
        actor.changeSprite("run",4)
                
        if actor.grounded == False:
            actor.doFall()
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
        if isinstance(newAction, Move):
            newAction.accel = False
        
class NeutralAction(baseActions.NeutralAction):
    def __init__(self):
        baseActions.NeutralAction.__init__(self,1)
        
    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("idle")
            self.frame += 1
        if actor.grounded == False: actor.doFall()

class Grabbing(baseActions.Grabbing):
    def __init__(self):
        baseActions.Grabbing.__init__(self,1)

    def update(self, actor):
        baseActions.Grabbing.update(self, actor)
        actor.change_x = 0
        if self.frame == 0:
            actor.changeSprite("pivot", 4)
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
        elif self.frame == self.lastFrame:
            if actor.bufferContains('jump',8):
                actor.doJump()
            else: actor.doIdle()
        if actor.grounded == False: actor.doFall()
        baseActions.Stop.update(self, actor)
        
class HitStun(baseActions.HitStun):
    def __init__(self,hitstun,direction):
        baseActions.HitStun.__init__(self, hitstun, direction)
        
    def update(self,actor):
        baseActions.HitStun.update(self, actor)
        
        if self.frame == 1:
            if actor.grounded:
                actor.changeSprite("land",1)
            else:
                actor.changeSprite("jump")
             
class Jump(baseActions.Jump):
    def __init__(self):
        baseActions.Jump.__init__(self,9,8)
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",0)
        elif self.frame == 2:
            actor.changeSpriteImage(1)
        elif self.frame == 4:
            actor.changeSpriteImage(2)
        elif self.frame == 6:
            actor.changeSpriteImage(3)
        elif self.frame == 8:
            actor.changeSprite("jump")
        elif self.frame == self.lastFrame:
            actor.doFall()
        baseActions.Jump.update(self, actor)
        

class AirJump(baseActions.AirJump):
    def __init__(self):
        baseActions.AirJump.__init__(self,10,4)
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("airjump",0)
        elif self.frame == 2:
            actor.changeSpriteImage(1)
        elif self.frame == 4:
            actor.changeSpriteImage(2)
        elif self.frame == 6:
            actor.changeSpriteImage(3)
        elif self.frame == 8:
            actor.changeSpriteImage(4)
        elif self.frame == self.lastFrame:
            actor.doFall()
        baseActions.AirJump.update(self, actor)
            
class Fall(baseActions.Fall):
    def __init__(self):
        baseActions.Fall.__init__(self)
        
    def update(self,actor):
        actor.changeSprite("jump")
        baseActions.Fall.update(self, actor)
            
class Land(baseActions.Land):
    def __init__(self):
        baseActions.Land.__init__(self)
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("land",0)
        else:
            if self.frame < 12:
                if self.frame % 3 == 0:
                    actor.changeSpriteImage(self.frame / 3)
        
        baseActions.Land.update(self, actor)

class Trip(baseActions.Trip):
    def __init__(self, length, direction):
        baseActions.Trip.__init__(self, length, direction)

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
                actor.changeSprite("land", 3-self.frame/3)
        baseActions.Getup.update(self, actor)

class PreShield(baseActions.PreShield):
    def __init__(self):
        baseActions.PreShield.__init__(self)

    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("jump")
        baseActions.PreShield.update(self, actor)
        
class Shield(baseActions.Shield):
    def __init__(self):
        baseActions.Shield.__init__(self)
    
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

    def tearDown(self, actor, newAction):
        actor.mask = None

    def update(self, actor):
        if self.frame == 0:
            actor.createMask([255, 0, 255], 999, True, 8)
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

class TechDodge(baseActions.TechDodge):
    def __init__(self):
        baseActions.TechDodge.__init__(self)

    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("nair",0)
        elif self.frame == self.startInvulnFrame:
            actor.changeSpriteImage(-round(abs(actor.change_x)))
        elif self.frame == self.endInvulnFrame:
            actor.changeSpriteImage(0)
        baseActions.TechDodge.update(self, actor)

class Trapped(baseActions.Trapped):
    def __init__(self, length):
        baseActions.Trapped.__init__(self, length)

    def update(self, actor):
        actor.changeSprite("idle")
        baseActions.Trapped.update(self, actor)

class Grabbed(baseActions.Grabbed):
    def __init__(self,height):
        baseActions.Grabbed.__init__(self, height)

    def setUp(self, actor):
        if (self.height > 65):
            self.rect.y += self.height-65

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
        baseActions.Release.update(self, actor)

class LedgeGrab(baseActions.LedgeGrab):
    def __init__(self,ledge):
        baseActions.LedgeGrab.__init__(self, ledge)
        self.sweetSpotLocation = [64,64]
        
    def update(self,actor):
        actor.changeSprite('jump')
        if self.ledge.side == 'left':
            if actor.facing == -1:
                actor.flip()
            actor.hurtbox.rect.topright = self.ledge.rect.midtop
            actor.rect.center = actor.hurtbox.rect.center
        else:
            if actor.facing == 1:
                actor.flip()
            actor.hurtbox.rect.topleft = self.ledge.rect.midtop
            actor.rect.center = actor.hurtbox.rect.center
        baseActions.LedgeGrab.update(self, actor)

class LedgeGetup(baseActions.LedgeGetup):
    def __init__(self):
        baseActions.LedgeGetup.__init__(self)

    def setUp(self,actor):
        baseActions.LedgeGetup.setUp(self,actor)

    def tearDown(self,actor,other):
        actor.change_x = 0

    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("getup",0)
            actor.rect.y -= 92
        if (self.frame >= 0) & (self.frame <= 6):
            actor.changeSpriteImage(self.frame)
            actor.change_y = -1
            actor.change_x = 0
        if (self.frame >= 8) & (self.frame <= 14):
            actor.change_y = 0
            actor.change_x = 11.5*actor.facing
            if (self.frame % 2 == 0):
                actor.changeSpriteImage(self.frame/2+4)
        if (self.frame > 15):
            if (self.frame % 3 == 2):
                actor.changeSpriteImage(self.frame/3+6)
            actor.change_x = actor.var['maxGroundSpeed']*actor.facing
        baseActions.LedgeGetup.update(self, actor)

########################################################
#             BEGIN HELPER METHODS                     #
########################################################
