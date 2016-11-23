from engine.subaction import *

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
            if hasattr(_actor, 'owner'):
                _actor = _actor.owner
            if hasattr(_actor, 'stats') and _actor.stats.has_key(self.variable):
                variable = _actor.stats[self.variable]
            elif _actor.variables.has_key(self.variable):
                variable = _actor.variables[self.variable]
            else: variable = getattr(_actor, self.variable)
        elif self.source == 'article' and hasattr(_actor, 'owner'):
            variable = _actor.variables[self.variable]
        elif self.source == 'object':
            variable = _actor.variables[self.variable]
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
        elif self.function == 'is':
            function = lambda var,val: var is val
        elif self.function == 'is not':
            function = lambda var,val: var is not val
        elif self.function == 'true':
            function = lambda var,val: bool(var)
        elif self.function == 'false':
            function = lambda var,val: not bool(var)
            
        cond = function(variable,self.value)
        print(self.source,self.variable,self.value)
        print('COND',cond)
        print('EVENTS',_action.events)
        print(self.if_actions,self.else_actions)
        
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