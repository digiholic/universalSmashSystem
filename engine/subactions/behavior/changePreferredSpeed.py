from engine.subaction import *

# The preferred speed is what a fighter will accelerate/decelerate to. Use this action if you
# want the fighter to gradually speed up to a point (for accelerating), or slow down to a point (for deccelerating)
class changeFighterPreferredSpeed(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('speed_x','float','changeFighterPreferredSpeed>xSpeed',None),
              NodeMap('x_relative','bool','changeFighterPreferredSpeed>xSpeed|relative',False),
              NodeMap('speed_y','float','changeFighterPreferredSpeed>ySpeed',None)
              ]
    def __init__(self,_speedX = None, _speedY = None, _xRelative = False):
        SubAction.__init__(self)
        self.speed_x = _speedX
        self.speed_y = _speedY
        self.x_relative = _xRelative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.speed_x is not None:
            if type(self.speed_x) is tuple:
                owner,value = self.speed_x
                if owner == 'actor':
                    if hasattr(_actor, 'owner'):
                        _actor = _actor.owner
                    self.speed_x = _actor.stats[value]
                elif owner == 'object' and hasattr(_actor, 'stats'):
                    self.speed_x = _actor.stats[value]
                elif owner == 'article' and hasattr(_actor, 'owner'):
                    self.speed_x = _actor.owner.stats[value]
                elif owner == 'action':
                    self.speed_x = getattr(self, value)
            if self.x_relative: _actor.preferred_xspeed = self.speed_x*_actor.facing
            else: _actor.preferred_xspeed = self.speed_x
            
        if self.speed_y is not None:
            if type(self.speed_y) is tuple:
                owner,value = self.speed_y
                if owner == 'actor':
                    if hasattr(_actor, 'owner'):
                        _actor = _actor.owner
                    self.speed_y = _actor.stats[value]
                elif owner == 'object' and hasattr(_actor, 'stats'):
                    self.speed_y = _actor.stats[value]
                elif owner == 'article' and hasattr(_actor, 'owner'):
                    self.speed_y = _actor.stats[value]
                elif owner == 'action':
                    self.speed_y = getattr(self, value)
            _actor.preferred_yspeed = self.speed_y
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ChangeSpeedProperties(_root,self)
    
    def getDisplayName(self):
        x_str = str(self.speed_x)+' X' if self.speed_x is not None else ''
        sep_str = ', ' if self.speed_x and self.speed_y else ''
        y_str = str(self.speed_y)+' Y' if self.speed_y is not None else ''
        return 'Change Preferred Speed: '+x_str+sep_str+y_str
    
    def getXmlElement(self):
        elem = ElementTree.Element('changeFighterPreferredSpeed')
        
        if self.speed_x is not None:
            x_elem = ElementTree.Element('xSpeed')
            if self.x_relative: x_elem.attrib['relative'] = 'True'
            x_elem.text = str(self.speed_x)
            elem.append(x_elem)
        
        if self.speed_y is not None:
            y_elem = ElementTree.Element('ySpeed')
            y_elem.text = str(self.speed_y)
            elem.append(y_elem)
        return elem