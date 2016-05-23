import engine.hitbox
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

class ifVar(SubAction):
    def __init__(self,variable,comparator='==',value=True,ifActions = [],elseActions = []):
        self.variable = variable
        self.comparator = comparator
        self.value = value
        self.ifActions = ifActions
        self.elseActions = elseActions
        
    def execute(self, action, actor):
        variable = getattr(action, self.variable)
        if self.comparator == '==':
            cond = variable == self.value
        elif self.comparator == '<':
            cond = variable < self.value
        elif self.comparator == '<=':
            cond = variable <= self.value
        elif self.comparator == '>':
            cond = variable > self.value
        elif self.comparator == '>=':
            cond = variable >= self.value
        elif self.comparator == '!=':
            cond = variable != self.value
            
        if cond:
            for act in self.ifActions:
                act.execute(action,actor)
        else:
            for act in self.elseActions:
                act.execute(action,actor)
    
    @staticmethod
    def buildFromXml(node):
        variable = node.attrib['var']
        #print(variable)
        
        cond = node.find('compare').attrib.get('cond')
        if cond is None: cond = '=='
        #print(cond)
        
        value = node.find('value')
        if value is not None:
            if value.attrib.get('type') == 'int':
                value = int(value.text)
            elif value.attrib.get('type') == 'float':
                value = float(value.text)
            elif value.attrib.get('type') == 'bool':
                value = value.text == 'True'
        #print(value)
        
        ifActions = []
        for ifact in node.find('compare'):
            if subActionDict.has_key(ifact.tag): #Subactions string to class dict
                ifActions.append(subActionDict[ifact.tag].buildFromXml(ifact))
        #print(ifActions)
        
        elseActions = []
        if node.find('else') is not None:
            for elseact in node.find('else'):
                if subActionDict.has_key(elseact.tag): #Subactions string to class dict
                    elseActions.append(subActionDict[elseact.tag].buildFromXml(elseact))
        #print(elseActions)
        
        return ifVar(variable, cond, value, ifActions, elseActions)
              
########################################################
#                SPRITE CHANGERS                       #
########################################################
      
# ChangeFighterSprite will change the sprite of the fighter (Who knew?)
# Optionally pass it a subImage index to start at that frame instead of 0
class changeFighterSprite(SubAction):
    def __init__(self,sprite,subImage = 0):
        SubAction.__init__(self)
        self.sprite = sprite
        
    def execute(self, action, actor):
        action.spriteName = self.sprite
        actor.changeSprite(self.sprite)
        
    @staticmethod
    def buildFromXml(node):
        return changeFighterSprite(node.text)
        
