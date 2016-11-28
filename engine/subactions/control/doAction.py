from engine.subaction import *

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
