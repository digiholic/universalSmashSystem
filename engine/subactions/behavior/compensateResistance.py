from engine.subaction import *

class compensateResistance(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('frames', 'float', 'compensateResistance', 0.0)]
        
    def __init__(self, _frames=0):
        SubAction.__init__(self)
        self.frames = _frames

    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if hasattr(_actor, 'owner'):
            _actor = _actor.owner    
        if _actor.change_x > 0:
            _actor.change_x += .5*_actor.stats['air_resistance']*settingsManager.getSetting('airControl')*self.frames
        elif _actor.change_x < 0:
            _actor.change_x -= .5*_actor.stats['air_resistance']*settingsManager.getSetting('airControl')*self.frames
        if _actor.change_y > 0:
            _actor.change_y += .5*_actor.stats['gravity']*settingsManager.getSetting('gravity')*self.frames
        if _actor.change_y < 0:
            _actor.change_y += .5*_actor.stats['gravity']*settingsManager.getSetting('gravity')*self.frames

    def getPropertiesPanel(self, _root):
        return SubAction.getPropertiesPanel(self, _root)

    def getDisplayName(self):
        return 'Compensate for ' + self.frames + ' frames of gravity and air resistance'
    
    def getDataLine(self, _parent):
        return dataSelector.NumLine(_parent, _parent.interior, 'Compensate gravity/air resistance frames: ', self, 'new_gravity')