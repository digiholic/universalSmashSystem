import engine.hitbox
import baseActions
import pygame.color
import builder.subactionSelector as subactionSelector
import xml.etree.ElementTree as ElementTree
from ast import literal_eval as make_tuple

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
    
    def getPropertiesPanel(self,root):
        return subactionSelector.BasePropertiesFrame(root,self)
    
    def getXmlElement(self):
        return ElementTree.Element(self.__class__.__name__)
    
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
class If(SubAction):
    def __init__(self,variable,source,function,value,ifActions,elseActions):
        self.variable = variable
        self.source = source
        self.function = function
        self.value = value
        self.ifActions = ifActions
        self.elseActions = elseActions
        
    def execute(self, action, actor):
        if self.source == 'fighter':
            if actor.attr.has_key(self.variable):
                variable = actor.attr[self.variable]
            else: variable = getattr(actor, self.variable)
        else:
            variable = getattr(action, self.variable)
        
        if self.function == '==':
            function = lambda var,val: var == val
        elif self.function == '!=':
            function = lambda var,val: not var == val
        elif self.function == '>=':
            function = lambda var,val: var >= val
        elif self.function == '<=':
            function = lambda var,val: var <= val
        elif self.function == '>':
            function = lambda var,val: var > val
        elif self.function == '<':
            function = lambda var,val: var < val
            
        cond = function(variable,self.value)
        
        if cond:
            if self.ifActions and action.conditionalActions.has_key(self.ifActions):
                for act in action.conditionalActions[self.ifActions]:
                    print(act)
                    act.execute(action,actor)
        else:
            if self.elseActions and action.conditionalActions.has_key(self.ifActions):
                for act in action.conditionalActions[self.ifActions]:
                    act.execute(action,actor)
                    
    def getDisplayName(self):
        return 'If ' + self.source + ' ' + self.variable
    
    def getXmlElement(self):
        elem = ElementTree.Element('If')
        elem.attrib['function'] = self.function
        
        variableElem = ElementTree.Element('variable')
        variableElem.attrib['source'] = self.source
        variableElem.text = str(self.variable)
        elem.append(variableElem)
        
        valueElem = ElementTree.Element('value')
        valueElem.attrib['type'] = type(self.value).__name__
        valueElem.text = str(self.value)
        elem.append(valueElem)
        
        if self.ifActions:
            passElem = ElementTree.Element('pass')
            passElem.text = self.ifActions
            elem.append(passElem)
        if self.elseActions:
            failElem = ElementTree.Element('fail')
            failElem.text = self.elseActions
            elem.append(failElem)
        
        return elem
    
    @staticmethod
    def buildFromXml(node):
        #load the function
        if node.attrib.has_key('function'):
            function = node.attrib['function']
        else:
            function = '=='
        
        #build the actual function
        
            
        #get the variable and source
        variable = node.find('variable').text
        if node.find('variable').attrib.has_key('source'):
            source = node.find('variable').attrib['source']
        else:
            source = 'action'
        
        #get the value
        value = node.find('value').text
        if node.find('value').attrib.has_key('type'):
            vartype = node.find('value').attrib['type']
        if vartype == 'int':
            value = int(value)
        elif vartype == 'float':
            value = float(value)
        elif vartype == 'bool':
            value = bool(value)
        
        ifActions = loadNodeWithDefault(node, 'pass', None)
        elseActions = loadNodeWithDefault(node, 'fail', None)
        return If(variable,source,function,value,ifActions,elseActions)

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
                  
########################################################
#                SPRITE CHANGERS                       #
########################################################
      
