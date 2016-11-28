from engine.subaction import *

class activateHurtbox(SubAction):
    subact_group = 'Hurtbox'
    fields = [NodeMap('hurtbox_name','string','activateHurtbox','')
              ]
    
    def __init__(self,_hurtboxName=''):
        SubAction.__init__(self)
        self.hurtbox_name = _hurtboxName
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.hurtboxes.has_key(self.hurtbox_name):
            _actor.activateHurtbox(_action.hurtboxes[self.hurtbox_name])
    
    def getPropertiesPanel(self, _root):
        #return subactionSelector.UpdateHurtboxProperties(_root,self)
        return None
    
    def getDisplayName(self):
        return 'Activate Hurtbox: ' + self.hurtbox_name
