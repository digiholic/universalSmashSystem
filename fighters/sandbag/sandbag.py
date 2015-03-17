import fighter
import sandbag_actions
import spriteObject


class Sandbag(fighter.Fighter):
    def __init__(self,sprite):
        fighter.Fighter.__init__(self,
                                 "sandbag", #Start Sprite
                                 "Sandbag", #Name
                                 {},
                                 .35,.35, #weight, gravity
                                 10, #MaxFallSpeed
                                 5,4, #MaxGroundSpeed, MaxAirSpeed
                                 0.2,0.2, #friction, air control
                                 1,8,10) #jumps, jump height, air jump height
        self.current_action = sandbag_actions.NeutralAction()
        self.sprite = spriteObject.ImageSprite("sandbag",[0,0],generateAlpha = False)