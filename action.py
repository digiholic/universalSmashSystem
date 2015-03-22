import pygame

# The action class is used for creating attacks, movement options,
# air dodges, rolls, and pretty much anything that happens to your
# character. It has a length, and keeps track of its current frame.
class Action():
    def __init__(self,length,startingFrame = 0):
        self.frame = startingFrame
        self.lastFrame = length
        self.actor = None
        self.hitboxes = pygame.sprite.Group()
        self.tags = []
        self.interruptTags = []
        
    
    # The update skeleton function. You must implement it for every action or you will get
    # an error.
    def update(self,actor):
        return None
    
    def stateTransitions(self,actor):
        return
    
    def setUp(self,actor):
        return
    
    def tearDown(self,actor):
        return
    
    def canBeInterrupted(self,other):
        if other:
            if self.interruptTags.count("ALL") > 0: return True
            for tag in self.interruptTags:
                if other.tags.count(tag) > 0: return True
            return False
        else:
            return False
    
