import engine.hitbox
import baseActions
import pygame.color
import Tkinter as tk

########################################################
#               ABSTRACT ACTIONS                       #
########################################################
def loadNodeWithDefault(node,subnode,default):
    if node is not None:
        return node.find(subnode).text if node.find(subnode)is not None else default
    else:
        return default

# This will load either a variable if the tag contains a "var" tag, or a literal
# value based on the type given. If the node doesn't exist, returns default instead.
def loadValueOrVariable(node, subnode, type="string", default=""):
    if node.find(subnode) is not None:
        if node.find(subnode).find('var') is not None: #if there's a var set
            varNode = node.find(subnode).find('var')
            if not varNode.attrib.has_key('from'):
                fromKey = 'action'
            else: fromKey = varNode.attrib['from']
            if fromKey == 'actor':
                return ('actor', varNode.text)
            elif fromKey == 'action':
                return ('action', varNode.text)
        else: #If it's a normal value
            if type=="int":
                return int(node.find(subnode).text)
            if type=="float":
                return float(node.find(subnode).text)
            if type=="bool":
                return bool(node.find(subnode).text)
            return varNode.text
    else: #If there is no node
        return default
    
# SubActions are a single part of an Action, such as moving a fighter, or tweaking a sprite.
class SubAction():
    def __init__(self):
        pass
    
    def execute(self, action, actor):
        pass
    
    def getDisplayName(self):
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
class ifAttribute(SubAction):
    def __init__(self,variable,comparator='==',value=True,ifActions = [],elseActions = []):
        self.variable = variable
        self.comparator = comparator
        self.value = value
        self.ifActions = ifActions
        self.elseActions = elseActions
        
    def execute(self, action, actor):
        variable = actor.var[self.variable]
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
    
    def getDisplayName(self):
        return 'If Fighter Attribute'
    
    @staticmethod
    def buildFromXml(node):
        variable = node.attrib['var']
        #print(variable)
        
        cond = node.find('cond').text if node.find('cond') is not None else '=='
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
        
        return ifAttribute(variable, cond, value, ifActions, elseActions)

class ifButton(SubAction):
    def __init__(self,button,held,bufferTime=0,ifActions = [],elseActions = []):
        self.button = button
        self.held = held
        self.bufferTime = bufferTime
        self.ifActions = ifActions
        self.elseActions = elseActions
        
    def execute(self, action, actor):
        if self.held:
            cond = self.button in actor.keysHeld
        else:
            cond = actor.keyBuffered(self.button, self.bufferTime)
        if cond:
            for act in self.ifActions:
                act.execute(action,actor)
        else:
            for act in self.elseActions:
                act.execute(action,actor)
    
    def getDisplayName(self):
        return 'If Button'
    
    @staticmethod
    def buildFromXml(node):
        button = node.find('button').text
        if node.find('button').attrib.has_key('held'): held = True
        else: held = False
        bufferTime = int(loadNodeWithDefault(node, 'buffer', 1))
        ifActions = []
        for ifact in node.find('if'):
            if subActionDict.has_key(ifact.tag): #Subactions string to class dict
                ifActions.append(subActionDict[ifact.tag].buildFromXml(ifact))
        #print(ifActions)
        
        elseActions = []
        if node.find('else') is not None:
            for elseact in node.find('else'):
                if subActionDict.has_key(elseact.tag): #Subactions string to class dict
                    elseActions.append(subActionDict[elseact.tag].buildFromXml(elseact))
        #print(elseActions)
        
        return ifButton(button, held, bufferTime, ifActions, elseActions)
    
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
    
    def getDisplayName(self):
        return 'If Variable'
    
    @staticmethod
    def buildFromXml(node):
        variable = node.attrib['var']
        #print(variable)
        
        cond = node.find('cond').text if node.find('cond') is not None else '=='
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
    
    def getDisplayName(self):
        return 'Change Sprite: '+self.sprite
        
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
    
    def getDisplayName(self):
        return 'Change Subimage: '+str(self.index)
        
    @staticmethod
    def buildFromXml(node):
        return changeFighterSubimage(int(node.text))
    
