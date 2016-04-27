import engine.action as action
import engine.hitbox as hitbox
import engine.article as article
import pygame
import math
import settingsManager

class Move(action.Action):
    def __init__(self,length):
        action.Action.__init__(self,length) 
        self.direction = -1
        
    def setUp(self,actor):
        self.direction = actor.facing

    def tearDown(self, actor, nextAction):
        actor.preferred_xspeed = 0
        
    def update(self, actor):
        if actor.grounded is False:
            actor.doFall()
        actor.preferred_xspeed = actor.var['maxGroundSpeed']*self.direction
        actor.accel(actor.var['staticGrip'])

        (key,invkey) = actor.getForwardBackwardKeys()
        if self.direction == actor.facing:
            if actor.keysContain(invkey):
                actor.flip()
        else:
            if not actor.keysContain(key):
                actor.flip()
        
        self.frame += 1
        if self.frame > self.lastFrame: self.frame = 1
        
    def stateTransitions(self,actor):
        moveState(actor,self.direction)
        (key,invkey) = actor.getForwardBackwardKeys()
        if self.frame > 0 and actor.keyBuffered(invkey, 0, state = 1):
            actor.doDash(-1*actor.getFacingDirection())
        elif self.frame > 0 and actor.keyBuffered(key, 0, state = 1):
            actor.doDash(actor.getFacingDirection())

class Dash(action.Action):
    def __init__(self,length): 
        action.Action.__init__(self,length)
        self.pivoted = False

    def setUp(self,actor):
        if actor.facing == 1: self.direction = 1
        else: self.direction = -1

    def tearDown(self, actor, nextAction):
        if not isinstance(nextAction, Run):
            actor.preferred_xspeed = 0

    def update(self, actor):
        if self.frame == 0:
            actor.preferred_xspeed = actor.var['maxGroundSpeed']*self.direction
        if actor.grounded is False:
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

class Run(action.Action):
    def __init__(self,length):
        action.Action.__init__(self,length)
        
    def setUp(self,actor):
        if actor.facing == 1: self.direction = 1
        else: self.direction = -1

    def tearDown(self, actor, nextAction):
        actor.preferred_xspeed = 0
            
    def update(self, actor):
        if self.frame == 0:
            actor.preferred_xspeed = math.copysign(actor.var['runSpeed'], actor.preferred_xspeed)
        if actor.grounded is False:
            actor.doFall()
        actor.accel(actor.var['staticGrip'])
        
        self.frame += 1
        if self.frame > self.lastFrame: self.frame = 0
    
    def stateTransitions(self,actor):
        runState(actor,self.direction)
        
class Pivot(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)

    def tearDown(self, actor, nextAction):
        actor.flip()

    def stateTransitions(self, actor):
        if actor.keyHeld('jump', self.frame):
            actor.doJump()
        
    def update(self,actor):
        if actor.grounded is False:
            actor.doFall()
        actor.accel(actor.var['staticGrip'])
        if self.frame != self.lastFrame:
            self.frame += 1
            actor.preferred_xspeed = 0
        if self.frame == self.lastFrame:
            (key, _) = actor.getForwardBackwardKeys()
            if actor.keysContain(key):
                if actor.checkSmash(key):
                    if actor.facing == 1:
                        actor.doDash(0)
                    else:
                        actor.doDash(180)
                else:
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
        if actor.grounded is False:
            actor.doFall()
        actor.accel(actor.var['staticGrip'])
        (key,invkey) = actor.getForwardBackwardKeys()
        if actor.keyHeld(key,self.frame):
            print("run")
            actor.doDash(actor.getFacingDirection())
        if actor.keyHeld(invkey,self.frame):
            print("pivot")
            actor.doPivot()

class RunPivot(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)

    def tearDown(self, actor, nextAction):
        actor.flip()
        
    def stateTransitions(self, actor):
        if actor.keyHeld('jump', self.frame):
            actor.doJump()
        
    def update(self,actor):
        if actor.grounded is False:
            actor.doFall()
        if self.frame != self.lastFrame:
            self.frame += 1
            actor.preferred_xspeed = 0
        if self.frame == self.lastFrame:
            (key, _) = actor.getForwardBackwardKeys()
            if actor.keysContain(key):
                if actor.facing == 1:
                    actor.doDash(0)
                else:
                    actor.doDash(180)
            else:
                actor.doIdle()

class RunStop(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)
        
    def update(self, actor):
        actor.preferred_xspeed = 0
        self.frame += 1
        
    def stateTransitions(self, actor):
        if actor.grounded is False:
            actor.doFall()
        (key,invkey) = actor.getForwardBackwardKeys()
        if actor.keyHeld(key,self.frame):
            print("run")
            actor.doRun(actor.getFacingDirection())
        if actor.keyHeld(invkey,self.frame):
            print("run pivot")
            actor.doRunPivot()

                
