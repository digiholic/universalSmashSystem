from engine.subaction import *

# ChangeFighterSprite will change the sprite of the fighter (Who knew?)
# Optionally pass it a subImage index to start at that frame instead of 0
class changeFighterSprite(SubAction):
    subact_group = 'Sprite'
    fields = [NodeMap('sprite','string','changeSprite','idle'),
              NodeMap('preserve_index','bool','changeSprite|preserve',False)
              ]
    
    def __init__(self):
        SubAction.__init__(self)
        self.sprite = 'idle' #default data
        self.preserve_index = False #default data
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.preserve_index: index = _actor.sprite.index
        else: index = 0
        _action.sprite_name = self.sprite
        _actor.changeSprite(self.sprite,index)
    
    def getDisplayName(self):
        return 'Change Sprite: '+self.sprite
    
    def getPropertiesPanel(self,_root):
        return subactionSelector.ChangeSpriteProperties(_root,self)
