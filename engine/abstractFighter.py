import pygame
import engine.baseActions as baseActions
import math
import settingsManager
import spriteManager
import engine.article as article
import math

class AbstractFighter():
    
    def __init__(self,
                 playerNum,
                 sprite,
                 name,
                 var):
        self.name = name
        self.var = var
        self.playerNum = playerNum
        self.franchise_icon = spriteManager.ImageSprite(settingsManager.createPath("sprites/default_franchise_icon.png"))

        # Super armor variables
        # Set with attacks to make them super armored
        # Remember to set them back at some point
        self.no_flinch_hits = 0
        self.flinch_damage_threshold = 0
        self.flinch_knockback_threshold = 0
        
        # dataLog holds information for the post-game results screen
        self.dataLog = None
        
        # Whenever a fighter is hit, they are 'tagged' by that player, if they die while tagged, that player gets a point
        self.hitTagged = None
        
        #Initialize engine variables
        self.keyBindings = settingsManager.getSetting('controls_' + str(playerNum))
        self.currentKeys = []
        self.inputBuffer = InputBuffer()
        self.keysHeld = []
        
        self.sprite = sprite
        self.mask = None
        self.ecb = ECB(self)
        
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
        
        #Process the hitbox locks
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
        
        #Update Sprite
        self.ecb.store()
        self.ecb.normalize()

        # Move x and resolve collisions
        self.rect.x += self.change_x
        block_hit_list = self.getCollisionsWith(self.gameState.platform_list)
        for block in block_hit_list:
            if block.solid:
                self.eject(block)
        
        # Move y and resolve collisions. This also requires us to check the direction we're colliding from and check for pass-through platforms
        self.rect.y += self.change_y
        block_hit_list = self.getCollisionsWith(self.gameState.platform_list)
        
        # checkForGround not needed anymore; its job is done by this conditional
        while len(block_hit_list) > 0:
            block = block_hit_list.pop()

            if block.solid & self.ecb.previousECB[0].rect.top >= block.rect.bottom+block.change_y:
                self.change_y = block.change_y
                self.rect.y = block.rect.bottom-block.change_y

            elif self.ecb.previousECB[0].rect.bottom-self.change_y <= block.rect.top+block.change_y:
                self.change_y = block.change_y+self.var['gravity']
                self.rect.y = block.rect.top-self.rect.height+block.change_y
                self.grounded = True
            
        
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
        
    def doGroundMove(self,direction):
        self.changeAction(baseActions.Move())

    def doDash(self,direction):
        self.changeAction(baseActions.Dash())

    def doRun(self,direction,speed):
        self.changeAction(baseActions.Run(speed))
    
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

    def doHitStun(self,hitstun,direction):
        self.changeAction(baseActions.HitStun(hitstun,direction))
    
    def doGroundAttack(self):
        return None

    def doDashAttack(self):
        return None
    
    def doAirAttack(self):
        return None

    def doGroundGrab(self):
        self.changeAction(baseActions.GroundGrab())

    def doGrabbing(self):
        self.changeAction(baseActions.Grabbing())

    def doAirGrab(self):
        return None

    def doGrabbed(self, height):
        self.changeAction(baseActions.Grabbed(height))

    def doRelease(self):
        self.changeAction(baseActions.Release())

    def doPummel(self):
        self.changeAction(baseActions.Pummel())

    def doThrow(self):
        self.changeAction(baseActions.Throw())
   
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
        self.changeAction(baseActions.LedgeGetup())
        
    def doGetTrumped(self):
        print("trumped")
        
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
    weight_influence - The degree to which weight influences knockback. Default value is 1, set to 0 to make knockback 
                 weight-independent, or to whatever other value you want to change the effect of weight on knockback
    hitstun_multiplier - The ratio of usual (calculated) hitstun to the hitstun that the hit should inflict. Default value is 
                 1 for normal levels of hitstun. To disable flinching, set to 0. 
    
    The knockback calculation is derived from the SSBWiki, and a bit of information from ColinJF and Amazing Ampharos on Smashboards,
    it is based off of Super Smash Bros. Brawl's knockback calculation, which is the one with the most information available (due to
    all the modding)
    """
    def applyKnockback(self, damage, kb, kbg, trajectory, weight_influence=1, hitstun_multiplier=1):
        self.change_x = 0
        self.change_y = 0
        self.dealDamage(damage)
        
        p = float(self.damage)
        d = float(damage)
        w = float(self.var['weight'])
        s = float(kbg)
        b = float(kb)

        # Thank you, ssbwiki!
        totalKB = (((((p/10) + (p*d)/20) * (200/(w*weight_influence+100))*1.4) + 5) * s) + b
        
        if damage < self.flinch_damage_threshold or totalKB < self.flinch_knockback_threshold:
            return 0
        
        #"Sakurai Angle" calculation
        if trajectory == 361:
            if self.grounded:
                if totalKB < 30: trajectory = 0
                else: trajectory = 43
            else: trajectory = 43
            print(trajectory)
            
        #Directional Incluence
        if (trajectory < 45 or trajectory > 315):
            if self.keysContain('up'):
                trajectory += 15
            if self.keysContain('down'):
                trajectory -= 15
        if (trajectory < 225 and trajectory > 135):
            if self.keysContain('up'):
                trajectory -= 15
            if self.keysContain('down'):
                trajectory += 15

        hitstun_frames = math.floor(totalKB*1.5*hitstun_multiplier) #Tweak this constant

        if self.no_flinch_hits > 0:
            if hitstun_frames > 0:
                self.no_flinch_hits -= 1
            return 0

        if hitstun_frames > 0:
            self.doHitStun(hitstun_frames,trajectory)

        print(totalKB, trajectory)
        self.setSpeed(totalKB, trajectory, False)
        self.preferred_xspeed = 0
        self.preferred_yspeed = 0

        return math.floor(totalKB)

        
    
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
        
    def die(self,respawn = True):
        self.damage = 0
        self.change_x = 0
        self.change_y = 0
        self.jumps = self.var['jumps']
        self.dataLog.setData('Falls',1,lambda x,y: x+y)
        if self.hitTagged != None:
            if hasattr(self.hitTagged, 'dataLog'):
                self.hitTagged.dataLog.setData('KOs',1,lambda x,y: x+y)
        
        if respawn:
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
        #If the hitbox belongs to something, get tagged by it
        if not hbox.owner == None:
            self.hitTagged = hbox.owner
            
        for lock in self.hitboxLock:
            if lock[1] == hbox.owner and lock[2] == hbox.hitbox_id:
                return False
        self.hitboxLock.append([time,hbox.owner,hbox.hitbox_id])
        return True
    
    def startShield(self):
        self.articles.add(article.ShieldArticle(settingsManager.createPath("sprites/melee_shield.png"),self))
        
    def shieldDamage(self,damage):
        if self.shieldIntegrity > 0:
            self.shieldIntegrity -= damage
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
    This function checks if the player has Smashed in a direction. It does this by noting if the direction was
    pressed recently and is now above a threshold
    """
    def checkSmash(self,direction):
        #TODO different for buttons than joysticks
        if self.inputBuffer.contains(direction, 4, 1.0, notReleased=True, threshold=True):
            return True
        return False
    
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
        #self.ecb.draw(screen,offset,scale)
        
        
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
        print "trying to escape"
        # Get the number of pixels we need to exit from the left
        #if self.sprite.boundingRect.right > other.rect.left:
        if self.ecb.xBar.rect.right > other.rect.left:
            dxLeft = self.ecb.xBar.rect.right - other.rect.left
        else: dxLeft = -1
        
        #if self.sprite.boundingRect.left < other.rect.right:
        if self.ecb.xBar.rect.left < other.rect.right:
            dxRight = other.rect.right - self.ecb.xBar.rect.left
        else: dxRight = -1
        
        if dxLeft == -1 and dxRight == -1: # If neither of our sides are inside the block
            dx = 0 # Don't move sideways
        elif dxLeft == -1: # If one of our sides is in, and it's not left,
            dx = -dxRight
        elif dxRight == -1: # If one of our sides is in, and it's not right,
            dx = dxLeft
        elif dxLeft < dxRight: # our distance out to the left is smaller than right
            dx = dxLeft
        else: # our distance out to the right is smaller than the left
            dx = -dxRight
        
        #if self.sprite.boundingRect.bottom > other.rect.top:
        if self.ecb.yBar.rect.bottom < other.rect.top:
            dyUp = self.ecb.yBar.rect.bottom - other.rect.top
        else: dyUp = -1
        
        if self.ecb.yBar.rect.top > other.rect.bottom:
            dyDown = other.rect.bottom - self.ecb.yBar.rect.top
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
    def contains(self, key, distanceBack = 0, state=1.0, andReleased=False, notReleased=False, threshold=False):
        if state == 1.0: notState = 0
        else: notState = 1.0
        js = [] #If the key shows up multiple times, we might need to check all of them.
        if distanceBack > self.lastIndex: distanceBack = self.lastIndex #So we don't check farther back than we have data for
        for i in range(self.lastIndex,(self.lastIndex - distanceBack - 1), -1):
            #first, check if the key exists in the distance.
            buff = self.buffer[i]
            for k,s in buff:
                if k == key:
                    if (threshold and s >= state) or (not threshold and s == state):
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


