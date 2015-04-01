import fighter
import actions

class Hitboxie(fighter.Fighter):
    def __init__(self,sprite,keybindings):
        var = {
                'weight': 1.0,
                'gravity': .7,
                'maxFallSpeed': 20,
                'maxGroundSpeed': 6,
                'maxAirSpeed': 6,
                'friction': 0.2,
                'airControl': 0.6,
                'jumps': 1,
                'jumpHeight': 12,
                'airJumpHeight':14
                }
        
        fighter.Fighter.__init__(self,
                                 "hitboxie_idle", #Start Sprite
                                 "HBoxie", #Name
                                 keybindings,
                                 var)
        self.current_action = actions.NeutralAction()
        
########################################################
#                  ACTION SETTERS                      #
########################################################
    
    def doIdle(self):
        self.changeAction(actions.NeutralAction())
            
    def doLand(self):
        self.changeAction(actions.Land())
        
    def doStop(self):
        if self.grounded:
            self.changeAction(actions.Stop())
            
    def doGroundMove(self,direction):
        newAction = actions.Move()
        if (self.facing == 1 and direction == 180) or (self.facing == -1 and direction == 0):
            self.doPivot()
        self.changeAction(newAction)
        
    def doPivot(self):
        newAction = actions.Pivot()
        #if self.current_action.canBeInterrupted(newAction):
        self.flip()
        self.changeAction(newAction)
    
    def doJump(self):
        if self.grounded:
            self.changeAction(actions.Jump())
        else:
            if self.jumps > 0:
                self.changeAction(actions.AirJump())
    
    def doGroundAttack(self):
        (key, invkey) = self.getForwardBackwardKeys()
        if self.keysContain(key):
            self.changeAction(actions.ForwardAttack())
        elif self.keysContain(invkey):
            self.flip()
            self.changeAction(actions.ForwardAttack())
             
    def doNeutralAttack(self):
        if isinstance(self.current_action,actions.NeutralAttack):
            self.current_action.nextJab = True
            return
        
        elif isinstance(self.current_action, actions.NeutralAttack2):
            self.current_action.nextJab = True
            return
            
        newAction = actions.NeutralAttack()
        if self.current_action.canBeInterrupted(newAction):
            self.changeAction(actions.NeutralAttack())     
    
    def doAirAttack(self):
        if not (self.keysContain(self.keyBindings.k_left) or self.keysContain(self.keyBindings.k_right) 
                or self.keysContain(self.keyBindings.k_up) or self.keysContain(self.keyBindings.k_down)):
            self.changeAction(actions.NeutralAir())
            
########################################################
#                  STATE CHANGERS                      #
########################################################
        
    def die(self):
        fighter.Fighter.die(self)
        self.changeAction(actions.Fall())
    
    def applyKnockback(self,kb,kbg,trajectory):
        fighter.Fighter.applyKnockback(self, kb, kbg, trajectory)
        self.changeAction(actions.HitStun(40,trajectory))
        
########################################################
#                 ENGINE FUNCTIONS                     #
########################################################

    def keyPressed(self,key):
        fighter.Fighter.keyPressed(self,key)