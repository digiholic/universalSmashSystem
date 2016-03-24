import engine.action as action
import pygame
import math
import settingsManager

"""
@ai-move-forward
@ai-move-backward
"""
class Move(action.Action):
    def __init__(self,length):
        action.Action.__init__(self,length) 
        self.direction = -1
        
    def setUp(self,actor):
        self.direction = actor.getForwardWithOffset(0)
        
    def update(self, actor):
        if actor.grounded == False:
            actor.doFall()
        actor.setPreferredSpeed(actor.var['maxGroundSpeed'],self.direction)
        actor.accel(actor.var['staticGrip'])

        (key,invkey) = actor.getForwardBackwardKeys()
        if self.direction == actor.getForwardWithOffset(0):
            if actor.keysContain(invkey):
                actor.flip()
        else:
            if not actor.keysContain(key):
                actor.flip()
        
        self.frame += 1
        if self.frame > self.lastFrame: self.frame = 0
        
    def stateTransitions(self,actor):
        moveState(actor,self.direction)

"""
@ai-move-forward
@ai-move-backward
"""
class Dash(action.Action):
    def __init__(self,length): 
        action.Action.__init__(self,length)
        self.pivoted = False

    def setUp(self,actor):
        if actor.facing == 1: self.direction = 0
        else: self.direction = 180

    def update(self, actor):
        if self.frame == 0:
            actor.setPreferredSpeed(actor.var['runSpeed'],self.direction)
        if actor.grounded == False:
            actor.doFall()
        if not self.pivoted:
            (key,invkey) = actor.getForwardBackwardKeys()
            if actor.keysContain(invkey):
                actor.flip() #Do the moonwalk!
                self.pivoted = True
        actor.accel(actor.var['staticGrip'])
        self.frame += 1
        if self.frame > self.lastFrame: 
            actor.doRun(actor.getFacingDirection())
    
    def stateTransitions(self,actor):
        dashState(actor,self.direction)
        
"""
@ai-move-forward
@ai-move-backward
"""
class Run(action.Action):
    def __init__(self,length):
        action.Action.__init__(self,length)
        
    def setUp(self,actor):
        if actor.facing == 1: self.direction = 0
        else: self.direction = 180
            
    def update(self, actor):
        if actor.grounded == False:
            actor.doFall()
        actor.accel(actor.var['staticGrip'])
        
        self.frame += 1
        if self.frame > self.lastFrame: self.frame = 0
    
    def stateTransitions(self,actor):
        runState(actor,self.direction)
        
class Pivot(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)
        
    def update(self,actor):
        if actor.grounded == False:
            actor.doFall()
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
        if actor.grounded == False:
            actor.doFall()
        (key,invkey) = actor.getForwardBackwardKeys()
        if actor.bufferContains(key,self.frame):
            print("run")
            actor.doDash(actor.getFacingDirection())
        if actor.bufferContains(invkey,self.frame):
            print("pivot")
            actor.doPivot()
                
class NeutralAction(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)
        
    def update(self, actor):
        return
    
    def stateTransitions(self, actor):
        if actor.grounded == False:
            actor.doFall()
        neutralState(actor)

"""
@ai-move-stop
@ai-move-forward
@ai-move-backward
"""
class Crouch(action.Action):
    def __init__(self, length):
        action.Action.__init__(self, length)
        self.direction = -1

    def setUp(self, actor):
        self.direction = actor.getForwardWithOffset(0)

    def stateTransitions(self, actor):
        if actor.grounded == False:
            actor.doFall()
        crouchState(actor)

    def update(self, actor):
        if actor.grounded == False:
            actor.doFall()
        actor.accel(actor.var['staticGrip'])
        (key, invkey) = actor.getForwardBackwardKeys()
        if actor.keysContain(key):
            actor.setPreferredSpeed(actor.var['crawlSpeed'], actor.getFacingDirection())
        elif actor.keysContain(invkey):
            actor.setPreferredSpeed(-actor.var['crawlSpeed'], actor.getFacingDirection())
        else:
            actor.setPreferredSpeed(0, self.direction)
        
        self.frame += 1
        if self.frame > self.lastFrame: self.frame = 0

