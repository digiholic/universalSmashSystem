import engine.subaction as subaction
import xml.etree.ElementTree as ElementTree

# The action class is used for creating attacks, movement options,
# air dodges, rolls, and pretty much anything that happens to your
# character. It has a length, and keeps track of its current frame.
class Action():
    def __init__(self,_length=0):
        self.frame = 0
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
        self.hurtboxes = {}
        self.articles = {}
        
        self.name = str(self.__class__).split('.')[-1]
        
        self.actions_at_frame = [[]]
        self.actions_before_frame = []
        self.actions_after_frame = []
        self.actions_at_last_frame = []
        self.actions_on_clank = []
        self.actions_on_prevail = []
        
        #Conditional Action Groups for ifs and things
        #Dict in the form of "name" -> [Action List]
        self.conditional_actions = dict()
        
        self.state_transition_actions = []
        self.set_up_actions = []
        self.tear_down_actions = []
        
        self.default_vars = dict()
            
    # The update skeleton function. You must implement it for every action or you will get
    # an error.
    def update(self,_actor):
        if self.sprite_rate is not 0:
            if self.sprite_rate < 0:
                _actor.changeSpriteImage((self.frame // self.sprite_rate)-1, _loop=self.loop)
            else:                 _actor.changeSpriteImage(self.frame // self.sprite_rate, _loop=self.loop)
                    
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
        for hitbox in self.hitboxes.values():
            hitbox.update()
        for hurtbox in self.hurtboxes.values():
            hurtbox.update()
            
    def updateAnimationOnly(self,_actor):
        animation_actions = (subaction.changeFighterSubimage, subaction.changeFighterSprite, subaction.shiftSpritePosition,
                            subaction.activateHitbox, subaction.deactivateHitbox, subaction.modifyHitbox, 
                            subaction.activateHurtbox, subaction.deactivateHurtbox, subaction.modifyHurtbox)
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
        
        if self.sprite_rate is not 0:
            if self.sprite_rate < 0:
                _actor.changeSpriteImage((self.frame // self.sprite_rate)-1, _loop=self.loop)
            else:
                _actor.changeSpriteImage(self.frame // self.sprite_rate, _loop=self.loop)

        for hitbox in self.hitboxes.values():
            hitbox.update()
        for hurtbox in self.hurtboxes.values():
            hurtbox.update()
                
        self.frame += 1         
    
                
    def stateTransitions(self,_actor):
        for act in self.state_transition_actions:
            act.execute(self,_actor)
    
    def setUp(self,_actor):
        self.sprite_rate = self.base_sprite_rate
        if self.last_frame > 0:
            _actor.changeSprite(self.sprite_name)
            if self.sprite_rate < 0:
                _actor.changeSpriteImage(len(_actor.sprite.image_library[_actor.sprite.flip][_actor.sprite.current_sheet])-1)
        
        for act in self.set_up_actions:
            act.execute(self,_actor)

        if not len(self.hurtboxes):
            self.hurtboxes['auto'] = _actor.auto_hurtbox
            _actor.activateHurtbox(self.hurtboxes['auto'])
            
    def tearDown(self,_actor,_nextAction):
        for hitbox in self.hitboxes.values():
            hitbox.kill()
        for hurtbox in self.hurtboxes.values():
            hurtbox.kill()
        for act in self.tear_down_actions:
            act.execute(self,_actor)

    def onPrevail(self,_actor,_hitbox,_other):
        for act in self.actions_on_prevail:
            act.execute(self,_actor)

    def onClank(self,_actor,_hitbox,_other):
        for act in self.actions_on_clank:
            act.execute(self,_actor)
