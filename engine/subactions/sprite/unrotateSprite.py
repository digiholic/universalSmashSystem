from engine.subaction import *

class unrotateSprite(SubAction):
    subact_group = 'Sprite'
    fields = []
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.unRotate()
        
    def getDisplayName(self):
        return 'Unrotate Sprite'
