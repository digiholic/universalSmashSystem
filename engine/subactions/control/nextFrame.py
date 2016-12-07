from engine.subaction import *

# Go to the next frame in the action
class nextFrame(SubAction):
    subact_group = 'Control'
    fields = []
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _action.frame += 1
    
    def getDisplayName(self):
        return 'Next Frame'

    def getDataLine(self, _parent):
        return SubAction.getDataLine(self, _parent)