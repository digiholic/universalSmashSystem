import engine.action as action
import engine.baseActions as baseActions
import engine.hitbox as hitbox
import engine.abstractFighter as abstractFighter


class NeutralAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self,22)
    
    def setUp(self, actor):
        actor.change_x = 0
        actor.preferred_xsped = 0
        actor.changeSprite("neutral",0)
        self.jabHitbox = self.outwardHitbox(actor)
    
    # Here's an example of creating an anonymous hitbox class.
    # This one calculates its trajectory based off of the angle between the two fighters.
    # Since this hitbox if specifically for this attack, we can hard code in the values.
    class outwardHitbox(hitbox.DamageHitbox):
        def __init__(self,actor):
            hitbox.DamageHitbox.__init__(self, [0,0], [80,80], actor, 2, 8, 0.2, 0, 20, 0)
            
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
        
class DownAttack(action.Action):
    def __init__(self):
        action.Action.__init__(self, 34)
    
    def setUp(self, actor):
        actor.change_x = 0
        actor.preferred_xsped = 0
        actor.changeSprite("dsmash",0)
        self.dsmashHitbox1 = hitbox.DamageHitbox([34,26],[24,52],actor,
                 12,8,0.75,20,60,1)
        self.dsmashHitbox2 = hitbox.DamageHitbox([-34,26],[24,52],actor,
                 12,8,0.75,160,60,1)
    
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
        action.Action.__init__(self, 42)
    
    def setUp(self,actor):
        self.fSmashHitbox = hitbox.DamageHitbox([20,0],[60,40],actor,12,1,1.0,40,60,0)
            
    def update(self,actor):
        if self.frame == 0:
            actor.change_x = 0
            actor.preferred_xspeed = 0
            actor.changeSprite("fsmash",0)
        elif self.frame == 3:
            actor.createMask([255,255,0],15,True,32)
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
        self.nairHitbox = hitbox.DamageHitbox([0,0],[72,72],actor,10,4,0.6,60,60,0)
        #self.dsmashSweetspot
    
    def stateTransitions(self, actor):
        if actor.bufferContains(actor.keyBindings.k_down):
            if actor.change_y >= 0:
                actor.change_y = actor.var['maxFallSpeed']
        baseActions.airControl(actor)
    
    def tearDown(self,actor,other):
        self.nairHitbox.kill()
    
    def update(self,actor):
        actor.landingLag = 28
        if self.frame % 2 == 0:
            actor.changeSpriteImage(self.subImage % 7)
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
            actor.changeSprite("fall")
            
        if self.frame == self.lastFrame:
            actor.current_action = Fall()
        baseActions.HitStun.update(self, actor)
             
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
            actor.changeSpriteImage(1)
        elif self.frame == self.endInvulnFrame:
            actor.changeSpriteImage(0)
        baseActions.AirDodge.update(self, actor)
        
########################################################
#             BEGIN HELPER METHODS                     #
########################################################