from engine.subaction import *

# Change the frame of the action to a value.
class changeActionFrame(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('new_frame','int','setFrame',0),
              NodeMap('relative','bool','setFrame|relative',None)
              ]
    
    def __init__(self,_newFrame=0,_relative=False):
        SubAction.__init__(self)
        self.new_frame = _newFrame
        self.relative = _relative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.relative: _action.frame += self.new_frame
        else: _action.frame = self.new_frame
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ChangeFrameProperties(_root,self)
    
    def getDisplayName(self):
        if self.relative:
            return 'Change Frame By: ' + str(self.new_frame)
        else:
            return 'Set Frame: ' + str(self.new_frame)