class NeutralAction(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)

    def update(self, actor):
        pass
    
    def stateTransitions(self, actor):
        if actor.grounded is False:
            actor.doFall()
        neutralState(actor)

class Crouch(action.Action):
    def __init__(self, length):
        action.Action.__init__(self, length)
        self.direction = -1

    def setUp(self, actor):
        self.direction = actor.getForwardWithOffset(0)

    def stateTransitions(self, actor):
        crouchState(actor)
        if actor.grounded is False:
            actor.doFall()
        if self.frame > 0 and actor.keyBuffered('down', 1, state = 1):
            blocks = actor.checkForGround()
            if blocks:
                #Turn it into a list of true/false if the block is solid
                blocks = map(lambda x:x.solid,blocks)
                #If none of the ground is solid
                if not any(blocks):
                    actor.doPlatformDrop()

    def tearDown(self, actor, nextAction):
        actor.preferred_xspeed = 0

    def update(self, actor):
        if actor.grounded is False:
            actor.doFall()
        actor.accel(actor.var['staticGrip'])
        (key, invkey) = actor.getForwardBackwardKeys()
        if actor.keysContain(key):
            actor.preferred_xspeed = actor.var['crawlSpeed']*actor.facing
        elif actor.keysContain(invkey):
            actor.preferred_xspeed = -actor.var['crawlSpeed']*actor.facing
        else:
            actor.preferred_xspeed = 0
        
        self.frame += 1
        if self.frame > self.lastFrame: self.frame = 0

class CrouchGetup(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)

    def stateTransitions(self, actor):
        if actor.grounded is False:
            actor.doFall()
        elif actor.keyBuffered('down', 1, state = 1):
            blocks = actor.checkForGround()
            if blocks:
                #Turn it into a list of true/false if the block is solid
                blocks = map(lambda x:x.solid,blocks)
                #If none of the ground is solid
                if not any(blocks):
                    actor.doPlatformDrop()

    def update(self, actor):
        actor.preferred_xspeed = 0
        self.frame += 1
        if self.frame >= self.lastFrame:
            actor.doIdle()

class BaseGrabbing(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)

    def tearDown(self, actor, newAction):
        if not isinstance(newAction, BaseGrabbing) and actor.isGrabbing():
            actor.grabbing.doIdle()

class Grabbing(BaseGrabbing):
    def __init__(self,length):
        BaseGrabbing.__init__(self, length)

    def stateTransitions(self, actor):
        if actor.grounded is False:
            actor.doFall()
        grabbingState(actor)
        
class HitStun(action.Action):
    def __init__(self,hitstun,direction,hitstop):
        action.Action.__init__(self, hitstun)
        self.direction = direction
        self.hitstop = hitstop

    def setUp(self, actor):
        actor.elasticity = actor.var['hitstunElasticity']

    def stateTransitions(self, actor):
        (direct,_) = actor.getDirectionMagnitude()
        if actor.keyBuffered('shield', 1) and self.frame < self.lastFrame:
            actor.doTryTech(self.lastFrame-self.frame, self.direction, self.hitstop)
        if self.frame >= self.lastFrame:
            tumbleState(actor)
            actor.elasticity = actor.var['hitstunElasticity']/2
        else:
            actor.elasticity = actor.var['hitstunElasticity']
            if self.frame > 2:
                hitstunLanding(actor)
        if self.frame > 2:
            if self.frame >= self.lastFrame and actor.change_y >= actor.var['maxFallSpeed']:#Hard landing during tumble
                actor.ground_elasticity = actor.var['hitstunElasticity']/2
            elif self.frame < self.lastFrame and actor.change_y >= actor.var['maxFallSpeed']: #Hard landing during hitstun
                actor.ground_elasticity = actor.var['hitstunElasticity']
            elif abs(actor.change_x) > actor.var['runSpeed']: #Skid trip
                actor.ground_elasticity = 0
                if actor.grounded:
                    actor.doTrip(self.lastFrame-self.frame, direct)
            elif self.frame >= self.lastFrame and actor.change_y < actor.var['maxFallSpeed']/2: #Soft landing during tumble
                actor.landingLag = self.lastFrame-self.frame+actor.var['heavyLandLag']//2
                actor.ground_elasticity = 0
            elif self.frame >= self.lastFrame: #Firm landing during tumble
                actor.landingLag = actor.var['heavyLandLag']
                actor.ground_elasticity = 0
            elif actor.change_y < actor.var['maxFallSpeed']//2: #Soft landing during hitstun
                actor.landingLag = actor.var['heavyLandLag']+self.lastFrame-self.frame
                actor.ground_elasticity = 0
            else: #Firm landing during hitstun
                actor.ground_elasticity = actor.var['hitstunElasticity']/2
        
    def tearDown(self, actor, newAction):
        actor.unRotate()
        actor.elasticity = 0
        actor.ground_elasticity = 0
        
    def update(self,actor):
        if self.frame == 0:
            (direct,mag) = actor.getDirectionMagnitude()
            print("direction:", direct)
            if direct != 0 and direct != 180:
                actor.grounded = False
                if mag > 10:
                    actor.rotateSprite(self.direction)
            actor.hitstop = self.hitstop
            if actor.grounded:
                actor.hitstopVibration = (3,0)
            else:
                actor.hitstopVibration = (0,3)
            actor.hitstopPos = actor.rect.center
        if self.frame % 15 == 10 and self.frame < self.lastFrame:
            if abs(actor.change_x) > 8 or abs(actor.change_y) > 8:
                art = article.AnimatedArticle(settingsManager.createPath('sprites/circlepuff.png'),actor,actor.rect.center,86,6)
                art.angle = actor.sprite.angle
                if actor.hitTagged and hasattr(actor.hitTagged, 'playerNum'):
                    for image in art.imageList:
                        art.recolor(image, [255,255,255], pygame.Color(settingsManager.getSetting('playerColor' + str(actor.hitTagged.playerNum))))
                actor.articles.add(art)
                    
        if self.frame == self.lastFrame:
            actor.unRotate()
            #Tumbling continues indefinetely, but can be cancelled out of

        self.frame += 1