class CrouchGetup(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)

    def update(self, actor):
        if actor.grounded == False:
            actor.doFall()
        elif actor.bufferContains('down') and self.frame > 0:
            blocks = actor.checkForGround()
            #Turn it into a list of true/false if the block is solid
            blocks = map(lambda x:x.solid,blocks)
            #If none of the ground is solid
            if not any(blocks):
                actor.doPlatformDrop()
        elif self.frame >= self.lastFrame:
            actor.doIdle()
        self.frame += 1

class BaseGrabbing(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)

    def tearDown(self, actor, newAction):
        if not isinstance(newAction, BaseGrabbing) and actor.isGrabbing():
            actor.grabbing.doIdle()

    def update(self, actor):
        if actor.isGrabbing():
            actor.grabbing.rect.centerx = actor.rect.centerx+actor.facing*actor.rect.width/2
            actor.grabbing.rect.bottom = actor.rect.bottom

class Grabbing(BaseGrabbing):
    def __init__(self,length):
        BaseGrabbing.__init__(self, length)

    def stateTransitions(self, actor):
        if actor.grounded == False:
            actor.doFall()
        grabbingState(actor)
        
"""
@ai-move-forward
@ai-move-backward
@ai-move-down
"""
class HitStun(action.Action):
    def __init__(self,hitstun,direction,hitstop):
        action.Action.__init__(self, hitstun)
        self.direction = direction
        self.hitstop = hitstop

    def stateTransitions(self, actor):
        (direct,_) = actor.getDirectionMagnitude()
        if actor.bufferContains('shield', 20) and self.frame < self.lastFrame:
            actor.doTryTech(self.lastFrame-self.frame, self.direction)
        elif actor.grounded and self.frame > 2:
            print actor.change_y
            if self.frame >= self.lastFrame and actor.change_y >= actor.var['maxFallSpeed']/2: #Hard landing during tumble
                actor.change_y = -0.4*actor.change_y
            elif self.frame < self.lastFrame and actor.change_y >= actor.var['maxFallSpeed']/2:
                actor.change_y = -0.8*actor.change_y #Hard landing during hitstun
            elif abs(actor.change_x) > actor.var['runSpeed']: #Skid trip
                actor.doTrip(self.lastFrame-self.frame, direct)
            elif self.frame >= self.lastFrame and actor.change_y < actor.var['maxFallSpeed']/2: #Soft landing during tumble
                actor.doIdle()
            elif self.frame >= self.lastFrame: #Firm landing during tumble
                actor.landingLag = actor.var['heavyLandLag']
                actor.doLand()
            elif actor.change_y < actor.var['maxFallSpeed']/2: #Soft landing during hitstun
                actor.landingLag = actor.var['heavyLandLag']
                actor.doLand()
            else: #Firm landing during hitstun
                actor.change_y = -0.4*actor.change_y
        elif self.frame >= self.lastFrame:
            tumbleState(actor)
        
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
            actor.hitstop = self.hitstop
            if actor.grounded:
                actor.hitstopVibration = (3,0)
            else:
                actor.hitstopVibration = (0,3)
            actor.hitstopPos = actor.rect.center
            
        if self.frame == self.lastFrame:
            actor.unRotate()
            #Tumbling continues indefinetely, but can be cancelled out of

        self.frame += 1

