import action
import pygame
import fighter


########################################################
#               ABSTRACT ACTIONS                       #
########################################################

# SubActions are a single part of an Action, such as moving a fighter, or tweaking a sprite.
class SubAction():
    def __init__(self,actor):
        self.owner = actor
    
    def execute(self,actor):
        return
    
# Conditional Subactions contain lists of other subactions they will run if the condition is true or false.
class ConditionalAction(SubAction):
    def __init__(self,actor,cond):
        SubAction.__init__(self, actor)
        self.ifActions = []
        self.elseActions = []
        self.cond = cond
        
    def execute(self,actor):
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
    def __init__(self,actor,attr,comp,val,ifActions = [], elseActions = []):
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
        ConditionalAction.__init__(self, actor, cond)
        self.ifActions = ifActions
        self.elseActions = elseActions

# The IfVar Subaction compares two values.
class ifVar(ConditionalAction):
    def __init__(self,actor,val1,comp,val2,ifActions = [], elseActions = []):
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
        ConditionalAction.__init__(self, actor, cond)
        self.ifActions = ifActions
        self.elseActions = elseActions


########################################################
#                SPRITE CHANGERS                       #
########################################################
      
# ChangeFighterSprite will change the sprite of the fighter (Who knew?)
# Optionally pass it a subImage index to start at that frame instead of 0
class changeFighterSprite(SubAction):
    def __init__(self,actor,sprite,subImage = 0):
        SubAction.__init__(self, actor)
        self.sprite = sprite
        self.subImage = subImage
        
    def execute(self,actor):
        actor.changeSprite(self.sprite,self.subImage)
        
# ChangeFighterSubimage will change the subimage of a sheetSprite without changing the sprite.
class changeFighterSubimage(SubAction):
    def __init__(self,actor,index):
        SubAction.__init__(self, actor)
        self.index = index
        
    def execute(self,actor):
        actor.sprite.getImageAtIndex(self.index)
        

########################################################
#               FIGHTER MOVEMENT                       #
########################################################

# The preferred speed is what a fighter will accelerate/decelerate to. Use this action if you
# want the fighter to gradually speed up to a point (for accelerating), or slow down to a point (for deccelerating)
class changeFighterPreferredSpeed(SubAction):
    pass

# ChangeFighterSpeed changes the speed directly, with no acceleration/deceleration.
class changeFighterSpeed(SubAction):
    pass

# ApplyForceVector is usually called when launched, but can be used as an alternative to setting speed. This one
# takes a direction in degrees (0 being forward, 90 being straight up, 180 being backward, 270 being downward)
# and a magnitude.
class applyForceVector(SubAction):
    pass

# ShiftFighterPositon directly changes the fighter's x and y coordinates without regard for wall checks, speed limites, or gravity.
# Don't use this for ordinary movement unless you're totally sure what you're doing.
# A good use for this is to jitter a hit opponent during hitlag, just make sure to put them back where they should be before actually launching.
class shiftFighterPosition(SubAction):
    pass
########################################################
#           ATTRIBUTES AND VARIABLES                   #
########################################################

# Change a fighter attribute, for example, weight or remaining jumps
class modifyAttribute(SubAction):
    pass

# Modify a variable in the action, such as a conditional flag of some sort.
class modifyActionVar(SubAction):
    pass

# Change the frame of the action to a value.
class changeActionFrame(SubAction):
    pass

# Go to the next frame in the action
class nextFrame(SubAction):
    pass

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