########################################################
#               FIGHTER MOVEMENT                       #
########################################################

# The preferred speed is what a fighter will accelerate/decelerate to. Use this action if you
# want the fighter to gradually speed up to a point (for accelerating), or slow down to a point (for deccelerating)
class changeFighterPreferredSpeed(SubAction):
    def __init__(self,pref_x = None, pref_y = None, xRelative = False):
        SubAction.__init__(self)
        self.pref_x = pref_x
        self.pref_y = pref_y
        self.xRelative = xRelative
        
    def execute(self, action, actor):
        if self.pref_x is not None:
            if type(self.pref_x) is tuple:
                owner,value = self.pref_x
                if owner == 'actor':
                    self.pref_x = actor.var[value]
                elif owner == 'action':
                    self.pref_x = getattr(self, value)
            if self.xRelative: actor.preferred_xspeed = self.pref_x*actor.facing
            else: actor.preferred_xspeed = self.pref_x
            
        if self.pref_y is not None:
            if type(self.pref_y) is tuple:
                owner,value = self.pref_y
                if owner == 'actor':
                    self.pref_y = actor.var[value]
                elif owner == 'action':
                    self.pref_y = getattr(self, value)
            actor.preferred_yspeed = self.pref_y
    
    def getDisplayName(self):
        return 'Change Preferred Speed: ' + str(self.pref_x) + ' X, ' + str(self.pref_y) + 'Y'
        
    @staticmethod
    def buildFromXml(node):
        xRelative = False
        speed_x = loadValueOrVariable(node, 'xSpeed', 'int', None)
        if speed_x and node.find('xSpeed').attrib.has_key("relative"): xRelative = True
        speed_y = loadValueOrVariable(node, 'ySpeed', 'int', None)
        return changeFighterPreferredSpeed(speed_x,speed_y,xRelative)
        
# ChangeFighterSpeed changes the speed directly, with no acceleration/deceleration.
class changeFighterSpeed(SubAction):
    def __init__(self,speed_x = None, speed_y = None, xRelative = False):
        SubAction.__init__(self)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.xRelative = xRelative
        
    def execute(self, action, actor):
        if self.speed_x is not None:
            if type(self.speed_x) is tuple:
                owner,value = self.speed_x
                if owner == 'actor':
                    self.speed_x = actor.var[value]
                elif owner == 'action':
                    self.speed_x = getattr(self, value)
            if self.xRelative: actor.change_x = self.speed_x*actor.facing
            else: actor.change_x = self.speed_x
        
        if self.speed_y is not None:
            if type(self.speed_y) is tuple:
                owner,value = self.speed_y
                if owner == 'actor':
                    self.speed_y = actor.var[value]
                elif owner == 'action':
                    self.speed_y = getattr(self, value)
            
            actor.change_y = self.speed_y
    
    def getDisplayName(self):
        return 'Change Fighter Speed: ' + str(self.speed_x) + ' X, ' + str(self.speed_y) + 'Y'
    
    @staticmethod
    def buildFromXml(node):
        xRelative = False
        speed_x = loadValueOrVariable(node, 'xSpeed', 'int', None)
        if speed_x and node.find('xSpeed').attrib.has_key("relative"): xRelative = True
        speed_y = loadValueOrVariable(node, 'ySpeed', 'int', None)
        return changeFighterSpeed(speed_x,speed_y,xRelative)

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
    def __init__(self,new_x = None, new_y = None, xRelative = False, yRelative = False):
        SubAction.__init__(self)
        self.new_x = new_x
        self.new_y = new_y
        self.xRelative = xRelative
        self.yRelative = yRelative
        
    def execute(self, action, actor):
        if self.new_x:
            if self.xRelative: actor.rect.x += self.new_x * actor.facing
            else: actor.rect.x = self.new_x
        if self.new_y:
            if self.yRelative: actor.rect.y += self.new_y
            else: actor.rect.y = self.new_y
    
    def getDisplayName(self):
        return 'Shift Position: ' + str(self.pref_x) + ' X, ' + str(self.pref_y) + 'Y'
    
    @staticmethod
    def buildFromXml(node):
        new_x = loadNodeWithDefault(node, 'xPos', None)
        new_y = loadNodeWithDefault(node, 'yPos', None)
        xRel = False
        yRel = False
        if node.find('xPos') is not None:
            new_x = int(new_x)
            xRel = node.find('xPos').attrib.has_key('relative')
        if node.find('yPos') is not None:
            new_y = int(new_y)
            yRel = node.find('yPos').attrib.has_key('relative')
        return shiftFighterPosition(new_x,new_y,xRel,yRel)

