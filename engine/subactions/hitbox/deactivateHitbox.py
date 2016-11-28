from engine.subaction import *

class deactivateHitbox(SubAction):
    subact_group = 'Hitbox'
    fields = [NodeMap('hitbox_name','string','deactivateHitbox','')
              ]
    
    def __init__(self,_hitboxName=''):
        SubAction.__init__(self)
        self.hitbox_name = _hitboxName
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.hitboxes.has_key(self.hitbox_name):
            _action.hitboxes[self.hitbox_name].kill()
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.UpdateHitboxProperties(_root,self)
    
    def getDisplayName(self):
        return 'Deactivate Hitbox: ' + self.hitbox_name
