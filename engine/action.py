import pygame

# The action class is used for creating attacks, movement options,
# air dodges, rolls, and pretty much anything that happens to your
# character. It has a length, and keeps track of its current frame.
class Action():
    def __init__(self,length,startingFrame = 0):
        self.frame = startingFrame
        self.lastFrame = length
        self.actor = None
        self.var = {}
        
    
    # The update skeleton function. You must implement it for every action or you will get
    # an error.
    def update(self,actor):
        return None
    
    def stateTransitions(self,actor):
        return
    
    def setUp(self,actor):
        return
    
    def tearDown(self,actor,newAction):
        return
    
"""
The Dynamic Action is created by the Builder. It contains most things that an action would
need, but anything more than that can still be defined as above.
"""
class DynamicAction(Action):
    def __init__(self,length,startingFrame=0):
        Action.__init__(self, length, startingFrame)
        self.actionsAtFrame = [[]]
        self.stateTransitionsAtFrame = [[]]
        self.setUpActions = []
        self.tearDownActions = []
        
    def update(self,actor):
        for act in self.actionsAtFrame[self.frame]:
            act.execute(actor)
    
    def stateTransitions(self,actor):
        for act in self.stateTransitionsAtFrame[self.frame]:
            act(actor)
    
    def setUp(self,actor):
        for act in self.setUpActions:
            act.execute(actor)
    
    def tearDown(self,actor):
        for act in self.tearDownActions:
            act.execute(actor)
        return    