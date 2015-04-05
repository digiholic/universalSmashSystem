import engine.action as action
import engine.baseActions as baseActions
import engine.hitbox as hitbox
import engine.abstractFighter as abstractFighter
import math

class NeutralAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,22)
    
    def setUp(self, actor):
        actor.change_x = 0
        actor.preferred_xsped = 0
        actor.changeSprite("hitboxie_neutral",0)
        self.jabHitbox = self.outwardHitbox(actor)
    
    # Here's an example of creating an anonymous hitbox class.
    # This one calculates its trajectory based off of the angle between the two fighters.
    # Since this hitbox if specifically for this attack, we can hard code in the values.
    class outwardHitbox(hitbox.DamageHitbox):
        def __init__(self,actor):
            hitbox.Hitbox.__init__(self, [0,0], [80,80], actor, 0)   
            
        def onCollision(self,other):
            other.dealDamage(2)
            angle = abstractFighter.getDirectionBetweenPoints(self.owner.rect.midbottom, other.rect.center)
            
            other.applyKnockback(8, 0.6, angle)
            print other.damage
            self.kill()
         
    def update(self, actor):
        if self.frame < 9:
            actor.changeSpriteImage(self.frame)
        elif self.frame == 9:
            self.hitboxes.add(self.jabHitbox)
        elif self.frame >= 10 and self.frame <= 13:
            actor.changeSpriteImage(9)
            #hitbox
        elif self.frame > 13:
            self.jabHitbox.kill()
            if not (self.frame) > 18:
                actor.changeSpriteImage(self.frame - 4)
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1
        
            
class ForwardAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self, 42)
    
    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[60,40],actor,15,5,1.0,20)
            
    def update(self,actor):
        if self.frame == 0:
            actor.change_x = 0
            actor.preferred_xspeed = 0
            actor.changeSprite("hitboxie_fsmash",0)
        elif self.frame == 3:
            actor.changeSpriteImage(1)
        elif self.frame == 6:
            actor.changeSpriteImage(2)
        elif self.frame == 9:
            actor.changeSpriteImage(3)
        elif self.frame == 12:
            actor.changeSpriteImage(4)
        elif self.frame == 15:
            actor.changeSpriteImage(5)
        elif self.frame == 18:
            actor.changeSpriteImage(6)
        elif self.frame == 21:
            actor.changeSpriteImage(7)
            self.hitboxes.add(self.fSmashHitbox)
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
                actor.changeSprite("hitboxie_run",0)
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
                actor.changeSprite("hitboxie_run",4)
                
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
                actor.changeSprite("hitboxie_run",0)
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
                actor.changeSprite("hitboxie_run",4)
                
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
            actor.changeSprite("hitboxie_pivot",4)
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
            print 'pivot'
            newAction.accel = False
        
class NeutralAction(baseActions.NeutralAction):
    def __init__(self):
        baseActions.NeutralAction.__init__(self,1)
        
    def update(self, actor):
        actor.changeSprite("hitboxie_idle")
        if actor.grounded == False: actor.current_action = Fall()
        
class Stop(baseActions.Stop):
    def __init__(self):
        baseActions.Stop.__init__(self, 9)
    
    def update(self, actor):
        if self.frame == 0:
            actor.changeSprite("hitboxie_pivot",0)
        elif self.frame == 3:
            actor.changeSpriteImage(1)
        elif self.frame == 6:
            actor.changeSpriteImage(2)
        elif self.frame == self.lastFrame:
            if actor.inputBuffer.contains(actor.keyBindings.k_up,5):
                actor.current_action = Jump()
            else: actor.current_action = NeutralAction()
        if actor.grounded == False: actor.current_action = Fall()
        baseActions.Stop.update(self, actor)
        
class HitStun(baseActions.HitStun):
    def __init__(self,hitstun,direction):
        baseActions.HitStun.__init__(self, hitstun, direction)
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("hitboxie_fall")
            
        if self.frame == self.lastFrame:
            actor.current_action = Fall()
        baseActions.HitStun.update(self, actor)
             
class Jump(baseActions.Jump):
    def __init__(self):
        baseActions.Jump.__init__(self,9,8)
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("hitboxie_land",0)
        elif self.frame == 2:
            actor.changeSpriteImage(1)
        elif self.frame == 4:
            actor.changeSpriteImage(2)
        elif self.frame == 6:
            actor.changeSpriteImage(3)
        elif self.frame == 8:
            actor.changeSprite("hitboxie_jump")
        elif self.frame == self.lastFrame:
            actor.current_action = Fall()
        baseActions.Jump.update(self, actor)
        

class AirJump(baseActions.AirJump):
    def __init__(self):
        baseActions.AirJump.__init__(self,10,4)
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("hitboxie_airjump",0)
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
        actor.changeSprite("hitboxie_jump")
        baseActions.Fall.update(self, actor)
            
class Land(baseActions.Land):
    def __init__(self):
        baseActions.Land.__init__(self)
        
    def update(self,actor):
        if self.frame == 0:
            actor.changeSprite("hitboxie_land",0)
        else:
            if self.frame < 12:
                if self.frame % 3 == 0:
                    actor.changeSpriteImage(self.frame / 3)
        
        baseActions.Land.update(self, actor)
            
        
        
########################################################
#             BEGIN HELPER METHODS                     #
########################################################