from engine.subaction import *
import builder.dataSelector as dataSelector

# ChangeFighterSpeed changes the speed directly, with no acceleration/deceleration.
class changeFighterSpeed(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('speed_x','float','changeFighterSpeed>xSpeed',None),
              NodeMap('x_relative','bool','changeFighterSpeed>xSpeed|relative',False),
              NodeMap('speed_y','float','changeFighterSpeed>ySpeed',None),
              NodeMap('y_relative','bool','changeFighterSpeed>ySpeed|relative',False),
              NodeMap('direction','int','changeFighterSpeed>direction',None),
              NodeMap('magnitude','float','changeFighterSpeed>magnitude',None),
              ]
    
    def __init__(self,_speedX = None, _speedY = None, _xRelative = False, _yRelative = False, _direction = None, _magnitude = None):
        SubAction.__init__(self)
        self.speed_x = _speedX
        self.speed_y = _speedY
        self.x_relative = _xRelative
        self.y_relative = _yRelative
        self.direction = _direction
        self.magnitude = _magnitude
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.direction is not None and self.magnitude is not None:
            x,y = settingsManager.getXYFromDM(self.direction,self.magnitude)
            _actor.change_x = x
            _actor.change_y = y    
        else:
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
                        self.speed_x = _actor.stats[value]
                    elif owner == 'action':
                        self.speed_x = getattr(self, value)
                if self.x_relative: _actor.change_x = self.speed_x*_actor.facing
                else: _actor.change_x = self.speed_x
            
            if self.speed_y is not None:
                if type(self.speed_y) is tuple:
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
                if self.y_relative:_actor.change_y += self.speed_y
                else: _actor.change_y = self.speed_y
        
        
    def getPropertiesPanel(self, _root):
        return subactionSelector.ChangeSpeedProperties(_root,self)
    
    def getDisplayName(self):
        x_str = str(self.speed_x)+' X' if self.speed_x is not None else ''
        sep_str = ', ' if self.speed_x and self.speed_y else ''
        y_str = str(self.speed_y)+' Y' if self.speed_y is not None else ''
        return 'Change Fighter Speed: '+x_str+sep_str+y_str
    
    def getXmlElement(self):
        elem = ElementTree.Element('changeFighterSpeed')
        
        if self.speed_x is not None:
            x_elem = ElementTree.Element('xSpeed')
            if self.x_relative: x_elem.attrib['relative'] = 'True'
            x_elem.text = str(self.speed_x)
            elem.append(x_elem)
            
        if self.speed_y is not None:
            y_elem = ElementTree.Element('ySpeed')
            if self.y_relative: y_elem.attrib['relative'] = 'True'
            y_elem.text = str(self.speed_y)
            elem.append(y_elem)
            
        return elem

    def getDataLine(self, _parent):
        return dataSelector.XYDataLine(_parent, _parent.interior, 'Change Speed: ', self, 'speed_x', 'speed_y', 'x_relative', 'y_relative')