########################################################
#                       ECB                            #
########################################################        
"""
The ECB (environment collision box) is really more like an ECC, it'll be a cross of two rects.
It'll have a height and width, a centerpoint where they intersect, and x and y offsets. It will
be used for platform collision, and it'll know its previous location to know which direction
it's coming from.
"""
class ECB():
    def __init__(self,actor):
        self.actor = actor
        
        self.yBar = spriteManager.RectSprite(pygame.Rect(0,0,5,self.actor.sprite.boundingRect.height), pygame.Color('#ECB134'))
        self.xBar = spriteManager.RectSprite(pygame.Rect(0,0,self.actor.sprite.boundingRect.width,5), pygame.Color('#ECB134'))
        
        self.yBar.rect.center = self.actor.sprite.boundingRect.center
        self.xBar.rect.center = self.actor.sprite.boundingRect.center
        
        self.previousECB = [spriteManager.RectSprite(self.yBar.rect,pygame.Color('#EA6F1C')),
                            spriteManager.RectSprite(self.xBar.rect,pygame.Color('#EA6F1C'))]
        
    """
    Resize the ECB. Give it a height, width, and center point.
    xoff is the offset from the center of the x-bar, where 0 is dead center, negative is left and positive is right
    yoff is the offset from the center of the y-bar, where 0 is dead center, negative is up and positive is down
    """
    def resize(self,height,width,center,xoff,yoff):
        pass
    
    """
    Returns the dimensions of the ECB of the previous frame
    """
    def getPreviousECB(self):
        pass
    
    """
    This one moves the ECB without resizing it.
    """
    def move(self,newCenter):
        self.yBar.rect.center = newCenter
        self.xBar.rect.center = newCenter
    
    """
    This stores the previous location of the ECB
    """
    def store(self):
        self.previousECB = [spriteManager.RectSprite(self.yBar.rect,pygame.Color('#EA6F1C')),
                            spriteManager.RectSprite(self.xBar.rect,pygame.Color('#EA6F1C'))
                            ]
    
    """
    Set the ECB's height and width to the sprite's, and centers it
    """
    def normalize(self):
        """
        self.yBar.rect = pygame.Rect(0,0,5,self.actor.sprite.boundingRect.height)
        self.xBar.rect = pygame.Rect(0,0,self.actor.sprite.boundingRect.width,5)
        
        self.yBar.rect.center = self.actor.sprite.boundingRect.center
        self.xBar.rect.center = self.actor.sprite.boundingRect.center
        """
        
        center = (self.actor.sprite.boundingRect.centerx + self.actor.current_action.ecbCenter[0],self.actor.sprite.boundingRect.centery + self.actor.current_action.ecbCenter[1])
        sizes = self.actor.current_action.ecbSize
        offsets = self.actor.current_action.ecbOffset
        
        
        if sizes[0] == 0: 
            self.xBar.rect.width = self.actor.sprite.boundingRect.width
        else:
            self.xBar.rect.width = sizes[0]
        if sizes[1] == 0: 
            self.yBar.rect.height = self.actor.sprite.boundingRect.height
        else:
            self.yBar.rect.height = sizes[1]
        
        self.yBar.rect.center = center
        self.xBar.rect.center = center
        
    def draw(self,screen,offset,scale):
        self.yBar.draw(screen,self.actor.gameState.stageToScreen(self.yBar.rect),scale)
        self.xBar.draw(screen,self.actor.gameState.stageToScreen(self.xBar.rect),scale)
        
        self.previousECB[0].draw(screen,self.actor.gameState.stageToScreen(self.previousECB[0].rect),scale)
        self.previousECB[1].draw(screen,self.actor.gameState.stageToScreen(self.previousECB[1].rect),scale)
        
