from engine.subaction import *
import engine.baseActions as baseActions

class transitionState(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('transition','string','transitionState','')
              ]
    
    def __init__(self,_transition=''):
        SubAction.__init__(self)
        self.transition = _transition
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.transition in baseActions.state_dict:
            baseActions.state_dict[self.transition](_actor)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.TransitionProperties(_root,self)
    
    def getDisplayName(self):
        return 'Apply Transition State: ' + str(self.transition)

    def getDataLine(self, _parent):
        return dataSelector.TransitionLine(_parent,_parent.interior,'Transition State:',self,'transition')