# ChangeFighterSprite will change the sprite of the fighter (Who knew?)
# Optionally pass it a subImage index to start at that frame instead of 0
class changeFighterSprite(SubAction):
    def __init__(self,sprite):
        SubAction.__init__(self)
        self.sprite = sprite
        
    def execute(self, action, actor):
        action.spriteName = self.sprite
        actor.changeSprite(self.sprite)
    
    def getDisplayName(self):
        return 'Change Sprite: '+self.sprite
    
    def getPropertiesPanel(self,root):
        return subactionSelector.ChangeSpriteProperties(root,self)
    
    def getXmlElement(self):
        elem = ElementTree.Element('changeSprite')
        elem.text = str(self.sprite)
        return elem
    
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
    
    def getPropertiesPanel(self, root):
        return subactionSelector.ChangeSubimageProperties(root,self)
    
    def getXmlElement(self):
        elem = ElementTree.Element('changeSubimage')
        elem.text = str(self.index)
        return elem
        
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
    
    def getPropertiesPanel(self, root):
        return subactionSelector.ChangePreferredSpeedProperties(root,self)
    
    def getDisplayName(self):
        return 'Change Preferred Speed: ' + str(self.pref_x) + ' X, ' + str(self.pref_y) + 'Y'
    
    def getXmlElement(self):
        elem = ElementTree.Element('changeFighterPreferredSpeed')
        
        if self.pref_x is not None:
            xElem = ElementTree.Element('xSpeed')
            if self.xRelative: xElem.attrib['relative'] = 'True'
            xElem.text = str(self.pref_x)
            elem.append(xElem)
        
        if self.pref_y is not None:
            yElem = ElementTree.Element('ySpeed')
            yElem.text = str(self.pref_y)
            elem.append(yElem)
        return elem
        
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
    
    def getPropertiesPanel(self, root):
        return subactionSelector.ChangeSpeedProperties(root,self)
    
    def getDisplayName(self):
        return 'Change Fighter Speed: ' + str(self.speed_x) + ' X, ' + str(self.speed_y) + 'Y'
    
    def getXmlElement(self):
        elem = ElementTree.Element('changeFighterSpeed')
        
        if self.speed_x is not None:
            xElem = ElementTree.Element('xSpeed')
            if self.xRelative: xElem.attrib['relative'] = 'True'
            xElem.text = str(self.speed_x)
            elem.append(xElem)
            
        if self.speed_y is not None:
            yElem = ElementTree.Element('ySpeed')
            yElem.text = str(self.speed_y)
            elem.append(yElem)
            
        return elem
    
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
    
    def getXmlElement(self):
        elem = ElementTree.Element('shiftPosition')
        
        if self.new_x is not None:
            xElem = ElementTree.Element('xSpeed')
            if self.xRelative: xElem.attrib['relative'] = 'True'
            xElem.text = str(self.new_x)
            elem.append(xElem)
        
        if self.new_y is not None:
            yElem = ElementTree.Element('ySpeed')
            if self.yRelative: yElem.attrib['relative'] = 'True'
            yElem.text = str(self.new_y)
            elem.append(yElem)
            
        return elem
    
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
    
    def getXmlElement(self):
        elem = ElementTree.Element('shiftSprite')
        
        if self.new_x is not None:
            xElem = ElementTree.Element('xPos')
            if self.xRelative: xElem.attrib['relative'] = 'True'
            xElem.text = str(self.new_x)
            elem.append(xElem)
        
        if self.new_y is not None:
            yElem = ElementTree.Element('yPos')
            yElem.text = str(self.new_y)
            elem.append(yElem)
            
        return elem
        
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
    
    def getXmlElement(self):
        elem = ElementTree.Element('updateLandingLag')
        if self.reset: elem.attrib['reset'] = 'True'
        elem.text = str(self.newLag)
        return elem
    
    @staticmethod
    def buildFromXml(node):
        return updateLandingLag(int(node.text),node.attrib.has_key('reset'))
########################################################
#           ATTRIBUTES AND VARIABLES                   #
########################################################

