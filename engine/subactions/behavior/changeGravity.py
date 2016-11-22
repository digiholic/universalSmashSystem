from engine.subaction import *

class changeGravity(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('new_gravity','float','changeGravity',False)]
    
    def __init__(self,_newGrav=1):
        SubAction.__init__(self)
        self.new_gravity = _newGrav
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if hasattr(_actor, 'owner'):
            _actor = _actor.owner
        _actor.calcGrav(self.new_gravity)
        
    def getPropertiesPanel(self, _root):
        #TODO Properties
        return SubAction.getPropertiesPanel(self, _root)
    
    def getDisplayName(self):
        return 'Change Gravity Multiplier to '+self.new_gravity
