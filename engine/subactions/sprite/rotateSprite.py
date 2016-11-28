from engine.subaction import *

class rotateSprite(SubAction):
    subact_group = 'Sprite'
    fields = [NodeMap('angle', 'int', 'rotateSprite', 0)]
    
    def __init__(self):
        SubAction.__init__(self)
        self.angle = 0
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.rotateSprite(self.angle)
    
    def getDisplayName(self):
        return 'Rotate Sprite ' + self.angle + ' degrees'
