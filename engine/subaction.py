import engine.hitbox
import engine.hurtbox
import engine.statusEffect
import baseActions
import pygame.color
import builder.subactionSelector as subactionSelector
import xml.etree.ElementTree as ElementTree
from ast import literal_eval as make_tuple
import settingsManager
import builder.dataSelector as dataSelector

"""
TODO -
    EnableAction
    DisableAction
    SetTimer
"""

class SubactionFactory():
    def __init__(self):
        self.initialized = False
        self.subaction_dict = dict()
        self.name_dict = dict()
    
    def initialize(self):
        from engine.subactions.armor import createArmor,modifyArmor,removeArmor
        from engine.subactions.articles import activateArticle,deactivateArticle,deactivateSelf,loadArticle,recenterOnOrigin
        from engine.subactions.behavior import applyHitstop,applyHitstun,applyScaledKnockback,changeECB,changeGravity,changePreferredSpeed,changeSpeed,compensateResistance,createMask,dealDamage,removeMask,setInvulnerability,shiftPosition,updateLandingLag
        from engine.subactions.control import event,setFrame,nextFrame,conditional,ifButton,doTransition,doAction,setVar,setFighterVar,executeCode,playSound,debugAction
        from engine.subactions.hitbox import activateHitbox,chargeHitbox,createHitbox,deactivateHitbox,modifyHitbox,unlockHitbox
        from engine.subactions.hurtbox import activateHurtbox,createHurtbox,deactivateHurtbox,modifyHurtbox
        from engine.subactions.sprite import changeSprite, changeSubimage, shiftSprite, flip, rotateSprite, unrotateSprite
        
        
        self.subaction_dict = {
                 #Control Flow
                 'event': event.Event,
                 'setFrame': setFrame.changeActionFrame,
                 'nextFrame': nextFrame.nextFrame,
                 'if': conditional.If,
                 'ifButton': ifButton.ifButton,
                 'transitionState': doTransition.transitionState,
                 'doAction': doAction.doAction,
                 'setVar': setVar.setVar,
                 'setFighterVar': setFighterVar.modifyFighterVar,
                 'exec': executeCode.executeCode,
                 'playSound': playSound.playSound,
                 'print': debugAction.debugAction,
                 
                 #Sprite Modifiers
                 'changeSprite': changeSprite.changeFighterSprite,
                 'changeSubimage': changeSubimage.changeFighterSubimage,
                 'shiftSprite': shiftSprite.shiftSpritePosition,
                 'flip': flip.flip,
                 'rotateSprite': rotateSprite.rotateSprite,
                 'unrotate': unrotateSprite.unrotateSprite,
                 
                 #Behavior
                 'shiftPosition': shiftPosition.shiftFighterPosition,
                 'changeFighterSpeed': changeSpeed.changeFighterSpeed,
                 'changeFighterPreferredSpeed': changePreferredSpeed.changeFighterPreferredSpeed,
                 'changeECB': changeECB.changeECB,
                 'updateLandingLag': updateLandingLag.updateLandingLag,
                 'createMask': createMask.createMask,
                 'removeMask': removeMask.removeMask,
                 'setInvulnerability': setInvulnerability.setInvulnerability,
                 'changeGravity': changeGravity.changeGravity,
                 'dealDamage': dealDamage.dealDamage,
                 'applyScaledKnockback': applyScaledKnockback.applyScaledKnockback,
                 'applyHitstun': applyHitstun.applyHitstun,
                 'compensateResistance': compensateResistance.compensateResistance,
                 'applyHitstop': applyHitstop.applyHitstop,
                 
                 #Hitbox Manipulation
                 'createHitbox': createHitbox.createHitbox,
                 'activateHitbox': activateHitbox.activateHitbox,
                 'deactivateHitbox': deactivateHitbox.deactivateHitbox,
                 'modifyHitbox': modifyHitbox.modifyHitbox,
                 'unlockHitbox': unlockHitbox.unlockHitbox,
                 'charge': chargeHitbox.charge,

                 #Hurtbox Manipulation
                 'createHurtbox': createHurtbox.createHurtbox,
                 'activateHurtbox': activateHurtbox.activateHurtbox,
                 'deactivateHurtbox': deactivateHurtbox.deactivateHurtbox,
                 'modifyHurtbox': modifyHurtbox.modifyHurtbox,

                 #Armor Manipulation
                 'createArmor': createArmor.createArmor,
                 'modifyArmor': modifyArmor.modifyArmor,
                 'removeArmor': removeArmor.removeArmor,
                 
                 #Articles
                 'loadArticle': loadArticle.loadArticle,
                 'activateArticle': activateArticle.activateArticle,
                 'deactivateArticle': deactivateArticle.deactivateArticle,
                 'recenterOnOrigin': recenterOnOrigin.recenterOnOrigin,
                 'deactivateSelf': deactivateSelf.deactivateSelf
                 }
        
        self.name_dict = {v: k for k, v in self.subaction_dict.items()} #reverse the above so a class object gets you the string

        self.initialized = True
    
    def getSubaction(self,_name):
        if not self.initialized:
            self.initialize()
        if self.subaction_dict.has_key(_name):
            return self.subaction_dict[_name]
        else: return None
        
    def getName(self,_subaction):
        if not self.initialized:
            self.initialize()
        if self.name_dict.has_key(_subaction):
            return self.name_dict[_subaction]
        else: return None
        
    def buildFromXml(self,_name,_node):
        if hasattr(self.getSubaction(_name), 'customBuildFromXml'):
            return self.getSubaction(_name).customBuildFromXml(_node)
        
        subAction = self.getSubaction(_name)()
        for node in self.getSubaction(_name).fields:
            node.populateFromXML(subAction, _node)
        return subAction
        