class shiftSpritePosition(SubAction):
    def __init__(self,new_x = None, new_y = None, xRelative = False):
        SubAction.__init__(self)
        self.new_x = new_x
        self.new_y = new_y
        self.xRelative = xRelative
        
    def execute(self, action, actor):
        (old_x,old_y) = actor.sprite.spriteOffset
        if self.new_x is not None:
            old_x = self.new_x
            if self.xRelative: old_x = old_x * actor.facing
        if self.new_y is not None:
            old_y = self.new_y
        
        actor.sprite.spriteOffset = (old_x,old_y)
        #print(actor.sprite.spriteOffset)
    
    def getDisplayName(self):
        return 'Shift Sprite: ' + str(self.new_x) + ' X, ' + str(self.new_y) + 'Y'
        
    @staticmethod
    def buildFromXml(node):
        new_x = loadNodeWithDefault(node, 'xPos', None)
        new_y = loadNodeWithDefault(node, 'yPos', None)
        xRel = False
        if node.find('xPos') is not None:
            new_x = int(new_x)
            xRel = node.find('xPos').attrib.has_key('relative')
        if node.find('yPos') is not None:
            new_y = int(new_y)
        return shiftSpritePosition(new_x,new_y,xRel)
    
class updateLandingLag(SubAction):
    def __init__(self,newLag,reset = False):
        self.newLag = newLag
        self.reset = reset
        
    def execute(self, action, actor):
        actor.updateLandingLag(self.newLag,self.reset)
    
    def getDisplayName(self):
        return 'Update Landing Lag: ' + str(self.newLag)
        
    @staticmethod
    def buildFromXml(node):
        return updateLandingLag(int(node.text),node.attrib.has_key('reset'))
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
    def __init__(self,newFrame,relative=False):
        SubAction.__init__(self)
        self.frame = newFrame
        self.relative = relative
        
    def execute(self, action, actor):
        if self.relative: action.frame += self.frame
        else: action.frame = self.frame
    
    def getDisplayName(self):
        if self.relative:
            return 'Change Frame By: ' + str(self.frame)
        else:
            return 'Set Frame: ' + str(self.frame)
            
    @staticmethod
    def buildFromXml(node):
        return changeActionFrame(int(node.text),node.attrib.has_key('relative'))
        
# Go to the next frame in the action
class nextFrame(SubAction):
    def execute(self, action, actor):
        action.frame += 1
    
    def getDisplayName(self):
        return 'Next Frame'
    
    @staticmethod
    def buildFromXml(node):
        return nextFrame()
    
# Call a fighter's do<Action> function to change the action.
class changeAction(SubAction):
    pass

class transitionState(SubAction):
    def __init__(self,transition):
        SubAction.__init__(self)
        self.transition = transition
    
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        baseActions.stateDict[self.transition](actor)
    
    def getDisplayName(self):
        return 'Apply Transition State: ' + str(self.transition)
        
    @staticmethod
    def buildFromXml(node):
        return transitionState(node.text)
        
