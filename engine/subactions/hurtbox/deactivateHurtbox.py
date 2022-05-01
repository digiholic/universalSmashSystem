from engine.subaction import *

class deactivateHurtbox(SubAction):
    subact_group = 'Hurtbox'
    fields = [NodeMap('hurtbox_name','string','deactivateHurtbox','')
              ]
    
    def __init__(self,_hurtboxName=''):
        SubAction.__init__(self)
        self.urtbox_name = _hurtboxName
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.hurtbox_name in _action.hurtboxes:
            _action.hurtboxes[self.hurtbox_name].kill()
    
    def getPropertiesPanel(self, _root):
        #return subactionSelector.UpdateHurtboxProperties(_root,self)
        return None
    
    def getDisplayName(self):
        return 'Deactivate Hurtbox: ' + self.hurtbox_name
