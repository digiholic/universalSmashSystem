import engine.abstractFighter as abstractFighter
import spriteObject
import os
import main

class Fighter(abstractFighter.AbstractFighter):
    def __init__(self,playerNum):
        var = {
                'weight': 2.0,
                'gravity': 1.0,
                'maxFallSpeed': 20,
                'maxGroundSpeed': 5,
                'maxAirSpeed': 4,
                'friction': 0.2,
                'airControl': 0.2,
                'jumps': 1,
                'jumpHeight': 8,
                'airJumpHeight':10
                }
        sprite = spriteObject.SheetSprite("sandbag",[0,0],92,generateAlpha = False,file = __file__)
        
        abstractFighter.AbstractFighter.__init__(self,
                                 playerNum,
                                 sprite, #Start Sprite
                                 "Sandbag", #Name
                                 var) #jumps, jump height, air jump height
        
        self.actions = main.importFromURI(__file__,'sandbag_actions.py')
        
        self.keyBindings = abstractFighter.Keybindings({})
        self.current_action = self.actions.NeutralAction()