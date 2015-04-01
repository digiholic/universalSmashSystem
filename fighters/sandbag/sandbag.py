import fighter
import sandbag_actions
import spriteObject


class Sandbag(fighter.Fighter):
    def __init__(self,sprite):
        var = {
                'weight': 2.0,
                'gravity': .35,
                'maxFallSpeed': 10,
                'maxGroundSpeed': 5,
                'maxAirSpeed': 4,
                'friction': 0.2,
                'airControl': 0.2,
                'jumps': 1,
                'jumpHeight': 8,
                'airJumpHeight':10
                }
        
        fighter.Fighter.__init__(self,
                                 "sandbag", #Start Sprite
                                 "Sandbag", #Name
                                 {},
                                 var) #jumps, jump height, air jump height
        self.current_action = sandbag_actions.NeutralAction()
        self.sprite = spriteObject.ImageSprite("sandbag",[0,0],generateAlpha = False)