from engine.subaction import *

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