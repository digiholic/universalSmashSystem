import engine.subaction as subaction
import xml.etree.ElementTree as ElementTree

# The action class is used for creating attacks, movement options,
# air dodges, rolls, and pretty much anything that happens to your
# character. It has a length, and keeps track of its current frame.
class Action():
    def __init__(self,length=0,starting_frame = 0):
        self.frame = starting_frame
        self.last_frame = length
        self.actor = None
        self.var = {}
        
        self.sprite_name = ""
        self.base_sprite_rate = 1
        self.sprite_rate = 1
        self.loop = False
        
        #These determine the size and shape of the fighter's ECB
        #Keep these at 0 to make it fit the sprite
        self.ecb_center = [0,0]
        self.ecb_size = [0,0]
        self.ecb_offset = [0,0]
        
        self.hitboxes = {}
        self.hitbox_locks = {}
        self.articles = {}
        
        
        """
        Empty constructors only used by DynamicActions
        """
        self.actions_at_frame = [[]]
        self.actions_before_frame = []
        self.actions_after_frame = []
        self.actions_at_last_frame = []
        self.actions_on_clank = []
        self.conditional_actions = dict()
        self.state_transition_actions = []
        self.set_up_actions = []
        self.tear_down_actions = []
        
    # The update skeleton function. You must implement it for every action or you will get
    # an error.
    def update(self,actor):
        if self.sprite_rate is not 0:
            if self.frame % self.sprite_rate == 0:
                if self.sprite_rate < 0:
                    actor.changeSpriteImage((self.frame / self.sprite_rate)-1, loop=self.loop)
                else:
                    actor.changeSpriteImage(self.frame / self.sprite_rate, loop=self.loop)
    
    def updateAnimationOnly(self,actor):
        self.update(actor) #If it's not a dynamic action, we're SOL on this one, so just let it go however it wants
                
    def stateTransitions(self,actor):
        return
    
    def setUp(self,actor):
        self.sprite_rate = self.base_sprite_rate
        actor.changeSprite(self.sprite_name)
        if self.sprite_rate < 0:
            actor.changeSpriteImage(len(actor.sprite.imageLibrary[actor.sprite.flip][actor.sprite.currentSheet])-1)
    
    def tearDown(self,actor,nextAction):
        for hitbox in self.hitboxes.values():
            hitbox.kill()
    
    def onClank(self,actor):
        return
    
"""
The Dynamic Action is created by the Builder. It contains most things that an action would
need, but anything more than that can still be defined as above.
"""
class DynamicAction(Action):
    def __init__(self,length,parent=None,var=dict(),starting_frame=0):
        Action.__init__(self,length,starting_frame)
        if parent:
            DynamicAction.__bases__ += (parent,)
        self.parent = parent
        
        self.actions_at_frame = [[]]
        self.actions_before_frame = []
        self.actions_after_frame = []
        self.actions_at_last_frame = []
        self.actions_on_clank = []
        
        #Conditional Action Groups for ifs and things
        #Dict in the form of "name" -> [Action List]
        self.conditional_actions = dict()
        
        self.state_transition_actions = []
        self.set_up_actions = []
        self.tear_down_actions = []
        self.default_vars = var
        for key,val in var.iteritems():
            setattr(self,key,val)
        
    def update(self,actor):
        for act in self.actions_before_frame:
            act.execute(self,actor)
        if self.frame < len(self.actions_at_frame):
            for act in self.actions_at_frame[self.frame]:
                act.execute(self,actor)
        if self.frame == self.last_frame:
            for act in self.actions_at_last_frame:
                act.execute(self,actor)
        for act in self.actions_after_frame:
            act.execute(self,actor)
        
        if self.parent: self.parent.update(self,actor)
    
    def updateAnimationOnly(self,actor):
        animation_actions = (subaction.changeFighterSubimage, subaction.changeFighterSprite, subaction.shiftSpritePosition,
                            subaction.activateHitbox, subaction.deactivateHitbox, subaction.modifyHitbox, subaction.updateHitbox)
        for act in self.actions_before_frame:
            if isinstance(act, animation_actions):
                act.execute(self,actor)
        if self.frame < len(self.actions_at_frame):
            for act in self.actions_at_frame[self.frame]:
                if isinstance(act, animation_actions):
                    act.execute(self,actor)
        if self.frame == self.last_frame:
            for act in self.actions_at_last_frame:
                if isinstance(act, animation_actions):
                    act.execute(self,actor)
        for act in self.actions_after_frame:
            if isinstance(act, animation_actions):
                act.execute(self,actor)
        Action.update(self, actor)
                
        self.frame += 1         
        
        
        
    def stateTransitions(self,actor):
        for act in self.state_transition_actions:
            act.execute(self,actor)
        if self.parent: self.parent.stateTransitions(self,actor)
    
    def setUp(self,actor):
        if self.parent: self.parent.setUp(self,actor)
        
        for act in self.set_up_actions:
            act.execute(self,actor)
        
    def tearDown(self,actor,newAction):
        if self.parent: self.parent.tearDown(self,actor,newAction)
        
        for act in self.tear_down_actions:
            act.execute(self,actor)

    def onClank(self,actor):
        Action.onClank(self, actor)
        for act in self.actions_on_clank:
            act.execute(self,actor)
        if self.parent: self.parent.onClank(self,actor)