class TryTech(HitStun):
    def __init__(self, hitstun, direction, hitstop):
        HitStun.__init__(self, hitstun, direction, hitstop)

    def stateTransitions(self, actor):
        (direct,mag) = actor.getDirectionMagnitude()
        if self.frame == 0:
            actor.elasticity = 0
        if self.frame < 20 and actor.grounded:
            print('Ground tech!')
            actor.unRotate()
            actor.doTrip(-175, direct)
        if self.frame >= 20:
            if self.frame >= self.lastFrame:
                tumbleState(actor)
                actor.elasticity = actor.var['hitstunElasticity']/2
            else:
                hitstunLanding(actor)
                actor.elasticity = actor.var['hitstunElasticity']
            if self.frame >= self.lastFrame and actor.change_y >= actor.var['maxFallSpeed']:#Hard landing during tumble
                actor.ground_elasticity = actor.var['hitstunElasticity']/2
            elif self.frame < self.lastFrame and actor.change_y >= actor.var['maxFallSpeed']: #Hard landing during hitstun
                actor.ground_elasticity = actor.var['hitstunElasticity']
            elif abs(actor.change_x) > actor.var['runSpeed']: #Skid trip
                actor.ground_elasticity = 0
                if actor.grounded:
                    actor.doTrip(self.lastFrame-self.frame, direct)
            elif self.frame >= self.lastFrame and actor.change_y < actor.var['maxFallSpeed']/2: #Soft landing during tumble
                actor.landingLag = self.lastFrame-self.frame+actor.var['heavyLandLag']//2
                actor.ground_elasticity = 0
            elif self.frame >= self.lastFrame: #Firm landing during tumble
                actor.landingLag = actor.var['heavyLandLag']
                actor.ground_elasticity = 0
            elif actor.change_y < actor.var['maxFallSpeed']//2: #Soft landing during hitstun
                actor.landingLag = actor.var['heavyLandLag']+self.lastFrame-self.frame
                actor.ground_elasticity = 0
            else: #Firm landing during hitstun
                actor.ground_elasticity = actor.var['hitstunElasticity']/2

    def update(self, actor):
        if self.frame >= 40:
            actor.doHitStun(self.lastFrame-self.frame, self.direction,0)
        HitStun.update(self, actor)

