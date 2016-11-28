from engine.subaction import *

class applyHitstop(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('frames', 'int', 'applyHitstop', 0),
              NodeMap('pushback', 'float', 'applyHitstop', 0.0),
              NodeMap('trajectory', 'float', 'applyHitstop', 0.0)]

    def __init__(self, _frames=0, _pushback=0.0, _trajectory=0.0):
        SubAction.__init__(self)
        self.frames = _frames
        self.pushback = _pushback
        self.trajectory = _trajectory

    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if hasattr(_actor, 'owner'):
            _actor = _actor.owner
        _actor.applyPushback(self.pushback, self.trajectory, self.frames)

    def getPropertiesPanel(self, _root):
        return SubAction.getPropertiesPanel(self, _root)

    def getDisplayName(self):
        return 'Apply hitstop'
