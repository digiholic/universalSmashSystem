import pygame
import action
import hitbox

            
class Move(action.Action):
    def __init__(self,length):
        action.Action.__init__(self,length)
        self.tags.append("run")
        self.interruptTags.append("jump")
        
    def update(self, actor):
        if actor.facing == 1: direction = 0
        else: direction = 180
        actor.setSpeed(actor.maxRunSpeed,direction)
        
        self.frame += 1
        if self.frame > self.lastFrame: self.frame = 0
        
class Pivot(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)
        self.tags.append("pivot")
        self.interruptTags.extend("jump")
        
    def update(self,actor):
        if self.frame != self.lastFrame:
            self.frame += 1
            actor.preferred_xspeed = 0
            
class Stop(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)
        self.interruptTags.append("jump")
    
    def update(self, actor):
        actor.preferred_xspeed = 0
        self.frame += 1
        
                
class NeutralAction(action.Action):
    def __init__(self,length):
        action.Action.__init__(self, length)
        self.interruptTags.append("ALL")
        
    def update(self, actor):
        return
    
class HitStun(action.Action):
    def __init__(self,hitstun,direction):
        action.Action.__init__(self, hitstun)
        self.direction = direction
    
    def update(self,actor):
        if self.frame == 0:
            actor.grounded = False
            actor.rotateSprite(self.direction)
            actor.preferred_xspeed = 0
            
        if self.frame == self.lastFrame:
            actor.unRotate()
            
        self.frame += 1

class Jump(action.Action):
    def __init__(self,length,jumpFrame):
        action.Action.__init__(self, length)
        self.tags.append("jump")
        self.jumpFrame = jumpFrame
        
    def update(self,actor):
        if self.frame == self.jumpFrame:
            actor.grounded = False
            actor.change_y = -actor.jumpHeight
            if actor.change_x > actor.maxAirSpeed:
                actor.change_x = actor.maxAirSpeed
            elif actor.change_x < -actor.maxAirSpeed:
                actor.change_x = -actor.maxAirSpeed
            
        self.frame += 1
        
class AirJump(action.Action):
    def __init__(self,length,jumpFrame):
        action.Action.__init__(self, length)
        self.tags.extend(["airjump","jump"])
        self.jumpFrame = jumpFrame
        
    def update(self,actor):
        if self.frame == 0:
            actor.jumps -= 1
        
        if self.frame < self.jumpFrame:
            actor.change_y = 0
        if self.frame == self.jumpFrame:
            actor.grounded = False
            actor.change_y = -actor.airJumpHeight
            
            if actor.bufferContains(pygame.K_LEFT):
                if actor.facing == 1:
                    actor.flip()
                    actor.change_x = actor.facing * actor.maxAirSpeed
            elif actor.bufferContains(pygame.K_RIGHT):
                if actor.facing == -1:
                    actor.flip()
                    actor.change_x = actor.facing * actor.maxAirSpeed    
        self.frame += 1
        
class Fall(action.Action):
    def __init__(self):
        action.Action.__init__(self, 1)
        self.interruptTags.extend(["jump","air-attack"])
        
    def update(self,actor):
        actor.grounded = False
        airControl(actor)
            
class Land(action.Action):
    def __init__(self):
        action.Action.__init__(self, 6)
        self.tags.append("land")
        
    def update(self,actor):
        self.lastFrame = actor.landingLag
        if self.frame == 4:
            self.interruptTags.extend(["shield","jab"])
        elif self.frame == self.lastFrame:
            actor.landingLag = 6
            self.interruptTags.append("run")
            if   actor.bufferContains(pygame.K_LEFT): actor.doGroundMove(-1)
            elif actor.bufferContains(pygame.K_RIGHT): actor.doGroundMove(1)
            else: actor.doIdle()
        actor.preferred_xspeed = 0
        self.frame+= 1

########################################################
#               TRANSITION STATES                     #
########################################################
def neutralState(actor):
    if actor.bufferContains(pygame.K_UP):
        actor.doJump()


########################################################
#             BEGIN HELPER METHODS                     #
########################################################

def airControl(actor):
    if actor.bufferContains(pygame.K_LEFT):
        actor.preferred_xspeed = -actor.maxAirSpeed
    elif actor.bufferContains(pygame.K_RIGHT):
        actor.preferred_xspeed = actor.maxAirSpeed
    
    if (actor.change_x < 0) and not actor.bufferContains(pygame.K_LEFT):
        actor.preferred_xspeed = 0
    elif (actor.change_x > 0) and not actor.bufferContains(pygame.K_RIGHT):
        actor.preferred_xspeed = 0
        
    actor.checkForGround()
    if actor.grounded:
        actor.doLand()