# Change a fighter attribute, for example, weight or remaining jumps
class modifyFighterVar(SubAction):
    def __init__(self,attr,val):
        SubAction.__init__(self)
        self.attr = attr
        self.val = val
        
    def execute(self, action, actor):
        if actor.var.has_key(self.attr):
            actor.var[self.attr] = self.val
        else: setattr(actor,self.attr,self.val)
        
    @staticmethod
    def buildFromXml(node):
        attr = node.attrib['var']
        value = node.find('value').text
        if node.find('value').attrib.has_key('type'):
            vartype = node.find('value').attrib['type']
        else: vartype = 'string'
        if vartype == 'int':
            value = int(value)
        elif vartype == 'float':
            value = float(value)
        elif vartype == 'bool':
            value = bool(value)
        return modifyFighterVar(attr,value)
    
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
        self.newFrame = newFrame
        self.relative = relative
        
    def execute(self, action, actor):
        if self.relative: action.frame += self.newFrame
        else: action.frame = self.newFrame
    
    def getDisplayName(self):
        if self.relative:
            return 'Change Frame By: ' + str(self.newFrame)
        else:
            return 'Set Frame: ' + str(self.newFrame)
    
    def getXmlElement(self):
        elem = ElementTree.Element('setFrame')
        if self.relative: elem.attrib['relative'] = 'True'
        elem.text = str(self.newFrame)
        return elem
            
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
    
class transitionState(SubAction):
    def __init__(self,transition):
        SubAction.__init__(self)
        self.transition = transition
    
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        baseActions.stateDict[self.transition](actor)
    
    def getDisplayName(self):
        return 'Apply Transition State: ' + str(self.transition)
    
    def getXmlElement(self):
        elem = ElementTree.Element('transitionState')
        elem.text = str(self.transition)
        return elem
    
    @staticmethod
    def buildFromXml(node):
        return transitionState(node.text)
        
########################################################
#                 HIT/HURTBOXES                        #
########################################################