"""
@ai-move-stop
"""
class TryTech(HitStun):
    def __init__(self, hitstun, direction):
        HitStun.__init__(self, hitstun, direction)

    def stateTransitions(self, actor):
        (direct,mag) = actor.getDirectionMagnitude()
        if self.frame < 20 and actor.grounded:
            print('Ground tech!')
            actor.unRotate()
            actor.doTrip(-175, direct)
        elif self.frame < 20:
            actor.rect.x += actor.change_x
            actor.rect.y += actor.change_y
            block_hit_list = actor.getCollisionsWith(actor.gameState.platform_list)
            actor.rect.x -= actor.change_x
            actor.rect.y -= actor.change_y
            for block in block_hit_list:
                if block.solid:
                    print('Wall tech!')
                    actor.change_x = 0
                    actor.change_y = 0

    def update(self, actor):
        if self.frame >= 40:
            actor.doHitStun(self.lastFrame-self.frame, self.direction)
        HitStun.update(self, actor)

class Trip(action.Action):
    def __init__(self,length,direction):
        action.Action.__init__(self, length)
        self.direction = direction
        print("direction:", self.direction)

    def update(self, actor):
        if actor.grounded == False:
            actor.doHitStun(self.lastFrame-self.frame, self.direction)
        if self.frame >= self.lastFrame + 180: #You aren't up yet?
            actor.doGetup(self.direction)
        self.frame += 1

    def stateTransitions(self, actor):
        if self.frame >= self.lastFrame:
            tripState(actor, self.direction)

class Getup(action.Action):
    def __init__(self, direction, length):
        action.Action.__init__(self, length)
        self.direction = direction

    def update(self, actor):
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1
        
"""
@ai-move-up
@ai-move-stop
"""
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
        
"""
@ai-move-up
@ai-move-stop
"""
class AirJump(action.Action):
    def __init__(self,length,jumpFrame):
        action.Action.__init__(self, length)
        self.jumpFrame = jumpFrame

    def setUp(self, actor):
        actor.jumps -= 1
        
    def update(self,actor):
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
        
"""
@ai-move-down
@ai-move-forward
@ai-move-backward
"""
class Fall(action.Action):
    def __init__(self):
        action.Action.__init__(self, 1)
    
    def stateTransitions(self,actor):
        airState(actor)
        grabLedges(actor)
        
    def update(self,actor):
        actor.grounded = False

"""
@ai-move-down
@ai-move-forward
@ai-move-backward
"""
class Helpless(action.Action):
    def __init__(self):
        action.Action.__init__(self, 1)

    def stateTransitions(self, actor):
        helplessControl(actor)
        grabLedges(actor)

    def update(self, actor):
        actor.grounded = False
            
class Land(action.Action):
    def __init__(self):
        action.Action.__init__(self, 6)

    def update(self,actor):
        if self.frame == 0:
            self.lastFrame = actor.landingLag
            if actor.bufferContains('shield', 20):
                print("l-cancel")
                self.lastFrame = self.lastFrame / 2
        elif actor.keysContain('down') and self.lastFrame - self.frame < actor.var['dropPhase']:
            blocks = actor.checkForGround()
            #Turn it into a list of true/false if the block is solid
            blocks = map(lambda x :x.solid,blocks)
            #If none of the ground is solid
            if not any(blocks):
                actor.doPlatformDrop()
        if self.frame == self.lastFrame:
            actor.landingLag = 6
            actor.doIdle()
            actor.platformPhase = 0
            actor.setPreferredSpeed(0, actor.getFacingDirection())
        self.frame+= 1

class HelplessLand(action.Action):
    def __init__(self):
        action.Action.__init__(self, 6)

    def update(self,actor):
        if self.frame == 0:
            self.lastFrame = actor.landingLag
            if actor.bufferContains('shield', 20):
                print("l-cancel")
                self.lastFrame = self.lastFrame / 2
        elif actor.keysContain('down') and self.lastFrame - self.frame < actor.var['dropPhase']:
            blocks = actor.checkForGround()
            #Turn it into a list of true/false if the block is solid
            blocks = map(lambda x:x.solid,blocks)
            #If none of the ground is solid
            if not any(blocks):
                actor.doPlatformDrop()
        if self.frame == self.lastFrame:
            actor.landingLag = 6
            actor.doIdle()
            actor.platformPhase = 0
            actor.setPreferredSpeed(0, actor.getFacingDirection())
        self.frame += 1

