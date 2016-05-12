########################################################
#               ABSTRACT ACTIONS                       #
########################################################

# SubActions are a single part of an Action, such as moving a fighter, or tweaking a sprite.
class SubAction():
    def __init__(self):
        pass
    
    def execute(self, action, actor):
        pass
    
    @staticmethod
    def buildFromXml(node):
        pass
    
# Conditional Subactions contain lists of other subactions they will run if the condition is true or false.
class ConditionalAction(SubAction):
    def __init__(self,cond):
        SubAction.__init__(self)
        self.ifActions = []
        self.elseActions = []
        self.cond = cond
        
    def execute(self, action, actor):
        if self.cond:
            for act in self.ifActions:
                act.execute(actor)
        else:
            for act in self.elseActions:
                act.execute(actor)


########################################################
#                 CONDITIONALS                         #
########################################################

# The IfAttribute SubAction compares a fighter attribute to a value.
class ifAttribute(ConditionalAction):
    def __init__(self,attr,comp,val,ifActions = [], elseActions = []):
        if comp == '==':
            cond = actor.var[attr] == val
        elif comp == '<':
            cond = actor.var[attr] < val
        elif comp == '<=':
            cond = actor.var[attr] <= val
        elif comp == '>':
            cond = actor.var[attr] > val
        elif comp == '>=':
            cond = actor.var[attr] >= val
        elif comp == '!=':
            cond = actor.var[attr] != val
        ConditionalAction.__init__(self, actor, action, cond)
        self.ifActions = ifActions
        self.elseActions = elseActions
    
# The IfVar Subaction compares two values.
class ifVar(ConditionalAction):
    def __init__(self,val1,comp,val2,ifActions = [], elseActions = []):
        if comp == '==':
            cond = val1 == val2
        elif comp == '<':
            cond = val1 < val2
        elif comp == '<=':
            cond = val1 <= val2
        elif comp == '>':
            cond = val1 > val2
        elif comp == '>=':
            cond = val1 >= val2
        elif comp == '!=':
            cond = val1 != val2
        ConditionalAction.__init__(self, action, cond)
        self.ifActions = ifActions
        self.elseActions = elseActions


########################################################
#                SPRITE CHANGERS                       #
########################################################
      
# ChangeFighterSprite will change the sprite of the fighter (Who knew?)
# Optionally pass it a subImage index to start at that frame instead of 0
class changeFighterSprite(SubAction):
    def __init__(self,sprite,subImage = 0):
        SubAction.__init__(self)
        self.sprite = sprite
        self.subImage = subImage
        
    def execute(self, action, actor):
        actor.changeSprite(self.sprite,self.subImage)
        
    @staticmethod
    def buildFromXml(node):
        return changeFighterSprite(node.text)
        
# ChangeFighterSubimage will change the subimage of a sheetSprite without changing the sprite.
class changeFighterSubimage(SubAction):
    def __init__(self,index):
        SubAction.__init__(self)
        self.index = index
        
    def execute(self, action, actor):
        actor.changeSpriteImage(self.index)
        
    @staticmethod
    def buildFromXml(node):
        return changeFighterSubimage(int(node.text))

########################################################
#               FIGHTER MOVEMENT                       #
########################################################

# The preferred speed is what a fighter will accelerate/decelerate to. Use this action if you
# want the fighter to gradually speed up to a point (for accelerating), or slow down to a point (for deccelerating)
class changeFighterPreferredSpeed(SubAction):
    def __init__(self,pref_x = None, pref_y = None):
        SubAction.__init__(self)
        self.pref_x = pref_x
        self.pref_y = pref_y
        
    def execute(self, action, actor):
        if self.pref_x:
            actor.preferred_xspeed = self.pref_x
        if self.pref_y:
            actor.preferred_yspeed = self.pref_y
        
        
