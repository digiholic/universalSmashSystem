import pygame
import spriteManager
import math
import random
import settingsManager
import engine.hitbox as hitbox
import engine.collisionBox as collisionBox
import subaction
import numpy

"""
Status effects are effects that should remain beyond the length of the action that called them.

owner - the fighter that the status effect applies its actions on. Can be None.
length - if this article has logic or animation, you can set this to be used in the update() method,
         just like a fighter's action.
"""
class StatusEffect():
    def __init__(self, _owner, _length=1, _tags = []):
        self.owner = _owner
        self.game_state = self.owner.game_state

        self.frame = 0
        self.last_frame = _length
        self.tags = _tags

        self.actions_at_frame = [[]]
        self.actions_before_frame = []
        self.actions_after_frame = []
        self.actions_at_last_frame = []
        self.events = dict()
        self.set_up_actions = []
        self.tear_down_actions = []

        self.default_vars = {}
        self.variables = {}

    ########################################################
    #                   UPDATE METHODS                     #
    ########################################################

    def update(self, *args): #Ignores actor
        #Do all of the subactions involving update
        for act in self.actions_before_frame:
            act.execute(self,self)
        if self.frame < len(self.actions_at_frame):
            for act in self.actions_at_frame[self.frame]:
                act.execute(self,self)
        if self.frame == self.last_frame:
            for act in self.actions_at_last_frame:
                act.execute(self,self)
        for act in self.actions_after_frame:
            act.execute(self,self)

        if self.frame == self.last_frame:
            self.deactivate()
        self.frame += 1

    def updateAnimationOnly(self, *args): #Ignores actor
        # Nothing else, as it should
        self.frame += 1

    def activate(self):
        self.owner.status_effects.append(self)

        self.variables = self.default_vars.copy()
        print(self.variables)

        for act in self.set_up_actions:
            act.execute(self,self)

    def deactivate(self):
        for act in self.tear_down_actions:
            act.execute(self,self)
        if self in self.owner.status_effects:
            self.owner.status_effects.remove(self)

    ########################################################
    #              COLLISIONS AND MOVEMENT                 #
    ########################################################

    def setSpeed(self, _speed, _direction):
        """ Set the article's speed. Instead of modifying the change_x and change_y values manually,
        this will calculate what they should be set at if you want to give a direction and
        magnitude instead.

        Parameters
        -----------
        _speed : float
            The total speed you want the fighter to move
        _direction : int
            The angle of the speed vector in degrees, 0 being right, 90 being up, 180 being left.
        """
        (x,y) = getXYFromDM(_direction, _speed)
        self.owner.change_x = x
        self.owner.change_y = y

    ########################################################
    #                 COMBAT FUNCTIONS                     #
    ########################################################

    def applySubactions(self, _subacts):
        for subact in _subacts:
            subact.execute(self.current_action, self)
        return True # Our hit filter stuff expects this

    ########################################################
    #                 HELPER FUNCTIONS                     #
    ########################################################

    def playSound(self, _sound):
        self.owner.playSound(_sound)

class TemporaryHitFilter(StatusEffect):
    def __init__(self, _owner, _armor, _length=1, _tags=[]):
        StatusEffect.__init__(self, _owner, _length, _tags)
        self.armor = _armor

    def activate(self):
        StatusEffect.activate(self)
        self.owner.armor[self] = self.armor

    def update(self, *args): #Ignores actor
        StatusEffect.update(self, *args)
        if not self.owner.mask and (self.frame < self.last_frame):
            self.owner.createMask([255,255,255], self.last_frame-self.frame, True, 12)

    def deactivate(self):
        StatusEffect.deactivate(self)
        if self in self.owner.armor:
            del self.owner.armor[self]
