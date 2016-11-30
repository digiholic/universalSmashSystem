from engine.subaction import *
import engine.article

# ChangeFighterSubimage will change the subimage of a sheetSprite without changing the sprite.
class changeFighterSubimage(SubAction):
    subact_group = 'Sprite'
    fields = [NodeMap('index','int','changeSubimage',0),
              NodeMap('relative','bool','changeSubimage|relative',False)
              ]
    
    def __init__(self,_index=0,_relative=False):
        SubAction.__init__(self)
        self.index = _index
        self.relative = _relative
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        
        if isinstance(_action, engine.article.Article) or isinstance(_action, engine.article.DynamicArticle):
            _actor = _action
        print(_actor,_action,self.index)
        _action.sprite_rate = 0 #sprite_rate has been broken, so we have to ignore it from now on
        #TODO changeSpriteRate subaction
        if self.relative: _actor.changeSpriteImage(self.index+_actor.sprite.index, _action.loop)
        else: _actor.changeSpriteImage(self.index, _action.loop)
        
    def getDisplayName(self):
        return 'Change Subimage: '+str(self.index)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ChangeSubimageProperties(_root,self)