class Trip(action.Action):
    def __init__(self,length,direction):
        action.Action.__init__(self, length)
        self.direction = direction
        print("direction:", self.direction)

    def setUp(self, actor):
        actor.invincible = 5
        actor.rect.bottom = actor.ecb.currentECB.rect.bottom

    def update(self, actor):
        if actor.grounded is False:
            actor.doHitStun(self.lastFrame-self.frame, self.direction,0)
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

    def stateTransitions(self, actor):
        if actor.keyHeld('attack') and actor.checkSmash('up') and self.frame < self.jumpFrame:
            print("Jump cancelled into up smash")
            actor.doGroundAttack()
        elif actor.keyHeld('special') and actor.checkSmash('up') and self.frame < self.jumpFrame:
            print("Jump cancelled into up special")
            actor.doGroundAttack()
        elif self.frame > self.jumpFrame+2:
            jumpState(actor)
        
    def update(self,actor):
        if self.frame == self.jumpFrame:
            actor.grounded = False
            if actor.keysContain('jump'):
                actor.change_y = -actor.var['jumpHeight']
            else: actor.change_y = -actor.var['shortHopHeight']
            if actor.change_x > actor.var['maxAirSpeed']:
                actor.change_x = actor.var['maxAirSpeed']
            elif actor.change_x < -actor.var['maxAirSpeed']:
                actor.change_x = -actor.var['maxAirSpeed']
        if self.frame < self.lastFrame:
            self.frame += 1
        if self.frame == self.lastFrame and not actor.keysContain('jump'):
            actor.doFall()

class AirJump(action.Action):
    def __init__(self,length,jumpFrame):
        action.Action.__init__(self, length)
        self.jumpFrame = jumpFrame
        #TODO: Change to add the number of buffer frames

    def stateTransitions(self, actor):
        jumpState(actor)

    def tearDown(self, actor, nextAction):
        actor.preferred_yspeed = actor.var['maxFallSpeed']
        
    def update(self,actor):
        if self.frame < self.jumpFrame:
            actor.change_y = 0
            actor.preferred_yspeed = 0
        if self.frame == self.jumpFrame:
            actor.grounded = False
            actor.change_y = -actor.var['airJumpHeight']
            actor.jumps -= 1
            if actor.keysContain('left'):
                if actor.facing == 1:
                    actor.flip()
                    actor.change_x = actor.facing * actor.var['maxAirSpeed']
            elif actor.keysContain('right'):
                if actor.facing == -1:
                    actor.flip()
                    actor.change_x = actor.facing * actor.var['maxAirSpeed']    
        if self.frame < self.lastFrame:
            self.frame += 1
        if self.frame == self.lastFrame and not actor.keysContain('jump'):
            actor.doFall()
        
class Fall(action.Action):
    def __init__(self):
        action.Action.__init__(self, 1)

    def setUp(self, actor):
        actor.preferred_xspeed = 0
        actor.preferred_yspeed = actor.var['maxFallSpeed']
    
    def stateTransitions(self,actor):
        airState(actor)
        grabLedges(actor)
        
    def update(self,actor):
        actor.grounded = False

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

    def setUp(self, actor):
        actor.rect.bottom = actor.ecb.currentECB.rect.bottom

    def tearDown(self, actor, nextAction):
        actor.preferred_xspeed = 0

    def update(self,actor):
        if self.frame == 0:
            actor.preferred_yspeed = actor.var['maxFallSpeed']
            self.lastFrame = actor.landingLag
            if actor.keyHeld('shield', 1):
                print("l-cancel")
                self.lastFrame = self.lastFrame // 2
        if actor.keyHeld('down'):
            blocks = actor.checkForGround()
            if blocks:   
                blocks = map(lambda x: x.solid, blocks)
                if not any(blocks):
                    actor.doPlatformDrop()
        if self.frame == 1:
            #actor.articles.add(article.LandingArticle(actor)) #this looks awful don't try it
            pass
        if self.frame >= self.lastFrame:
            actor.landingLag = actor.var['heavyLandLag']
            actor.doIdle()
            actor.platformPhase = 0
            actor.preferred_xspeed = 0
        self.frame+= 1

class HelplessLand(action.Action):
    def __init__(self):
        action.Action.__init__(self, 6)

    def setUp(self, actor):
        actor.rect.bottom = actor.ecb.currentECB.rect.bottom

    def update(self,actor):
        if self.frame == 0:
            actor.change_y = 0
            actor.preferred_yspeed = actor.var['maxFallSpeed']
            self.lastFrame = actor.landingLag
            if actor.keyHeld('shield', 20):
                print("l-cancel")
                self.lastFrame = self.lastFrame // 2
        if actor.keyHeld('down', 8):
            blocks = actor.checkForGround()
            if blocks:
                blocks = map(lambda x: x.solid, blocks)
                if not any(blocks):
                    actor.doPlatformDrop()
        if self.frame >= self.lastFrame:
            actor.landingLag = 6
            actor.doIdle()
            actor.platformPhase = 0
            actor.preferred_xspeed = 0
        self.frame += 1

