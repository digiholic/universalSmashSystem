import engine.subaction as subaction
import xml.etree.ElementTree as ElementTree

# The action class is used for creating attacks, movement options,
# air dodges, rolls, and pretty much anything that happens to your
# character. It has a length, and keeps track of its current frame.
class Action():
    def __init__(self,_length=0,_starting_frame = 0):
        self.frame = _starting_frame
        self.last_frame = _length
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
    def update(self,_actor):
        if self.sprite_rate is not 0:
            if self.frame % self.sprite_rate == 0:
                if self.sprite_rate < 0:
                    _actor.changeSpriteImage((self.frame / self.sprite_rate)-1, _loop=self.loop)
                else:
                    _actor.changeSpriteImage(self.frame / self.sprite_rate, _loop=self.loop)
    
    def updateAnimationOnly(self,_actor):
        self.update(_actor) #If it's not a dynamic action, we're SOL on this one, so just let it go however it wants
                
    def stateTransitions(self,_actor):
        return
    
    def setUp(self,_actor):
        _actor.action_frame = 0
        self.sprite_rate = self.base_sprite_rate
        if self.last_frame > 0:
            _actor.changeSprite(self.sprite_name)
            if self.sprite_rate < 0:
                _actor.changeSpriteImage(len(_actor.sprite.imageLibrary[_actor.sprite.flip][_actor.sprite.currentSheet])-1)
    
    def tearDown(self,_actor,_nextAction):
        for hitbox in self.hitboxes.values():
            hitbox.kill()
    
    def onClank(self,_actor):
        return
    
"""
The Dynamic Action is created by the Builder. It contains most things that an action would
need, but anything more than that can still be defined as above.
"""
class DynamicAction(Action):
    def __init__(self,_length,_parent=None,_var=dict(),_startingFrame=0):
        Action.__init__(self,_length,_startingFrame)
        if _parent:
            DynamicAction.__bases__ += (_parent,)
        self.parent = _parent
        
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
        self.default_vars = _var
        for key,val in _var.iteritems():
            setattr(self,key,val)
        
    def update(self,_actor):
        for act in self.actions_before_frame:
            act.execute(self,_actor)
        if self.frame < len(self.actions_at_frame):
            for act in self.actions_at_frame[self.frame]:
                act.execute(self,_actor)
        if self.frame == self.last_frame:
            for act in self.actions_at_last_frame:
                act.execute(self,_actor)
        for act in self.actions_after_frame:
            act.execute(self,_actor)
        
        if self.parent: self.parent.update(self,_actor)
    
    def updateAnimationOnly(self,_actor):
        animation_actions = (subaction.changeFighterSubimage, subaction.changeFighterSprite, subaction.shiftSpritePosition,
                            subaction.activateHitbox, subaction.deactivateHitbox, subaction.modifyHitbox, subaction.updateHitbox)
        for act in self.actions_before_frame:
            if isinstance(act, animation_actions):
                act.execute(self,_actor)
        if self.frame < len(self.actions_at_frame):
            for act in self.actions_at_frame[self.frame]:
                if isinstance(act, animation_actions):
                    act.execute(self,_actor)
        if self.frame == self.last_frame:
            for act in self.actions_at_last_frame:
                if isinstance(act, animation_actions):
                    act.execute(self,_actor)
        for act in self.actions_after_frame:
            if isinstance(act, animation_actions):
                act.execute(self,_actor)
        Action.update(self, _actor)
                
        self.frame += 1         
        
        
        
    def stateTransitions(self,_actor):
        for act in self.state_transition_actions:
            act.execute(self,_actor)
        if self.parent: self.parent.stateTransitions(self,_actor)
    
    def setUp(self,_actor):
        if self.parent: self.parent.setUp(self,_actor)
        
        for act in self.set_up_actions:
            act.execute(self,_actor)
        
    def tearDown(self,_actor,_newAction):
        if self.parent: self.parent.tearDown(self,_actor,_newAction)
        
        for act in self.tear_down_actions:
            act.execute(self,_actor)

    def onClank(self,_actor):
        Action.onClank(self, _actor)
        for act in self.actions_on_clank:
            act.execute(self,_actor)
        if self.parent: self.parent.onClank(self,_actor)
