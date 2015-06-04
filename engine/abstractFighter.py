import pygame
import engine.baseActions as baseActions
import math
import settingsManager
import spriteManager
import engine.article as article

class AbstractFighter():
    
    def __init__(self,
                 playerNum,
                 sprite,
                 name,
                 var):
        
        self.var = var
        self.playerNum = playerNum
        
        #Initialize engine variables
        self.keyBindings = settingsManager.getSetting('controls_' + str(playerNum))
        self.currentKeys = []
        self.inputBuffer = InputBuffer()
        self.keysHeld = []
        
        self.sprite = sprite
        self.mask = None
        
        self.active_hitboxes = pygame.sprite.Group()
        self.articles = pygame.sprite.Group()
        
        self.shield = False
        self.shieldIntegrity = 100
        
        # HitboxLock is a list of hitboxes that will not hit the fighter again for a given amount of time.
        # Each entry in the list is in the form of (frames remaining, owner, hitbox ID)
        self.hitboxLock = []
        
        # When a fighter lets go of a ledge, he can't grab another one until he gets out of the area.
        self.ledgeLock = False
        
        #initialize the action
        self.current_action = None
        self.hurtbox = spriteManager.RectSprite(self.sprite.boundingRect,[255,255,0])
        
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
        
        for lock in self.hitboxLock:
            if lock[0] <= 0:
                self.hitboxLock.remove(lock)
            else:
                lock[0] -= 1
        
        if self.ledgeLock:
            ledges = pygame.sprite.spritecollide(self, self.gameState.platform_ledges, False)
            if len(ledges) == 0: # If we've cleared out of all of the ledges
                self.ledgeLock = False
                
        # We set the hurbox to be the Bounding Rect of the sprite.
        # It is done here, so that the hurtbox can be changed by the action.
        self.hurtbox.rect = self.sprite.boundingRect
        
        #Step three, change state and update
        self.current_action.stateTransitions(self)
        self.current_action.update(self) #update our action             
        
        if self.mask: self.mask = self.mask.update()
        self.shieldIntegrity += 0.5
        if self.shieldIntegrity > 100: self.shieldIntegrity = 100
        
        for art in self.articles:
            art.update()
        
        # This will "unstick" us if a sprite change would have gotten us in the wall
        block_hit_list = self.getCollisionsWith(self.gameState.platform_list)
        for block in block_hit_list:
            if block.solid:
                self.eject(block)
        
        # Gravity
        self.calc_grav()
        self.checkForGround()
        
        #Make a copy of where we were, so we know where we came from
        originalRect = self.rect.copy()
                
        # Move x and resolve collisions
        self.rect.x += self.change_x
        block_hit_list = self.getCollisionsWith(self.gameState.platform_list)
        for block in block_hit_list:
            if block.solid:
                self.eject(block)
        
        # Move y and resolve collisions. This also requires us to check the direction we're colliding from and check for pass-through platforms
        self.rect.y += self.change_y
        block_hit_list = self.getCollisionsWith(self.gameState.platform_list)
        
        if len(block_hit_list) > 0:
            block = block_hit_list.pop()
            if block.solid:
                if originalRect.top >= block.rect.bottom: #if we came in from below
                    self.rect.top = block.rect.bottom
                elif originalRect.bottom <= block.rect.top:
                    self.rect.bottom = block.rect.top
                self.change_y = 0
            elif originalRect.bottom <= block.rect.top:
                self.change_y = 0
                self.rect.bottom = block.rect.top
            
        #Check for deaths  
        #TODO: Do this better  
        if self.rect.right < self.gameState.blast_line.left: self.die()
        if self.rect.left > self.gameState.blast_line.right: self.die()
        if self.rect.top > self.gameState.blast_line.bottom: self.die()
        if self.rect.bottom < self.gameState.blast_line.top: self.die()
        
        #Update Sprite
        self.sprite.updatePosition(self.rect)
        self.hurtbox.rect = self.sprite.boundingRect
        
    """
    Change speed to get closer to the preferred speed without going over.
    xFactor - The factor by which to change xSpeed. Usually self.var['friction'] or self.var['airControl']
    """
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
    
    """
    Check if the fighter is on the ground.
    Sets the fighter's Grounded flag.
    """
    def checkForGround(self):
        originalRect = self.rect.copy()
        #Check if there's a platform below us to update the grounded flag 
        self.rect.y += 2
        
        #platform_hit_list = pygame.sprite.spritecollide(self, self.gameState.platform_list, False)
        platform_hit_list = self.getCollisionsWith(self.gameState.platform_list)
        self.rect.y -= 2
        
        
        for block in platform_hit_list:
            if originalRect.bottom <= block.rect.top:
                self.grounded = True
                return

        self.grounded = False
    
    """
    A simple function that converts the facing variable into a direction in degrees.
    """
    def getFacingDirection(self):
        if self.facing == 1: return 0
        else: return 180
        