subactionFactory = SubactionFactory()
                
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
        else: source = 'object'
        
        return VarData(source,varTag.text)
    if _data.find('function') is not None:
        funcTag = _data.find('function')
        if funcTag.attrib.has_key('source'): source = funcTag.attrib['source']
        else: source = 'object'
        
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
        else: scope = 'object'
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
        if self.source == 'article' and hasattr(_actor, 'owner'):
            if _actor.variables.has_key(self.var):
                return _actor.variables[self.var]
            elif hasattr(_actor, self.var):
                return getattr(_actor, self.var)
            else: return None
        if self.source == 'object':
            if hasattr(_actor, 'stats') and _actor.stats.has_key(self.var):
                return _actor.stats[self.var]
            elif _actor.variables.has_key(self.var):
                return _actor.variables[self.var]
            elif hasattr(_actor, self.var):
                return getattr(_actor, self.var)
            else: return None
        if self.source == 'actor':
            if hasattr(_actor, 'owner'):
                _actor = _actor.owner
            if _actor.stats.has_key(self.var):
                return _actor.stats[self.var]
            elif _actor.variables.has_key(self.var):
                return _actor.variables[self.var]
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
                
        if self.source == 'article' and hasattr(_actor, 'owner'):
            if hasattr(_actor, self.functionName):
                method = getattr(_actor, self.functionName)
                return method(**self.args)
            else:
                print('No such function exists in article: '+str(self.functionName))
                return None
        elif self.source == 'object':
            if hasattr(_actor, self.functionName):
                method = getattr(_actor, self.functionName)
                return method(**self.args)
            else:
                print('No such function exists in object: '+str(self.functionName))
                return None
        elif self.source == 'actor':
            if hasattr(_actor, 'owner'):
                _actor = _actor.owner
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
            if hasattr(_actor, 'owner'):
                _actor = _actor.owner
            working_locals = {field: getattr(_actor, field) for field in dir(_actor)}
        elif self.scope == 'article' and hasattr(_actor, 'owner'):
            working_locals = {field: getattr(_actor, field) for field in dir(_actor)}
        elif self.scope == 'object':
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
            elif fromKey == 'object':
                return ('object', var_node.text)
            elif fromKey == 'action':
                return ('action', var_node.text)
            elif fromKey == 'article':
                return ('article', var_node.text)
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
    
    def getDataLine(self,_parent):
        return dataSelector.InfoLine(_parent,_parent.interior,self.getDisplayName())
    
    def getPropertiesPanel(self,_root):
        return subactionSelector.BasePropertiesFrame(_root,self)
    
    def getXmlElement(self):
        elem = ElementTree.Element(subactionFactory.getName(self.__class__))
        for node in self.fields:
            node.storeAsXML(self, elem)
            
        return elem
    
    @staticmethod
    def buildFromXml(_name,_node):
        subactionFactory.buildFromXml(_name, _node)