class PlatformDrop(action.Action):
    def __init__(self, length, phaseFrame, phaseLength):
        action.Action.__init__(self, length)
        self.phaseFrame = phaseFrame
        self.phaseLength = phaseLength

    def stateTransitions(self, actor):
        if actor.keyHeld('attack') and actor.checkSmash('down') and self.frame < self.phaseFrame:
            print("Platform drop cancelled into down smash")
            actor.doGroundAttack()
        elif actor.keyHeld('special') and actor.checkSmash('down') and self.frame < self.phaseFrame:
            print("Platform drop cancelled into down special")
            actor.doGroundSpecial()
    
    def update(self,actor):
        if self.frame == self.phaseFrame:
            actor.platformPhase = self.phaseLength
        if self.frame == self.lastFrame:
            actor.doFall()
        self.frame += 1
        
class PreShield(action.Action):
    def __init__(self):
        action.Action.__init__(self, 4)

    def setUp(self, actor):
        self.reflectHitbox = hitbox.PerfectShieldHitbox([0,0], [actor.hurtbox.rect.width+10, actor.hurtbox.rect.height+10], actor, hitbox.HitboxLock())

    def tearDown(self, actor, nextAction):
        self.reflectHitbox.kill()

    def stateTransitions(self, actor):
        shieldState(actor)

    def update(self, actor):
        if self.frame == 0:
            actor.active_hitboxes.add(self.reflectHitbox)
        if actor.grounded is False:
            self.reflectHitbox.kill()
            actor.doFall()
        if self.frame == self.lastFrame:
            self.reflectHitbox.kill()
            actor.doShield()
        self.frame += 1

class Shield(action.Action):
    def __init__(self):
        action.Action.__init__(self, 4)
   
    def stateTransitions(self, actor):
        shieldState(actor)
   
    def tearDown(self, actor, newAction):
        if not isinstance(newAction, ShieldStun):
            actor.shield = False
       
    def update(self, actor):
        if actor.grounded is False:
            actor.shield = False
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
        elif self.frame >= 2 and self.frame < self.lastFrame:
            actor.shield = False
            self.frame += 1
        elif self.frame >= self.lastFrame:
            actor.doIdle()
        else: self.frame += 1

class ShieldStun(action.Action):
    def __init__(self, length):
        action.Action.__init__(self, length)

    def tearDown(self, actor, newAction):
        if not isinstance(newAction, Shield) and not isinstance(newAction, ShieldStun):
            actor.shield = False

    def update(self, actor):
        if actor.grounded is False:
            actor.shield = False
            actor.doFall()
        if self.frame >= self.lastFrame and actor.keysContain('shield'):
            actor.doShield()
        elif self.frame >= self.lastFrame:
            actor.doIdle()
        self.frame += 1

class Stunned(action.Action):
    def __init__(self, length):
        action.Action.__init__(self, length)

    def update(self, actor):
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1

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
            self.lastFrame = 40 + actor.damage//2
        if (self.height > actor.rect.height):
            actor.rect.top = actor.grabbedBy.rect.bottom-self.height
        else:
            actor.rect.bottom = actor.grabbedBy.rect.bottom
        actor.rect.centerx = actor.grabbedBy.rect.centerx+actor.grabbedBy.facing*actor.grabbedBy.rect.width/2.0
        Trapped.update(self, actor)
        
class Release(action.Action):
    def __init__(self):
        action.Action.__init__(self,5)

    def update(self, actor):
        if actor.grounded is False:
            actor.doFall()
        if self.frame == self.lastFrame:
            actor.doIdle()
        self.frame += 1
        
class ForwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 46)
        self.startInvulnFrame = 6
        self.endInvulnFrame = 34

    def tearDown(self, actor, nextAction):
        actor.preferred_xspeed = 0
        if actor.invulnerable > 0:
            actor.invulnerable = 0
        actor.mask = None
        
    def update(self, actor):
        if actor.grounded is False:
            actor.doFall()
        if self.frame == 1:
            actor.change_x = actor.facing * actor.var['dodgeSpeed']
        elif self.frame == self.startInvulnFrame:
            actor.createMask([255,255,255], 22, True, 24)
            actor.invulnerable = self.endInvulnFrame-self.startInvulnFrame
        elif self.frame == self.endInvulnFrame:
            actor.flip()
            actor.change_x = 0
        elif self.frame == self.lastFrame:
            if actor.keyHeld('shield'):
                actor.doShield()
            else:
                actor.doIdle()
        self.frame += 1

