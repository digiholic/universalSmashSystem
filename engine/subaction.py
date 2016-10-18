import engine.hitbox
import engine.hurtbox
import baseActions
import pygame.color
import builder.subactionSelector as subactionSelector
import xml.etree.ElementTree as ElementTree
from ast import literal_eval as make_tuple
import settingsManager

"""
TODO -
    EnableAction
    DisableAction
    SetTimer
"""

########################################################
#               ABSTRACT ACTIONS                       #
########################################################
def loadNodeWithDefault(_node,_sub_node,_default):
    if _node is not None:
        return _node.find(_sub_node).text if _node.find(_sub_node)is not None else _default
    else:
        return _default

"""
Gets data or builds a variable. Any time anything needs data, this should be used.
"""
def parseData(_data,_type="string",_default=None):
    if _data is None: #If there is no data, return default
        return _default
    if _data.find('var') is not None: #If the data has a Var tag
        varTag = _data.find('var')
        
        if varTag.attrib.has_key('source'): source = varTag.attrib['source']
        else: source = 'actor'
        
        return VarData(source,varTag.text)
    if _data.find('function') is not None:
        funcTag = _data.find('function')
        if funcTag.attrib.has_key('source'): source = funcTag.attrib['source']
        else: source = 'actor'
        
        funcName = loadNodeWithDefault(funcTag, 'functionName', '')
        
        args = dict()
        if funcTag.find('args') is not None:
            for arg in funcTag.find('args'):
                if arg.attrib.has_key('type'):
                    vartype = arg.attrib['type']
                else: vartype = 'string'
                
                val = parseData(arg, vartype, _default)
                args[arg.tag] = val
                
        return FuncData(source,funcName,args)

    if _data.find('eval') is not None:
        evalTag = _data.find('eval')
        if evalTag.attrib.has_key('scope'): scope = evalTag.attrib['scope']
        else: scope = 'action'
        return EvalData(scope, evalTag.text)
        
    
    if _type=="dynamic":
        if _data.attrib.has_key('type'):
            _type = _data.attrib['type']
        else: _type = 'string'
    if _type=="string": return _data.text
    if _type=="int": return int(_data.text)
    if _type=="float": return float(_data.text)
    if _type=="bool": return (_data.text.lower() == 'true')
    if _type=="tuple": return make_tuple(_data.text)

"""
An object that will load a variable from either an action or a fighter.
Pulls data at runtime
"""
class VarData():
    def __init__(self,_source,_var):
        self.source = _source
        self.var = _var
        
    def unpack(self,_action,_actor):
        if self.source == 'actor':
            if _actor.stats.has_key(self.var):
                return _actor.stats[self.var]
            elif _actor.vars.has_key(self.var):
                return _actor.vars[self.var]
            elif hasattr(_actor, self.var):
                return getattr(_actor, self.var)
            else: return None
        if self.source == 'action':
            if hasattr(_action, self.var):
                return getattr(_action, self.var)
        if self.source == 'timing':
            if hasattr(_actor, 'key_bindings') and hasattr(_actor.key_bindings, 'timing_window'):
                return _actor.key_bindings.timing_window[self.var]
        return None

"""
An object to pull a value from a function. Pulls at runtime.
@_source: The source of the function. A filepath, or "actor" or "action"
@_functionName: The function to call
@_args: A dict of arguments to pass the function
"""
class FuncData():
    def __init__(self,_source,_functionName,_args):
        self.source = _source
        self.functionName = _functionName
        self.args = _args
        
    def unpack(self,_action,_actor):
        for argname,arg in self.args.iteritems():
            if isinstance(arg, FuncData) or isinstance(arg, VarData) or isinstance(arg, EvalData):
                self.args[argname] = arg.unpack(_action,_actor)
                
        if self.source == 'actor':
            if hasattr(_actor, self.functionName):
                method = getattr(_actor, self.functionName)
                return method(**self.args)
            else:
                print('No such function exists in actor: '+str(self.functionName))
                return None
        elif self.source == 'action':
            if hasattr(_action, self.functionName):
                method = getattr(_action, self.functionName)
                return method(**self.args)
            else:
                print('No such function exists in action: '+str(self.functionName))
                return None
        else:
            module = settingsManager.importFromURI(self.source, self.source.split('/')[-1])
            print(module)
            if hasattr(module, self.functionName):
                method = getattr(module, self.functionName)
                return method(**self.args)
            else:
                print('No such function exists in '+ module +': '+str(self.functionName))
                return None
            #TODO we'll fix this later. Add in the ability to call a function by filepath.
        return None

"""
An object that will execute a line of python code and returns its return value
Pulls data at runtime
"""
class EvalData(object):
    def __init__(self,_scope,_str):
        self.str = _str
        self.scope = _scope
        
    def unpack(self,_action,_actor):
        if self.scope == 'action':
            working_locals = {field: getattr(_action, field) for field in dir(_action)}
        elif self.scope == 'actor':
            working_locals = {field: getattr(_actor, field) for field in dir(_actor)}
        elif self.scope == 'global':
            working_locals = globals()
        elif self.scope == 'battle':
            working_locals = {field: getattr(_actor.game_state, field) for field in dir(_actor.game_state)}
        elif self.scope == 'local':
            working_locals = locals()
        else:
            print(self.scope + " is not a valid scope")
            return None
        return eval(self.str, globals(), working_locals)
    
