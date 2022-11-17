from engine.subaction import *

class activateHitbox(SubAction):
    subact_group = 'Hitbox'
    fields = [NodeMap('hitbox_name','string','activateHitbox','')
              ]
    
    def __init__(self,_hitboxName=''):
        SubAction.__init__(self)
        self.hitbox_name = _hitboxName
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.hitbox_name in _action.hitboxes:
            _actor.activateHitbox(_action.hitboxes[self.hitbox_name])
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.UpdateHitboxProperties(_root,self)
    
    def getDisplayName(self):
        return 'Activate Hitbox: ' + self.hitbox_name
