from engine.subaction import *

class applyScaledKnockback(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('damage', 'float', 'applyScaledKnockback', 0.0),
              NodeMap('base_knockback', 'float', 'applyScaledKnockback', 0.0),
              NodeMap('knockback_growth', 'float', 'applyScaledKnockback', 0.0),
              NodeMap('trajectory', 'float', 'applyScaledKnockback', 0.0),
              NodeMap('weight_influence', 'float', 'applyScaledKnockback', 1.0)]

    def __init__(self, _damage=0, _baseKnockback=0, _knockbackGrowth=0, _trajectory=0, _weightInfluence=1):
        SubAction.__init__(self)
        self.damage = _damage
        self.base_knockback = _baseKnockback
        self.knockback_growth = _knockbackGrowth
        self.trajectory = _trajectory
        self.weight_influence = _weightInfluence

    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if hasattr(_actor, 'owner'):
            _actor = _actor.owner
        percent_portion = (_actor.damage/10.0) + (_actor.damage*self.damage)/20.0
        weight_portion = 200.0/(_actor.stats['weight']*settingsManager.getSetting('weight')*self.weight_influence+100)
        scaled_kb = (((percent_portion * weight_portion *1.4) + 5) * self.knockback_growth) 
        _actor.applyKnockback(scaled_kb+self.base_knockback, self.trajectory)

    def getPropertiesPanel(self, _root):
        return SubAction.getPropertiesPanel(self, _root)

    def getDisplayName(self):
        #TODO better description
        return 'Apply scaled knockback'
