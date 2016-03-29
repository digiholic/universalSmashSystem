import engine.action as action
import engine.baseActions as baseActions
import engine.hitbox as hitbox
import engine.article as article
import engine.abstractFighter as abstractFighter
import math

import settingsManager #TEMPORARY until I figure out article sprites

class SplatArticle(article.AnimatedArticle):
    def __init__(self, owner, origin, direction):
        article.AnimatedArticle.__init__(self, owner.article_path+'/hitboxie_projectile.png', owner, origin, imageWidth=16,length=120)
        self.direction = direction
        self.change_x = self.direction*24
        self.change_y = 0
        self.hitbox = hitbox.DamageHitbox(self.rect.center, [12,12], self.owner, 6, 2, 0, 0, 1, hitbox.HitboxLock(), 1, 1, -1, 0)  
        self.hitbox.article = self
            
    # Override the onCollision of the hitbox
    def onCollision(self, other):
        othersClasses = list(map(lambda x :x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]
        if 'AbstractFighter' in othersClasses or 'Platform' in othersClasses:
            self.hitbox.kill()
            self.kill()
        #TODO check for verticality of platform landing
            
    def update(self):
        self.rect.x += self.change_x
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
        actor.preferred_xspeed = 0
        actor.changeSprite("nspecial",0)
        
    def tearDown(self, actor, new):
        pass
    
    def stateTransitions(self, actor):
        pass
               
    def update(self, actor):
        actor.changeSpriteImage(math.floor(self.frame//4))
        if self.frame == 24:
            self.projectile.rect.center = (actor.sprite.boundingRect.centerx + (24 * actor.facing),actor.sprite.boundingRect.centery-8)
            actor.articles.add(self.projectile)
            actor.active_hitboxes.add(self.projectile.hitbox)
            print(actor.active_hitboxes)
            
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
        actor.landingLag = 16
        actor.changeSpriteImage(math.floor(self.frame//4))
        if self.frame == 24:
            self.projectile.rect.center = (actor.sprite.boundingRect.centerx + (24 * actor.facing),actor.sprite.boundingRect.centery-8)
            actor.articles.add(self.projectile)
            actor.active_hitboxes.add(self.projectile.hitbox)
            print(actor.active_hitboxes)
            if actor.bufferContains('special', 8):
                actor.changeAction(NeutralAirSpecial())
            
        if self.frame == self.lastFrame:
            actor.landingLag = 8
            actor.changeAction(Fall())
        self.frame += 1

"""
@ai-move-forward
@ai-move-stop
@ai-move-up
"""
class ForwardSpecial(action.Action):
    def __init__(self):
        action.Action.__init__(self, 64)
        self.spriteImage = 0

    def setUp(self, actor):
        actor.change_x = 0
        actor.preferred_xspeed = 0
        actor.flinch_knockback_threshold = 4
        actor.changeSprite("nair",0)
        self.chainHitbox = hitbox.AutolinkHitbox([0,0], [80,80], actor, 2, 1, hitbox.HitboxLock(), 1, 1, -1, -7)
        self.flingHitbox = self.sideSpecialHitbox(actor)
        self.numFrames = 0
    
    def onClank(self,actor):
        if actor.grounded:
            actor.landingLag = 15
            actor.doLand()
        else:
            actor.landingLag = 15
            actor.doFall()
    
    class sideSpecialHitbox(hitbox.DamageHitbox):
        def __init__(self,actor):
            hitbox.DamageHitbox.__init__(self, [0,0], [80,80], actor, 5, 2, .2, 300, 1, hitbox.HitboxLock(), 1, 6, 0, 0)

        def onCollision(self, other):
            hitbox.Hitbox.onCollision(self, other)
            if 'AbstractFighter' in list(map(lambda x:x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]:
                if other.lockHitbox(self):
                    if other.shield:
                        other.shieldDamage(math.floor(self.damage*self.shield_multiplier))
                    elif other.grounded:
                        other.dealDamage(self.damage)
                        (actorDirect,_) = self.owner.getDirectionMagnitude()
                        other.doTrip(35, other.getForwardWithOffset(actorDirect))
                    else:
                        other.applyKnockback(self.damage, self.baseKnockback, self.knockbackGrowth, self.trajectory, self.weight_influence, self.hitstun)
                            
    def stateTransitions(self, actor):
        if actor.change_x//actor.facing <= 0 and self.frame >= 8:
            baseActions.grabLedges(actor)

    def tearDown(self, actor, newAction):
        self.chainHitbox.kill()
        self.flingHitbox.kill()
        actor.flinch_knockback_threshold = 0
        self.preferred_xspeed = 0

    def update(self, actor):
        actor.changeSpriteImage(self.spriteImage%16)
        if self.frame <= self.lastFrame-2:
            self.spriteImage += 1
            if self.frame <= 1:
                actor.preferred_xspeed = 0
                actor.change_x = 0
                actor.preferred_yspeed = 2
                if actor.keysContain('shield'):
                    actor.doShield()
                elif actor.keysContain('special') and self.lastFrame < 240:
                    self.lastFrame += 1
                    self.frame -= 1
            else: #Actually launch forwards
                actor.preferred_yspeed = actor.var['maxFallSpeed']
                self.numFrames += 1
                self.chainHitbox.update()
                actor.active_hitboxes.add(self.chainHitbox)
                (key, invkey) = actor.getForwardBackwardKeys()
                if self.frame == 2:
                    actor.setSpeed(actor.var['runSpeed'], actor.getForwardWithOffset(0))
                    actor.change_y = -8
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
                self.flingHitbox.damage += int(float(self.numFrames)/float(16))
                self.flingHitbox.priority += int(float(self.numFrames)/float(16))
                self.flingHitbox.baseKnockback += float(self.numFrames)/float(16)
                self.flingHitbox.update()
                actor.active_hitboxes.add(self.flingHitbox)
            else:
                self.flingHitbox.kill()
            self.chainHitbox.kill()
            if self.frame >= self.lastFrame:
                if actor.grounded:
                    actor.landingLag = 15
                    actor.doLand()
                else:
                    actor.landingLag = 15
                    actor.doFall()

        self.frame += 1
           
class NeutralAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,17)
    
    def setUp(self, actor):
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
        if self.frame < 4:
            actor.changeSpriteImage(self.frame)
        elif self.frame == 4:
            actor.active_hitboxes.add(self.jabHitbox)
        elif self.frame >= 5 and self.frame <= 8:
            actor.changeSpriteImage(9)
        elif self.frame > 8:
            self.jabHitbox.kill()
            if not (self.frame) > 13:
                actor.changeSpriteImage(self.frame + 1)
        if self.frame == self.lastFrame:
            actor.doIdle()
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

    def tearDown(self, actor, newAction):
        self.sweetHitbox.kill()
        self.tangyHitbox.kill()
        self.sourHitbox.kill()

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
            self.sweetHitbox.kill()
            actor.active_hitboxes.add(self.sourHitbox)
        elif self.frame == 12:
            self.tangyHitbox.kill()
        elif self.frame == 16:
            self.sourHitbox.kill()
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1

class UpSmash(action.Action):
    def __init__(self):
        action.Action.__init__(self, 48)
        self.chargeLevel = 0
        
    def setUp(self,actor):
        self.popupHBox = hitbox.DamageHitbox([0,0],[100,100],actor,0,20,0,90,0,hitbox.HitboxLock())
        self.weakHBoxL = hitbox.DamageHitbox([0,-80],[80,80],actor,2,5,0,150,0,hitbox.HitboxLock())
        self.weakHBoxR = hitbox.DamageHitbox([0,-80],[80,80],actor,2,5,0,30,0,hitbox.HitboxLock())
        self.uSmashHitbox = hitbox.DamageHitbox([0,-80],[120,120],actor,8,2.0,.25,80,1,hitbox.HitboxLock())
    
    def tearDown(self, actor, newAction):
        self.uSmashHitbox.kill()
        
    def update(self,actor):
        if self.frame >= 3 and self.frame <= 11 and not actor.keysContain('attack') and self.chargeLevel > 0:
            self.frame = 12
            actor.mask = None
            
        if self.frame == 0:
            actor.preferred_xspeed = 0
            actor.changeSprite("usmash",0)
        elif self.frame == 3:
            actor.changeSpriteImage(1)
        elif self.frame == 6:
            if actor.keysContain('attack') and self.chargeLevel == 0:
                actor.createMask([255,255,0],72,True,32)
            actor.changeSpriteImage(2)
        elif self.frame == 9:
            actor.changeSpriteImage(3)
        elif self.frame == 12:
            if actor.keysContain('attack') and self.chargeLevel <= 5:
                print("charging...")
                self.chargeLevel += 1
                self.uSmashHitbox.damage += 1
                if self.chargeLevel % 3 == 0:
                    self.weakHBoxL.damage += 1
                    self.weakHBoxR.damage += 1
                self.uSmashHitbox.baseKnockback += 0.2
                self.frame = 6
        elif self.frame == 15:
            actor.changeSpriteImage(4)
        elif self.frame == 18:
            actor.mask = None
            actor.changeSpriteImage(5)
            actor.active_hitboxes.add(self.popupHBox)
        elif self.frame == 21:
            actor.changeSpriteImage(6)
            self.popupHBox.kill()
            actor.active_hitboxes.add(self.weakHBoxL)
        elif self.frame == 24:
            actor.changeSpriteImage(7)
            self.weakHBoxL.kill()
            actor.active_hitboxes.add(self.weakHBoxR)
        elif self.frame == 27:
            actor.changeSpriteImage(8)
            self.weakHBoxR.kill()
            actor.active_hitboxes.add(self.weakHBoxL)
        elif self.frame == 30:
            actor.changeSpriteImage(9)
            self.weakHBoxL.kill()
            actor.active_hitboxes.add(self.weakHBoxR)
        elif self.frame == 33:
            actor.changeSpriteImage(10)
            self.weakHBoxR.kill()
            actor.active_hitboxes.add(self.uSmashHitbox)
        elif self.frame == self.lastFrame:
            self.uSmashHitbox.kill()
            actor.doIdle()
        
        self.frame += 1 
       
"""
@ai-move-forward
""" 
class DashAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,32)

    def setUp(self, actor):
        actor.preferred_xspeed = actor.change_x
        actor.changeSprite("nair")

        self.dashHitbox = hitbox.DamageHitbox([0,0],[70,70],actor,2,8,0.2,20,1,hitbox.HitboxLock())
        self.chainHitbox = hitbox.AutolinkHitbox([0,0],[70,70],actor,2,1,hitbox.HitboxLock(),1,1.5)

    def tearDown(self,actor,other):
        self.dashHitbox.kill()
        self.chainHitbox.kill()
        actor.preferred_xspeed = 0

    def update(self,actor):
        if self.frame%2 == 0 and self.frame <= 8:
            actor.changeSpriteImage(self.frame//2)
        elif self.frame <= 24:
            actor.changeSpriteImage((self.frame-4)%16)
        elif self.frame%2 == 0:
            actor.changeSpriteImage((self.frame//2-8)%16)

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
            actor.preferred_xspeed = 0

        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1
        
class DownAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self, 34)
    
    def setUp(self, actor):
        actor.preferred_xspeed = 0
        actor.changeSprite("dtilt",0)
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

class DownSmash(action.Action):
    def __init__(self):
        action.Action.__init__(self, 54)
        self.chargeLevel = 0

    def setUp(self, actor):
        actor.preferred_xspeed = 0
        actor.changeSprite("dsmash", 0)
        hitbox_lock = hitbox.HitboxLock()
        self.spikeBox1 = hitbox.DamageHitbox([0, 26], [90, 40], actor, 2, 4, 0, 270, 1, hitbox.HitboxLock())
        self.spikeBox2 = hitbox.DamageHitbox([0, 26], [90, 40], actor, 2, 4, 0, 270, 1, hitbox.HitboxLock())
        self.dsmashHitbox1 = hitbox.DamageHitbox([23,26],[46,40],actor,8,8,0.3,20,1,hitbox_lock)
        self.dsmashHitbox2 = hitbox.DamageHitbox([-23,26],[46,40],actor,8,8,0.3,160,1,hitbox_lock)

    def tearDown(self, actor, nextAction):
        self.spikeBox1.kill()
        self.spikeBox2.kill()
        self.dsmashHitbox1.kill()
        self.dsmashHitbox2.kill()

    def update(self, actor):
        if self.frame <= 6 and not actor.keysContain('attack'):
            self.frame = 7
            actor.mask = None
        if self.frame == 0: 
            if actor.keysContain('attack') and self.chargeLevel == 0:
                actor.createMask([255,255,0],72,True,32)
            actor.changeSpriteImage(0)
        elif self.frame == 6:
            actor.changeSpriteImage(0)
            if actor.keysContain('attack') and self.chargeLevel <= 5:
                print("charging...")
                self.chargeLevel += 1
                self.dsmashHitbox1.damage += 1
                self.dsmashHitbox2.damage += 1
                self.frame = 0
        elif self.frame > 6 and self.frame < self.lastFrame:
            actor.changeSpriteImage((self.frame//2-3)%6)
            if self.frame == 14:
                actor.active_hitboxes.add(self.spikeBox1)
            elif self.frame == 18:
                self.spikeBox1.kill()
            elif self.frame == 26:
                actor.active_hitboxes.add(self.spikeBox2)
            elif self.frame == 30:
                self.spikeBox2.kill()
            elif self.frame == 38:
                actor.active_hitboxes.add(self.dsmashHitbox1)
                actor.active_hitboxes.add(self.dsmashHitbox2)
            elif self.frame == 42:
                self.dsmashHitbox1.kill()
                self.dsmashHitbox2.kill()
        elif self.frame == self.lastFrame:
            actor.doIdle()
        
        self.frame += 1 
        
class ForwardAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)

    def tearDown(self,actor,nextAction):
        self.fSmashHitbox.kill()
    
    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,8,2.0,0.3,40,1,hitbox.HitboxLock())
            
    def update(self,actor):
        if self.frame == 0:
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

class ForwardSmash(action.Action):
    def __init__(self):
        action.Action.__init__(self, 42)
        self.chargeLevel = 0
        
    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,12,0.8,.35,40,1,hitbox.HitboxLock())

    def tearDown(self,actor,nextAction):
        self.fSmashHitbox.kill()
            
    def update(self,actor):
        if self.frame >= 3 and self.frame <= 8 and not actor.keysContain('attack') and self.chargeLevel > 0:
            self.frame = 9
            actor.mask = None
            
        if self.frame == 0:
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

"""
@ai-move-down
@ai-move-forward
@ai-move-backward
"""
class NeutralAir(action.Action):
    def __init__(self):
        action.Action.__init__(self, 34)
    
    def setUp(self, actor):
        actor.preferred_xspeed = 0
        actor.changeSprite("nair",0)
        self.subImage = 0
        self.nairHitbox = hitbox.SakuraiAngleHitbox([0,0],[72,72],actor,10,4,0.06,40,1,hitbox.HitboxLock(),1,1,1,0)
    
    def stateTransitions(self, actor):
        if actor.keysContain('down'):
            if actor.change_y >= 0:
                actor.change_y = max(math.floor(actor.var['maxFallSpeed'] / 2), actor.change_y)
        baseActions.airControl(actor)
    
    def tearDown(self,actor,other):
        self.nairHitbox.kill()
    
    def update(self,actor):
        actor.landingLag = 20
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
            actor.landingLag = 12
            actor.changeAction(Fall())
        self.frame += 1

"""
@ai-move-down
@ai-move-stop
@ai-move-forward
@ai-move-backward
"""
class DownAir(action.Action):
    def __init__(self):
        action.Action.__init__(self,30)
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
        actor.rect.y += self.bottom
        self.downHitbox.kill()
        self.leftDiagonalHitbox.kill()
        self.rightDiagonalHitbox.kill()
        self.leftSourSpot.kill()
        self.rightSourSpot.kill()
        
    def update(self, actor):
        actor.landingLag = 26
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
            actor.landingLag = 16
            actor.changeAction(Fall())
        self.frame += 1
"""
@ai-move-forward
@ai-move-backward
@ai-move-down
"""
class UpAir(action.Action):
    def __init__(self):
        action.Action.__init__(self, 28)
        
    def setUp(self, actor):
        sharedLock = hitbox.HitboxLock()
        self.sourspot = hitbox.DamageHitbox([0,18],[60,47], actor, 6, 8, 0.05, 60, 1, sharedLock, 1, 1, 1, 0)
        self.semisweet = hitbox.DamageHitbox([0,-21],[30,32], actor, 8, 6, 0.1, 75, 1, sharedLock, 1, 1, 1, 0)
        self.sweetspot = hitbox.DamageHitbox([0,-21],[30,32], actor, 12, 6, 0.2, 90, 1, sharedLock, 1, 1, 1, 0)
    
    def stateTransitions(self, actor):
        baseActions.airControl(actor)
        
    def tearDown(self, actor, newAction):
        self.sourspot.kill()
        self.semisweet.kill()
        self.sweetspot.kill()
    
    def update(self, actor):
        actor.landingLag = 22
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
            actor.changeSpriteImage(4)
            self.sourspot.kill()
        elif self.frame == self.lastFrame:
            actor.doFall()
        self.frame += 1

class GroundGrab(action.Action):
    def __init__(self):
        action.Action.__init__(self, 36)

    def setUp(self, actor):
        self.grabHitbox = hitbox.GrabHitbox([30,0], [30,30], actor, hitbox.HitboxLock(), 30)

    def tearDown(self, actor, other):
        self.grabHitbox.kill()

    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("pivot", 0)
        elif self.frame == 3:
            actor.changeSpriteImage(1)
        elif self.frame == 6:
            actor.changeSpriteImage(2)
        elif self.frame == 9:
            actor.changeSpriteImage(3)
            actor.active_hitboxes.add(self.grabHitbox)
        elif self.frame == 12:
            actor.changeSpriteImage(4)
        elif self.frame == 15:
            actor.changeSpriteImage(3)
            self.grabHitbox.kill()
        elif self.frame == 20:
            actor.changeSpriteImage(2)
        elif self.frame == 25:
            actor.changeSpriteImage(1)
        elif self.frame == 30:
            actor.changeSpriteImage(0)
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1

class Pummel(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self,17)

    def update(self, actor):
        baseActions.BaseGrabbing.update(self, actor)
        if self.frame == 0:
            actor.changeSprite("neutral", self.frame)
        elif self.frame < 4:
            actor.changeSpriteImage(self.frame)
        elif actor.isGrabbing() and self.frame == 4:
            actor.grabbing.dealDamage(2)
        elif self.frame >= 5 and self.frame <= 8:
            actor.changeSpriteImage(9)
        elif self.frame > 8:
            if not (self.frame) > 13:
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
        self.bottomHitbox.update()
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

"""
@ai-move-up
"""
class UpThrow(baseActions.BaseGrabbing):
    def __init__(self):
        baseActions.BaseGrabbing.__init__(self, 100)

    def setUp(self, actor):
        actor.changeSprite("land")

    def tearDown(self, actor, nextAction):
        baseActions.BaseGrabbing.tearDown(self, actor, nextAction)

    def update(self, actor):
        baseActions.BaseGrabbing.update(self, actor)
        if self.frame < 8:
            actor.changeSpriteImage(self.frame/2+1)
        elif self.frame == 8:
            actor.change_y -= 45
            actor.landingLag = 12
        else:
            actor.change_y += 2
            if actor.change_y > actor.var['maxFallSpeed']:
                actor.change_y = actor.var['maxFallSpeed']
            if actor.grounded:
                if actor.isGrabbing():
                    actor.grabbing.applyKnockback(9, 12, 0.15, actor.getForwardWithOffset(70))
                actor.doLand()
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
            actor.grabbing.applyKnockback(7, 10, 0.1, actor.getForwardWithOffset(180), 0.5)
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
        elif self.frame == 10:
            actor.changeSpriteImage(5)
        elif self.frame == 12:
            actor.changeSpriteImage(6)
        elif self.frame == 14:
            actor.changeSpriteImage(7)
        elif self.frame == 16:
            actor.changeSpriteImage(8)
        elif self.frame == self.lastFrame: 
            actor.flip()
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

"""
@ai-move-stop
"""
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
        elif self.frame == self.lastFrame:
            if actor.bufferContains('jump',8):
                actor.doJump()
            else: actor.doIdle()
        baseActions.Stop.update(self, actor)

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

class CrouchGetup(baseActions.CrouchGetup):
    def __init__(self):
        baseActions.CrouchGetup.__init__(self, 9)

    def setUp(self, actor):
        actor.changeSprite('land', 2)

    def update(self, actor):
        actor.changeSpriteImage(3-self.frame/3)
        baseActions.CrouchGetup.update(self, actor)
        
class HitStun(baseActions.HitStun):
    def __init__(self,hitstun,direction,hitstop):
        baseActions.HitStun.__init__(self, hitstun, direction,hitstop)
    
    def update(self, actor):
        baseActions.HitStun.update(self, actor)
        if self.frame == 1:
            if actor.grounded:
                actor.changeSprite("land",1)
            else:
                actor.changeSprite("jump")
        
class TryTech(baseActions.TryTech):
    def __init__(self,hitstun,direction,hitstop):
        baseActions.TryTech.__init__(self, hitstun, direction, hitstop)

    def update(self,actor):
        baseActions.TryTech.update(self, actor)
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

class Helpless(baseActions.Helpless):
    def __init__(self):
        baseActions.Helpless.__init__(self)

    def tearDown(self, actor, newAction):
        actor.mask = None

    def update(self, actor):
        if self.frame == 0:
            actor.createMask([191, 63, 191], 99999, True, 8)
        actor.changeSprite("jump")
        baseActions.Helpless.update(self, actor)
            
class Land(baseActions.Land):
    def __init__(self):
        baseActions.Land.__init__(self)
        
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

class PlatformDrop(baseActions.PlatformDrop):
    def __init__(self):
        baseActions.PlatformDrop.__init__(self, 12)
    
    def stateTransitions(self, actor):
        if self.frame > 5:
            baseActions.airControl(actor)
        
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
        if (self.frame >= 0) & (self.frame <= 6):
            actor.changeSpriteImage(self.frame)
            if self.frame > 2:
                actor.change_y = -20
            actor.change_x = 0
        if (self.frame >= 8) & (self.frame <= 14):
            actor.change_y = 0
            actor.change_x = 11.5*actor.facing
            if (self.frame % 2 == 0):
                actor.changeSpriteImage(self.frame//2+4)
        if (self.frame > 15):
            if (self.frame % 3 == 2):
                actor.changeSpriteImage(self.frame//3+6)
            actor.change_x = actor.var['maxGroundSpeed']*actor.facing
        baseActions.LedgeGetup.update(self, actor)

########################################################
#             BEGIN HELPER METHODS                     #
########################################################
