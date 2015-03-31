########################################################
#               ABSTRACT ACTIONS                       #
########################################################

# SubActions are a single part of an Action, such as moving a fighter, or tweaking a sprite.
class SubAction():
    def __init__(self,actor,action):
        self.owner = actor
        self.action = action
    
    def execute(self):
        return
    
# Conditional Subactions contain lists of other subactions they will run if the condition is true or false.
class ConditionalAction(SubAction):
    def __init__(self,actor,action,cond):
        SubAction.__init__(self, actor, action)
        self.ifActions = []
        self.elseActions = []
        self.cond = cond
        
    def execute(self):
        if self.cond:
            for act in self.ifActions:
                act.execute(self.owner)
        else:
            for act in self.elseActions:
                act.execute(self.owner)

########################################################
#                 CONDITIONALS                         #
########################################################

# The IfAttribute SubAction compares a fighter attribute to a value.
class ifAttribute(ConditionalAction):
    def __init__(self,actor,action,attr,comp,val,ifActions = [], elseActions = []):
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
    def __init__(self,actor,action,val1,comp,val2,ifActions = [], elseActions = []):
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
        ConditionalAction.__init__(self, actor,action, cond)
        self.ifActions = ifActions
        self.elseActions = elseActions


########################################################
#                SPRITE CHANGERS                       #
########################################################
      
# ChangeFighterSprite will change the sprite of the fighter (Who knew?)
# Optionally pass it a subImage index to start at that frame instead of 0
class changeFighterSprite(SubAction):
    def __init__(self,actor,action,sprite,subImage = 0):
        SubAction.__init__(self, actor, action)
        self.sprite = sprite
        self.subImage = subImage
        
    def execute(self):
        self.owner.changeSprite(self.sprite,self.subImage)
        
# ChangeFighterSubimage will change the subimage of a sheetSprite without changing the sprite.
class changeFighterSubimage(SubAction):
    def __init__(self,actor,action,index):
        SubAction.__init__(self, actor, action)
        self.index = index
        
    def execute(self):
        self.owner.sprite.getImageAtIndex(self.index)
        

########################################################
#               FIGHTER MOVEMENT                       #
########################################################

# The preferred speed is what a fighter will accelerate/decelerate to. Use this action if you
# want the fighter to gradually speed up to a point (for accelerating), or slow down to a point (for deccelerating)
class changeFighterPreferredSpeed(SubAction):
    def __init__(self,actor,action,pref_x = None, pref_y = None):
        SubAction.__init__(self, actor, action)
        self.pref_x = pref_x
        self.pref_y = pref_y
        
    def execute(self):
        if self.pref_x:
            self.owner.preferred_xspeed = self.pref_x
        if self.pref_y:
            self.owner.preferred_yspeed = self.pref_y
        
        
# ChangeFighterSpeed changes the speed directly, with no acceleration/deceleration.
class changeFighterSpeed(SubAction):
    def __init__(self,actor,action,speed_x = None, speed_y = None):
        SubAction.__init__(self, actor, action)
        self.speed_x = speed_x
        self.speed_y = speed_y
        
    def execute(self):
        if self.speed_x:
            self.owner.change_x = self.speed_x
        if self.speed_y:
            self.owner.change_x = self.speed_y

# ApplyForceVector is usually called when launched, but can be used as an alternative to setting speed. This one
# takes a direction in degrees (0 being forward, 90 being straight up, 180 being backward, 270 being downward)
# and a magnitude.
# Set the "preferred" flag to make the vector affect preferred speed instead of directly changing speed.
class applyForceVector(SubAction):
    def __init__(self,actor,action, magnitude, direction, preferred = False):
        SubAction.__init__(self, actor, action)
        self.magnitude= magnitude
        self.direction = direction
        self.preferred = preferred
        
    def execute(self):
        self.owner.setSpeed(self.magnitude,self.direction,self.preferred)

# ShiftFighterPositon directly changes the fighter's x and y coordinates without regard for wall checks, speed limites, or gravity.
# Don't use this for ordinary movement unless you're totally sure what you're doing.
# A good use for this is to jitter a hit opponent during hitlag, just make sure to put them back where they should be before actually launching.
class shiftFighterPosition(SubAction):
    def __init__(self,actor,action,new_x = None, new_y = None):
        SubAction.__init__(self, actor, action)
        self.new_x = new_x
        self.new_y = new_y
        
    def execute(self):
        if self.new_x:
            self.owner.rect.x = self.new_x
        if self.new_y:
            self.owner.rect.y = self.new_y
########################################################
#           ATTRIBUTES AND VARIABLES                   #
########################################################

# Change a fighter attribute, for example, weight or remaining jumps
class modifyAttribute(SubAction):
    def __init__(self,actor,action,attr,val):
        SubAction.__init__(self, actor, action)
        self.attr = attr
        self.val = val
        
    def execute(self):
        self.owner.var[self.attr] = self.val
        
# Modify a variable in the action, such as a conditional flag of some sort.
class modifyActionVar(SubAction):
    def __init__(self,actor,action,var,val):
        SubAction.__init__(self, actor, action)
        self.var = var
        self.val = val
    
    def execute(self):
        if self.action.var.has_key(self.var):
            self.action.var[self.var] = self.val
        else:
            self.action.var.update({self.var:self.val})
                   
# Change the frame of the action to a value.
class changeActionFrame(SubAction):
    def __init__(self,actor,action,newFrame):
        SubAction.__init__(self, actor, action)
        self.frame = newFrame
    
    def execute(self):
        self.action.frame = self.frame
        
# Go to the next frame in the action
class nextFrame(SubAction):
    def execute(self):
        self.action.frame += 1

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

# Change the fighter's Hurtbox (where they have to be hit to take damage)
# This is not done automatically when sprites change, so if your sprite takes the fighter out of his usual bounding box, make sure to change it.
# If a hurtbox overlaps a hitbox, the hitbox will be resolved first, so the fighter won't take damage in the case of clashes.
class modifyHurtBox(SubAction):
    pass