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
        self.hitbox = hitbox.DamageHitbox(self.rect.center, [12,12], self.owner, 4, 0, 0, 90, 1, 4)  
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
        self.rect.x += 12 * self.direction
        self.rect.y += self.change_y
        self.change_y += 0.5
        self.hitbox.rect.center = self.rect.center
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
        if actor.bufferContains('down'):
            if actor.change_y >= 0:
                actor.change_y = actor.var['maxFallSpeed']
        baseActions.airControl(actor)
        
    def tearDown(self, actor, new):
        pass
               
    def update(self, actor):
        actor.landingLag = 35
        actor.changeSpriteImage(math.floor(self.frame/4))
        if self.frame == 24:
            self.projectile.rect.center = (actor.sprite.boundingRect.centerx + (24 * actor.facing),actor.sprite.boundingRect.centery-8)
            actor.articles.add(self.projectile)
            actor.active_hitboxes.add(self.projectile.hitbox)
            print actor.active_hitboxes
            if actor.inputBuffer.contains('special', 10):
                actor.changeAction(NeutralAirSpecial())
            
        if self.frame == self.lastFrame:
            actor.landingLag = 20
            actor.changeAction(Fall())
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
                self.frame = 0
                
    # Here's an example of creating an anonymous hitbox class.
    # This one calculates its trajectory based off of the angle between the two fighters.
    # Since this hitbox if specifically for this attack, we can hard code in the values.
    class outwardHitbox(hitbox.DamageHitbox):
        def __init__(self,actor):
            hitbox.DamageHitbox.__init__(self, [0,0], [80,80], actor, 2, 8, 0.02, 0, 1, 0)
            
        def onCollision(self,other):
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
        actor.setSpeed(actor.change_x, actor.facing)
        actor.changeSprite("nair")

        self.upperHitbox = hitbox.DamageHitbox([10,-30],[60,30],actor,2,12,0,0,1,101,0)
        self.lowerHitbox = hitbox.DamageHitbox([10,30],[60,30],actor,2,12,0,0,1,101,0)

    def tearDown(self,actor,other):
        self.upperHitbox.kill()
        self.lowerHitbox.kill()
        actor.setSpeed(0, actor.facing)

    def update(self,actor):
        if self.frame%2 == 0 and self.frame <= 8:
            actor.changeSpriteImage(self.frame/2)
        elif self.frame <= 24:
            actor.changeSpriteImage((self.frame-4)%16)
        elif self.frame%2 == 0:
            actor.changeSpriteImage((self.frame/2-8)%16)

        self.upperHitbox.rect.center = [actor.rect.center[0], actor.rect.center[1]-30]
        self.lowerHitbox.rect.center = [actor.rect.center[0], actor.rect.center[1]+30]

        if self.frame == 8:
            actor.active_hitboxes.add(self.upperHitbox)
            actor.active_hitboxes.add(self.lowerHitbox)
        if self.frame == 12:
            self.upperHitbox.hitbox_id = 102
            self.lowerHitbox.hitbox_id = 102
        if self.frame == 16:
            self.upperHitbox.hitbox_id = 103
            self.lowerHitbox.hitbox_id = 103
        if self.frame == 20:
            self.upperHitbox.baseKnockback = 10
            self.lowerHitbox.baseKnockback = 10
            self.upperHitbox.knockbackGrowth = 0.09
            self.lowerHitbox.knockbackGrowth = 0.09
            self.upperHitbox.trajectory = actor.getForwardWithOffset(20)
            self.lowerHitbox.trajectory = actor.getForwardWithOffset(20)
            self.upperHitbox.weight_influence = 1
            self.lowerHitbox.weight_influence = 1
            self.upperHitbox.hitbox_id = 104
            self.lowerHitbox.hitbox_id = 104
        if self.frame == 24:
            self.upperHitbox.kill()
            self.lowerHitbox.kill()

        if self.frame == self.lastFrame:
            actor.setSpeed(0, actor.facing)
            actor.doIdle()
        self.frame += 1
            

        
class DownAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self, 34)
    
    def setUp(self, actor):
        actor.change_x = 0
        actor.preferred_xspeed = 0
        actor.changeSprite("dsmash",0)
        self.dsmashHitbox1 = hitbox.DamageHitbox([34,26],[24,52],actor,12,8,0.075,20,1,2)
        self.dsmashHitbox2 = hitbox.DamageHitbox([-34,26],[24,52],actor,12,8,0.075,160,1,2)
    
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
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,8,2.0,0.3,40,1,0)
            
    def update(self,actor):
        actor.change_y = 0
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
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,12,0.8,.35,40,1,0)
            
    def update(self,actor):
        actor.change_y = 0
        
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
        
        def stateTransitions(self,actor):
            if self.frame > 36:
                baseActions.neutralState(actor)    

class NeutralAir(action.Action):
    def __init__(self):
        action.Action.__init__(self, 34)
    
    def setUp(self, actor):
        actor.change_x = 0
        actor.preferred_xsped = 0
        actor.changeSprite("nair",0)
        self.subImage = 0
        self.nairHitbox = hitbox.DamageHitbox([0,0],[72,72],actor,10,4,0.06,361,1,0)
    
    def stateTransitions(self, actor):
        if actor.bufferContains('down'):
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
            self.nairHitbox.rect.center = actor.rect.center
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

class GroundGrab(action.Action):
    def __init__(self):
        action.Action.__init__(self, 35)

    def setUp(self, actor):
        self.grabHitbox = hitbox.GrabHitbox([40,0], [40,40], actor, 0, 30)

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

class Pummel(action.Action):
    def __init__(self):
        action.Action.__init__(self,22)

    def update(self, actor):
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
        
class Throw(action.Action):
    def __init__(self):
        action.Action.__init__(self,28)

    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[120,40],actor,10,20.0,0.20,40,1,0)

    def tearDown(self, actor, other):
        self.fSmashHitbox.kill()

    def update(self, actor): 
        actor.change_y = 0
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
            actor.current_action = Fall()
        baseActions.Move.update(self, actor)
        if (self.frame == self.lastFrame):
            self.frame = 12
        
class Run(baseActions.Run):
    def __init__(self,accel = True):
        baseActions.Run.__init__(self,15)
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
            actor.current_action = Fall()
        baseActions.Run.update(self, actor)
        if (self.frame == self.lastFrame):
            self.frame = 12
                   
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
        if actor.grounded == False: actor.current_action = Fall()

class Grabbing(baseActions.Grabbing):
    def __init__(self):
        baseActions.Grabbing.__init__(self,1)

    def update(self, actor):
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
            if actor.inputBuffer.contains('jump',5):
                actor.current_action = Jump()
            else: actor.current_action = NeutralAction()
        if actor.grounded == False: actor.current_action = Fall()
        baseActions.Stop.update(self, actor)
        
class HitStun(baseActions.HitStun):
    def __init__(self,hitstun,direction):
        baseActions.HitStun.__init__(self, hitstun, direction)
        
    def update(self,actor):          
        if self.frame == self.lastFrame:
            actor.current_action = Fall()
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
            actor.current_action = Fall()
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
            actor.current_action = Fall()
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
        
class Shield(baseActions.Shield):
    def __init__(self):
        baseActions.Shield.__init__(self)
    
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("jump")
        baseActions.Shield.update(self, actor)
        
class ShieldBreak(baseActions.ShieldBreak):
    def __init__(self):
        baseActions.ShieldBreak.__init__(self)
    
    def tearDown(self,actor,newAction):
        actor.mask = None
        
        
    def update(self,actor):
        if self.frame == 0:
            actor.createMask([255,0,255],999,True,8)
        baseActions.ShieldBreak.update(self, actor)
        
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

class Grabbed(baseActions.Grabbed):
    def __init__(self,height):
        baseActions.Grabbed.__init__(self, height)

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
