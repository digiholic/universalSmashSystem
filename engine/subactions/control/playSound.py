from engine.subaction import *

class playSound(SubAction):
    subact_group = 'Control'
    fields = [NodeMap('sound','string','playSound','')
              ]
    
    def __init__(self,_sound=''):
        SubAction.__init__(self)
        self.sound = _sound
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        _actor.playSound(self.sound)
        
    def getDisplayName(self):
        return 'Play Sound: '+str(self.sound)
