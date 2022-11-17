from engine.subaction import *

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
        elif self.source == 'fighter': 
            if hasattr(_actor, 'owner'):
                source = _actor.owner
            else:
                source = _actor
        elif self.source == 'object':
            source = _actor
        elif self.source == 'article' and hasattr(_actor, 'owner'):
            source = _actor
        if not self.attr =='': #If there's a variable to set
            if hasattr(source, 'stats') and self.attr in source.stats: #if it has a var dict, let's check it first
                if self.relative: source.stats[self.attr] += self.val
                else: source.stats[self.attr] = self.val
            elif hasattr(source, 'variables') and self.attr in source.variables:
                if self.relative: source.variables[self.attr] += self.val
                else: source.variables[self.attr] = self.val
            else:
                print(source,self.attr,self.val)
                if self.relative:
                    setattr(source, self.attr, getattr(source, self.attr)+self.val)
                else: setattr(source,self.attr,self.val)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyFighterVarProperties(_root,self)
    
    def getDisplayName(self):
        return 'Set '+self.source+' '+self.attr+' to '+str(self.val)
