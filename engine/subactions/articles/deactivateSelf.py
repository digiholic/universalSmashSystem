from engine.subaction import *

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
    