# ChangeFighterSpeed changes the speed directly, with no acceleration/deceleration.
class changeFighterSpeed(SubAction):
    def __init__(self,speed_x = None, speed_y = None):
        SubAction.__init__(self)
        self.speed_x = speed_x
        self.speed_y = speed_y
        
    def execute(self, action, actor):
        if self.speed_x:
            actor.change_x = self.speed_x
        if self.speed_y:
            actor.change_x = self.speed_y

    @staticmethod
    def buildFromXml(node):
        speed_x = int(node.find('xSpeed').text)
        speed_y = int(node.find('ySpeed').text)
        print(speed_x)
        print(speed_y)
        return changeFighterSpeed(speed_x,speed_y)
# ApplyForceVector is usually called when launched, but can be used as an alternative to setting speed. This one
# takes a direction in degrees (0 being forward, 90 being straight up, 180 being backward, 270 being downward)
# and a magnitude.
# Set the "preferred" flag to make the vector affect preferred speed instead of directly changing speed.
class applyForceVector(SubAction):
    def __init__(self, magnitude, direction, preferred = False):
        SubAction.__init__(self)
        self.magnitude= magnitude
        self.direction = direction
        self.preferred = preferred
        
    def execute(self, action, actor):
        actor.setSpeed(self.magnitude,self.direction,self.preferred)

# ShiftFighterPositon directly changes the fighter's x and y coordinates without regard for wall checks, speed limites, or gravity.
# Don't use this for ordinary movement unless you're totally sure what you're doing.
# A good use for this is to jitter a hit opponent during hitlag, just make sure to put them back where they should be before actually launching.
class shiftFighterPosition(SubAction):
    def __init__(self,new_x = None, new_y = None):
        SubAction.__init__(self)
        self.new_x = new_x
        self.new_y = new_y
        
    def execute(self, action, actor):
        if self.new_x:
            actor.rect.x = self.new_x
        if self.new_y:
            actor.rect.y = self.new_y
########################################################
#           ATTRIBUTES AND VARIABLES                   #
########################################################

# Change a fighter attribute, for example, weight or remaining jumps
class modifyAttribute(SubAction):
    def __init__(self,attr,val):
        SubAction.__init__(self)
        self.attr = attr
        self.val = val
        
    def execute(self, action, actor):
        actor.var[self.attr] = self.val
        
# Modify a variable in the action, such as a conditional flag of some sort.
class modifyActionVar(SubAction):
    def __init__(self,var,val):
        SubAction.__init__(self)
        self.var = var
        self.val = val
    
    def execute(self, action, actor):
        if action.var.has_key(self.var):
            action.var[self.var] = self.val
        else:
            action.var.update({self.var:self.val})
                   
# Change the frame of the action to a value.
class changeActionFrame(SubAction):
    def __init__(self,newFrame):
        SubAction.__init__(self)
        self.frame = newFrame
    
    def execute(self, action, actor):
        action.frame = self.frame
        
    @staticmethod
    def buildFromXml(node):
        return changeActionFrame(int(node.text))
        
# Go to the next frame in the action
class nextFrame(SubAction):
    def execute(self, action, actor):
        action.frame += 1
    
    @staticmethod
    def buildFromXml(node):
        return nextFrame()
    
# Call a fighter's do<Action> function to change the action.
class changeAction(SubAction):
    pass

########################################################
#                 HIT/HURTBOXES                        #
########################################################

# Create a new hitbox
class createHitBox(SubAction):
    pass

# Change the properties of an existing hitbox, such as position, or power
class modifyHitBox(SubAction):
    pass

class activateHitbox(SubAction):
    pass

class deactivateHitbox(SubAction):
    pass

class updateHitbox(SubAction):
    pass


# Change the fighter's Hurtbox (where they have to be hit to take damage)
# This is not done automatically when sprites change, so if your sprite takes the fighter out of his usual bounding box, make sure to change it.
# If a hurtbox overlaps a hitbox, the hitbox will be resolved first, so the fighter won't take damage in the case of clashes.
class modifyHurtBox(SubAction):
    pass