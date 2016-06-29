import engine.subaction as subaction
import xml.etree.ElementTree as ElementTree

# The action class is used for creating attacks, movement options,
# air dodges, rolls, and pretty much anything that happens to your
# character. It has a length, and keeps track of its current frame.
class Action():
    def __init__(self,length=0,startingFrame = 0):
        self.frame = startingFrame
        self.lastFrame = length
        self.actor = None
        self.var = {}
        
        self.spriteName = ""
        self.baseSpriteRate = 1
        self.spriteRate = 1
        self.loop = False
        
        #These determine the size and shape of the fighter's ECB
        #Keep these at 0 to make it fit the sprite
        self.ecbCenter = [0,0]
        self.ecbSize = [0,0]
        self.ecbOffset = [0,0]
        
        self.hitboxes = {}
        self.hitboxLocks = {}
        self.articles = {}
    
    # The update skeleton function. You must implement it for every action or you will get
    # an error.
    def update(self,actor):
        if self.spriteRate is not 0:
            if self.frame % self.spriteRate == 0:
                if self.spriteRate < 0:
                    actor.changeSpriteImage((self.frame / self.spriteRate)-1, loop=self.loop)
                else:
                    actor.changeSpriteImage(self.frame / self.spriteRate, loop=self.loop)
            
    def stateTransitions(self,actor):
        return
    
    def setUp(self,actor):
        self.spriteRate = self.baseSpriteRate
        actor.changeSprite(self.spriteName)
        if self.spriteRate < 0:
            actor.changeSpriteImage(len(actor.sprite.imageLibrary[actor.sprite.flip][actor.sprite.currentSheet])-1)
    
    def tearDown(self,actor,nextAction):
        for hitbox in self.hitboxes:
            hitbox.kill()
    
    def onClank(self,actor):
        return
    
"""
The Dynamic Action is created by the Builder. It contains most things that an action would
need, but anything more than that can still be defined as above.
"""
class DynamicAction(Action):
    def __init__(self,length,parent=None,var=None,startingFrame=0):
        Action.__init__(self,length,startingFrame)
        if parent:
            DynamicAction.__bases__ += (parent,)
        self.parent = parent
        
        self.actionsAtFrame = [[]]
        self.actionsBeforeFrame = []
        self.actionsAfterFrame = []
        self.actionsAtLastFrame = []
        self.actionsOnClank = []
        
        self.stateTransitionActions = []
        self.setUpActions = []
        self.tearDownActions = []
        self.defaultVars = var
        for key,val in var.iteritems():
            setattr(self,key,val)
        
    def update(self,actor):
        for act in self.actionsBeforeFrame:
            act.execute(self,actor)
        if self.frame < len(self.actionsAtFrame):
            for act in self.actionsAtFrame[self.frame]:
                act.execute(self,actor)
        if self.frame == self.lastFrame:
            for act in self.actionsAtLastFrame:
                act.execute(self,actor)
        for act in self.actionsAfterFrame:
            act.execute(self,actor)
        
        if self.parent: self.parent.update(self,actor)
    
    def updateAnimationOnly(self,actor):
        Action.update(self, actor)
        
        animationActions = (subaction.changeFighterSubimage, subaction.changeFighterSprite, subaction.shiftSpritePosition)
        for act in self.actionsBeforeFrame:
            if isinstance(act, animationActions):
                act.execute(self,actor)
        if self.frame < len(self.actionsAtFrame):
            for act in self.actionsAtFrame[self.frame]:
                if isinstance(act, animationActions):
                    act.execute(self,actor)
        if self.frame == self.lastFrame:
            for act in self.actionsAtLastFrame:
                if isinstance(act, animationActions):
                    act.execute(self,actor)
        for act in self.actionsAfterFrame:
            if isinstance(act, animationActions):
                act.execute(self,actor)
                
        self.frame += 1         
        
        
    def stateTransitions(self,actor):
        for act in self.stateTransitionActions:
            act.execute(self,actor)
        if self.parent: self.parent.stateTransitions(self,actor)
    
    def setUp(self,actor):
        if self.parent: self.parent.setUp(self,actor)
        
        for act in self.setUpActions:
            act.execute(self,actor)
        
    def tearDown(self,actor,newAction):
        if self.parent: self.parent.tearDown(self,actor,newAction)
        
        for act in self.tearDownActions:
            act.execute(self,actor)

    def onClank(self,actor):
        Action.onClank(self, actor)
        for act in self.actionsOnClank:
            act.execute(self,actor)
        if self.parent: self.parent.onClank(self,actor)