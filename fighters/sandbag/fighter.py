import engine.abstractFighter as abstractFighter
import spriteManager
import os
import main
import settingsManager

class Fighter(abstractFighter.AbstractFighter):
    def __init__(self,playerNum):
        var = {
                'weight': 200,
                'gravity': 1.0,
                'maxFallSpeed': 20,
                'maxGroundSpeed': 5,
                'maxAirSpeed': 4,
                'friction': 1.0,
                'dashGrip': 1.0,
                'airControl': 0.2,
                'jumps': 1,
                'jumpHeight': 8,
                'airJumpHeight':10
                }
        path = os.path.join(os.path.dirname(__file__),"sprites")
        sprite = spriteManager.SpriteHandler(path,"","sandbag",128,{})
        
        abstractFighter.AbstractFighter.__init__(self,
                                 playerNum,
                                 sprite, #Start Sprite
                                 "Sandbag", #Name
                                 var) #jumps, jump height, air jump height
        
        self.actions = main.importFromURI(__file__,'sandbag_actions.py')
        
        self.keyBindings = settingsManager.Keybindings({})
        self.current_action = self.actions.NeutralAction()
        
    def update(self):
        abstractFighter.AbstractFighter.update(self)

    #These are so grabbing the bag doesn't crash the game
    def doGroundMove(self):
        self.changeAction(self.actions.NeutralAction())

    def doStop(self):
        self.changeAction(self.actions.NeutralAction())

    def doIdle(self):
        self.changeAction(self.actions.NeutralAction())
        
def cssIcon(): return None

def getFighter(playerNum,colorNum):
    return Fighter(playerNum)