class BackwardRoll(action.Action):
    def __init__(self):
        action.Action.__init__(self, 50)
        self.startInvulnFrame = 6
        self.endInvulnFrame = 34

    def tearDown(self, actor, nextAction):
        actor.preferred_xspeed = 0
        if actor.invulnerable > 0:
            actor.invulnerable = 0
        actor.mask = None
        
    def update(self, actor):
        if actor.grounded is False:
            actor.doFall()
        if self.frame == 1:
            actor.change_x = actor.facing * -actor.var['dodgeSpeed']
        elif self.frame == self.startInvulnFrame:
            actor.createMask([255,255,255], 22, True, 24)
            actor.invulnerable = self.endInvulnFrame-self.startInvulnFrame
        elif self.frame == self.endInvulnFrame:
            actor.change_x = 0
        elif self.frame == self.lastFrame:
            if actor.keyHeld('shield'):
                actor.doShield()
            else:
                actor.doIdle()
        self.frame += 1
        
class SpotDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
        self.startInvulnFrame = 4
        self.endInvulnFrame = 20

    def tearDown(self, actor, nextAction):
        actor.preferred_xspeed = 0
        if actor.invulnerable > 0:
            actor.invulnerable = 0
        actor.mask = None
        
    def update(self,actor):
        if actor.grounded is False:
            actor.doFall()
        elif actor.keyBuffered('down', 1) and self.frame > 0:
            blocks = actor.checkForGround()
            if blocks:
                blocks = map(lambda x:x.solid,blocks)
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
            if actor.keyHeld('shield'):
                actor.doShield()
            else:
                actor.doIdle()
        self.frame += 1
        
class AirDodge(action.Action):
    def __init__(self):
        action.Action.__init__(self, 24)
        self.startInvulnFrame = 4
        self.endInvulnFrame = 20
        self.move_vec = [0,0]
    
    def setUp(self,actor):
        if settingsManager.getSetting('enableWavedash'):
            actor.landingLag = 16
        else:
            actor.landingLag = 24
        if settingsManager.getSetting('airDodgeType') == 'directional':
            self.move_vec = actor.getSmoothedInput()
            actor.change_x = self.move_vec[0]*actor.var['dodgeSpeed']
            actor.change_y = self.move_vec[1]*actor.var['dodgeSpeed']
        
    def tearDown(self,actor,other):
        if settingsManager.getSetting('airDodgeType') == 'directional':
            actor.preferred_yspeed = actor.var['maxFallSpeed']
            actor.preferred_xspeed = 0
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
                actor.preferred_xspeed = actor.change_x
                actor.preferred_yspeed = actor.change_y
            elif self.frame >= 16:
                actor.change_x = 0
                actor.change_y = 0
                actor.preferred_xspeed = 0
                actor.preferred_yspeed = 0
            elif self.frame == self.lastFrame:
                actor.preferred_yspeed = actor.var['maxFallSpeed']
                
        if self.frame == self.startInvulnFrame:
            actor.createMask([255,255,255],16,True,24)
            actor.invulnerable = self.endInvulnFrame-self.startInvulnFrame
        elif self.frame == self.endInvulnFrame:
            actor.landingLag = 24
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
        (direct) = actor.getDirectionMagnitude()
        if self.frame < 20 and actor.grounded:
            print('Ground tech!')
            actor.unRotate()
            actor.doTrip(-175, direct)
        AirDodge.stateTransitions(self, actor)
        
class LedgeGrab(action.Action):
    def __init__(self,ledge):
        action.Action.__init__(self, 1)
        self.ledge = ledge

    def setUp(self, actor):
        actor.createMask([255,255,255], settingsManager.getSetting('ledgeInvincibilityTime'), True, 12)
        actor.invulnerable = settingsManager.getSetting('ledgeInvincibilityTime')
        
    def tearDown(self,actor,newAction):
        self.ledge.fighterLeaves(actor)
        
    def stateTransitions(self,actor):
        ledgeState(actor)
        
    def update(self,actor):
        actor.jumps = actor.var['jumps']
        actor.setSpeed(0, actor.getFacingDirection())

class LedgeGetup(action.Action):
    def __init__(self, length):
        action.Action.__init__(self, length)

    def setUp(self, actor):
        if actor.facing == 1:
            actor.rect.left -= actor.rect.width//2
        else:
            actor.rect.right += actor.rect.width//2
    
    def update(self,actor):
        if self.frame >= self.lastFrame:
            actor.doIdle()
        self.frame += 1

########################################################
#               TRANSITION STATES                     #
########################################################
def neutralState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.keyHeld('shield'):
        actor.doPreShield()
    elif actor.keyHeld('attack'):
        actor.doGroundAttack()
    elif actor.keyHeld('special'):
        actor.doGroundSpecial()
    elif actor.keyHeld('jump'):
        actor.doJump()
    elif actor.keysContain('down', 0.5):
        actor.doCrouch()
    elif actor.keysContain(invkey):
        actor.doGroundMove(actor.getForwardWithOffset(180))
    elif actor.keysContain(key):
        actor.doGroundMove(actor.getForwardWithOffset(0))

