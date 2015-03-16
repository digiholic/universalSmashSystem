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
        
        #facing right = 1, left = -1
        self.facing = 1
        
        #list of all of the other things to worry about
        self.gameState = None
        
    def update(self):
        self.current_action.update(self) #update it              
        
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
        if   key == pygame.K_LEFT  and self.currentKeys.count(pygame.K_RIGHT): self.currentKeys.remove(pygame.K_RIGHT)
        elif key == pygame.K_RIGHT and self.currentKeys.count(pygame.K_LEFT):  self.currentKeys.remove(pygame.K_LEFT)
        self.currentKeys.append(key)
        return True
        
    def keyReleased(self,key):
        #This one can fail, if the key has been removed by a conflicting key (such as left/right)
        #Returns true if the key release was actually removed
        if self.currentKeys.count(key):
            self.currentKeys.remove(key)
            return True
        return False
    
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
        
    def setSpeed(self,speed,direction,accelerate=False,acceleration=0):
        vectors = getXYFromDM(direction,speed)
        x = vectors.pop(0)
        y = vectors.pop(0)
        #print x, " ", y
        if accelerate:
            self.change_x = x
            self.change_y = y
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