########################################################
#                  ACTION SETTERS                      #
########################################################
    """
    These functions are meant to be overridden. They are
    provided so the baseActions can change the AbstractFighter's
    actions. If you've changed any of the base actions
    for the fighter (including adding a sprite change)
    override the corresponding method and have it set
    an instance of your overridden action.
    """

    def changeAction(self,newAction):
        newAction.setUp(self)
        self.current_action.tearDown(self,newAction)
        self.current_action = newAction
        
    def doIdle(self):
        self.changeAction(baseActions.NeutralAction())
        
    def doGroundMove(self,direction,run=False):
        if run: self.current_action = baseActions.Run()
        else: self.changeAction(baseActions.Move())
    
    def doPivot(self):
        self.changeAction(baseActions.Pivot())
    
    def doStop(self):
        self.changeAction(baseActions.NeutralAction())
    
    def doLand(self):
        self.changeAction(baseActions.Land())
    
    def doFall(self):
        self.changeAction(baseActions.Fall())
        
    def doGroundJump(self):
        self.changeAction(baseActions.Jump())
    
    def doAirJump(self):
        self.changeAction(baseActions.AirJump())
    
    def doGroundAttack(self):
        return None
    
    def doAirAttack(self):
        return None
   
    def doShield(self):
        self.changeAction(baseActions.Shield())
        
    def doShieldBreak(self):
        self.changeAction(baseActions.ShieldBreak())
        
    def doForwardRoll(self):
        self.changeAction(baseActions.ForwardRoll())
    
    def doBackwardRoll(self):
        self.changeAction(baseActions.BackwardRoll())
        
    def doSpotDodge(self):
        self.changeAction(baseActions.SpotDodge())
        
    def doAirDodge(self):
        self.changeAction(baseActions.AirDodge())
        
    def doLedgeGrab(self,ledge):
        self.changeAction(baseActions.LedgeGrab(ledge))
        
    def doLedgeGetup(self):
        print "getup"
        
    def doGetTrumped(self):
        print "trumped"
        
