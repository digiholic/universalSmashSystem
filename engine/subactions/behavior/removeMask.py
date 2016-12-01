from engine.subaction import *

class removeMask(SubAction):
    subact_group = 'Behavior'
    fields = []
    
    def __init__(self):
        SubAction.__init__(self)
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.mask = None
        
    def getDisplayName(self):
        return 'Remove Color Mask'

    def getDataLine(self, _parent):
        return SubAction.getDataLine(self, _parent)