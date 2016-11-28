from engine.subaction import *

class applyHitstun(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('damage', 'float', 'applyHitstun', 0.0),
              NodeMap('base_knockback', 'float', 'applyHitstun', 0.0),
              NodeMap('knockback_growth', 'float', 'applyHitstun', 0.0),
              NodeMap('trajectory', 'float', 'applyHitstun', 0.0),
              NodeMap('weight_influence', 'float', 'applyHitstun', 1.0),
              NodeMap('base_hitstun', 'float', 'applyHitstun', 10.0),
              NodeMap('hitstun_multiplier', 'float', 'applyHitstun', 2.0)]

    def __init__(self, _damage=0, _baseKnockback=0, _knockbackGrowth=0, _trajectory=0, _weightInfluence=1, _baseHitstun=10, _hitstunMultiplier=2):
        SubAction.__init__(self)
        self.damage = _damage
        self.base_knockback = _baseKnockback
        self.knockback_growth = _knockbackGrowth
        self.trajectory = _trajectory
        self.weight_influence = _weightInfluence
        self.base_hitstun = _baseHitstun
        self.hitstun_multiplier = _hitstunMultiplier

    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if hasattr(_actor, 'owner'):
            _actor = _actor.owner
        percent_portion = (_actor.damage/10.0) + (_actor.damage*self.damage)/20.0
        weight_portion = 200.0/(_actor.stats['weight']*self.weight_influence+100)
        scaled_kb = (((percent_portion * weight_portion *1.4) + 5) * self.knockback_growth)
        _actor.applyHitstun(scaled_kb+self.base_knockback, self.hitstun_multiplier, self.base_hitstun, self.trajectory)

    def getPropertiesPanel(self, _root):
        return SubAction.getPropertiesPanel(self, _root)

    def getDisplayName(self):
        return 'Apply hitstun'