def crouchState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.keyHeld('shield'):
        if actor.keysContain(invkey):
            actor.doBackwardRoll()
        elif actor.keysContain(key):
            actor.doForwardRoll()
        else:
            actor.doSpotDodge()
    if actor.keyHeld('attack'):
        actor.doGroundAttack()
    elif actor.keyHeld('special'):
        actor.doGroundSpecial()
    elif actor.keyHeld('jump'):
        actor.doJump()
    elif not actor.keysContain('down'):
        actor.doCrouchGetup()

def airState(actor):
    airControl(actor)
    if actor.keyHeld('shield'):
        actor.doAirDodge()
    elif actor.keyHeld('attack'):
        actor.doAirAttack()
    elif actor.keyHeld('special'):
        actor.doAirSpecial()
    elif actor.keyHeld('jump') and actor.jumps > 0:
        actor.doAirJump()
    elif actor.keysContain('down'):
        actor.platformPhase = 1
        actor.calc_grav(actor.var['fastfallMultiplier'])

def tumbleState(actor):
    airControl(actor)
    if actor.keyHeld('shield'):
        actor.doTechDodge()
    elif actor.keyHeld('attack'):
        actor.doAirAttack()
    elif actor.keyHeld('special'):
        actor.doAirSpecial()
    elif actor.keyHeld('jump') and actor.jumps > 0:
        actor.doAirJump()
    elif actor.keysContain('down'):
        actor.platformPhase = 1
        actor.calc_grav(actor.var['fastfallMultiplier'])
            
def moveState(actor, direction):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.keyHeld('shield') and actor.keyHeld('attack'):
        actor.doGroundGrab()
    elif actor.keyHeld('attack'):
        actor.doGroundAttack()
    elif actor.keyHeld('special'):
        actor.doGroundSpecial()
    elif actor.keyHeld('jump'):
        actor.doJump()
    elif actor.keysContain('down', 0.5):
        actor.doCrouch()
    elif not actor.keysContain('left') and not actor.keysContain('right') and not actor.keysContain('down'):
        actor.doStop()
    elif actor.preferred_xspeed < 0 and not actor.keysContain('left',1) and actor.keysContain('right',1):
        actor.doStop()
    elif actor.preferred_xspeed > 0 and not actor.keysContain('right',1) and actor.keysContain('left',1):
        actor.doStop()

def dashState(actor, direction):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.keysContain('shield') and actor.keyHeld('attack'):
        actor.doDashGrab()
    elif actor.keyHeld('attack'):
        if actor.checkSmash(key):
            print("Dash cancelled into forward smash")
            actor.doGroundAttack()
        else:
            actor.doDashAttack()
    elif actor.keyHeld('special'):
        actor.doGroundSpecial()
    elif actor.keyHeld('jump'):
        actor.doJump()
    elif actor.keysContain('down', 0.5):
        actor.doStop()
    elif not actor.keysContain('left') and not actor.keysContain('right') and not actor.keysContain('down'):
        actor.doStop()
    elif actor.preferred_xspeed < 0 and not actor.keysContain('left',1) and actor.keysContain('right',1):
        actor.doStop()
    elif actor.preferred_xspeed > 0 and not actor.keysContain('right',1) and actor.keysContain('left',1):
        actor.doStop()

def runState(actor, direction):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.keysContain('shield') and actor.keyHeld('attack'):
        actor.doDashGrab()
    elif actor.keyHeld('attack'):
        actor.doDashAttack()
    elif actor.keyHeld('special'):
        actor.doGroundSpecial()
    elif actor.keyHeld('jump'):
        actor.doJump()
    elif actor.keysContain('down', 0.5):
        actor.doRunStop()
    elif not actor.keysContain('left') and not actor.keysContain('right') and not actor.keysContain('down'):
        actor.doRunStop()
    elif actor.preferred_xspeed < 0 and not actor.keysContain('left',1) and actor.keysContain('right',1):
        actor.doRunStop()
    elif actor.preferred_xspeed > 0 and not actor.keysContain('right',1) and actor.keysContain('left',1):
        actor.doRunStop()

def jumpState(actor):
    airControl(actor)
    if actor.keyHeld('shield'):
        actor.doAirDodge()
    elif actor.keyHeld('attack'):
        actor.doAirAttack()
    elif actor.keyHeld('special'):
        actor.doAirSpecial()
    elif actor.keysContain('down'):
        actor.platformPhase = 1
        actor.calc_grav(actor.var['fastfallMultiplier'])
            
