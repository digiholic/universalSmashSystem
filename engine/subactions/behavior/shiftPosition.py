from engine.subaction import *

# ShiftFighterPositon directly changes the fighter's x and y coordinates without regard for wall checks, speed limites, or gravity.
# Don't use this for ordinary movement unless you're totally sure what you're doing.
# A good use for this is to jitter a hit opponent during hitlag, just make sure to put them back where they should be before actually launching.
class shiftFighterPosition(SubAction):
    subact_group = 'Behavior'
    fields = [NodeMap('new_x','int','shiftPosition>xPos',None),
              NodeMap('x_relative','bool','shiftPosition>xPos|relative',False),
              NodeMap('new_y','int','shiftPosition>yPos',None),
              NodeMap('y_relative','bool','shiftPosition>yPos|relative',False)
              ]
    
    def __init__(self,_newX = None, _newY = None, _xRelative = False, _yRelative = False):
        SubAction.__init__(self)
        self.new_x = _newX
        self.new_y = _newY
        self.x_relative = _xRelative
        self.y_relative = _yRelative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.new_x:
            if self.x_relative: _actor.posx += self.new_x * _actor.facing
            else: _actor.posx = self.new_x
        if self.new_y:
            if self.y_relative: _actor.posy += self.new_y
            else: _actor.posy = self.new_y
            
    def getDisplayName(self):
        return 'Shift Position: ' + str(self.new_x) + ' X, ' + str(self.new_y) + 'Y'
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ShiftPositionProperties(_root,self)
    
    def getXmlElement(self):
        elem = ElementTree.Element('shiftPosition')
        
        if self.new_x is not None:
            x_elem = ElementTree.Element('xPos')
            if self.x_relative: x_elem.attrib['relative'] = 'True'
            x_elem.text = str(self.new_x)
            elem.append(x_elem)
        
        if self.new_y is not None:
            y_elem = ElementTree.Element('yPos')
            if self.y_relative: y_elem.attrib['relative'] = 'True'
            y_elem.text = str(self.new_y)
            elem.append(y_elem)
            
        return elem
    
    def getDataLine(self, _parent):
        return dataSelector.XYDataLine(_parent, _parent.interior, 'Shift Position: ', self, 'new_x', 'new_y', 'x_relative', 'y_relative')