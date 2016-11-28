from engine.subaction import *

class transitionState(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('transition','string','transitionState','')
              ]
    
    def __init__(self,_transition=''):
        SubAction.__init__(self)
        self.transition = _transition
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if baseActions.state_dict.has_key(self.transition):
            baseActions.state_dict[self.transition](_actor)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.TransitionProperties(_root,self)
    
    def getDisplayName(self):
        return 'Apply Transition State: ' + str(self.transition)
