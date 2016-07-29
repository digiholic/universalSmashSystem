import engine.abstractFighter as abstractFighter
import spriteManager
import os
import settingsManager
import engine.baseActions as baseActions

class Fighter(abstractFighter.AbstractFighter):
    def __init__(self,baseDir,playerNum):
        var = {
                'weight': 200,
                'gravity': 1.0,
                'maxFallSpeed': 20,
                'maxGroundSpeed': 5,
                'runSpeed': 5,
                'maxAirSpeed': 4,
                'friction': 1.0,
                'dashGrip': 1.0,
                'airControl': 0.2,
                'jumps': 1,
                'jumpHeight': 8,
                'airJumpHeight':10,
                'heavyLandLag': 4
                }
        path = os.path.join(os.path.dirname(__file__),"sprites")
        sprite = spriteManager.SpriteHandler(path,"sandbag_","idle",128,{})
        
        abstractFighter.AbstractFighter.__init__(self,baseDir,playerNum)
        
        self.actions = baseActions
        
        self.current_action = self.actions.NeutralAction()
    
def cssIcon(): return None

def getFighter(baseDir,playerNum):
    return Fighter(baseDir,playerNum)
