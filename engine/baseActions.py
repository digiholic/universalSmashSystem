import engine.action as action
import pygame
           
class Move(action.Action):
    def __init__(self,length):
        action.Action.__init__(self,length)
        self.direction = -1
        
    def setUp(self,actor):
        self.direction = actor.getForwardWithOffset(0)
        
    def update(self, actor):
        actor.setSpeed(actor.var['maxGroundSpeed'],self.direction)
        
        self.frame += 1
        if self.frame > self.lastFrame: self.frame = 0
        
    def stateTransitions(self,actor):
        moveState(actor,self.direction)
        
class Run(action.Action):
    def __init__(self,length):
        action.Action.__init__(self,length)
        
    def setUp(self,actor):
        if actor.facing == 1: self.direction = 0
        else: self.direction = 180
            
    def update(self, actor):
        actor.setSpeed(actor.var['maxGroundSpeed']*1.5,self.direction, False)
        
        self.frame += 1
        if self.frame > self.lastFrame: self.frame = 0
    
    def stateTransitions(self,actor):
        moveState(actor,self.direction)
        
class Pivot(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)
        
    def update(self,actor):
        if self.frame != self.lastFrame:
            self.frame += 1
            actor.preferred_xspeed = 0
        if self.frame == self.lastFrame:
            (key, _) = actor.getForwardBackwardKeys()
            if actor.keysContain(key):
                if actor.facing == 1:
                    actor.doGroundMove(0)
                else:
                    actor.doGroundMove(180)
            else:
                actor.doIdle()
            
class Stop(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)
        
    def update(self, actor):
        actor.preferred_xspeed = 0
        self.frame += 1
        
    def stateTransitions(self, actor):
        (key,invkey) = actor.getForwardBackwardKeys()
        if actor.bufferContains(key,12,andReleased=True) and actor.keysContain(key):
            print("run")
            actor.doGroundMove(actor.getFacingDirection(),True)
        if actor.bufferContains(invkey,5,notReleased = True):
            actor.doPivot()
                
class NeutralAction(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)

        
    def update(self, actor):
        return
    
    def stateTransitions(self, actor):
        neutralState(actor)
        
class HitStun(action.Action):
    def __init__(self,hitstun,direction):
        action.Action.__init__(self, hitstun)
        self.direction = direction
        
    def tearDown(self, actor, newAction):
        actor.unRotate()
        
    def update(self,actor):
        if self.frame == 0:
            (direct,mag) = actor.getDirectionMagnitude()
            print("direction:", direct)
            if direct != 0 and direct != 180:
                actor.grounded = False
                if mag > 10:
                    actor.rotateSprite(self.direction)
            actor.preferred_xspeed = 0
            
        if self.frame == self.lastFrame:
            actor.unRotate()
            
        self.frame += 1

class Jump(action.Action):
    def __init__(self,length,jumpFrame):
        action.Action.__init__(self, length)
        self.jumpFrame = jumpFrame
        
    def update(self,actor):
        if self.frame == self.jumpFrame:
            actor.grounded = False
            if actor.keysContain('jump'):
                actor.change_y = -actor.var['jumpHeight']
            else: actor.change_y = -actor.var['jumpHeight']/1.5
            ##TODO Add in shorthop height as an attribute
            if actor.change_x > actor.var['maxAirSpeed']:
                actor.change_x = actor.var['maxAirSpeed']
            elif actor.change_x < -actor.var['maxAirSpeed']:
                actor.change_x = -actor.var['maxAirSpeed']
            
        self.frame += 1
        
class AirJump(action.Action):
    def __init__(self,length,jumpFrame):
        action.Action.__init__(self, length)
        self.jumpFrame = jumpFrame
        
    def update(self,actor):
        if self.frame == 0:
            actor.jumps -= 1
        
        if self.frame < self.jumpFrame:
            actor.change_y = 0
        if self.frame == self.jumpFrame:
            actor.grounded = False
            actor.change_y = -actor.var['airJumpHeight']
            
            if actor.keysContain('left'):
                if actor.facing == 1:
                    actor.flip()
                    actor.change_x = actor.facing * actor.var['maxAirSpeed']
            elif actor.keysContain('right'):
                if actor.facing == -1:
                    actor.flip()
                    actor.change_x = actor.facing * actor.var['maxAirSpeed']    
        self.frame += 1
        