########################################################
#                 HIT/HURTBOXES                        #
########################################################

# Create a new hitbox
class createHitbox(SubAction):
    def __init__(self,name,hitboxType,
                 center,size,
                 damage,baseKnockback,knockbackGrowth,trajectory,hitstun=1,
                 hitboxLock="",
                 damageMultiplier=1,velocityMultiplier=1,hp=1,
                 weightInfluence=1,shieldMultiplier=1,transcendence=0,priorityDiff=0,
                 chargeDamage=0,chargeBKB=0,chargeKBG=0,
                 xBias=0,yBias=0,xDraw=0.1,yDraw=0.1,
                 base_hitstun=1, hitlag_multiplier=1):
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
        self.damageMultiplier = damageMultiplier
        self.velocityMultiplier = velocityMultiplier
        self.hp = hp
        self.weightInfluence = weightInfluence
        self.shieldMultiplier = shieldMultiplier
        self.transcendence = transcendence
        self.priorityDiff = priorityDiff
        self.chargeDamage = chargeDamage
        self.chargeBKB = chargeBKB
        self.chargeKBG = chargeKBG
        self.xBias = xBias
        self.yBias = yBias
        self.xDraw = xDraw
        self.yDraw = yDraw
        self.baseHitstun = base_hitstun
        self.hitlagMultiplier = hitlag_multiplier
        
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        #Use an existing hitbox lock by name, or create a new one
        if self.hitboxLock and action.hitboxLocks.has_key(self.hitboxLock):
            hitboxLock = action.hitboxLocks[self.hitboxLock]
        else:
            hitboxLock = engine.hitbox.HitboxLock()
            action.hitboxLocks[self.hitboxLock] = hitboxLock
        
        #Create the hitbox of the right type    
        if self.hitboxType == "damage":
            hitbox = engine.hitbox.DamageHitbox(self.center, self.size, actor, 
                                       self.damage, self.baseKnockback, self.knockbackGrowth, self.trajectory, self.hitstun, 
                                       hitboxLock,
                                       self.weightInfluence, self.shieldMultiplier, self.transcendence, self.priorityDiff,
                                       self.chargeDamage, self.chargeBKB, self.chargeKBG,
                                       self.baseHitstun, self.hitlagMultiplier)
        elif self.hitboxType == "sakurai":
            hitbox = engine.hitbox.SakuraiAngleHitbox(self.center, self.size, actor,
                                                      self.damage, self.baseKnockback, self.knockbackGrowth, self.trajectory, self.hitstun,
                                                      hitboxLock,
                                                      self.weightInfluence, self.shieldMultiplier, self.transcendence, self.priorityDiff,
                                                      self.chargeDamage, self.chargeBKB, self.chargeKBG,
                                                      self.baseHitstun, self.hitlagMultiplier)
        elif self.hitboxType == "autolink":
            hitbox = engine.hitbox.AutolinkHitbox(self.center, self.size, actor,
                                                  self.damage,self.hitstun,
                                                  hitboxLock,
                                                  self.xBias,self.yBias,
                                                  self.shieldMultiplier,self.velocityMultiplier,self.transcendence,self.priorityDiff,
                                                  self.chargeDamage,self.chargeBKB,self.chargeKBG,
                                                  self.baseHitstun, self.hitlagMultiplier)
        elif self.hitboxType == "funnel":
            hitbox = engine.hitbox.FunnelHitbox(self.center, self.size, actor, self.damage, self.baseKnockback, self.trajectory, self.hitstun, hitboxLock,
                                                self.xDraw, self.yDraw, self.shieldMultiplier, self.transcendence, self.priorityDiff,\
                                                self.chargeDamage, self.chargeBKB, self.chargeKBG,
                                                self.baseHitstun, self.hitlagMultiplier)
        elif self.hitboxType == "grab":
            pass
        elif self.hitboxType == "reflector":
            hitbox = engine.hitbox.ReflectorHitbox(self.center, self.size, actor,
                                                   hitboxLock,
                                                   self.damageMultiplier, self.velocityMultiplier,
                                                   self.hp, self.trajectory, self.transcendence)
        action.hitboxes[self.name] = hitbox
    
    def getDisplayName(self):
        return 'Create New Hitbox: ' + self.name
        
    @staticmethod
    def buildFromXml(node):
        SubAction.buildFromXml(node)
        #mandatory fields
        name = node.find('name').text
        hitboxType = node.attrib['type'] if node.attrib.has_key('type') else "damage"
        center = map(int, node.find('center').text.split(','))
        size = map(int, node.find('size').text.split(','))
        damage = float(loadNodeWithDefault(node, 'damage', 0))
        baseKnockback = float(loadNodeWithDefault(node, 'baseKnockback', 0))
        knockbackGrowth = float(loadNodeWithDefault(node, 'knockbackGrowth', 0))
        trajectory = int(loadNodeWithDefault(node, 'trajectory', 0))
        
        hitstun = float(loadNodeWithDefault(node, 'hitstun', 1.0))
        hitboxLock = loadNodeWithDefault(node, 'hitboxLock', "")
        damageMultiplier = float(loadNodeWithDefault(node, 'damageMultiplier', 1.0))
        velocityMultiplier = float(loadNodeWithDefault(node, 'velocityMultiplier', 1.0))
        hp = int(loadNodeWithDefault(node, 'hp', 1))
        weightInfluence = float(loadNodeWithDefault(node, 'weightInfluence', 1.0))
        shieldMultiplier = float(loadNodeWithDefault(node, 'shieldMultiplier', 1.0))
        transcendence = int(loadNodeWithDefault(node, 'transcendence', 0))
        priorityDiff = float(loadNodeWithDefault(node, 'priority', 1.0))
        
        chargeDamage = float(loadNodeWithDefault(node.find('chargeable'), 'damage', 0))
        chargeBKB = float(loadNodeWithDefault(node.find('chargeable'), 'baseKnockback', 0))
        chargeKBG = float(loadNodeWithDefault(node.find('chargeable'), 'knockbackGrowth', 0))
        
        xBias = float(loadNodeWithDefault(node, 'xBias', 0))
        yBias = float(loadNodeWithDefault(node, 'yBias', 0))
        xDraw = float(loadNodeWithDefault(node, 'xDraw', 0.1))
        yDraw = float(loadNodeWithDefault(node, 'yDraw', 0.1))
        
        base_hitstun = int(loadNodeWithDefault(node, 'baseHitstun', 1))
        hitlag_multiplier = int(loadNodeWithDefault(node, 'hitlagMultiplier', 1))
        
        return createHitbox(name, hitboxType, center, size, damage, baseKnockback, knockbackGrowth,
                     trajectory, hitstun, hitboxLock, damageMultiplier, velocityMultiplier, hp, weightInfluence, shieldMultiplier, transcendence,
                     priorityDiff, chargeDamage, chargeBKB, chargeKBG,
                     xBias, yBias, xDraw, yDraw,
                     base_hitstun, hitlag_multiplier)
        