########################################################
#                  STATE CHANGERS                      #
########################################################
    """
    These involve the game engine. They will likely be
    sufficient for your character implementation, although
    in a heavily modified game engine, these might no
    longer be relevant. Override only if you're changing
    the core functionality of the fighter system. Extend
    as you see fit, if you need to tweak sprites or
    set flags.
    """
    
    """
    Flip the fighter so he is now facint the other way.
    Also flips the sprite for you.
    """
    def flip(self):
        self.facing = -self.facing
        self.sprite.flipX()
    
    """
    Deal damage to the fighter.
    Checks to make sure the damage caps at 999.
    If you want to have higher damage, override this function and remove it.
    This function is called in the applyKnockback function, so you shouldn't
    need to call this function directly for normal attacks, although you can
    for things like poison, non-knockback attacks, etc.
    """ 
    def dealDamage(self, damage):
        self.damage += damage
        if self.damage >= 999:
            self.damage = 999
    
    """
    Do Knockback to the fighter.
    
    damage - the damage dealt by the attack. This is used in some calculations, so it is applied here.
    kb - the base knockback of the attack.
    kbg - the knockback growth ratio of the attack.
    trajectory - the direction the attack sends the fighter, in degrees, with 0 being right, 90 being upward, 180 being left.
                 This is an absolute direction, irrelevant of either character's facing direction. Those tend to be taken
                 into consideration in the hitbox collision event itself, to allow the hitbox to also take in the attacker's
                 current state as well as the fighter receiving knockback.
    
    The knockback calculation is derived from the SSBWiki, and a bit of information from ColinJF and Amazing Ampharos on Smashboards,
    it is based off of Super Smash Bros. Brawl's knockback calculation, which is the one with the most information available (due to
    all the modding)
    """
    def applyKnockback(self, damage, kb, kbg, trajectory):
        self.change_x = 0
        self.change_y = 0
        self.dealDamage(damage)
        
        p = float(self.damage)
        d = float(damage)
        w = float(self.var['weight'])
        s = float(kbg)
        b = float(kb)
        
        # Thank you, ssbwiki!
        totalKB = (((((p/10) + (p*d)/20) * (200/(w+100))*1.4) + 5) * s) + b
        
        #"Sakurai Angle" calculation
        if trajectory == 361:
            if self.grounded:
                if totalKB < 30: trajectory = 0
                else: trajectory = 43
            else: trajectory = 43
            print trajectory
            
        #Directional Incluence
        if (trajectory < 45 or trajectory > 315) or (trajectory < 225 and trajectory > 135):
            if self.keysContain('up'):
                trajectory += 15
            if self.keysContain('down'):
                trajectory -= 15
        print totalKB, trajectory
        self.setSpeed(totalKB, trajectory, False)
        self.preferred_xspeed = 0
        self.preferred_yspeed = 0
    
    """
    Set the actor's speed. Instead of modifying the change_x and change_y values manually,
    this will calculate what they should be set at if you want to give a direction and
    magnitude instead.
    
    speed - the total speed you want the fighter to move
    direction - the angle of the speed vector, 0 being right, 90 being up, 180 being left.
    preferred - whether or not this should be changing the preferred speed instead of modifying it directly.
                defaults to True, meaning this will change the preferred speed (meaning the fighter will accelerate/decelerate to that speed)
                if set to False, the fighter's speed will instantly change to that speed.
    """
    def setSpeed(self,speed,direction,preferred = True):
        (x,y) = getXYFromDM(direction,speed)
        if preferred:
            self.preferred_xspeed = x
            self.preferred_yspeed = y
        else:
            self.change_x = x
            self.change_y = y
        
    def rotateSprite(self,direction):
        self.sprite.rotate(-1 * (90 - direction))
            
    def unRotate(self):
        self.sprite.rotate()
        
    def die(self):
        self.damage = 0
        self.change_x = 0
        self.change_y = 0
        self.jumps = self.var['jumps']
        self.rect.midtop = self.gameState.size.midtop
        
    def changeSprite(self,newSprite,frame=0):
        self.sprite.changeImage(newSprite)
        if frame != 0: self.sprite.changeSubImage(frame)
        
    def changeSpriteImage(self,frame):
        self.sprite.changeSubImage(frame)
    
    """
    This will "lock" the hitbox so that another hitbox with the same ID from the same fighter won't hit again.
    Returns true if it was successful, false if it already exists in the lock.
    
    hbox - the hitbox we are checking for
    time - the time to lock the hitbox
    """
    def lockHitbox(self,hbox,time):
        for lock in self.hitboxLock:
            if lock[1] == hbox.owner and lock[2] == hbox.hitbox_id:
                return False
        self.hitboxLock.append([time,hbox.owner,hbox.hitbox_id])
        return True
    
    def startShield(self):
        self.articles.add(article.ShieldArticle(settingsManager.createPath("sprites/melee_shield.png"),self))
        
    def shieldDamage(self,damage):
        if self.shieldIntegrity > 0:
            self.shieldIntegrity -= 1
        elif self.shieldIntegrity <= 0:
            self.doShieldBreak()
    
