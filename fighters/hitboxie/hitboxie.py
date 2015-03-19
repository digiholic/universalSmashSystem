import fighter
import actions

class Hitboxie(fighter.Fighter):
    def __init__(self,sprite,keybindings):
        fighter.Fighter.__init__(self,
                                 "hitboxie_idle", #Start Sprite
                                 "HBoxie", #Name
                                 keybindings,
                                 .35,.35, #weight, gravity
                                 10, #MaxFallSpeed
                                 6,5, #MaxGroundSpeed, MaxAirSpeed
                                 0.2,0.4, #friction, air control
                                 1,8,10) #jumps, jump height, air jump height
        self.current_action = actions.NeutralAction()
                         
    
########################################################
#                  ACTION SETTERS                      #
########################################################
    
    def doIdle(self):
        self.current_action = actions.NeutralAction()
            
    def doLand(self):
        self.current_action = actions.Land()
        
    def doStop(self):
        if self.grounded:
            self.current_action = actions.Stop()
            
    def doGroundMove(self,direction):
        #dist = self.bufferGetDistanceBack((self.keyBindings.k_right,False))
        #if (dist and dist < 2):
        newAction = actions.Move()
        #if self.current_action.canBeInterrupted(newAction):
        if self.facing != direction:
            self.flip()
        self.current_action = newAction
        
    def doPivot(self,direction):
        newAction = actions.Pivot()
        #if self.current_action.canBeInterrupted(newAction):
        if self.facing != direction:
            self.flip()
        self.current_action = newAction
    
    def doJump(self):
        if self.grounded:
            self.current_action = actions.Jump()
        else:
            if self.jumps > 0:
                self.current_action = actions.AirJump()
            
    def doNeutralAttack(self):
        if isinstance(self.current_action,actions.NeutralAttack):
            self.current_action.nextJab = True
            return
        
        elif isinstance(self.current_action, actions.NeutralAttack2):
            self.current_action.nextJab = True
            return
            
        newAction = actions.NeutralAttack()
        if self.current_action.canBeInterrupted(newAction):
            self.current_action = actions.NeutralAttack()        
    
    def doAirAttack(self):
        if not (self.keysContain(self.keyBindings.k_left) or self.keysContain(self.keyBindings.k_right) 
                or self.keysContain(self.keyBindings.k_up) or self.keysContain(self.keyBindings.k_down)):
            self.current_action = actions.NeutralAir()
            
########################################################
#                  STATE CHANGERS                      #
########################################################
        
    def die(self):
        fighter.Fighter.die(self)
        self.current_action = actions.Fall()
    
    def applyKnockback(self,kb,kbg,trajectory):
        fighter.Fighter.applyKnockback(self, kb, kbg, trajectory)
        self.current_action = actions.HitStun(40,trajectory)
        
########################################################
#                 ENGINE FUNCTIONS                     #
########################################################

    def keyPressed(self,key):
        fighter.Fighter.keyPressed(self,key)
        if key == self.keyBindings.k_right:
            if self.grounded:
                if self.change_x < 0:
                    self.doPivot(1)
                else:
                    self.doGroundMove(1)
        elif key == self.keyBindings.k_left:
            if self.grounded:
                if self.change_x > 0:
                    self.doPivot(-1)
                else:
                    self.doGroundMove(-1)
        elif key == self.keyBindings.k_up:
            self.doJump()
            
        elif key == self.keyBindings.k_attack:
            if self.grounded:
                self.doNeutralAttack()
            else:
                self.doAirAttack()
                
    def keyReleased(self,key):
        if fighter.Fighter.keyReleased(self,key):
            if key == self.keyBindings.k_right:
                self.doStop()
            elif key == self.keyBindings.k_left:
                self.doStop()