"""
@ai-move-down
"""
class PlatformDrop(action.Action):
    def __init__(self, length):
        action.Action.__init__(self, length)
    
    def update(self,actor):
        if self.frame == 0:
            actor.platformPhase = actor.var['dropPhase']
        if self.frame == self.lastFrame:
            actor.doFall()
        self.frame += 1
        
class PreShield(action.Action):
    def __init__(self):
        action.Action.__init__(self, 4)

    def stateTransitions(self, actor):
        shieldState(actor)

    def update(self, actor):
        if actor.grounded == False:
            actor.doFall()
        if self.frame == self.lastFrame:
            actor.doShield()
        self.frame += 1

class Shield(action.Action):
    def __init__(self):
        action.Action.__init__(self, 2)
   
    def stateTransitions(self, actor):
        shieldState(actor)
   
    def tearDown(self, actor, newAction):
        if not isinstance(newAction, ShieldStun):
            actor.shield = False
       
    def update(self, actor):
        if actor.grounded == False:
            actor.doFall()
        if self.frame == 0:
            actor.shield = True
            actor.startShield()
            if actor.keysContain('shield'):
                self.frame += 1
            else:
                self.frame += 2
        elif self.frame == 1:
            if actor.keysContain('shield'):
                actor.shieldDamage(1)
            else:
                self.frame += 1
        elif self.frame >= self.lastFrame:
            actor.shield = False
            actor.doIdle()
        else: self.frame += 1

class ShieldStun(action.Action):
    def __init__(self, length):
        action.Action.__init__(self, length)

    def tearDown(self, actor, newAction):
        if not isinstance(newAction, Shield) and not isinstance(newAction, ShieldStun):
            actor.shield = False

    def update(self, actor):
        if actor.grounded == False:
            actor.doFall()
        if self.frame >= self.lastFrame and actor.keysContain('shield'):
            actor.doShield()
        self.frame += 1

class Stunned(action.Action):
    def __init__(self, length):
        action.Action.__init__(self, length)

    def update(self, actor):
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1

"""
@ai-move-stop
"""
class Trapped(action.Action):
    def __init__(self, length):
        action.Action.__init__(self, length)
        self.time = 0
        self.lastPosition = [0,0]

    def update(self,actor):
        newPosition = actor.getSmoothedInput()
        cross = newPosition[0]*self.lastPosition[1]-newPosition[1]*self.lastPosition[0]
        self.frame += (cross**2)*4
        self.lastPosition = newPosition
        if self.frame >= self.lastFrame:
            actor.doIdle()
        # Throws and other grabber-controlled releases are the grabber's responsibility
        # Also, the grabber should always check to see if the grabbee is still under grab
        self.frame += 1
        self.time += 1
        print(self.frame, self.time)

class Grabbed(Trapped):
    def __init__(self,height):
        Trapped.__init__(self, 40)
        self.height = height

    def update(self,actor):
        if self.frame == 0:
            self.lastFrame = 40 + actor.damage/2
        Trapped.update(self, actor)
        
class Release(action.Action):
    def __init__(self):
        action.Action.__init__(self,5)

    def update(self, actor):
        if actor.grounded == False:
            actor.doFall()
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1
        
"""
@ai-move-forward
@ai-move-stop
"""
class ForwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 46)
        self.startInvulnFrame = 6
        self.endInvulnFrame = 34

    def tearDown(self, actor, nextAction):
        if actor.invulnerable > 0:
            actor.invulnerable = 0
        actor.mask = None
        
    def update(self, actor):
        if actor.grounded == False:
            actor.doFall()
        if self.frame == 1:
            actor.change_x = actor.facing * 10
        elif self.frame == self.startInvulnFrame:
            actor.createMask([255,255,255], 22, True, 24)
            actor.invulnerable = self.endInvulnFrame-self.startInvulnFrame
        elif self.frame == self.endInvulnFrame:
            actor.flip()
            actor.change_x = 0
        elif self.frame == self.lastFrame:
            if actor.keysContain('shield'):
                actor.doShield()
            else:
                actor.doIdle()
        self.frame += 1
        
