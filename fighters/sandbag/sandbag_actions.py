import engine.baseActions as baseActions

########################################################
#            BEGIN OVERRIDE CLASSES                    #
########################################################

class Move(baseActions.Move):
    def __init__(self):
        baseActions.Move.__init__(self)
        
    def update(self, actor):
        #Put override code here
        baseActions.Move.update(self, actor)
        
        
class Pivot(baseActions.Pivot):
    def __init__(self):
        baseActions.Pivot.__init__(self)
        
    def update(self,actor):
        #Put override code here
        baseActions.Pivot.update(self, actor)
        
class NeutralAction(baseActions.NeutralAction):
    def __init__(self):
        baseActions.NeutralAction.__init__(self,1)
        
    def update(self, actor):
        #Put override code here
        baseActions.NeutralAction.update(self, actor)
        
class HitStun(baseActions.HitStun):
    def __init__(self,hitstun,direction):
        baseActions.HitStun.__init__(self, hitstun, direction)
        
    def update(self,actor):
        if actor.grounded:
            actor.doIdle()
        baseActions.HitStun.update(self, actor)
        
class Jump(baseActions.Jump):
    def __init__(self):
        baseActions.Jump.__init__(self)
        
    def update(self,actor):
        #Put override code here
        baseActions.Jump.update(self, actor)
        

class AirJump(baseActions.AirJump):
    def __init__(self):
        baseActions.AirJump.__init__(self)
    
    def update(self,actor):
        #Put override code here
        baseActions.AirJump.update(self, actor)
            
class Fall(baseActions.Fall):
    def __init__(self):
        baseActions.Fall.__init__(self)
        
    def update(self,actor):
        #Put override code here
        baseActions.Fall.update(self, actor)

class Trip(baseActions.Trip):
    def __init__(self, length, direction):
        baseActions.Trip.__init__(self, length, direction)

    def update(self, actor):
        actor.rotateSprite(self.direction)
        if self.frame == self.lastFrame:
            actor.unRotate()
            actor.doIdle()
        baseActions.Trip.update(self, actor)

    def tearDown(self, actor, newAction):
        actor.unRotate()
            
class Land(baseActions.Land):
    def __init__(self):
        baseActions.Land.__init__(self)
        
    def update(self,actor):
        #Put override code here
        baseActions.Land.update(self, actor)

class Grabbed(baseActions.Grabbed):
    def __init__(self, height):
        baseActions.Grabbed.__init__(self, height)

    def update(self,actor):
        baseActions.Grabbed.update(self, actor)
            
########################################################
#             BEGIN HELPER METHODS                     #
########################################################
