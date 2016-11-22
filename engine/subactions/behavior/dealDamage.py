from engine.subaction import *

class dealDamage(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('damage', 'float', 'dealDamage', 0.0)]

    def __init__(self,_damage=0):
        SubAction.__init__(self)
        self.damage = _damage

    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if hasattr(_actor, 'owner'):
            _actor = _actor.owner
        _actor.dealDamage(self.damage)

    def getPropertiesPanel(self, _root):
        return SubAction.getPropertiesPanel(self, _root)

    def getDisplayName(self):
        return 'Deal ' + self.damage + ' damage'
