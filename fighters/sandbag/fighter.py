import engine.abstractFighter as abstractFighter
import spriteManager
import os
import settingsManager
import engine.baseActions as baseActions

class Fighter(abstractFighter.AbstractFighter):
    def __init__(self,base_dir,player_num):
        var = {
                'weight': 200,
                'gravity': 1.0,
                'max_fall_speed': 20,
                'max_ground_speed': 5,
                'run_speed': 5,
                'max_air_speed': 4,
                'friction': 1.0,
                'dashGrip': 1.0,
                'air_control': 0.2,
                'jumps': 1,
                'jump_height': 8,
                'air_jump_height':10,
                'heavy_land_lag': 4
                }
        path = os.path.join(os.path.dirname(__file__),"sprites")
        sprite = spriteManager.SpriteHandler(path,"sandbag_","idle",128,{})
        
        abstractFighter.AbstractFighter.__init__(self,base_dir,player_num)
        
        self.actions = baseActions
        
        self.current_action = self.actions.NeutralAction()
    
def cssIcon(): return None

def getFighter(base_dir,player_num):
    return Fighter(base_dir,player_num)