# Change the properties of an existing hitbox, such as position, or power
class modifyHitbox(SubAction):
    def __init__(self,hitboxName,hitboxVars):
        SubAction.__init__(self)
        self.hitboxName = hitboxName
        self.hitboxVars = hitboxVars
        
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        hitbox = action.hitboxes[self.hitboxName]
        if hitbox:
            for name,value in self.hitboxVars.iteritems():
                if hasattr(hitbox, name):
                    setattr(hitbox, name, value)
    
    def getDisplayName(self):
        return 'Modify Hitbox: ' + str(self.hitboxName)
    
    @staticmethod
    def buildFromXml(node):
        SubAction.buildFromXml(node)
        hitboxName = node.attrib['name']
        hitboxVars = {}
        for var in node:
            t = var.attrib['type'] if var.attrib.has_key('type') else None
            if t and t == 'int':
                hitboxVars[var.tag] = int(var.text)
            elif t and t == 'float':
                hitboxVars[var.tag] = float(var.text)
            else: hitboxVars[var.tag] = var.text
        print(hitboxVars)
        return modifyHitbox(hitboxName,hitboxVars)
        
class activateHitbox(SubAction):
    def __init__(self,hitboxName):
        SubAction.__init__(self)
        self.hitboxName = hitboxName
    
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        actor.active_hitboxes.add(action.hitboxes[self.hitboxName])
    
    def getDisplayName(self):
        return 'Activate Hitbox: ' + self.hitboxName
    
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
    
    def getDisplayName(self):
        return 'Deactivate Hitbox: ' + self.hitboxName
    
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
    
    def getDisplayName(self):
        return 'Update Hitbox Position: ' + self.hitboxName
    
    @staticmethod
    def buildFromXml(node):
        return updateHitbox(node.text)