########################################################
#                 ENGINE FUNCTIONS                     #
########################################################
    """
    These functions are not meant to be overridden, and
    likely won't need to be extended. Most of these are
    input/output related, and shouldn't be trifled with.
    Many of them reference outside variables, so 
    functionality can be changed by tweaking those values.
    Edit at your own risk.
    """

    """
    Add a key to the buffer. This function should be adding
    to the buffer, and ONLY adding to the buffer. Any sort
    of calculations and state changes should probably be done
    in the stateTransitions function of the current action.
    """
    def keyPressed(self,key):
        k = self.keyBindings.get(key)
        self.inputBuffer.append((k,1.0))
        self.keysHeld.append(k)
        
        if k == 'left':
            if self.keysContain('right'):
                self.inputBuffer.append(('right',0))
                self.keysHeld.remove('right')
        elif k == 'right':
            if self.keysContain('left'):
                self.inputBuffer.append(('left',0))
                self.keysHeld.remove('left')
                
    """
    As above, but opposite.
    """
    def keyReleased(self,key):
        k = self.keyBindings.get(key)
        if self.keysContain(k):
            self.inputBuffer.append((k,0))
            self.keysHeld.remove(k)
            return True
        else: return False
    
    def joyButtonPressed(self,pad,button):
        # TODO: Check gamepad first
        self.keyPressed(button)
                
    def joyButtonReleased(self,pad,button):
        # TODO: Check gamepad first
        self.keyReleased(button)
        
    def joyAxisMotion(self,pad,axis):
        #TODO - Actually check if this the right gamePad
        value = round(pad.get_axis(axis),3) # We really only need three decimals of precision
        if abs(value) < 0.05: value = 0
        if value < 0: sign = '-'
        else: sign = '+'
        
        k = self.keyBindings.get('axis ' + str(axis) + sign)
        self.inputBuffer.append((k,value)) # This should hopefully append something along the line of ('left',0.8)
        self.keysHeld.append(k)
    
    """
    A wrapper for the InputBuffer.contains function, since this will be called a lot.
    For a full description of the arguments, see the entry in InputBuffer.
    """
    def bufferContains(self,key, distanceBack = 0, state=1.0, andReleased=False, notReleased=False):
        return self.inputBuffer.contains(key, distanceBack, state, andReleased, notReleased)
    
    """
    This checks for keys that are currently being held, whether or not they've actually been pressed recently.
    This is used, for example, to transition from a landing state into a running one. Using the InputBuffer
    would mean that you'd either need to iterate over the WHOLE buffer and look for one less release than press,
    or limit yourself to having to press the button before landing, whether you were moving in the air or not.
    If you are looking for a button PRESS, use bufferContains. If you are looking for IF A KEY IS STILL BEING HELD,
    this is your function.
    """
    def keysContain(self,key):
        return key in self.keysHeld    
    
    """
    This returns a tuple of the key for forward, then backward
    Useful for checking if the fighter is pivoting, or doing a back air, or getting the
    proper key to dash-dance, etc.
    
    The best way to use this is something like
    (key,invkey) = actor.getForwardBackwardKeys()
    which will assign the variable "key" to the forward key, and "invkey" to the backward key.
    """
    def getForwardBackwardKeys(self):
        if self.facing == 1: return ('right','left')
        else: return ('left','right')
        
    def draw(self,screen,offset,scale):
        if (settingsManager.getSetting('showSpriteArea')): spriteManager.RectSprite(self.rect).draw(screen, offset, scale)
        self.sprite.draw(screen,offset,scale)
        
        if self.mask: self.mask.draw(screen,offset,scale)
        for art in self.articles:
            art.draw(screen,offset,scale)
        
        
    #Gets the proper direction, adjusted for facing
    """
    Use this function to get a direction that is angled from the direction the fighter
    is facing, rather than angled from right. For example, sending the opponent 30 degrees
    is fine when facing right, but if you're facing left, you'd still be sending them to the right!
    
    Hitboxes use this calculation a lot. It'll return the proper angle that is the given offset
    from "forward". Defaults to 0, which will give either 0 or 180, depending on the direction
    of the fighter.
    """
    def getForwardWithOffset(self,offSet = 0):
        if self.facing == 1:
            return offSet
        else:
            return 180 - offSet
        
    def createMask(self,color,duration,pulse = False,pulseSize = 16):
        self.mask = spriteManager.MaskSprite(self.sprite,color,duration,pulse, pulseSize)
        
    def getDirectionMagnitude(self):
        if self.change_x == 0:
            magnitude = self.change_y
            direction = 90 if self.change_y < 0 else 270
            return (direction,magnitude)
        if self.change_y == 0:
            magnitude = self.change_x
            direction = 0 if self.change_x > 0 else 180
            return(direction,magnitude)
        
        direction = math.atan(float(-self.change_y)/float(self.change_x))
        direction = math.degrees(direction)
        if direction < 0: direction = 180 + direction
        direction = round(direction)
        magnitude = math.sqrt(math.pow(self.change_x, 2) + math.pow(-self.change_y, 2))
        
        return (direction,magnitude)
        
    """
    Pixel Perfect Collision (almost!).
    This will return a list of all sprites in the given group
    that collide with the fighter, not counting transparency.
    """
    def getCollisionsWith(self,spriteGroup):
        self.sprite.updatePosition(self.rect)
        collideSprite = spriteManager.RectSprite(self.sprite.boundingRect)
        return pygame.sprite.spritecollide(collideSprite, spriteGroup, False)
        
        
    def eject(self,other):
        # Get the number of pixels we need to exit from the left
        if self.sprite.boundingRect.right > other.rect.left:
            dxLeft = self.sprite.boundingRect.right - other.rect.left
        else: dxLeft = -1
        
        if self.sprite.boundingRect.left < other.rect.right:
            dxRight = other.rect.right - self.sprite.boundingRect.left
        else: dxRight = -1
        
        if dxLeft == -1 and dxRight == -1: # If neither of our sides are inside the block
            dx = 0 # Don't move sideways
        elif dxLeft == -1: # If one of our sides is in, and it's not left,
            dx = dxRight
        elif dxRight == -1: # If one of our sides is in, and it's not right,
            dx = -dxLeft
        elif dxLeft < dxRight: # our distance out to the left is smaller than right
            dx = -dxLeft
        else: # our distance out to the right is smaller than the left
            dx = dxRight
        
        if self.sprite.boundingRect.bottom > other.rect.top:
            dyUp = self.sprite.boundingRect.bottom - other.rect.top
        else: dyUp = -1
        
        if self.sprite.boundingRect.top < other.rect.bottom:
            dyDown = other.rect.bottom - self.sprite.boundingRect.top
        else: dyDown = -1
        
        if dyUp == -1 and dyDown == -1: # If neither of our sides are inside the block
            dy = 0 # Don't move sideways
        elif dyUp == -1: # If one of our sides is in, and it's not left,
            dy = dyDown
        elif dyDown == -1: # If one of our sides is in, and it's not right,
            dy = -dyUp
        elif dyUp < dyDown: # our distance out to the left is smaller than right
            dy = -dyUp
        else: # our distance out to the right is smaller than the left
            dy = dyDown
            
        if abs(dx) < abs(dy):
            self.rect.x += dx
            self.sprite.boundingRect.x += dx
        
        elif abs(dy) < abs(dx):
            self.rect.y += dy
            self.sprite.boundingRect.y += dy
        else:
            self.rect.x += dx
            self.rect.y += dy
            self.sprite.boundingRect.x += dx
            self.sprite.boundingRect.y += dy
        
