from engine.subaction import *

# Change a fighter attribute, for example, weight or remaining jumps
class modifyFighterVar(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('attr','string','setFighterVar|var',''),
              NodeMap('val','dynamic','setFighterVar>value',None),
              NodeMap('relative','bool','setFighterVar>value|relative',False),
              NodeMap('source','string','setFighterVar|source','object')
              ]
              
    def __init__(self,_attr='',_val=None,_relative=False,_source='object'):
        SubAction.__init__(self)
        self.attr = _attr
        self.val = _val
        self.relative = _relative
        self.source = _source
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.source == 'actor' and hasattr(_actor, 'owner'):
            _actor = _actor.owner
        if not self.attr =='':
            if hasattr(_actor, 'stats') and _actor.stats.has_key(self.attr):
                if self.relative: _actor.stats[self.attr] += self.val
                else: _actor.stats[self.attr] = self.val
            elif _actor.variables.has_key(self.attr):
                if self.relative: _actor.variables[self.attr] += self.val
                else: _actor.variables[self.attr] = self.val
            else:
                if self.relative:
                    setattr(_actor, self.attr, getattr(_actor, self.attr)+1)
                else: setattr(_actor,self.attr,self.val)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyFighterVarProperties(_root,self)
    
    def getDisplayName(self):
        return 'Set '+self.source+' '+self.attr+' to '+str(self.val)
