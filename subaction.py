import action
import pygame
import fighter

class SubAction():
    def __init__(self,actor):
        self.owner = actor
    
    def execute(self,actor):
        return
    
class ConditionalAction(SubAction):
    def __init__(self,actor,cond):
        SubAction.__init__(self, actor)
        self.ifActions = []
        self.elseActions = []
        self.cond = cond
        
    def execute(self,actor):
        if self.cond:
            for act in self.ifActions:
                act.execute(actor)
        else:
            for act in self.elseActions:
                act.execute(actor)
                
class ifAttribute(ConditionalAction):
    def __init__(self,actor,attr,comp,val,ifActions = [], elseActions = []):
        if comp == '==':
            cond = actor.var[attr] == val
        elif comp == '<':
            cond = actor.var[attr] < val
        elif comp == '<=':
            cond = actor.var[attr] <= val
        elif comp == '>':
            cond = actor.var[attr] > val
        elif comp == '>=':
            cond = actor.var[attr] >= val
        elif comp == '!=':
            cond = actor.var[attr] != val
        ConditionalAction.__init__(self, actor, cond)
        self.ifActions = ifActions
        self.elseActions = elseActions
        
class ifVar(ConditionalAction):
    def __init__(self,actor,val1,comp,val2,ifActions = [], elseActions = []):
        if comp == '==':
            cond = val1 == val2
        elif comp == '<':
            cond = val1 < val2
        elif comp == '<=':
            cond = val1 <= val2
        elif comp == '>':
            cond = val1 > val2
        elif comp == '>=':
            cond = val1 >= val2
        elif comp == '!=':
            cond = val1 != val2
        ConditionalAction.__init__(self, actor, cond)
        self.ifActions = ifActions
        self.elseActions = elseActions
        
class changeFighterSprite(SubAction):
    def __init__(self,actor,sprite,subImage = -1):
        SubAction.__init__(self, actor)
        self.sprite = sprite
        self.subImage = subImage
        
    def execute(self,actor):
        actor.sprite.changeImage("hitboxie_fall")
        if self.subImage != -1:
            actor.sprite.getImageAtIndex(self.subImage)
        
class changeFighterSubimage(SubAction):
    def __init__(self,actor,index):
        SubAction.__init__(self, actor)
        self.index = index
        
    def execute(self,actor):
        actor.sprite.getImageAtIndex(self.index)
        