"""
Used for building subActions dynamically. Each one has a path to get to its XML data,
and a variable to set in the SubAction. It is used to read from XML and store as XML.

Paths are in the form of root|attrib>node|attrib>subnode
For example, this XML string:

    <root testAttrib="0">
        <subNode0 />
        <subNode1>
            <subSubNode0 attrib="1" />
        </subNode1>
    </root>

Can have the following paths
    "root"
    "root|testAttrib"
    "root>subNode0"
    "root>subNode1"
    "root>subNode1>subSubNode0"
    "root>subNode1>subSubNode0|attrib"
"""
class NodeMap():
    def __init__(self,_variableName,_variableType,_path,_defaultValue):
        self.variableName = _variableName
        self.variableType = _variableType
        self.path = _path
        self.defaultValue = _defaultValue
        
    def getTypeFromData(self,_data):
        if self.variableType=="dynamic":
            if _data.attrib.has_key('type'):
                self.variableType = _data.attrib['type']
            else: self.variableType = 'string'
        if self.variableType=="string": return _data
        if self.variableType=="int": return int(_data)
        if self.variableType=="float": return float(_data)
        if self.variableType=="bool": return (_data.lower() == 'true')
        if self.variableType=="tuple": make_tuple(_data)
            
            
    def populateFromXML(self,_subAction,_rootNode):
        nodeList = []
        currentPosition = _rootNode
        for node in self.path.split('>'):
            nodeList.append(node.split('|'))
            
        #if it's set up right, the first node in the list should be the same as our root node
        if nodeList[0][0] == _rootNode.tag:
            if len(nodeList) == 1: #We only have the root or a root attribute
                nodePath = nodeList[0]
                if len(nodePath) > 1: #If we've hit an attribute
                    if _rootNode.attrib.has_key(nodePath[1]):
                        _subAction.defaultVars[self.variableName] = self.getTypeFromData(_rootNode.attrib[nodePath[1]])
                        setattr(_subAction, self.variableName, self.getTypeFromData(_rootNode.attrib[nodePath[1]]))
                    else:
                        _subAction.defaultVars[self.variableName] = self.defaultValue
                        setattr(_subAction, self.variableName, self.defaultValue)
                    return
                else:
                    _subAction.defaultVars[self.variableName] = parseData(_rootNode, self.variableType, self.defaultValue)
                    setattr(_subAction, self.variableName, parseData(_rootNode, self.variableType, self.defaultValue))
                    return
                
            for nodePath in nodeList[1:]: #iterate through everything else
                currentPosition = currentPosition.find(nodePath[0])
                if currentPosition is None: #If we hit a dead end
                    _subAction.defaultVars[self.variableName] = self.defaultValue
                    setattr(_subAction,self.variableName,self.defaultValue)
                    return
                if len(nodePath) > 1: #If we've hit an attribute
                    if currentPosition.attrib.has_key(nodePath[1]):
                        _subAction.defaultVars[self.variableName] = self.getTypeFromData(currentPosition.attrib[nodePath[1]])
                        setattr(_subAction, self.variableName, self.getTypeFromData(currentPosition.attrib[nodePath[1]]))
                    else:
                        _subAction.defaultVars[self.variableName] = self.defaultValue
                        setattr(_subAction, self.variableName, self.defaultValue)
                    return
                
            #If we leave the loop and haven't exited, we didn't hit an attrib either.
            _subAction.defaultVars[self.variableName] = parseData(currentPosition, self.variableType, self.defaultValue)
            setattr(_subAction, self.variableName, parseData(currentPosition, self.variableType, self.defaultValue))
            return
        
        _subAction.defaultVars[self.variableName] = self.defaultValue
        setattr(_subAction,self.variableName,self.defaultValue)
        return
        #Iterate through list, scanning nodes as you go
    
    def storeAsXML(self,_subAction,_rootNode):
        nodeList = []
        currentPosition = _rootNode
        for node in self.path.split('>'):
            nodeList.append(node.split('|'))
            
        if nodeList[0][0] == _rootNode.tag:
            if len(nodeList) == 1: #We only have the root or a root attribute
                nodePath = nodeList[0]
                if len(nodePath) > 1: #If we've hit an attribute
                    _rootNode.attrib[nodePath[1]] = str(getattr(_subAction, self.variableName))
                    return
                else:
                    _rootNode.text = str(getattr(_subAction, self.variableName))
                    return
                
            for nodePath in nodeList[1:]: #iterate through everything else
                if currentPosition.find(nodePath[0]) is None:
                    elem = ElementTree.Element(nodePath[0])
                    currentPosition.append(elem)
                
                currentPosition = currentPosition.find(nodePath[0])
                
                if len(nodePath) > 1: #If we've hit an attribute
                    currentPosition.attrib[nodePath[1]] = str(getattr(_subAction, self.variableName))
                    return
            #If we leave the loop and haven't exited, we didn't hit an attrib either.
            currentPosition.text = str(getattr(_subAction, self.variableName))
            return
        
        setattr(_subAction,self.variableName,self.defaultValue)
        return
    
    def getBuilderEntry(self):
        pass
        
# This will load either a variable if the tag contains a "var" tag, or a literal
# value based on the type given. If the _node doesn't exist, returns default instead.
def loadValueOrVariable(_node, _sub_node, _type="string", _default=""):
    if _node.find(_sub_node) is not None:
        if _node.find(_sub_node).find('var') is not None: #if there's a var set
            var_node = _node.find(_sub_node).find('var')
            if not var_node.attrib.has_key('from'):
                fromKey = 'action'
            else: fromKey = var_node.attrib['from']
            if fromKey == 'actor':
                return ('actor', var_node.text)
            elif fromKey == 'action':
                return ('action', var_node.text)
        else: #If it's a normal value
            if _type=="int":
                return int(_node.find(_sub_node).text)
            if _type=="float":
                return float(_node.find(_sub_node).text)
            if _type=="bool":
                return bool(_node.find(_sub_node).text)
            return var_node.text
    else: #If there is no _node
        return _default
    
# SubActions are a single part of an Action, such as moving a fighter, or tweaking a sprite.
class SubAction():
    subact_group = 'None'
    fields = []
    
    def __init__(self):
        self.defaultVars = dict()
    
    def execute(self, _action, _actor):
        for tag,variable in self.defaultVars.iteritems():
            if isinstance(variable, VarData) or isinstance(variable, FuncData) or isinstance(variable, EvalData):
                setattr(self, tag, variable.unpack(_action,_actor))
                
    def getDisplayName(self):
        return ''
    
    def getPropertiesPanel(self,_root):
        return subactionSelector.BasePropertiesFrame(_root,self)
    
    def getXmlElement(self):
        elem = ElementTree.Element(name_dict[self.__class__])
        for node in self.fields:
            node.storeAsXML(self, elem)
            
        return elem
    
    @staticmethod
    def buildFromXml(_subactName,_node):
        if hasattr(subaction_dict[_subactName], 'customBuildFromXml'):
            return subaction_dict[_subactName].customBuildFromXml(_node)
        
        subAction = subaction_dict[_subactName]()
        for node in subaction_dict[_subactName].fields:
            node.populateFromXML(subAction, _node)
        return subAction
    
########################################################
#                 CONDITIONALS                         #
########################################################
class If(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('variable','string','if>variable',''),
              NodeMap('source','string','if>variable|source','action'),
              NodeMap('function','string','if|function','=='),
              NodeMap('value','dynamic','if>value',True),
              NodeMap('if_actions','string','if>pass',''),
              NodeMap('else_actions','string','if>fail','')
              ]
    
    def __init__(self,_variable='',_source='action',_function='==',_value='True',_ifActions='',_elseActions=''):
        SubAction.__init__(self)
        self.variable = _variable
        self.source = _source
        self.function = _function
        self.value = _value
        self.if_actions = _ifActions
        self.else_actions = _elseActions
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.variable == '': return
        if self.source == 'fighter' or self.source == 'actor':
            #If this is for an article, we want to use the owner as the actor
            if isinstance(_actor, engine.article.DynamicArticle):
                actor = _actor.owner
            else: actor = _actor
            
            if actor.stats.has_key(self.variable):
                variable = actor.stats[self.variable]
            elif actor.vars.has_key(self.variable):
                variable = actor.vars[self.variable]
            else: variable = getattr(actor, self.variable)
        else:
            variable = getattr(_action, self.variable)
        
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
            if self.if_actions and _action.events.has_key(self.if_actions):
                for act in _action.events[self.if_actions]:
                    act.execute(_action,_actor)
                    
        else:
            if self.else_actions and _action.events.has_key(self.else_actions):
                for act in _action.events[self.else_actions]:
                    act.execute(_action,_actor)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.IfProperties(_root,self)
                    
    def getDisplayName(self):
        return 'If '+self.source+' '+self.variable+' '+str(self.function)+' '+str(self.value)+': '+self.if_actions
    
    def getXmlElement(self):
        elem = ElementTree.Element('If')
        elem.attrib['function'] = self.function
        
        variable_elem = ElementTree.Element('variable')
        variable_elem.attrib['source'] = self.source
        variable_elem.text = str(self.variable)
        elem.append(variable_elem)
        
        value_elem = ElementTree.Element('value')
        value_elem.attrib['type'] = type(self.value).__name__
        value_elem.text = str(self.value)
        elem.append(value_elem)
        
        if self.if_actions:
            pass_elem = ElementTree.Element('pass')
            pass_elem.text = self.if_actions
            elem.append(pass_elem)
        if self.else_actions:
            fail_elem = ElementTree.Element('fail')
            fail_elem.text = self.else_actions
            elem.append(fail_elem)
        
        return elem