class unlockHitbox(SubAction):
    def __init__(self,hitboxName):
        SubAction.__init__(self)
        self.hitboxName = hitboxName
        
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        action.hitboxes[self.hitboxName].hitbox_lock = engine.hitbox.HitboxLock()
    
    def getDisplayName(self):
        return 'Unlock Hitbox: ' + self.hitboxName
    
    @staticmethod
    def buildFromXml(node):
        return unlockHitbox(node.text)
    
# Change the fighter's Hurtbox (where they have to be hit to take damage)
# This is not done automatically when sprites change, so if your sprite takes the fighter out of his usual bounding box, make sure to change it.
# If a hurtbox overlaps a hitbox, the hitbox will be resolved first, so the fighter won't take damage in the case of clashes.
class modifyHurtBox(SubAction):
    def __init__(self,center,size,imageCenter = False):
        SubAction.__init__(self)
        self.center = center
        self.size = size
        self.imageCenter = imageCenter
        
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        actor.hurtbox.rect.size = self.size
        if self.imageCenter:
            actor.hurtbox.rect.centerx = (actor.sprite.boundingRect.centerx + self.center[0])
            actor.hurtbox.rect.centery = (actor.sprite.boundingRect.centery + self.center[1])
        else:
            actor.hurtbox.rect.centerx = actor.sprite.rect.centerx + self.center[0]
            actor.hurtbox.rect.centery = actor.sprite.rect.centery + self.center[1]
        
    def getDisplayName(self):
        return 'Modify Fighter Hurtbox'
    @staticmethod
    def buildFromXml(node):
        imageCenter = False
        center = map(int, node.find('center').text.split(','))
        if node.find('center').attrib.has_key('centerOn') and node.find('center').attrib['centerOn'] == 'image':
            imageCenter = True
        size = map(int, node.find('size').text.split(','))
        return modifyHurtBox(center,size,imageCenter)

class changeECB(SubAction):
    def __init__(self,center,size,ecbOffset):
        SubAction.__init__(self)
        self.center = center
        self.size = size
        self.offset = ecbOffset
        
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        action.ecbSize = self.size
        action.ecbCenter = self.center
        action.ecbOffset = self.offset
    
    def getDisplayName(self):
        return 'Modify Fighter Collision Box'
    
    @staticmethod
    def buildFromXml(node):
        center=[0,0]
        size = [0,0]
        ecbOffset = [0,0]
        if node.find('center') is not None:
            center = map(int, node.find('center').text.split(','))
        if node.find('size') is not None:
            size = map(int, node.find('size').text.split(','))
        if node.find('offset') is not None:
            ecbOffset = map(int, node.find('offset').text.split(','))
        return changeECB(center,size,ecbOffset)

class loadArticle(SubAction):
    def __init__(self,article,name):
        SubAction.__init__(self)
        self.article = article
        self.name = name
        
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        action.articles[self.name] = actor.loadArticle(self.article)
        print(action.articles)
    
    def getDisplayName(self):
        return 'Load Article: ' + self.name
        
    @staticmethod
    def buildFromXml(node):
        return loadArticle(node.text,node.attrib['name'])
        