# Create a new hitbox
class createHitbox(SubAction):
    def __init__(self, name, hitboxType, hitboxLock, variables):
        SubAction.__init__(self)
        
        self.hitboxName = name
        self.hitboxType = hitboxType if hitboxType is not None else "damage"
        self.hitboxLock = hitboxLock
        self.hitboxVars = variables
        
    def execute(self, action, actor):
        SubAction.execute(self, action, actor)
        #Use an existing hitbox lock by name, or create a new one
        if self.hitboxLock and action.hitboxLocks.has_key(self.hitboxLock):
            hitboxLock = action.hitboxLocks[self.hitboxLock]
        else:
            hitboxLock = engine.hitbox.HitboxLock(self.hitboxLock)
            action.hitboxLocks[self.hitboxLock] = hitboxLock
        
        #Create the hitbox of the right type    
        if self.hitboxType == "damage":
            hitbox = engine.hitbox.DamageHitbox(actor,hitboxLock,self.hitboxVars)
        elif self.hitboxType == "sakurai":
            hitbox = engine.hitbox.SakuraiAngleHitbox(actor,hitboxLock,self.hitboxVars)
        elif self.hitboxType == "autolink":
            hitbox = engine.hitbox.AutolinkHitbox(actor,hitboxLock,self.hitboxVars)
        elif self.hitboxType == "funnel":
            hitbox = engine.hitbox.FunnelHitbox(actor,hitboxLock,self.hitboxVars)
        elif self.hitboxType == "grab":
            pass
        elif self.hitboxType == "reflector":
            hitbox = engine.hitbox.ReflectorHitbox(self.center, self.size, actor,
                                                   hitboxLock,
                                                   self.damageMultiplier, self.velocityMultiplier,
                                                   self.hp, self.trajectory, self.transcendence)
        action.hitboxes[self.hitboxName] = hitbox
    
    def getDisplayName(self):
        return 'Create New Hitbox: ' + self.hitboxName
    
    def getPropertiesPanel(self, root):
        return subactionSelector.ModifyHitboxProperties(root,self,newHitbox=True)
       
    def getXmlElement(self):
        elem = ElementTree.Element('createHitbox')
        elem.attrib['type'] = self.hitboxType
        nameElem = ElementTree.Element('name')
        nameElem.text = self.hitboxName
        elem.append(nameElem)
        for tag,value in self.hitboxVars.iteritems():
            newElem = ElementTree.Element(tag)
            newElem.text = str(value)
            elem.append(newElem)
        lockElem = ElementTree.Element('hitboxLock')
        lockElem.text = self.hitboxLock
        elem.append(lockElem)
        return elem
    
    @staticmethod
    def buildFromXml(node):
        SubAction.buildFromXml(node)
        #mandatory fields
        hitboxType = node.attrib['type'] if node.attrib.has_key('type') else "damage"
        
        #build the variable dict
        variables = {}
        #these lists let the code know which keys should be which types.
        tupleType = ['center','size']
        floatType = ['damage','baseKnockback','knockbackGrowth','hitsun','damageMultiplier','velocityMultiplier',
                     'weightInfluence','shieldMultiplier','priorityDiff','chargeDamage','chargeBKB','chargeKBG',
                     'xBias','yBias','xDraw','yDraw','hitlag_multiplier']
        intType = ['trajectory','hp','transcendence','base_hitstun',]
        for child in node:
            tag = child.tag
            val = child.text
            #special cases
            hitboxLock = None
            if tag == 'name':
                name = val
            elif tag == 'hitboxLock':
                hitboxLock = val
            elif tag in tupleType:
                variables[tag] = make_tuple(val)
            elif tag in floatType:
                variables[tag] = float(val)
            elif tag in intType:
                variables[tag] = int(val)
            
        
        return createHitbox(name, hitboxType, hitboxLock, variables)
        
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
    
    def getPropertiesPanel(self, root):
        return subactionSelector.ModifyHitboxProperties(root,self,newHitbox=False)
        
    def getXmlElement(self):
        elem = ElementTree.Element('modifyHitbox')
        elem.attrib['name'] = self.hitboxName
        for tag,value in self.hitboxVars.iteritems():
            newElem = ElementTree.Element(tag)
            newElem.text = str(value)
            elem.append(newElem)
        return elem
    
    @staticmethod
    def buildFromXml(node):
        SubAction.buildFromXml(node)
        hitboxName = node.attrib['name']
        hitboxVars = {}
        
        tupleType = ['center','size']
        floatType = ['damage','baseKnockback','knockbackGrowth','hitsun','damageMultiplier','velocityMultiplier',
                     'weightInfluence','shieldMultiplier','priorityDiff','chargeDamage','chargeBKB','chargeKBG',
                     'xBias','yBias','xDraw','yDraw','hitlag_multiplier']
        intType = ['trajectory','hp','transcendence','base_hitstun','x_offset','y_offset','width','height']
        
        for child in node:
            tag = child.tag
            val = child.text
            #special cases
            if tag in tupleType:
                hitboxVars[tag] = make_tuple(val)
            elif tag in floatType:
                hitboxVars[tag] = float(val)
            elif tag in intType:
                hitboxVars[tag] = int(val)
        
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
    
    def getXmlElement(self):
        elem = ElementTree.Element('activateHitbox')
        elem.text = self.hitboxName
        return elem
    
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
    
    def getXmlElement(self):
        elem = ElementTree.Element('deactivateHitbox')
        elem.text = self.hitboxName
        return elem
    
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
    
    def getXmlElement(self):
        elem = ElementTree.Element('updateHitbox')
        elem.text = self.hitboxName
        return elem
    
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
    
    def getXmlElement(self):
        elem = ElementTree.Element('unlockHitbox')
        elem.text = self.hitboxName
        return elem
    
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
                 'setFighterVar': modifyFighterVar,
                 'changeSprite': changeFighterSprite,
                 'changeSubimage': changeFighterSubimage,
                 'changeFighterSpeed': changeFighterSpeed,
                 'changeFighterPreferredSpeed': changeFighterPreferredSpeed,
                 'shiftPosition': shiftFighterPosition,
                 'shiftSprite': shiftSpritePosition,
                 'setFrame': changeActionFrame,
                 'nextFrame': nextFrame,
                 'if': If,
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
