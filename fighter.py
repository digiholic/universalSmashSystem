import pygame
import baseActions
import math
import spriteObject


class Fighter():
    
    def __init__(self,
                 sprite,
                 name,
                 keybindings,
                 var):
        
        self.var = var
        
        #Initialize engine variables
        self.keyBindings = Keybindings(keybindings)
        self.sprite = spriteObject.SheetSprite(sprite,[0,0],92)
        self.currentKeys = []
        self.inputBuffer = InputBuffer()
        self.keysHeld = []
        
        #initialize the action
        self.current_action = None
        
        #state variables and flags
        self.angle = 0
        self.grounded = False
        self.rect = self.sprite.rect
        self.jumps = self.var['jumps']
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
        #Step one, push the input buffer
        self.inputBuffer.push()
        
        #Step two, accelerate/decelerate
        if self.grounded: self.accel(self.var['friction'])
        else: self.accel(self.var['airControl'])
        
        #Step three, change state and update
        self.current_action.stateTransitions(self)
        self.current_action.update(self) #update our action              
        self.gameState.active_hitboxes.add(self.current_action.hitboxes)
        
        # Gravity
        self.calc_grav()
        self.checkForGround()
        
        #Execute horizontal movement        
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
        
        #Execute vertial movement
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
        
        #Check for deaths    
        if self.rect.right < self.gameState.blast_line.left: self.die()
        if self.rect.left > self.gameState.blast_line.right: self.die()
        if self.rect.top > self.gameState.blast_line.bottom: self.die()
        if self.rect.bottom < self.gameState.blast_line.top: self.die()
        
        #Update Sprite
        self.sprite.rect = self.rect
    
    # Change speed to get closer to the preferred speed without going over.
    # xFactor - The factor by which to change xSpeed. Usually self.var['friction'] or self.var['airControl']
    def accel(self,xFactor):
        if self.change_x > self.preferred_xspeed: #if we're going too fast
            diff = self.change_x - self.preferred_xspeed
            self.change_x -= min(diff,xFactor)
        elif self.change_x < self.preferred_xspeed: #if we're going too slow
            diff = self.preferred_xspeed - self.change_x
            self.change_x += min(diff,xFactor)
    
    # Change ySpeed according to gravity.        
    def calc_grav(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += self.var['gravity']
            if self.change_y > self.var['maxFallSpeed']: self.change_y = self.var['maxFallSpeed']
       
        if self.grounded: self.jumps = self.var['jumps']
    
    # Check if the fighter is on the ground.
    # Returns True if fighter is grounded, False if airborne.
    def checkForGround(self):
        #Check if there's a platform below us to update the grounded flag 
        self.rect.y += 2
        platform_hit_list = pygame.sprite.spritecollide(self, self.gameState.platform_list, False)
        self.rect.y -= 2      
        if (len(platform_hit_list) > 0): self.grounded = True
        else: self.grounded = False
    
        
########################################################
#                  ACTION SETTERS                      #
########################################################
# These functions are meant to be overridden. They are
# provided so the baseActions can change the Fighter's
# actions. If you've changed any of the base actions
# for the fighter (including adding a sprite change)
# override the corresponding method and have it set
# an instance of your overridden action.

    def changeAction(self,newAction):
        newAction.setUp(self)
        self.current_action.tearDown(self)
        self.current_action = newAction
        
    def doIdle(self):
        self.changeAction(baseActions.NeutralAction())
        
    def doGroundMove(self,direction):
        if direction == 0: key = self.keyBindings.k_right
        else: key = self.keyBindings.k_left
        if (self.inputBuffer.contains(key, 12, andReleased = True)):
            self.current_action = baseActions.Run()
        
        self.changeAction(baseActions.Move())
    
    def doPivot(self):
        self.changeAction(baseActions.Pivot())
    
    def doStop(self):
        self.changeAction(baseActions.NeutralAction())
    
    def doLand(self):
        self.current_action = baseActions.Land()
    
    def doGroundJump(self):
        self.current_action = baseActions.Jump()
    
    def doAirJump(self):
        self.current_action = baseActions.AirJump()
    
    def doGroundAttack(self):
        return None
    
    def doAirAttack(self):
        return None
   
   
########################################################
#                  STATE CHANGERS                      #
########################################################
# These involve the game engine. They will likely be
# sufficient for your character implementation, although
# in a heavily modified game engine, these might no
# longer be relevant. Override only if you're changing
# the core functionality of the fighter system. Extend
# as you see fit, if you need to tweak sprites or
# set flags.
    
    def flip(self):
        self.facing = -self.facing
        self.sprite.flipX()
        
    def dealDamage(self, damage):
        self.damage += damage
    
    def applyKnockback(self, kb, kbg, trajectory):
        self.change_x = 0
        self.change_y = 0
        totalKB = (kb + kbg*self.damage) / self.var['weight']
        #Directional Incluence
        if (trajectory < 45 or trajectory > 315) or (trajectory < 225 and trajectory > 135):
            if self.keysContain(self.keyBindings.k_up):
                trajectory += 15
            if self.keysContain(self.keyBindings.k_down):
                trajectory -= 15
        self.setSpeed(totalKB, trajectory, False)
        self.preferred_xspeed = 0
        self.preferred_yspeed = 0
    
    def setSpeed(self,speed,direction,preferred = True):
        vectors = getXYFromDM(direction,speed)
        x = vectors.pop(0)
        y = vectors.pop(0)
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
    
    def die(self):
        self.damage = 0
        self.change_x = 0
        self.change_y = 0
        self.jumps = self.var['jumps']
        self.rect.midtop = self.gameState.size.midtop
        
    def changeSprite(self,newSprite,frame=0):
        self.sprite.changeImage(newSprite)
        if frame != 0: self.sprite.getImageAtIndex(frame)
        
    def changeSpriteImage(self,frame):
        self.sprite.getImageAtIndex(frame)

    
########################################################
#                 ENGINE FUNCTIONS                     #
########################################################
# These functions are not meant to be overridden, and
# likely won't need to be extended. Most of these are
# input/output related, and shouldn't be trifled with.
# Many of them reference outside variables, so 
# functionality can be changed by tweaking those values.
# Edit at your own risk.

    def keyPressed(self,key):
        self.inputBuffer.append((key,True))
        self.keysHeld.append(key)
        if key == self.keyBindings.k_left:
            if self.keysContain(self.keyBindings.k_right):
                self.keyReleased(self.keyBindings.k_right)
        elif key == self.keyBindings.k_right:
            if self.keysContain(self.keyBindings.k_left):
                self.keyReleased(self.keyBindings.k_left)
        
    def keyReleased(self,key):
        if self.keysContain(key):
            self.inputBuffer.append((key,False))
            self.keysHeld.remove(key)
            return True
        else: return False
    
    
    def bufferContains(self,key, distanceBack = 0, state=True, andReleased=False, notReleased=False):
        return self.inputBuffer.contains(key, distanceBack, state, andReleased, notReleased)
    
    #This checks for keys that are currently being held, whether or not they've actually been pressed recently.
    def keysContain(self,key):
        return (self.keysHeld.count(key) != 0)    
    
    #This returns a tuple of the key for forward, then backward
    def getForwardBackwardKeys(self):
        if self.facing == 1: return (self.keyBindings.k_right,self.keyBindings.k_left)
        else: return (self.keyBindings.k_left,self.keyBindings.k_right)
        
    def draw(self,screen,offset,scale):
        #spriteObject.RectSprite(self.rect.topleft, self.rect.size).draw(screen)
        self.sprite.draw(screen,offset,scale)
        for hbox in self.current_action.hitboxes:
            offset = self.gameState.stageToScreen(hbox.rect)
            hbox.draw(screen,offset,scale)
        
    #Gets the proper direction, adjusted for facing
    def getForwardWithOffset(self,offSet = 0):
        if self.facing == 1:
            return offSet
        else:
            return 180 - offSet
    
########################################################
#             STATIC HELPER FUNCTIONS                  #
########################################################
# Functions that don't require a fighter instance to use
        
#A helper function to get the X and Y magnitudes from the Direction and Magnitude of a trajectory
def getXYFromDM(direction,magnitude):
    rad = math.radians(direction)
    x = round(math.cos(rad) * magnitude,5)
    y = -round(math.sin(rad) * magnitude,5)
    return [x,y]

def getDirectionBetweenPoints(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    dx = x2 - x1
    dy = y2 - y1
    return (180 * math.atan2(dy, dx)) / math.pi 
    

########################################################
#                   KEYBINDINGS                        #
########################################################
class Keybindings():
    
    def __init__(self,keyBindings):
        self.keyBindings = keyBindings
        self.k_left = self.keyBindings.get('left',pygame.K_LEFT)
        self.k_right = self.keyBindings.get('right',pygame.K_RIGHT)
        self.k_up = self.keyBindings.get('up',pygame.K_UP)
        self.k_down = self.keyBindings.get('down',pygame.K_DOWN)
        self.k_jump = self.keyBindings.get('jump',pygame.K_UP)
        self.k_attack = self.keyBindings.get('attack',pygame.K_z)
        self.k_shield = self.keyBindings.get('shield',pygame.K_a)
        
        
########################################################
#                  INPUT BUFFER                        #
########################################################        
class InputBuffer():
    
    def __init__(self):
        self.buffer = [[]]
        self.workingBuff = []
        self.lastIndex = 0
      
    #Put an empty list at the head of the buffer. This is called at the head of every frame.
    #Inputs are pushed on to the list at index 0
    def push(self):
        self.buffer.append(self.workingBuff)
        self.workingBuff = []
        self.lastIndex += 1
        
    def contains(self,key, distanceBack = 0, state=True, andReleased=False, notReleased=False):
        js = [] #If the key shows up multiple times, we might need to check all of them.
        if distanceBack > self.lastIndex: distanceBack = self.lastIndex
        for i in range(self.lastIndex,(self.lastIndex - distanceBack - 1), -1):
            #first, check if the key exists in the distance.
            buff = self.buffer[i]
            if buff.count((key,state)):
                js.append(i)
                if not (andReleased or notReleased): return True #If we don't care whether it was released or not, we can return True now.
        
        #If it's not in there, return false.
        if len(js) == 0: return False
        #Note, if, for some stupid reason, both andReleased and notReleased are set, it will prioritize andReleased
        for j in js:
            for i in range(j,self.lastIndex+1):
                buff = self.buffer[i]
                if buff.count((key,not state)): #If we encounter the inversion of the key we're looking for
                    if andReleased: return True #If we're looking for a release, we found it
                    if notReleased: return False #If we're looking for a held, we didn't get it
        #If we go through the buffer up to the key press and we don't find its inversion...
        if andReleased: return False
        if notReleased: return True
        #... do the opposite of above.
        
        return False #This statement should never be reached. If you do, have a boolean.
                
    #Get a sub-buffer of N frames
    def getLastNFrames(self,n):
        retBuffer = []
        if n > self.lastIndex: n = self.lastIndex
        for i in range(self.lastIndex,self.lastIndex - n,-1):
            retBuffer.append(self.buffer[i])
        return retBuffer
    
    def append(self,key):
        self.workingBuff.append(key)