"""
@ai-move-backward
@ai-move-stop
"""
class BackwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 50)
        self.startInvulnFrame = 6
        self.endInvulnFrame = 34

    def tearDown(self, actor, nextAction):
        if actor.invulnerable > 0:
            actor.invulnerable = 0
        actor.mask = None
        
    def update(self, actor):
        if actor.grounded == False:
            actor.doFall()
        if self.frame == 1:
            actor.change_x = actor.facing * -10
        elif self.frame == self.startInvulnFrame:
            actor.createMask([255,255,255], 22, True, 24)
            actor.invulnerable = self.endInvulnFrame-self.startInvulnFrame
        elif self.frame == self.endInvulnFrame:
            actor.change_x = 0
        elif self.frame == self.lastFrame:
            if actor.keysContain('shield'):
                actor.doShield()
            else:
                actor.doIdle()
        self.frame += 1
        
"""
@ai-move-stop
"""
class SpotDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
        self.startInvulnFrame = 4
        self.endInvulnFrame = 20

    def tearDown(self, actor, nextAction):
        if actor.invulnerable > 0:
            actor.invulnerable = 0
        actor.mask = None
        
    def update(self,actor):
        if actor.grounded == False:
            actor.doFall()
        elif actor.bufferContains('down') and self.frame > 0:
            blocks = actor.checkForGround()
            #Turn it into a list of true/false if the block is solid
            blocks = map(lambda x:x.solid,blocks)
            #If none of the ground is solid
            if not any(blocks):
                actor.doPlatformDrop()
        if self.frame == 1:
            actor.change_x = 0
        elif self.frame == self.startInvulnFrame:
            actor.createMask([255,255,255],16,True,24)
            actor.invulnerable = self.endInvulnFrame - self.startInvulnFrame
        elif self.frame == self.endInvulnFrame:
            pass
        elif self.frame == self.lastFrame:
            if actor.keysContain('shield'):
                actor.doShield()
            else:
                actor.doIdle()
        self.frame += 1
        
"""
@ai-move-forward
@ai-move-backward
@ai-move-up
@ai-move-down
@ai-move-stop
"""
class AirDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
        self.startInvulnFrame = 4
        self.endInvulnFrame = 20
        self.move_vec = [0,0]
    
    def setUp(self,actor):
        actor.landingLag = 24
        if settingsManager.getSetting('airDodgeType') == 'directional':
            self.move_vec = actor.getSmoothedInput()
            actor.change_x = self.move_vec[0]*10
            actor.change_y = self.move_vec[1]*10
        
    def tearDown(self,actor,other):
        if settingsManager.getSetting('airDodgeType') == 'directional':
            actor.gravityEnabled = True
        if actor.mask: actor.mask = None
        if actor.invulnerable > 0:
            actor.invulnerable = 0
    
    def stateTransitions(self, actor):
        if actor.grounded:
            if not settingsManager.getSetting('enableWavedash'):
                actor.change_x = 0
            actor.doLand()
                
    def update(self,actor):
        if settingsManager.getSetting('airDodgeType') == 'directional':
            if self.frame == 0:
                actor.gravityEnabled = False
            elif self.frame >= 16:
                actor.change_x = 0
                actor.change_y = 0
            elif self.frame == self.lastFrame:
                actor.gravityEnabled = True
                
        if self.frame == self.startInvulnFrame:
            actor.createMask([255,255,255],16,True,24)
            actor.invulnerable = self.endInvulnFrame-self.startInvulnFrame
        elif self.frame == self.endInvulnFrame:
            pass
        elif self.frame == self.lastFrame:
            if settingsManager.getSetting('freeDodgeSpecialFall'):
                actor.doHelpless()
            else:
                actor.doFall()
        self.frame += 1