class Fall(action.Action):
    def __init__(self):
        action.Action.__init__(self, 1)
    
    def stateTransitions(self,actor):
        airState(actor)
        grabLedges(actor)
        
    def update(self,actor):
        actor.grounded = False
            
class Land(action.Action):
    def __init__(self):
        action.Action.__init__(self, 6)

    def update(self,actor):
        if self.frame == 0:
            self.lastFrame = actor.landingLag
            if actor.bufferContains('shield',distanceBack=22):
                print("l-cancel")
                self.lastFrame = self.lastFrame / 2    
        if self.frame == self.lastFrame:
            actor.landingLag = 6
            if   actor.keysHeld.count('left'): actor.doGroundMove(180)
            elif actor.keysHeld.count('right'): actor.doGroundMove(0)
            else: actor.doIdle()
        actor.preferred_xspeed = 0
        self.frame+= 1

class Shield(action.Action):
    def __init__(self):
        action.Action.__init__(self, 5)
        self.shieldFrame = 4
    
    def stateTransitions(self, actor):
        shieldState(actor)
    
    def tearDown(self, actor, newAction):
        actor.shield = False
        
    def update(self, actor):
        if self.frame == self.shieldFrame:
            actor.shield = True
            actor.startShield()
            if actor.keysContain('shield'):
                actor.shieldDamage(1)
            else:
                self.frame += 1
        elif self.frame == self.lastFrame:
            actor.shield = False
            actor.doIdle()
        else: self.frame += 1

class ShieldBreak(action.Action):
    def __init__(self):
        action.Action.__init__(self, 2)
        
    def update(self,actor):
        if self.frame == 0:
            actor.shield = False
            actor.change_y = -15
        elif self.frame == self.lastFrame:
            if actor.shieldIntegrity == 100:
                actor.doIdle()
            else:
                self.frame -= 1
        self.frame += 1
        
class ForwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 46)
        self.startInvulnFrame = 6
        self.endInvulnFrame = 34
        
    def update(self, actor):
        if self.frame == 1:
            actor.change_x = actor.facing * 10
        elif self.frame == self.startInvulnFrame:
            actor.createMask([255,255,255], 22, True, 24)
            #actor.invulnerable
        elif self.frame == self.endInvulnFrame:
            actor.flip()
            actor.change_x = 0
            #actor.vulnerable
        elif self.frame == self.lastFrame:
            if actor.keysContain('shield'):
                actor.doShield()
            else:
                actor.doIdle()
        self.frame += 1
        
class BackwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 50)
        self.startInvulnFrame = 6
        self.endInvulnFrame = 34
        
    def update(self, actor):
        if self.frame == 1:
            actor.change_x = actor.facing * -10
        elif self.frame == self.startInvulnFrame:
            actor.createMask([255,255,255], 22, True, 24)
            #actor.invulnerable
        elif self.frame == self.endInvulnFrame:
            actor.change_x = 0
            #actor.vulnerable
        elif self.frame == self.lastFrame:
            if actor.keysContain('shield'):
                actor.doShield()
            else:
                actor.doIdle()
        self.frame += 1
        
class SpotDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
        self.startInvulnFrame = 4
        self.endInvulnFrame = 20
        
    def update(self,actor):
        if self.frame == 1:
            actor.change_x = 0
        elif self.frame == self.startInvulnFrame:
            actor.createMask([255,255,255],16,True,24)
            #actor.invulnerable
        elif self.frame == self.endInvulnFrame:
            pass
            #actor.vulnerable
        elif self.frame == self.lastFrame:
            if actor.keysContain('shield'):
                actor.doShield()
            else:
                actor.doIdle()
        self.frame += 1
        
class AirDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
        self.startInvulnFrame = 4
        self.endInvulnFrame = 20
    
    def setUp(self,actor):
        actor.landingLag = 24
        
    def tearDown(self,actor,other):
        if actor.mask: actor.mask = None
        #remove invuln
    
    def stateTransitions(self, actor):
        airControl(actor)
            
    def update(self,actor):
        if self.frame == self.startInvulnFrame:
            actor.createMask([255,255,255],16,True,24)
            #actor.invulnerable
        elif self.frame == self.endInvulnFrame:
            pass
            #actor.vulnerable
        elif self.frame == self.lastFrame:
            actor.doFall()
        self.frame += 1
        
class LedgeGrab(action.Action):
    def __init__(self,ledge):
        action.Action.__init__(self, 1)
        self.ledge = ledge
        
    def tearDown(self,actor,newAction):
        self.ledge.fighterLeaves(actor)
        
    def stateTransitions(self,actor):
        ledgeState(actor)
        
    def update(self,actor):
        actor.jumps = actor.var['jumps']
        actor.change_y = 0
########################################################
#               TRANSITION STATES                     #
########################################################
def neutralState(actor):
    if actor.bufferContains('attack'):
        actor.doGroundAttack()
    elif actor.bufferContains('jump',10):
        actor.doJump()
    elif actor.bufferContains('left',8):
        actor.doGroundMove(180)
    elif actor.bufferContains('right',8):
        actor.doGroundMove(0)
    elif actor.bufferContains('shield',8):
        actor.doShield()
    
def airState(actor):
    airControl(actor)
    if actor.bufferContains('jump'):
        actor.doJump()
    if actor.bufferContains('down'):
        if actor.change_y >= 0:
            actor.change_y = actor.var['maxFallSpeed']
            actor.landingLag = 14
    if actor.bufferContains('attack',8):
        actor.doAirAttack()
    if actor.bufferContains('shield',8):
        actor.doAirDodge()
            
def moveState(actor, direction):
    if actor.bufferContains('jump'):
        actor.doJump()
    (key,_) = actor.getForwardBackwardKeys()
    if actor.bufferContains(key, state=0):
        actor.doStop()
    if actor.bufferContains('attack'):
        print("attacking")
        actor.doGroundAttack()
            
def shieldState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.bufferContains('jump'):
        actor.doJump()
    elif actor.bufferContains('attack'):
        pass
        #grab
    elif actor.bufferContains(key):
        actor.doForwardRoll()
    elif actor.bufferContains(invkey):
        actor.doBackwardRoll()
    elif actor.bufferContains('down'):
        actor.doSpotDodge()

def ledgeState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.bufferContains(key):
        print("up")
        actor.doLedgeGetup
    elif actor.bufferContains(invkey):
        actor.ledgeLock = True
        actor.change_y = 0
        actor.change_x = 0
        actor.doFall()
########################################################
#             BEGIN HELPER METHODS                     #
########################################################

def airControl(actor):
    if actor.keysHeld.count('left'):
        actor.preferred_xspeed = -actor.var['maxAirSpeed']
    elif actor.keysHeld.count('right'):
        actor.preferred_xspeed = actor.var['maxAirSpeed']
    
    if (actor.change_x < 0) and not actor.keysHeld.count('left'):
        actor.preferred_xspeed = 0
    elif (actor.change_x > 0) and not actor.keysHeld.count('right'):
        actor.preferred_xspeed = 0

    if actor.grounded:
        actor.doLand()

def grabLedges(actor):
    # Check if we're colliding with any ledges.
    if not actor.ledgeLock: #If we're not allowed to re-grab, don't bother calculating
        ledge_hit_list = pygame.sprite.spritecollide(actor, actor.gameState.platform_ledges, False)
        for ledge in ledge_hit_list:
            # Don't grab any ledges if the actor is holding down
            if actor.keysContain('down') == False:
                # If the ledge is on the left side of a platform, and we're holding right
                if ledge.side == 'left' and actor.keysContain('right'):
                    ledge.fighterGrabs(actor)
                elif ledge.side == 'right' and actor.keysContain('left'):
                    ledge.fighterGrabs(actor)