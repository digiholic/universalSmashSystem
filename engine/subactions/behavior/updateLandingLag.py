from engine.subaction import *

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
        if hasattr(_actor, 'owner'):
            _actor = _actor.owner
        _actor.updateLandingLag(self.new_lag,self.reset)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.UpdateLandingLagProperties(_root,self)
    
    def getDisplayName(self):
        if self.reset: start_str = 'Reset '
        else: start_str = 'Update '
        return start_str+'Landing Lag: ' + str(self.new_lag)