class TechDodge(AirDodge):
    def __init__(self):
        AirDodge.__init__(self)

    def stateTransitions(self, actor):
        if actor.grounded and self.frame < 20:
            actor.doTrip(-175, direct)
            return
        airControl(actor)
        
"""
@ai-move-stop
@ai-move-forward
@ai-move-backward
@ai-move-up
@ai-move-down
"""
class LedgeGrab(action.Action):
    def __init__(self,ledge):
        action.Action.__init__(self, 1)
        self.ledge = ledge

    def setUp(self, actor):
        actor.createMask([255,255,255], 120, True, 12)
        if actor.invulnerable > -30:
            actor.invulnerable = settingsManager.getSetting('ledgeInvincibilityTime')
        
    def tearDown(self,actor,newAction):
        self.ledge.fighterLeaves(actor)
        
    def stateTransitions(self,actor):
        ledgeState(actor)
        
    def update(self,actor):
        actor.jumps = actor.var['jumps']
        actor.setSpeed(0, actor.getFacingDirection())

"""
@ai-move-forward
@ai-move-up
@ai-move-stop
"""
class LedgeGetup(action.Action):
    def __init__(self):
        action.Action.__init__(self, 27)
    
    def update(self,actor):
        if self.frame >= self.lastFrame:
            actor.doStop()
        self.frame += 1

########################################################
#               TRANSITION STATES                     #
########################################################
def neutralState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.bufferContains('shield', 8):
        actor.doPreShield()
    elif actor.bufferContains('attack', 8):
        actor.doGroundAttack()
    elif actor.bufferContains('special', 8):
        actor.doGroundSpecial()
    elif actor.bufferContains('jump', 8):
        actor.doJump()
    elif actor.keysContain('left'):
        actor.doGroundMove(180)
    elif actor.keysContain('right'):
        actor.doGroundMove(0)
    elif actor.keysContain('down'):
        actor.doCrouch()

def crouchState(actor):
    if actor.bufferContains('attack', 8):
        actor.doGroundAttack()
    elif actor.bufferContains('special', 8):
        actor.doGroundSpecial()
    elif actor.bufferContains('jump', 8):
        actor.doJump()
    elif not actor.keysContain('down'):
        actor.doCrouchGetup()

def airState(actor):
    airControl(actor)
    if actor.bufferContains('shield', 8):
        actor.doAirDodge()
    elif actor.bufferContains('attack', 8):
        actor.doAirAttack()
    elif actor.bufferContains('special', 8):
        actor.doAirSpecial()
    elif actor.bufferContains('jump', 8) and actor.jumps > 0:
        actor.doAirJump()
    elif actor.keysContain('down'):
        actor.platformPhase = 1
        actor.change_y += actor.var['airControl']
        if actor.change_y > actor.var['maxFallSpeed']:
            actor.change_y = actor.var['maxFallSpeed']

def tumbleState(actor):
    airControl(actor)
    if actor.bufferContains('shield', 8):
        actor.doTechDodge()
    elif actor.bufferContains('attack', 8):
        actor.doAirAttack()
    elif actor.bufferContains('special', 8):
        actor.doAirSpecial()
    elif actor.bufferContains('jump', 8) and actor.jumps > 0:
        actor.doAirJump()
    elif actor.keysContain('down'):
        if actor.change_y >= 0:
            actor.platformPhase = 1
            actor.change_y = actor.var['maxFallSpeed']
            
def moveState(actor, direction):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.bufferContains('attack', 8):
        actor.doGroundAttack()
    elif actor.bufferContains('special', 8):
        actor.doGroundSpecial()
    elif actor.bufferContains('jump', 8):
        actor.doJump()
    elif direction == actor.getForwardWithOffset(0) and not actor.keysContain(key):
        actor.doStop()
    elif direction == actor.getForwardWithOffset(180) and not actor.keysContain(invkey):
        actor.doStop()