########################################################
#             STATIC HELPER FUNCTIONS                  #
########################################################
# Functions that don't require a fighter instance to use
        
"""
A helper function to get the X and Y magnitudes from the Direction and Magnitude of a trajectory
"""
def getXYFromDM(direction,magnitude):
    rad = math.radians(direction)
    x = round(math.cos(rad) * magnitude,5)
    y = -round(math.sin(rad) * magnitude,5)
    return (x,y)

"""
Get the direction between two points. 0 means the second point is to the right of the first,
90 is straight above, 180 is straight left. Used in some knockback calculations.
"""

def getDirectionBetweenPoints(p1, p2):
    (x1, y1) = p1
    (x2, y2) = p2
    dx = x2 - x1
    dy = y1 - y2
    return (180 * math.atan2(dy, dx)) / math.pi 
        
########################################################
#                  INPUT BUFFER                        #
########################################################        
"""
The input buffer is a list of all of the buttons pressed and released,
and the frames they're put in on. It's used to check for buttons that
were pressed in the past, such as for a wall tech, or a buffered jump,
but can also be used to re-create the entire battle (once a replay manager
is set up)
"""
class InputBuffer():
    
    def __init__(self):
        self.buffer = [[]]
        self.workingBuff = []
        self.lastIndex = 0
      
    """
    Pushes the buttons for the frame into the buffer, then extends the index by one.
    """
    def push(self):
        self.buffer.append(self.workingBuff)
        self.workingBuff = []
        self.lastIndex += 1
     
    """
    The big function. This checks if the buffer contains a key, with a lot of configurability.
    
    key - the key to look for
    distance-Back - how many frames to look back, if set to 0, will check only the current frame.
    state - Whether to check for a press (True) or release (False). Set this flag to False if you want
            to look for when a button was released.
    andReleased - Check if the button was pressed AND released in the given distance. Technically, this can also
                  be used with state=False to check for a button that was released then pressed again in the time
                  frame, but I can't think of a situation that would be useful in.
    notReleased - Check if the button was pressed in the given distance, and is still being held.
    """
    def contains(self, key, distanceBack = 0, state=1.0, andReleased=False, notReleased=False):
        if state == 1.0: notState = 0
        else: notState = 1.0
        js = [] #If the key shows up multiple times, we might need to check all of them.
        if distanceBack > self.lastIndex: distanceBack = self.lastIndex #So we don't check farther back than we have data for
        for i in range(self.lastIndex,(self.lastIndex - distanceBack - 1), -1):
            #first, check if the key exists in the distance.
            buff = self.buffer[i]
            if (key,state) in buff:
                js.append(i)
                if not (andReleased or notReleased): return True #If we don't care whether it was released or not, we can return True now.
        
        #If it's not in there, return false.
        if len(js) == 0: return False
        #Note, if, for some stupid reason, both andReleased and notReleased are set, it will prioritize andReleased
        for j in js:
            for i in range(j,self.lastIndex+1):
                buff = self.buffer[i]
                if (key,notState) in buff: #If we encounter the inversion of the key we're looking for
                    if andReleased: return True #If we're looking for a release, we found it
                    if notReleased: return False #If we're looking for a held, we didn't get it
        #If we go through the buffer up to the key press and we don't find its inversion...
        if andReleased: return False
        if notReleased: return True
        #... do the opposite of above.
        
        return False #This statement should never be reached. If you do, enjoy your boolean.
                
    """
    Get a sub-buffer of N frames
    """
    def getLastNFrames(self,n):
        retBuffer = []
        if n > self.lastIndex: n = self.lastIndex
        for i in range(self.lastIndex,self.lastIndex - n,-1):
            retBuffer.append(self.buffer[i])
        return retBuffer
    
    """
    put a key into the current working buffer. The working buffer is all of the inputs for
    one frame, before the frame is actually executed.
    """
    def append(self,key):
        self.workingBuff.append(key)