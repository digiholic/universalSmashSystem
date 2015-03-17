import pygame
import math
import spriteObject

class Fighter():
    
    def __init__(self,
                 sprite,
                 name,
                 weight,
                 gravity,
                 maxFallSpeed,
                 maxRunSpeed,
                 maxAirSpeed,
                 groundFriction,
                 airControl,
                 jumps,
                 jumpHeight,
                 airJumpHeight):
        
        self.sprite = spriteObject.SheetSprite(sprite,[0,0],92)
        self.currentKeys = []
        self.inputBuffer = [[],[],[],[],[],[]]
        self.keysHeld = []
        
        #initialize important variables
        self.gravity = gravity
        self.maxJumps = jumps
        self.jumpHeight = jumpHeight
        self.airJumpHeight = airJumpHeight
        self.groundFriction = groundFriction
        self.airControl = airControl
        self.maxRunSpeed = maxRunSpeed
        self.maxAirSpeed = maxAirSpeed
        self.angle = 0
        
        #initialize the action list
        self.current_action = None
        
        #state variables and flags
        self.grounded = False
        self.rect = self.sprite.rect
        self.jumps = self.maxJumps
        self.damage = 0
        self.landingLag = 6
        
        self.change_x = 0
        self.change_y = 0
        self.preferred_xspeed = 0
        self.preferred_yspeed = 0
        
        #facing right = 1, left = -1
        self.facing = 1
        
        #list of all of the other things to worry about
        self.gameState = None
        
    def update(self):
        self.inputBuffer.pop()
        self.inputBuffer.insert(0, self.currentKeys)
        self.currentKeys = []
        
        #accelerate/decelerate
        if self.grounded: self.accel(self.groundFriction)
        else: self.accel(self.airControl)
        
        self.current_action.update(self) #update our action              
        
        # Gravity
        self.calc_grav()
        self.checkForGround()
                
        self.rect.x += self.change_x
        block_hit_list = pygame.sprite.spritecollide(self, self.gameState.platform_list, False)
        
        for block in block_hit_list:
            # If we are moving right,
            # set our right side to the left side of the item we hit
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                # Otherwise if we are moving left, do the opposite.
                self.rect.left = block.rect.right
        
        self.rect.y += self.change_y
        block_hit_list = pygame.sprite.spritecollide(self, self.gameState.platform_list, False)
        
        
        for block in block_hit_list:
 
            # Reset our position based on the top/bottom of the object.
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
 
            # Stop our vertical movement
            self.change_y = 0
            
        if self.rect.right < self.gameState.blast_line.left: self.die()
        if self.rect.left > self.gameState.blast_line.right: self.die()
        if self.rect.top > self.gameState.blast_line.bottom: self.die()
        if self.rect.bottom < self.gameState.blast_line.top: self.die()
        
        self.sprite.rect = self.rect
    
    def accel(self,xFactor):
        if self.change_x > self.preferred_xspeed: #if we're going too fast
            diff = self.change_x - self.preferred_xspeed
            self.change_x -= min(diff,xFactor)
        elif self.change_x < self.preferred_xspeed: #if we're going too slow
            diff = self.preferred_xspeed - self.change_x
            self.change_x += min(diff,xFactor)
            
    def calc_grav(self):
        """ Calculate effect of gravity. """
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += self.gravity
        
        # See if we are on the ground.
        #if self.rect.y >= self.gameState.size.height - self.rect.height and self.change_y >= 0:
            #self.change_y = 0
            #self.rect.y = self.gameState.size.height - self.rect.height
            #self.grounded = True
        if self.grounded: self.jumps = self.maxJumps
    
    def checkForGround(self):
        #Check if there's a platform below us to update the grounded flag 
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.gameState.platform_list, False)
        self.rect.y -= 2      
        if (len(platform_hit_list) > 0): self.grounded = True
        #elif self.rect.y >= self.gameState.size.height - self.rect.height and self.change_y >= 0:
            #self.change_y = 0
            #self.rect.y = self.gameState.size.height - self.rect.height
            #self.grounded = True
        else: self.grounded = False
    
    def keyPressed(self,key):
        self.currentKeys.append((key,True))
        self.keysHeld.append(key)
        return True
        
    def keyReleased(self,key):
        self.keysHeld.remove(key)
        self.inputBuffer.append((key,False))
        return True
    
    #Check the input buffer for the given key. If "Held" is set to True,
    #the function will check to make sure the key is still being held down at the time of execution.
    #If you are checking for a key release instead of a press, state can be set to False to check for a release.
    def bufferContains(self,key,held=False,state = True):
        keyCount = 0
        for buff in self.inputBuffer:
            if buff.count((key,state)):
                keyCount += 1
            if held:
                if buff.count((key,not state)):
                    keyCount -= 1
        return (keyCount >= 1)
    
    def die(self):
        print "DEAD"
        self.damage = 0
        self.change_x = 0
        self.change_y = 0
        self.jumps = self.maxJumps
        self.rect.midtop = self.gameState.size.midtop
        
    def doStop(self):
        return None
    
    def doGroundMove(self):
        return None
    
    def doLand(self):
        return None
    
    def doPivot(self):
        return None
    
    def doGroundJump(self):
        return None
    
    def doAirJump(self):
        return None
    
    def doNeutralAttack(self):
        return None
    
    def doAirAttack(self):
        return None
    
    def keysContain(self,key):
        return (self.currentKeys.count(key) != 0)    
    
    def flip(self):
        self.facing = -self.facing
        self.sprite.flipX()
        
    def dealDamage(self, damage):
        self.damage += damage
    
    def applyKnockback(self, kb, kbg, trajectory):
        self.change_x = 0
        self.change_y = 0
        totalKB = kb + kbg*self.damage
        #Directional Incluence
        if (trajectory < 45 or trajectory > 315) or (trajectory < 225 and trajectory > 135):
            if self.keysContain(pygame.K_UP):
                trajectory += 15
            if self.keysContain(pygame.K_DOWN):
                trajectory -= 15
        self.setSpeed(totalKB, trajectory)
    
    def draw(self,screen,offset,scale):
        #spriteObject.RectSprite(self.rect.topleft, self.rect.size).draw(screen)
        self.sprite.draw(screen,offset,scale)
        for hbox in self.current_action.hitboxes:
            offset = self.gameState.stageToScreen(hbox.rect)
            hbox.draw(screen,offset,scale)
        
    def setSpeed(self,speed,direction,preferred = True):
        vectors = getXYFromDM(direction,speed)
        x = vectors.pop(0)
        y = vectors.pop(0)
        #print x, " ", y
        if preferred:
            self.preferred_xspeed = x
            self.preferred_yspeed = y
        else:
            self.change_x = x
            self.change_y = y
        
    def rotateSprite(self,direction):
        self.angle += -direction
        self.sprite.image = pygame.transform.rotate(self.sprite.image,-direction)
        #self.rect = self.sprite.image.get_rect(center=self.rect.center)
        
        
    def unRotate(self):
        self.sprite.image = pygame.transform.rotate(self.sprite.image, -self.angle)
        #self.rect = self.sprite.image.get_rect(center=self.rect.center)
        self.angle = 0
    
        
#A helper function to get the X and Y magnitudes from the Direction and Magnitude of a trajectory
def getXYFromDM(direction,magnitude):
    rad = math.radians(direction)
    x = round(math.cos(rad) * magnitude,5)
    y = -round(math.sin(rad) * magnitude,5)
    return [x,y]