# ChangeFighterSubimage will change the subimage of a sheetSprite without changing the sprite.
class changeFighterSubimage(SubAction):
    def __init__(self,index):
        SubAction.__init__(self)
        self.index = index
        
    def execute(self, action, actor):
        action.spriteRate = 0 #spriteRate has been broken, so we have to ignore it from now on
        #TODO changeSpriteRate subaction
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
class createHitbox(SubAction):
    def __init__(self,name,hitboxType,
                 center,size,
                 damage,baseKnockback,knockbackGrowth,trajectory,hitstun=1,
                 hitboxLock="",
                 weightInfluence=1,shieldMultiplier=1,transcendence=0,priorityDiff=0,
                 xBias=0,yBias=0,xDraw=0.1,yDraw=0.1):
        SubAction.__init__(self)
        
        self.name = name
        self.hitboxType = hitboxType if hitboxType is not None else "damage"
        self.center = center
        self.size = size
        self.damage = damage
        self.baseKnockback = baseKnockback
        self.knockbackGrowth = knockbackGrowth
        self.trajectory = trajectory
        self.hitstun = hitstun
        self.hitboxLock = hitboxLock
        self.weightInfluence = weightInfluence
        self.shieldMultiplier = shieldMultiplier
        self.transcendence = transcendence
        self.priorityDiff = priorityDiff
        self.xBias = xBias
        self.yBias = yBias
        self.xDraw = xDraw
        self.yDraw = yDraw
        
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        #Use an existing hitbox lock by name, or create a new one
        if action.hitboxLocks.has_key(self.hitboxLock):
            hitboxLock = action.hitboxLocks[self.hitboxLock]
        else:
            hitboxLock = engine.hitbox.HitboxLock()
            action.hitboxLocks[self.hitboxLock] = hitboxLock
        
        #Create the hitbox of the right type    
        if self.hitboxType == "damage":
            hitbox = engine.hitbox.DamageHitbox(self.center, self.size, actor, 
                                       self.damage, self.baseKnockback, self.knockbackGrowth, self.trajectory, self.hitstun, 
                                       hitboxLock,
                                       self.weightInfluence, self.shieldMultiplier, self.transcendence, self.priorityDiff)
        elif self.hitboxType == "sakurai":
            pass
        elif self.hitboxType == "autolink":
            pass
        elif self.hitboxType == "funnel":
            pass
        elif self.hitboxType == "grab":
            pass
        elif self.hitboxType == "reflector":
            pass
        action.hitboxes[self.name] = hitbox
        
    @staticmethod
    def buildFromXml(node):
        SubAction.buildFromXml(node)
        #mandatory fields
        name = node.find('name').text
        hitboxType = node.attrib['type'] if node.attrib.has_key('type') else "damage"
        center = map(int, node.find('center').text.split(','))
        size = map(int, node.find('size').text.split(','))
        damage = float(node.find('damage').text)
        baseKnockback = float(node.find('baseKnockback').text)
        knockbackGrowth = float(node.find('knockbackGrowth').text)
        trajectory = int(node.find('trajectory').text)
        
        hitstun = float(loadNodeWithDefault(node, 'hitstun', 1.0))
        hitboxLock = loadNodeWithDefault(node, 'hitboxLock', "")
        weightInfluence = float(loadNodeWithDefault(node, 'weightInfluence', 1.0))
        shieldMultiplier = float(loadNodeWithDefault(node, 'shieldMultiplier', 1.0))
        transcendence = int(loadNodeWithDefault(node, 'transcendence', 0))
        priorityDiff = float(loadNodeWithDefault(node, 'priority', 1.0))
        xBias = float(loadNodeWithDefault(node, 'xBias', 0))
        yBias = float(loadNodeWithDefault(node, 'yBias', 0))
        xDraw = float(loadNodeWithDefault(node, 'xDraw', 0.1))
        yDraw = float(loadNodeWithDefault(node, 'yDraw', 0.1))
        
        return createHitbox(name, hitboxType, center, size, damage, baseKnockback, knockbackGrowth,
                     trajectory, hitstun, hitboxLock, weightInfluence, shieldMultiplier, transcendence,
                     priorityDiff, xBias, yBias, xDraw, yDraw)

def loadNodeWithDefault(node,subnode,default):
    return node.find(subnode).text if node.find(subnode)is not None else default
        
# Change the properties of an existing hitbox, such as position, or power
class modifyHitbox(SubAction):
    pass

class activateHitbox(SubAction):
    def __init__(self,hitboxName):
        SubAction.__init__(self)
        self.hitboxName = hitboxName
    
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        actor.active_hitboxes.add(action.hitboxes[self.hitboxName])
    
    @staticmethod
    def buildFromXml(node):
        return activateHitbox(node.text)
    
class deactivateHitbox(SubAction):
    def __init__(self,hitboxName):
        SubAction.__init__(self)
        self.hitboxName = hitboxName
    
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        action.hitboxes[self.hitboxName].kill()
    
    @staticmethod
    def buildFromXml(node):
        return deactivateHitbox(node.text)

class updateHitbox(SubAction):
    def __init__(self,hitboxName):
        SubAction.__init__(self)
        self.hitboxName = hitboxName
    
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        action.hitboxes[self.hitboxName].update()
    
    @staticmethod
    def buildFromXml(node):
        return updateHitbox(node.text)


# Change the fighter's Hurtbox (where they have to be hit to take damage)
# This is not done automatically when sprites change, so if your sprite takes the fighter out of his usual bounding box, make sure to change it.
# If a hurtbox overlaps a hitbox, the hitbox will be resolved first, so the fighter won't take damage in the case of clashes.
class modifyHurtBox(SubAction):
    pass

subActionDict = {
                 'changeSprite': changeFighterSprite,
                 'changeSubimage': changeFighterSubimage,
                 'setFrame': changeActionFrame,
                 'nextFrame': nextFrame,
                 'ifVar': ifVar,
                 'createHitbox': createHitbox,
                 'activateHitbox': activateHitbox,
                 'deactivateHitbox': deactivateHitbox,
                 'updateHitbox': updateHitbox
                 }