class activateArticle(SubAction):
    def __init__(self,name):
        SubAction.__init__(self)
        self.name = name
        
    def execute(self, action, actor):
        action.articles[self.name].activate()
    
    def getDisplayName(self):
        return 'Activate Article: ' + self.name
        
    @staticmethod
    def buildFromXml(node):
        return activateArticle(node.text)
    
class deactivateArticle(SubAction):
    def __init__(self,name):
        SubAction.__init__(self)
        self.name = name
        
    def execute(self, action, actor):
        action.articles[self.name].deactivate()
    
    def getDisplayName(self):
        return 'Deactivate Article: ' + self.name
        
    @staticmethod
    def buildFromXml(node):
        return deactivateArticle(node.text)

class doAction(SubAction):
    def __init__(self,action):
        SubAction.__init__(self)
        self.action = action
        
    def execute(self, action, actor):
        actor.doAction(self.action)
        
    def getDisplayName(self):
        return 'Change Action: ' + self.action
    
    @staticmethod
    def buildFromXml(node):
        return doAction(node.text)

class createMask(SubAction):        
    def __init__(self,color,duration,pulseLength):
        SubAction.__init__(self)
        self.color = color
        self.duration = duration
        self.pulseLength = pulseLength
        
    def execute(self, action, actor):
        pulse = True if self.pulseLength > 0 else False
        color = [self.color.r,self.color.g,self.color.b]
        actor.createMask(color,self.duration,pulse,self.pulseLength)
    
    def getDisplayName(self):
        return 'Create Color Mask: ' + str(self.color)
    
    @staticmethod
    def buildFromXml(node):
        color = pygame.color.Color(node.find('color').text)
        duration = int(node.find('duration').text)
        pulseLength = int(loadNodeWithDefault(node, 'pulse', 0))
        return createMask(color,duration,pulseLength)

class removeMask(SubAction):
    def __init__(self):
        SubAction.__init__(self)
    
    def execute(self, action, actor):
        actor.mask = None
        
    def getDisplayName(self):
        return 'Remove Color Mask'
    
    @staticmethod
    def buildFromXml(node):
        return removeMask()
            
class debugAction(SubAction):
    def __init__(self,statement):
        SubAction.__init__(self)
        self.statement = statement
        
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        print(self.statement)
    
    def getDisplayName(self):
        return 'Print Debug'
    
    @staticmethod
    def buildFromXml(node):
        return debugAction(node.text)
        
subActionDict = {
                 'changeSprite': changeFighterSprite,
                 'changeSubimage': changeFighterSubimage,
                 'changeFighterSpeed': changeFighterSpeed,
                 'changeFighterPreferredSpeed': changeFighterPreferredSpeed,
                 'shiftPosition': shiftFighterPosition,
                 'shiftSprite': shiftSpritePosition,
                 'setFrame': changeActionFrame,
                 'nextFrame': nextFrame,
                 'ifAttribute': ifAttribute,
                 'ifVar': ifVar,
                 'ifButton': ifButton,
                 'modifyHurtbox': modifyHurtBox,
                 'changeECB': changeECB,
                 'createHitbox': createHitbox,
                 'activateHitbox': activateHitbox,
                 'deactivateHitbox': deactivateHitbox,
                 'updateHitbox': updateHitbox,
                 'modifyHitbox': modifyHitbox,
                 'unlockHitbox': unlockHitbox,
                 'loadArticle': loadArticle,
                 'activateArticle': activateArticle,
                 'deactivateArticle': deactivateArticle,
                 'transitionState': transitionState,
                 'updateLandingLag': updateLandingLag,
                 'doAction': doAction,
                 'createMask': createMask,
                 'removeMask': removeMask,
                 'print': debugAction
                 }
