from engine.subaction import *

class createMask(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('color','string','createMask>color','#FFFFFF'),
              NodeMap('duration','int','createMask>duration',0),
              NodeMap('pulse_length','int','createMask>pulse',0)
              ]
    
    def __init__(self,_color='#FFFFFF',_duration=0,_pulseLength=0):
        SubAction.__init__(self)
        self.color = _color
        self.duration = _duration
        self.pulse_length = _pulseLength
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        pulse = True if self.pulse_length > 0 else False
        colorobj = pygame.color.Color(self.color)
        color = [colorobj.r,colorobj.g,colorobj.b]
        _actor.createMask(color,self.duration,pulse,self.pulse_length)
    
    def getDisplayName(self):
        return 'Create Color Mask: ' + str(self.color)
