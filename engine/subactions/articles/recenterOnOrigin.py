from engine.subaction import *

class recenterOnOrigin(SubAction):
    fields = []
    
    def __init__(self):
        SubAction.__init__(self)
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.recenter()
        
    def getDisplayName(self):
        return 'Recenter On Origin'
