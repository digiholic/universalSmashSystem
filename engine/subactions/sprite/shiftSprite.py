from engine.subaction import *

class shiftSpritePosition(SubAction):
    subact_group = 'Sprite'
    fields = [NodeMap('new_x','int','shiftSprite>xPos',None),
              NodeMap('x_relative','bool','shiftSprite>xPos|relative',None),
              NodeMap('new_y','int','shiftSprite>yPos',None)
              ]
    
    def __init__(self,_newX = None, _newY = None, _xRelative = False):
        SubAction.__init__(self)
        self.new_x = _newX
        self.new_y = _newY
        self.x_relative = _xRelative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        (old_x,old_y) = _actor.sprite.spriteOffset
        if self.new_x is not None:
            old_x = self.new_x
            if self.x_relative: old_x = old_x * _actor.facing
        if self.new_y is not None:
            old_y = self.new_y
        
        _actor.sprite.spriteOffset = (old_x,old_y)
        #print(actor.sprite.spriteOffset)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ShiftSpriteProperties(_root,self)
    
    def getDisplayName(self):
        return 'Shift Sprite: ' + str(self.new_x) + ' X, ' + str(self.new_y) + 'Y'
    
    def getXmlElement(self):
        elem = ElementTree.Element('shiftSprite')
        
        if self.new_x is not None:
            x_elem = ElementTree.Element('xPos')
            if self.x_relative: x_elem.attrib['relative'] = 'True'
            x_elem.text = str(self.new_x)
            elem.append(x_elem)
        
        if self.new_y is not None:
            y_elem = ElementTree.Element('yPos')
            y_elem.text = str(self.new_y)
            elem.append(y_elem)
            
        return elem