class ifButton(SubAction):
    subact_group = 'Control'
    
    def __init__(self,_button='',_check='keyBuffered',_bufferFrom=0,_bufferTo=0,_threshold=0.1,_ifActions='',_elseActions='',_beyondAction=False):
        SubAction.__init__(self)
        self.button = _button
        self.check = _check
        self.buffer_from = _bufferFrom
        self.buffer_to = _bufferTo
        self.threshold = _threshold
        self.if_actions = _ifActions
        self.else_actions = _elseActions
        self.beyond_action = _beyondAction
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.button == '': return

        if self.beyond_action:
            working_from = self.buffer_from
        else:
            working_from = max(min(_actor.last_input_frame, self.buffer_from), 1)
        
        if self.check == 'keysContain':
            cond = _actor.keysContain(self.button, self.threshold)
        elif self.check == 'keyBuffered':
            cond = _actor.keyBuffered(self.button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'keyTapped':
            cond = _actor.keyTapped(self.button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'keyHeld':
            cond = _actor.keyHeld(self.button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'keyUp':
            cond = _actor.keyUp(self.button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'keyReinput':
            cond = _actor.keyReinput(self.button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'keyIdle':
            cond = _actor.keyIdle(self.button, working_from, self.threshold, self.buffer_to)
        elif self.check == 'smash':
            cond = _actor.checkSmash(self.button)
        elif self.check == 'tap':
            cond = _actor.checkTap(self.button)
        else:
            return

        if cond:
            if self.if_actions and _action.events.has_key(self.if_actions):
                for act in _action.events[self.if_actions]:
                    act.execute(_action,_actor)
        else:
            if self.else_actions and _action.events.has_key(self.else_actions):
                for act in _action.events[self.else_actions]:
                    act.execute(_action,_actor)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.IfButtonProperties(_root,self)
    
    def getDisplayName(self):
        if self.check == 'keysContain':
            pressed_text = 'is pressed to a depth of at least ' + str(self.threshold)
        elif self.check == 'keyBuffered':
            pressed_text = 'was pressed to a depth of at least ' + str(self.threshold) + ' between frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'keyTapped':
            pressed_text = 'was tapped to a depth of at least ' + str(self.threshold) + ' within frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'keyHeld':
            pressed_text = 'was held to a depth of at least ' + str(self.threshold) + ' through frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'keyUp':
            pressed_text = 'was released from a depth of at least ' + str(self.threshold) + ' between frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'keyReinput':
            pressed_text = 'was released and reinput from a depth of at least ' + str(self.threshold) + ' within frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'keyIdle':
            pressed_text = 'was released from a depth of at least ' + str(self.threshold) + ' through frames ' + str(self.buffer_to) + ' and ' + str(self.buffer_from)
        elif self.check == 'smash':
            pressed_text = 'was smashed'
        elif self.check == 'tap':
            pressed_text = 'was tapped'
        else:
            return 'Unknown check type: ' + self.check

        if self.beyond_action:
            pressed_text += ':'
        else:
            pressed_text += ' during this action:'
            
        return 'If '+self.button+' '+pressed_text+self.if_actions
    
    def getXmlElement(self):
        elem = ElementTree.Element('ifButton')
        
        button_elem = ElementTree.Element('button')
        
        check_elem = ElementTree.Element('check')
        check_elem.text = self.check
        elem.append(check_elem)
        
        from_elem = ElementTree.Element('from')
        from_elem.text = str(self.buffer_from)
        if self.beyond_action: from_elem.attrib['beyondAction'] = 'True'
        elem.append(from_elem)
        
        to_elem = ElementTree.Element('to')
        to_elem.text = str(self.buffer_to)
        elem.append(to_elem)
        
        threshold_elem = ElementTree.Element('threshold')
        threshold_elem.text = str(self.threshold)
        elem.append(threshold_elem)
        
        if self.if_actions:
            pass_elem = ElementTree.Element('pass')
            pass_elem.text = self.if_actions
            elem.append(pass_elem)
        if self.else_actions:
            fail_elem = ElementTree.Element('fail')
            fail_elem.text = self.else_actions
            elem.append(fail_elem)
        
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        button = _node.find('button')
        if button.attrib.has_key('check'):
            check = button.attrib['check']
        else: check = 'keyBuffered'
        button = button.text
        buffer_from = int(loadNodeWithDefault(_node, 'from', 1))
        buffer_to = int(loadNodeWithDefault(_node, 'to', 0))
        threshold = float(loadNodeWithDefault(_node, 'threshold', 0.1))
        
        if_actions = loadNodeWithDefault(_node, 'pass', None)
        else_actions = loadNodeWithDefault(_node, 'fail', None)
        
        return ifButton(button, check, buffer_from, buffer_to, threshold, if_actions, else_actions, _node.attrib.has_key('beyondAction'))
                  
########################################################
#                SPRITE CHANGERS                       #
########################################################
      
# ChangeFighterSprite will change the sprite of the fighter (Who knew?)
# Optionally pass it a subImage index to start at that frame instead of 0
class changeFighterSprite(SubAction):
    subact_group = 'Sprite'
    fields = [NodeMap('sprite','string','changeSprite','idle'),
              NodeMap('preserve_index','bool','changeSprite|preserve',False)
              ]
    
    def __init__(self):
        SubAction.__init__(self)
        self.sprite = 'idle' #default data
        self.preserve_index = False #default data
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.preserve_index: index = _actor.sprite.index
        else: index = 0
        _action.sprite_name = self.sprite
        _actor.changeSprite(self.sprite,index)
    
    def getDisplayName(self):
        return 'Change Sprite: '+self.sprite
    
    def getPropertiesPanel(self,_root):
        return subactionSelector.ChangeSpriteProperties(_root,self)
    
# ChangeFighterSubimage will change the subimage of a sheetSprite without changing the sprite.
class changeFighterSubimage(SubAction):
    subact_group = 'Sprite'
    fields = [NodeMap('index','int','changeSubimage',0),
              NodeMap('relative','bool','changeSubimage|relative',False)
              ]
    
    def __init__(self,_index=0,_relative=False):
        SubAction.__init__(self)
        self.index = _index
        self.relative = _relative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _action.sprite_rate = 0 #sprite_rate has been broken, so we have to ignore it from now on
        #TODO changeSpriteRate subaction
        if self.relative: _actor.changeSpriteImage(self.index+_actor.sprite.index)
        else: _actor.changeSpriteImage(self.index)
        
    def getDisplayName(self):
        return 'Change Subimage: '+str(self.index)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ChangeSubimageProperties(_root,self)

class flip(SubAction):
    subact_group = 'Sprite'
    fields = []
    def __init__(self):
        SubAction.__init__(self)
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.flip()
        
    def getDisplayName(self):
        return 'Flip Sprite'
    
    def getPropertiesPanel(self, _root):
        return None
    
########################################################
#               FIGHTER MOVEMENT                       #
########################################################

# The preferred speed is what a fighter will accelerate/decelerate to. Use this action if you
# want the fighter to gradually speed up to a point (for accelerating), or slow down to a point (for deccelerating)
class changeFighterPreferredSpeed(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('speed_x','float','changeFighterPreferredSpeed>xSpeed',None),
              NodeMap('x_relative','bool','changeFighterPreferredSpeed>xSpeed|relative',False),
              NodeMap('speed_y','float','changeFighterPreferredSpeed>ySpeed',None)
              ]
    def __init__(self,_speedX = None, _speedY = None, _xRelative = False):
        SubAction.__init__(self)
        self.speed_x = _speedX
        self.speed_y = _speedY
        self.x_relative = _xRelative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.speed_x is not None:
            if type(self.speed_x) is tuple:
                owner,value = self.speed_x
                if owner == 'actor':
                    self.speed_x = _actor.stats[value]
                elif owner == 'action':
                    self.speed_x = getattr(self, value)
            if self.x_relative: _actor.preferred_xspeed = self.speed_x*_actor.facing
            else: _actor.preferred_xspeed = self.speed_x
            
        if self.speed_y is not None:
            if type(self.speed_y) is tuple:
                owner,value = self.speed_y
                if owner == 'actor':
                    self.speed_y = _actor.stats[value]
                elif owner == 'action':
                    self.speed_y = getattr(self, value)
            _actor.preferred_yspeed = self.speed_y
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ChangeSpeedProperties(_root,self)
    
    def getDisplayName(self):
        x_str = str(self.speed_x)+' X' if self.speed_x is not None else ''
        sep_str = ', ' if self.speed_x and self.speed_y else ''
        y_str = str(self.speed_y)+' Y' if self.speed_y is not None else ''
        return 'Change Preferred Speed: '+x_str+sep_str+y_str
    
    def getXmlElement(self):
        elem = ElementTree.Element('changeFighterPreferredSpeed')
        
        if self.speed_x is not None:
            x_elem = ElementTree.Element('xSpeed')
            if self.x_relative: x_elem.attrib['relative'] = 'True'
            x_elem.text = str(self.speed_x)
            elem.append(x_elem)
        
        if self.speed_y is not None:
            y_elem = ElementTree.Element('ySpeed')
            y_elem.text = str(self.speed_y)
            elem.append(y_elem)
        return elem

# ChangeFighterSpeed changes the speed directly, with no acceleration/deceleration.
class changeFighterSpeed(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('speed_x','float','changeFighterSpeed>xSpeed',None),
              NodeMap('x_relative','bool','changeFighterSpeed>xSpeed|relative',False),
              NodeMap('speed_y','float','changeFighterSpeed>ySpeed',None),
              NodeMap('y_relative','bool','changeFighterSpeed>ySpeed|relative',False),
              NodeMap('direction','int','changeFighterSpeed>direction',None),
              NodeMap('magnitude','float','changeFighterSpeed>magnitude',None),
              ]
    
    def __init__(self,_speedX = None, _speedY = None, _xRelative = False, _yRelative = False, _direction = None, _magnitude = None):
        SubAction.__init__(self)
        self.speed_x = _speedX
        self.speed_y = _speedY
        self.x_relative = _xRelative
        self.y_relative = _yRelative
        self.direction = _direction
        self.magnitude = _magnitude
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.direction is not None and self.magnitude is not None:
            x,y = settingsManager.getXYFromDM(self.direction,self.magnitude)
            _actor.change_x = x
            _actor.change_y = y    
        else:
            if self.speed_x is not None:
                if type(self.speed_x) is tuple:
                    owner,value = self.speed_x
                    if owner == 'actor':
                        self.speed_x = _actor.stats[value]
                    elif owner == 'action':
                        self.speed_x = getattr(self, value)
                if self.x_relative: _actor.change_x = self.speed_x*_actor.facing
                else: _actor.change_x = self.speed_x
            
            if self.speed_y is not None:
                if type(self.speed_y) is tuple:
                    owner,value = self.speed_y
                    if owner == 'actor':
                        self.speed_y = _actor.stats[value]
                    elif owner == 'action':
                        self.speed_y = getattr(self, value)
                if self.y_relative:_actor.change_y += self.speed_y
                else: _actor.change_y = self.speed_y
        
        
    def getPropertiesPanel(self, _root):
        return subactionSelector.ChangeSpeedProperties(_root,self)
    
    def getDisplayName(self):
        x_str = str(self.speed_x)+' X' if self.speed_x is not None else ''
        sep_str = ', ' if self.speed_x and self.speed_y else ''
        y_str = str(self.speed_y)+' Y' if self.speed_y is not None else ''
        return 'Change Fighter Speed: '+x_str+sep_str+y_str
    
    def getXmlElement(self):
        elem = ElementTree.Element('changeFighterSpeed')
        
        if self.speed_x is not None:
            x_elem = ElementTree.Element('xSpeed')
            if self.x_relative: x_elem.attrib['relative'] = 'True'
            x_elem.text = str(self.speed_x)
            elem.append(x_elem)
            
        if self.speed_y is not None:
            y_elem = ElementTree.Element('ySpeed')
            if self.y_relative: y_elem.attrib['relative'] = 'True'
            y_elem.text = str(self.speed_y)
            elem.append(y_elem)
            
        return elem
    
class changeGravity(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('new_gravity','float','changeGravity',False)]
    
    def __init__(self,_newGrav=1):
        SubAction.__init__(self)
        self.new_gravity = _newGrav
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.calcGrav(self.new_gravity)
        
    def getPropertiesPanel(self, _root):
        #TODO Properties
        return SubAction.getPropertiesPanel(self, _root)
    
    def getDisplayName(self):
        return 'Change Gravity Multiplier to '+self.new_gravity
    
# ApplyForceVector is usually called when launched, but can be used as an alternative to setting speed. This one
# takes a direction in degrees (0 being forward, 90 being straight up, 180 being backward, 270 being downward)
# and a magnitude.
# Set the "preferred" flag to make the vector affect preferred speed instead of directly changing speed.
class applyForceVector(SubAction):
    def __init__(self, _magnitude, _direction, _preferred = False):
        SubAction.__init__(self)
        self.magnitude= _magnitude
        self.direction = _direction
        self.preferred = _preferred
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.setSpeed(self.magnitude,self.direction,self.preferred)

# ShiftFighterPositon directly changes the fighter's x and y coordinates without regard for wall checks, speed limites, or gravity.
# Don't use this for ordinary movement unless you're totally sure what you're doing.
# A good use for this is to jitter a hit opponent during hitlag, just make sure to put them back where they should be before actually launching.
class shiftFighterPosition(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('new_x','int','shiftPosition>xPos',None),
              NodeMap('x_relative','bool','shiftPosition>xPos|relative',False),
              NodeMap('new_y','int','shiftPosition>yPos',None),
              NodeMap('y_relative','bool','shiftPosition>yPos|relative',False)
              ]
    
    def __init__(self,_newX = None, _newY = None, _xRelative = False, _yRelative = False):
        SubAction.__init__(self)
        self.new_x = _newX
        self.new_y = _newY
        self.x_relative = _xRelative
        self.y_relative = _yRelative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.new_x:
            if self.x_relative: _actor.rect.x += self.new_x * _actor.facing
            else: _actor.rect.x = self.new_x
        if self.new_y:
            if self.y_relative: _actor.rect.y += self.new_y
            else: _actor.rect.y = self.new_y
            
    def getDisplayName(self):
        return 'Shift Position: ' + str(self.new_x) + ' X, ' + str(self.new_y) + 'Y'
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ShiftPositionProperties(_root,self)
    
    def getXmlElement(self):
        elem = ElementTree.Element('shiftPosition')
        
        if self.new_x is not None:
            x_elem = ElementTree.Element('xPos')
            if self.x_relative: x_elem.attrib['relative'] = 'True'
            x_elem.text = str(self.new_x)
            elem.append(x_elem)
        
        if self.new_y is not None:
            y_elem = ElementTree.Element('yPos')
            if self.y_relative: y_elem.attrib['relative'] = 'True'
            y_elem.text = str(self.new_y)
            elem.append(y_elem)
            
        return elem
    
    
class setInvulnerability(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('invuln_amt','int','setInvulnerability',0),
              ]
    
    def __init__(self,_amt=0):
        self.invuln_amt = _amt
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.invulnerable = self.invuln_amt
    
    def getDisplayName(self):
        return "Set invulnerability time to "+str(self.invuln_amt)
    
    def getPropertiesPanel(self,_root):
        #TODO add this
        return subactionSelector.BasePropertiesFrame(_root,self)
    
class shiftSpritePosition(SubAction):
    subact_group = 'Sprite'
    fields = [NodeMap('new_x','int','shiftSprite>xPos',None),
              NodeMap('x_relative','bool','shiftSprite>xPos|relative',None),
              NodeMap('new_y','int','shiftSprite>yPos',None)
              ]
    
    def __init__(self,_newX = None, _newY = None, _xRelative = False):
        SubAction.__init__(self)
        self.new_x = _newX
        self.new_y = _newY
        self.x_relative = _xRelative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        (old_x,old_y) = _actor.sprite.spriteOffset
        if self.new_x is not None:
            old_x = self.new_x
            if self.x_relative: old_x = old_x * _actor.facing
        if self.new_y is not None:
            old_y = self.new_y
        
        _actor.sprite.spriteOffset = (old_x,old_y)
        #print(actor.sprite.spriteOffset)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ShiftSpriteProperties(_root,self)
    
    def getDisplayName(self):
        return 'Shift Sprite: ' + str(self.new_x) + ' X, ' + str(self.new_y) + 'Y'
    
    def getXmlElement(self):
        elem = ElementTree.Element('shiftSprite')
        
        if self.new_x is not None:
            x_elem = ElementTree.Element('xPos')
            if self.x_relative: x_elem.attrib['relative'] = 'True'
            x_elem.text = str(self.new_x)
            elem.append(x_elem)
        
        if self.new_y is not None:
            y_elem = ElementTree.Element('yPos')
            y_elem.text = str(self.new_y)
            elem.append(y_elem)
            
        return elem
        
class updateLandingLag(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('new_lag','int','updateLandingLag',0),
              NodeMap('reset','bool','updateLandingLag|reset',False)
              ]
    
    def __init__(self,_newLag=0,_reset = False):
        SubAction.__init__(self)
        self.new_lag = _newLag
        self.reset = _reset
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.updateLandingLag(self.new_lag,self.reset)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.UpdateLandingLagProperties(_root,self)
    
    def getDisplayName(self):
        if self.reset: start_str = 'Reset '
        else: start_str = 'Update '
        return start_str+'Landing Lag: ' + str(self.new_lag)

    
########################################################
#           ATTRIBUTES AND VARIABLES                   #
########################################################

# Change a fighter attribute, for example, weight or remaining jumps
class modifyFighterVar(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('attr','string','setFighterVar|var',''),
              NodeMap('val','dynamic','setFighterVar>value',None),
              NodeMap('relative','bool','setFighterVar>value|relative',False)
              ]
              
    def __init__(self,_attr='',_val=None,_relative=False):
        SubAction.__init__(self)
        self.attr = _attr
        self.val = _val
        self.relative = _relative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if not self.attr =='':
            if _actor.stats.has_key(self.attr):
                if self.relative: _actor.stats[self.attr] += self.val
                else: _actor.stats[self.attr] = self.val
            elif _actor.vars.has_key(self.attr):
                if self.relative: _actor.vars[self.attr] += self.val
                else: _actor.vars[self.attr] = self.val
            else:
                if self.relative:
                    setattr(_actor, self.attr, getattr(_actor, self.attr)+1)
                else: setattr(_actor,self.attr,self.val)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyFighterVarProperties(_root,self)
    
    def getDisplayName(self):
        return 'Set fighter '+self.attr+' to '+str(self.val)
    
    
# Modify a variable in the action or fighter, such as a conditional flag of some sort.
class setVar(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('source','string','setVar|source',''),
              NodeMap('attr','string','setVar>variable',''),
              NodeMap('val','dynamic','setVar>value',None),
              NodeMap('relative','bool','setVar>value|relative',False)
              ]
              
    def __init__(self,_source='action',_attr='',_val=None,_relative=False):
        SubAction.__init__(self)
        self.attr = _attr
        self.source = _source
        self.val = _val
        self.relative = _relative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.source == 'action': source = _action
        elif self.source == 'fighter': source = _actor
        if not self.attr =='': #If there's a variable to set
            if hasattr(source, 'stats') and source.stats.has_key(self.attr): #if it has a var dict, let's check it first
                if self.relative: source.stats[self.attr] += self.val
                else: source.stats[self.attr] = self.val
            elif hasattr(source, 'vars') and source.varss.has_key(self.attr):
                if self.relative: source.vars[self.attr] += self.val
                else: source.vars[self.attr] = self.val
            else:
                print(source,self.attr,self.val)
                if self.relative:
                    setattr(source, self.attr, getattr(source, self.attr)+self.val)
                else: setattr(source,self.attr,self.val)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyFighterVarProperties(_root,self)
    
    def getDisplayName(self):
        return 'Set '+self.source+' '+self.attr+' to '+str(self.val)
                   
# Change the frame of the action to a value.
class changeActionFrame(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('new_frame','int','setFrame',0),
              NodeMap('relative','bool','setFrame|relative',None)
              ]
    
    def __init__(self,_newFrame=0,_relative=False):
        SubAction.__init__(self)
        self.new_frame = _newFrame
        self.relative = _relative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.relative: _action.frame += self.new_frame
        else: _action.frame = self.new_frame
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ChangeFrameProperties(_root,self)
    
    def getDisplayName(self):
        if self.relative:
            return 'Change Frame By: ' + str(self.new_frame)
        else:
            return 'Set Frame: ' + str(self.new_frame)
    
        
# Go to the next frame in the action
class nextFrame(SubAction):
    subact_group = 'Control'
    fields = []
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _action.frame += 1
    
    def getDisplayName(self):
        return 'Next Frame'

    
class transitionState(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('transition','string','transitionState','')
              ]
    
    def __init__(self,_transition=''):
        SubAction.__init__(self)
        self.transition = _transition
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if baseActions.state_dict.has_key(self.transition):
            baseActions.state_dict[self.transition](_actor)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.TransitionProperties(_root,self)
    
    def getDisplayName(self):
        return 'Apply Transition State: ' + str(self.transition)
    
########################################################
#                 HIT/HURTBOXES                        #
########################################################

# Create a new hitbox
class createHitbox(SubAction):
    subact_group = 'Hitbox'
    
    def __init__(self, _name='', _hitboxType='damage', _hitboxLock='', _variables={}, _owner_event = '', _other_event = ''):
        SubAction.__init__(self)
        
        self.hitbox_name = _name
        self.hitbox_type = _hitboxType if _hitboxType is not None else "damage"
        self.hitbox_lock = _hitboxLock
        self.hitbox_vars = _variables
        self.owner_event = _owner_event
        self.other_event = _other_event
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if not isinstance(_actor, engine.abstractFighter.AbstractFighter):
            _actor = _actor.owner
        if self.hitbox_name == '': return #Don't make a hitbox without a name or we'll lose it
        #Use an existing hitbox lock by name, or create a new one
        
        if self.hitbox_lock and _action.hitbox_locks.has_key(self.hitbox_lock):
            hitbox_lock = _action.hitbox_locks[self.hitbox_lock]
        else:
            hitbox_lock = engine.hitbox.HitboxLock(self.hitbox_lock)
            _action.hitbox_locks[self.hitbox_lock] = hitbox_lock
        
        #Create the hitbox of the right type    
        if self.hitbox_type == "damage":
            hitbox = engine.hitbox.DamageHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "sakurai":
            hitbox = engine.hitbox.SakuraiAngleHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "autolink":
            hitbox = engine.hitbox.AutolinkHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "funnel":
            hitbox = engine.hitbox.FunnelHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "grab":
            hitbox = engine.hitbox.GrabHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "reflector":
            hitbox = engine.hitbox.ReflectorHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "absorber":
            hitbox = engine.hitbox.AbsorberHitbox(_actor,hitbox_lock,self.hitbox_vars)
        elif self.hitbox_type == "invulnerable":
            hitbox = engine.hitbox.InvulnerableHitbox(_actor, hitbox_lock, self.hitbox_vars)
        elif self.hitbox_type == "shield":
            hitbox = engine.hitbox.ShieldHitbox(_actor, hitbox_lock, self.hitbox_vars)
        elif self.hitbox_type == "throw":
            hitbox = engine.hitbox.ThrowHitbox(_actor, hitbox_lock, self.hitbox_vars)
            
        if hasattr(_action, 'events'): #Articles don't have events, and this can be called from article
            if _action.events.has_key(self.owner_event):
                hitbox.owner_on_hit_actions = _action.events[self.owner_event]
            if _action.events.has_key(self.other_event):
                hitbox.other_on_hit_actions = _action.events[self.other_event]
        
        _action.hitboxes[self.hitbox_name] = hitbox
    
    def getDisplayName(self):
        return 'Create New Hitbox: ' + self.hitbox_name
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyHitboxProperties(_root,self,newHitbox=True)
       
    def getXmlElement(self):
        elem = ElementTree.Element('createHitbox')
        elem.attrib['type'] = self.hitbox_type
        name_elem = ElementTree.Element('name')
        name_elem.text = self.hitbox_name
        elem.append(name_elem)
        for tag,value in self.hitbox_vars.iteritems():
            new_elem = ElementTree.Element(tag)
            new_elem.text = str(value)
            elem.append(new_elem)
        lock_elem = ElementTree.Element('hitboxLock')
        lock_elem.text = self.hitbox_lock
        elem.append(lock_elem)
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        #mandatory fields
        hitbox_type = _node.attrib['type'] if _node.attrib.has_key('type') else "damage"
        
        #build the variable dict
        variables = {}
        #these lists let the code know which keys should be which types.
        tuple_type = ['center','size']
        float_type = ['damage','base_knockback','knockback_growth','hitsun','damage_multiplier','velocity_multiplier',
                     'weight_influence','shield_multiplier','priority_diff','charge_damage','charge_base_knockback','charge_knockback_growth',
                     'x_bias','y_bias','x_draw','y_draw','hitlag_multiplier','hitstun_multiplier']
        int_type = ['trajectory','hp','transcendence','base_hitstun']
        boolean_type = ['ignore_shields', 'ignore_armor']
        hitbox_lock = None
            
        for child in _node:
            tag = child.tag
            val = child.text
            
            owner_event = ''
            other_event = ''
            #special cases
            if tag == 'name':
                name = val
            elif tag == 'hitboxLock':
                hitbox_lock = val
            elif tag == 'onHitOwner':
                owner_event = val
            elif tag == 'onHitOther':
                other_event = val
            elif tag in tuple_type:
                variables[tag] = make_tuple(val)
            elif tag in float_type:
                variables[tag] = float(val)
            elif tag in int_type:
                variables[tag] = int(val)
            else:
                print('string variable',tag,val)
                variables[tag] = val
            
        
        return createHitbox(name, hitbox_type, hitbox_lock, variables, owner_event, other_event)
        
# Change the properties of an existing hitbox, such as position, or power
class modifyHitbox(SubAction):
    subact_group = 'Hitbox'
    
    def __init__(self,_hitboxName='',_hitboxVars={}):
        SubAction.__init__(self)
        self.hitbox_name = _hitboxName
        self.hitbox_vars = _hitboxVars
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.hitboxes.has_key(self.hitbox_name):
            hitbox = _action.hitboxes[self.hitbox_name]
            if hitbox:
                for name,value in self.hitbox_vars.iteritems():
                    if hasattr(hitbox, name):
                        if isinstance(value, VarData) or isinstance(value, FuncData) or isinstance(value, EvalData):
                            setattr(hitbox, name, value.unpack(_action,_actor))
                            if name in hitbox.variable_dict:
                                hitbox.variable_dict[name] = value.unpack(_action, _actor)
                        else: 
                            setattr(hitbox, name, value)
                            if name in hitbox.variable_dict:
                                hitbox.variable_dict[name] = value
        
    def getDisplayName(self):
        return 'Modify Hitbox: ' + str(self.hitbox_name)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyHitboxProperties(_root,self,newHitbox=False)
        
    def getXmlElement(self):
        elem = ElementTree.Element('modifyHitbox')
        elem.attrib['name'] = self.hitbox_name
        for tag,value in self.hitbox_vars.iteritems():
            new_elem = ElementTree.Element(tag)
            new_elem.text = str(value)
            elem.append(new_elem)
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        hitbox_name = _node.attrib['name']
        hitbox_vars = {}
        
        tuple_type = ['center','size','color']
        float_type = ['damage','base_knockback','knockback_growth','hitsun','damageMultiplier','velocityMultiplier',
                     'weightInfluence','shieldMultiplier','priorityDiff','charge_damage','charge_base_knockback','charge_knockback_growth',
                     'x_bias','y_bias','x_draw','y_draw','hitlag_multiplier']
        int_type = ['trajectory','hp','transcendence','base_hitstun','x_offset','y_offset','width','height']
        boolean_type = ['ignore_shields', 'ignore_armor']
        
        for child in _node:
            tag = child.tag
            val = child.text
            
            #special cases
            if tag in tuple_type:
                _type = 'tuple'
            elif tag in float_type:
                _type = 'float'
            elif tag in int_type:
                _type = 'int'
            elif tag in boolean_type:
                _type = 'bool'
            
            val = parseData(child, _type, None)
            hitbox_vars[tag] = val
            
        return modifyHitbox(hitbox_name,hitbox_vars)
        
class activateHitbox(SubAction):
    subact_group = 'Hitbox'
    fields = [NodeMap('hitbox_name','string','activateHitbox','')
              ]
    
    def __init__(self,_hitboxName=''):
        SubAction.__init__(self)
        self.hitbox_name = _hitboxName
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.hitboxes.has_key(self.hitbox_name):
            _actor.activateHitbox(_action.hitboxes[self.hitbox_name])
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.UpdateHitboxProperties(_root,self)
    
    def getDisplayName(self):
        return 'Activate Hitbox: ' + self.hitbox_name
    

class deactivateHitbox(SubAction):
    subact_group = 'Hitbox'
    fields = [NodeMap('hitbox_name','string','deactivateHitbox','')
              ]
    
    def __init__(self,_hitboxName=''):
        SubAction.__init__(self)
        self.hitbox_name = _hitboxName
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.hitboxes.has_key(self.hitbox_name):
            _action.hitboxes[self.hitbox_name].kill()
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.UpdateHitboxProperties(_root,self)
    
    def getDisplayName(self):
        return 'Deactivate Hitbox: ' + self.hitbox_name

class unlockHitbox(SubAction):
    subact_group = 'Hitbox'
    fields = [NodeMap('hitbox_name','string','unlockHitbox','')
              ]
    
    def __init__(self,_hitboxName=''):
        SubAction.__init__(self)
        self.hitbox_name = _hitboxName
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.hitboxes.has_key(self.hitbox_name):
            _action.hitboxes[self.hitbox_name].hitbox_lock = engine.hitbox.HitboxLock()
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.UpdateHitboxProperties(_root,self)
    
    def getDisplayName(self):
        return 'Unlock Hitbox: ' + self.hitbox_name

class charge(SubAction):
    subact_group = 'Hitbox'
    fields = [NodeMap('max_charge','int','charge|maxCharge',10),
              NodeMap('start_charge_frame','int','charge',0),
              NodeMap('supress_mask','bool','charge|noMask',False),
              NodeMap('charge_deposit','string','charge|chargeDeposit','charge'),
              NodeMap('button_check','string','charge|buttonCheck','attack')
              ]
    
    def __init__(self,_max=10,_chargeFrame=0,_noMask=False,_chargeDeposit='charge',_buttonCheck='attack'):
        SubAction.__init__(self)
        self.max_charge = _max
        self.start_charge_frame = _chargeFrame
        self.supress_mask = _noMask
        self.charge_deposit = _chargeDeposit
        self.button_check = _buttonCheck
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if hasattr(_action, self.charge_deposit):
            setattr(_action, self.charge_deposit, getattr(_action, self.charge_deposit)+1)
        else:
            setattr(_action, self.charge_deposit, 1)
            #If we're starting out, start flashing unless asked not to
            if not self.supress_mask:
                _actor.createMask([255,255,0],72,True,32)
        
        if _actor.keysContain(self.button_check) and getattr(_action, self.charge_deposit) <= self.max_charge:
            _action.frame = self.start_charge_frame
        else:
            #We're moving on. Turn off the flashing
            _actor.mask = None

# Create a new hurtbox
class createHurtbox(SubAction):
    subact_group = 'Hurtbox'
    
    def __init__(self, _name='', _variables={}):
        SubAction.__init__(self)
        self.hurtbox_name = _name
        self.hurtbox_vars = _variables
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if not isinstance(_actor, engine.abstractFighter.AbstractFighter):
            _actor = _actor.owner
        if self.hurtbox_name == '': return 
        
        hurtbox = engine.hurtbox.Hurtbox(_actor,self.hurtbox_vars)
        _action.hurtboxes[self.hurtbox_name] = hurtbox
        _actor.activateHurtbox(_action.hurtboxes[self.hurtbox_name])
    
    def getDisplayName(self):
        return 'Create New Hurtbox: ' + self.hurtbox_name
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyHurtboxProperties(_root,self,newHurtbox=True)
       
    def getXmlElement(self):
        elem = ElementTree.Element('createHurbox')
        name_elem = ElementTree.Element('name')
        name_elem.text = self.hurtbox_name
        elem.append(name_elem)
        for tag,value in self.hurtbox_vars.iteritems():
            new_elem = ElementTree.Element(tag)
            new_elem.text = str(value)
            elem.append(new_elem)
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        #build the variable dict
        variables = {}
        #these lists let the code know which keys should be which types.
        tuple_type = ['center','size','fix_size_multiplier','self_size_multiplier']
            
        for child in _node:
            tag = child.tag
            val = child.text

            if tag == 'name':
                name = val
            elif tag in tuple_type:
                variables[tag] = make_tuple(val)
            else:
                print('string variable',tag,val)
                variables[tag] = val
            
        return createHurtbox(name, variables)

# Change the properties of an existing hurtbox
class modifyHurtbox(SubAction):
    subact_group = 'Hurtbox'
    
    def __init__(self,_hurtboxName='',_hurtboxVars={}):
        SubAction.__init__(self)
        self.hurtbox_name = _hurtboxName
        self.hurtbox_vars = _hurtboxVars
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.hurtboxes.has_key(self.hurtbox_name):
            hurtbox = _action.hurtboxes[self.hurtbox_name]
            if hurtbox:
                for name,value in self.hurtbox_vars.iteritems():
                    if hasattr(hurtbox, name):
                        if isinstance(value, VarData) or isinstance(value, FuncData) or isinstance(value, EvalData):
                            setattr(hurtbox, name, value.unpack(_action,_actor))
                        else: setattr(hurtbox, name, value)
        
    def getDisplayName(self):
        return 'Modify Hurtbox: ' + str(self.hurtbox_name)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyHurtboxProperties(_root,self,newHurtbox=False)
        
    def getXmlElement(self):
        elem = ElementTree.Element('modifyHurtbox')
        elem.attrib['name'] = self.hurtbox_name
        for tag,value in self.hurtbox_vars.iteritems():
            new_elem = ElementTree.Element(tag)
            new_elem.text = str(value)
            elem.append(new_elem)
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        hurtbox_name = loadNodeWithDefault(_node, 'name', 'auto')
        hurtbox_vars = {}
        
        tuple_type = ['center','size','fix_size_multiplier','self_size_multiplier']
        
        for child in _node:
            tag = child.tag
            val = child.text
            
            #special cases
            if tag in tuple_type:
                _type = 'tuple'
            else: _type = 'string'
            val = parseData(child, _type, None)
            hurtbox_vars[tag] = val
            
        return modifyHurtbox(hurtbox_name,hurtbox_vars)

class activateHurtbox(SubAction):
    subact_group = 'Hurtbox'
    fields = [NodeMap('hurtbox_name','string','activateHurtbox','')
              ]
    
    def __init__(self,_hurtboxName=''):
        SubAction.__init__(self)
        self.hurtbox_name = _hurtboxName
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.hurtboxes.has_key(self.hurtbox_name):
            _actor.activateHurtbox(_action.hurtboxes[self.hurtbox_name])
    
    def getPropertiesPanel(self, _root):
        #return subactionSelector.UpdateHurtboxProperties(_root,self)
        return None
    
    def getDisplayName(self):
        return 'Activate Hurtbox: ' + self.hurtbox_name
    
class deactivateHurtbox(SubAction):
    subact_group = 'Hurtbox'
    fields = [NodeMap('hurtbox_name','string','deactivateHurtbox','')
              ]
    
    def __init__(self,_hurtboxName=''):
        SubAction.__init__(self)
        self.urtbox_name = _hurtboxName
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.hurtboxes.has_key(self.hurtbox_name):
            _action.hurtboxes[self.hurtbox_name].kill()
    
    def getPropertiesPanel(self, _root):
        #return subactionSelector.UpdateHurtboxProperties(_root,self)
        return None
    
    def getDisplayName(self):
        return 'Deactivate Hurtbox: ' + self.hurtbox_name

class changeECB(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('center','tuple','changeECB>center',(0,0)),
              NodeMap('size','tuple','changeECB>size',(0,0)),
              NodeMap('offset','tuple','changeECB>offset',(0,0))
              ]
    
    def __init__(self,_center=[0,0],_size=[0,0],_ecbOffset=[0,0]):
        SubAction.__init__(self)
        self.center = _center
        self.size = _size
        self.offset = _ecbOffset
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _action.ecb_size = self.size
        _action.ecb_center = self.center
        _action.ecb_offset = self.offset
    
    def getDisplayName(self):
        return 'Modify Fighter Collision Box'
    
    @staticmethod
    def customBuildFromXml(_node):
        center=[0,0]
        size = [0,0]
        ecb_offset = [0,0]
        if _node.find('center') is not None:
            center = map(int, _node.find('center').text.split(','))
        if _node.find('size') is not None:
            size = map(int, _node.find('size').text.split(','))
        if _node.find('offset') is not None:
            ecb_offset = map(int, _node.find('offset').text.split(','))
        return changeECB(center,size,ecb_offset)

class loadArticle(SubAction):
    subact_group = 'Article'
    fields = [NodeMap('article','string','loadArticle',None),
              NodeMap('name','string','loadArticle|name','')
              ]
    
    def __init__(self,_article=None,_name=''):
        SubAction.__init__(self)
        self.article = _article
        self.name = _name
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.article:
            _action.articles[self.name] = _actor.loadArticle(self.article)
    
    def getDisplayName(self):
        return 'Load Article: ' + self.name
    
class activateArticle(SubAction):
    subact_group = 'Article'
    fields = [NodeMap('name','string','activateArticle','')
              ]
    
    def __init__(self,_name=''):
        SubAction.__init__(self)
        self.name = _name
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.articles.has_key(self.name):
            _action.articles[self.name].activate()
        
    def getDisplayName(self):
        return 'Activate Article: ' + self.name
    
class deactivateArticle(SubAction):
    subact_group = 'Article'
    fields = [NodeMap('name','string','deactivateArticle','')
              ]
    
    def __init__(self,_name=''):
        SubAction.__init__(self)
        self.name = _name
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.articles.has_key(self.name):
            _action.articles[self.name].deactivate()
    
    def getDisplayName(self):
        return 'Deactivate Article: ' + self.name
    
class doAction(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('action','string','doAction','NeutralAction')
              ]
    
    def __init__(self,_action='NeutralAction'):
        SubAction.__init__(self)
        self.action = _action
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.doAction(self.action)
        
    def getDisplayName(self):
        return 'Change Action: ' + self.action
    
    
class createMask(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('color','string','createMask>color','#FFFFFF'),
              NodeMap('duration','int','createMask>duration',0),
              NodeMap('pulse_length','int','createMask>pulse',0)
              ]
    
    def __init__(self,_color='#FFFFFF',_duration=0,_pulseLength=0):
        SubAction.__init__(self)
        self.color = _color
        self.duration = _duration
        self.pulse_length = _pulseLength
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        pulse = True if self.pulse_length > 0 else False
        colorobj = pygame.color.Color(self.color)
        color = [colorobj.r,colorobj.g,colorobj.b]
        _actor.createMask(color,self.duration,pulse,self.pulse_length)
    
    def getDisplayName(self):
        return 'Create Color Mask: ' + str(self.color)

class removeMask(SubAction):
    subact_group = 'Behavior'
    fields = []
    
    def __init__(self):
        SubAction.__init__(self)
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.mask = None
        
    def getDisplayName(self):
        return 'Remove Color Mask'
    
class playSound(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('sound','string','playSound','')
              ]
    
    def __init__(self,_sound=''):
        SubAction.__init__(self)
        self.sound = _sound
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.playSound(self.sound)
        
    def getDisplayName(self):
        return 'Play Sound: '+str(self.sound)
    
class debugAction(SubAction):
    fields = [NodeMap('statement','string','print','')
              ]
    
    def __init__(self,_statement=''):
        SubAction.__init__(self)
        self.statement = _statement
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if isinstance(self.statement, tuple):
            source,name = self.statement
            if source == 'action':
                print('action.'+name+': '+str(getattr(_action, name)))
            else:
                if _actor.stats.has_key(name):
                    print('fighter['+name+']: '+str(_actor.stats[name]))
                else:
                    print('fighter.'+name+': '+str(getattr(_actor, name)))
        else:
            print(self.statement)
    
    def getDisplayName(self):
        return 'Print Debug'
    
######################################################################
#                         Article Subactions                         #
######################################################################
class deactivateSelf(SubAction):
    subact_group = 'Article'
    fields = []
    
    def __init__(self):
        SubAction.__init__(self)
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.deactivate()
        
    def getDisplayName(self):
        return 'Deactivate Self'
    
class recenterOnOrigin(SubAction):
    fields = []
    
    def __init__(self):
        SubAction.__init__(self)
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.recenter()
        
    def getDisplayName(self):
        return 'Recenter On Origin'
    
class executeCode(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('codeString', 'string', 'exec', ''),
              NodeMap('scope', 'string', 'exec|scope', 'action')]
    
    def __init__(self):
        SubAction.__init__(self)
        self.codeString = ''
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.scope == 'action':
            working_locals = {field: getattr(_action, field) for field in dir(_action)}
        elif self.scope == 'actor':
            working_locals = {field: getattr(_actor, field) for field in dir(_actor)}
        elif self.scope == 'global':
            working_locals = globals()
        elif self.scope == 'battle':
            working_locals = {field: getattr(_actor.game_state, field) for field in dir(_actor.game_state)}
        elif self.scope == 'local':
            working_locals = locals()
        else:
            print(self.scope + " is not a valid scope")
            return None
        exec self.codeString in globals(), working_locals

    def getDisplayName(self):
        return 'Execute ' + self.codeString + ' in the ' + self.scope + ' scope'
    
class rotateSprite(SubAction):
    subact_group = 'Sprite'
    fields = [NodeMap('angle', 'int', 'rotateSprite', 0)]
    
    def __init__(self):
        SubAction.__init__(self)
        self.angle = 0
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.rotateSprite(self.angle)
    
    def getDisplayName(self):
        return 'Rotate Sprite ' + self.angle + ' degrees'
            
class unrotateSprite(SubAction):
    subact_group = 'Sprite'
    fields = []
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.unRotate()
        
    def getDisplayName(self):
        return 'Unrotate Sprite'
    
subaction_dict = {
                 #Control Flow
                 'setFrame': changeActionFrame,
                 'nextFrame': nextFrame,
                 'if': If,
                 'ifButton': ifButton,
                 'transitionState': transitionState,
                 'doAction': doAction,
                 'setFighterVar': modifyFighterVar,
                 'setVar': setVar,
                 'exec': executeCode,
                 
                 #Sprite Modifiers
                 'changeSprite': changeFighterSprite,
                 'changeSubimage': changeFighterSubimage,
                 'shiftSprite': shiftSpritePosition,
                 'flip': flip,
                 'rotateSprite': rotateSprite,
                 'unrotate': unrotateSprite,
                 
                 #Behavior
                 'shiftPosition': shiftFighterPosition,
                 'changeFighterSpeed': changeFighterSpeed,
                 'changeFighterPreferredSpeed': changeFighterPreferredSpeed,
                 'changeECB': changeECB,
                 'updateLandingLag': updateLandingLag,
                 'createMask': createMask,
                 'removeMask': removeMask,
                 'setInvulnerability': setInvulnerability,
                 'changeGravity': changeGravity,
                 
                 #Hitbox Manipulation
                 'createHitbox': createHitbox,
                 'activateHitbox': activateHitbox,
                 'deactivateHitbox': deactivateHitbox,
                 'modifyHitbox': modifyHitbox,
                 'unlockHitbox': unlockHitbox,
                 'charge': charge,

                 #Hurtbox Manipulation
                 'createHurtbox': createHurtbox,
                 'activateHurtbox': activateHurtbox,
                 'deactivateHurtbox': deactivateHurtbox,
                 'modifyHurtbox': modifyHurtbox,
                 
                 #Articles
                 'loadArticle': loadArticle,
                 'activateArticle': activateArticle,
                 'deactivateArticle': deactivateArticle,
                 'recenterOnOrigin': recenterOnOrigin,
                 'deactivateSelf': deactivateSelf,
                 
                 'playSound': playSound,
                 
                 'print': debugAction
                 }

name_dict = {v: k for k, v in subaction_dict.items()} #reverse the above so a class object gets you the string
