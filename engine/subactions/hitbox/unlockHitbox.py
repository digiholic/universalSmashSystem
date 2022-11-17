from engine.subaction import *

class unlockHitbox(SubAction):
    subact_group = 'Hitbox'
    fields = [NodeMap('hitbox_name','string','unlockHitbox','')
              ]
    
    def __init__(self,_hitboxName=''):
        SubAction.__init__(self)
        self.hitbox_name = _hitboxName
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.hitbox_name in _action.hitboxes:
            _action.hitboxes[self.hitbox_name].hitbox_lock = engine.hitbox.HitboxLock()
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.UpdateHitboxProperties(_root,self)
    
    def getDisplayName(self):
        return 'Unlock Hitbox: ' + self.hitbox_name