def dashState(actor, direction):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.bufferContains('attack', 8):
        actor.doDashAttack()
    elif actor.bufferContains('special', 8):
        actor.doGroundSpecial()
    elif actor.bufferContains('jump', 8):
        actor.doJump()
    elif direction == actor.getForwardWithOffset(0) and not actor.keysContain(key):
        actor.doStop()
    elif direction == actor.getForwardWithOffset(180) and not actor.keysContain(invkey):
        actor.doStop()

def runState(actor, direction):
    (key,_) = actor.getForwardBackwardKeys()
    if actor.bufferContains('attack', 8):
        actor.doDashAttack()
    elif actor.bufferContains('special', 8):
        actor.doGroundSpecial()
    elif actor.bufferContains('jump', 8):
        actor.doJump()
    elif not actor.keysContain(key):
        actor.doStop()
            
def shieldState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.bufferContains('attack'):
        actor.doGroundGrab()
    elif actor.bufferContains('jump'):
        actor.doJump()
    elif actor.bufferContains(key):
        actor.doForwardRoll()
    elif actor.bufferContains(invkey):
        actor.doBackwardRoll()
    elif actor.bufferContains('down'):
        actor.doSpotDodge()

def ledgeState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    actor.setSpeed(0, actor.getFacingDirection())
    if actor.bufferContains('jump', 8):
        actor.ledgeLock = True
        actor.doJump()
    elif actor.bufferContains(key):
        actor.ledgeLock = True
        actor.doLedgeGetup()
    elif actor.keysContain(invkey):
        actor.ledgeLock = True
        actor.doFall()
    elif actor.keysContain('down'):
        actor.ledgeLock = True
        actor.doFall()

def grabbingState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    # Check to see if they broke out
    # If they did, release them
    if not actor.isGrabbing():
        actor.doRelease()
    elif actor.bufferContains('shield', 8):
        actor.doRelease()
    elif actor.bufferContains('attack', 8):
        actor.doPummel()
    elif actor.bufferContains(key, 8):
        actor.doThrow()
    elif actor.bufferContains(invkey, 8):
        actor.doThrow()
    elif actor.bufferContains('up', 8):
        actor.doThrow()
    elif actor.bufferContains('down', 8):
        actor.doThrow()

def tripState(actor, direction):
    (key, invkey) = actor.getForwardBackwardKeys()
    if actor.bufferContains('attack', 8):
        actor.doGetupAttack(direction)
    elif actor.bufferContains('up', 8):
        actor.doGetup(direction)
    elif actor.bufferContains(key, 8):
        actor.doForwardRoll()
    elif actor.bufferContains(key, 8):
        actor.doBackwardRoll()
    elif actor.bufferContains('down', 8):
        actor.doSpotDodge()

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

    if actor.change_y >= actor.var['maxFallSpeed'] and actor.landingLag < actor.var['heavyLandLag']:
        actor.landingLag = actor.var['heavyLandLag']

    if actor.grounded:
        actor.change_x = 0
        actor.doLand()

def helplessControl(actor):
    if actor.keysHeld.count('left'):
        actor.preferred_xspeed = -actor.var['maxAirSpeed']
    elif actor.keysHeld.count('right'):
        actor.preferred_xspeed = actor.var['maxAirSpeed']
    
    if (actor.change_x < 0) and not actor.keysHeld.count('left'):
        actor.preferred_xspeed = 0
    elif (actor.change_x > 0) and not actor.keysHeld.count('right'):
        actor.preferred_xspeed = 0

    if actor.change_y >= actor.var['maxFallSpeed'] and actor.landingLag < actor.var['heavyLandLag']:
        actor.landingLag = actor.var['heavyLandLag']

    if actor.grounded:
        actor.change_x = 0
        actor.doHelplessLand()

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