def shieldState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    if actor.keyHeld('attack'):
        actor.doGroundGrab()
    elif actor.keyHeld('jump'):
        actor.doJump()
    elif actor.keyHeld(key):
        actor.doForwardRoll()
    elif actor.keyHeld(invkey):
        actor.doBackwardRoll()
    elif actor.keyHeld('down'):
        actor.doSpotDodge()

def ledgeState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    actor.setSpeed(0, actor.getFacingDirection())
    if actor.keyHeld('shield'):
        actor.ledgeLock = True
        actor.doLedgeRoll()
    elif actor.keyHeld('attack'):
        actor.ledgeLock = True
        actor.doLedgeAttack()
    elif actor.keyHeld('jump'):
        actor.ledgeLock = True
        actor.doJump()
    elif actor.keyBuffered(key):
        actor.ledgeLock = True
        actor.doLedgeGetup()
    elif actor.keyBuffered(invkey):
        actor.ledgeLock = True
        actor.doFall()
    elif actor.keyBuffered('down'):
        actor.ledgeLock = True
        actor.doFall()

def grabbingState(actor):
    (key,invkey) = actor.getForwardBackwardKeys()
    # Check to see if they broke out
    # If they did, release them
    if not actor.isGrabbing():
        actor.doRelease()
    elif actor.keyHeld('shield', 0):
        actor.doRelease()
    elif actor.keyHeld('attack', 0):
        actor.doPummel()
    elif actor.keyHeld(key):
        actor.doThrow()
    elif actor.keyHeld(invkey):
        actor.doThrow()
    elif actor.keyHeld('up'):
        actor.doThrow()
    elif actor.keyHeld('down'):
        actor.doThrow()

def tripState(actor, direction):
    (key, invkey) = actor.getForwardBackwardKeys()
    if actor.keyHeld('attack'):
        actor.doGetupAttack(direction)
    elif actor.keyHeld('up'):
        actor.doGetup(direction)
    elif actor.keyHeld(key):
        actor.doForwardRoll()
    elif actor.keyHeld(invkey):
        actor.doBackwardRoll()
    elif actor.keyHeld('down'):
        actor.doSpotDodge()

########################################################
#             BEGIN HELPER METHODS                     #
########################################################

def airControl(actor):
    if actor.keysContain('left'):
        actor.preferred_xspeed = -actor.var['maxAirSpeed']
    elif actor.keysContain('right'):
        actor.preferred_xspeed = actor.var['maxAirSpeed']
    
    if (actor.change_x < 0) and not actor.keysContain('left'):
        actor.preferred_xspeed = 0
    elif (actor.change_x > 0) and not actor.keysContain('right'):
        actor.preferred_xspeed = 0

    if actor.change_y >= actor.var['maxFallSpeed'] and actor.landingLag < actor.var['heavyLandLag']:
        actor.landingLag = actor.var['heavyLandLag']

    if actor.grounded and actor.ground_elasticity == 0:
        actor.preferred_xspeed = 0
        actor.preferred_yspeed = actor.var['maxFallSpeed']
        actor.doLand()

def helplessControl(actor):
    if actor.keysContain('left'):
        actor.preferred_xspeed = -actor.var['maxAirSpeed']
    elif actor.keysContain('right'):
        actor.preferred_xspeed = actor.var['maxAirSpeed']
    
    if (actor.change_x < 0) and not actor.keysContain('left'):
        actor.preferred_xspeed = 0
    elif (actor.change_x > 0) and not actor.keysContain('right'):
        actor.preferred_xspeed = 0

    if actor.change_y >= actor.var['maxFallSpeed'] and actor.landingLag < actor.var['heavyLandLag']:
        actor.landingLag = actor.var['heavyLandLag']

    if actor.grounded and actor.ground_elasticity == 0:
        actor.preferred_xspeed = 0
        actor.preferred_yspeed = actor.var['maxFallSpeed']
        actor.doHelplessLand()

def hitstunLanding(actor):
    if actor.grounded and actor.ground_elasticity == 0:
        actor.preferred_xspeed = 0
        actor.preferred_yspeed = actor.var['maxFallSpeed']
        actor.doLand()

def grabLedges(actor):
    # Check if we're colliding with any ledges.
    if not actor.ledgeLock: #If we're not allowed to re-grab, don't bother calculating
        ledge_hit_list = pygame.sprite.spritecollide(actor, actor.gameState.platform_ledges, False)
        for ledge in ledge_hit_list:
            # Don't grab any ledges if the actor is holding down
            if actor.keysContain('down') is False:
                # If the ledge is on the left side of a platform, and we're holding right
                if ledge.side == 'left' and actor.keysContain('right'):
                    ledge.fighterGrabs(actor)
                elif ledge.side == 'right' and actor.keysContain('left'):
                    ledge.fighterGrabs(actor)
