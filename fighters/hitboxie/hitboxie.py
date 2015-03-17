import fighter
import actions
import baseActions
import pygame

class Hitboxie(fighter.Fighter):
    def __init__(self,sprite):
        fighter.Fighter.__init__(self,
                                 "hitboxie_idle", #Start Sprite
                                 "HBoxie", #Name
                                 .35,.35, #weight, gravity
                                 10, #MaxFallSpeed
                                 6,4, #MaxGroundSpeed, MaxAirSpeed
                                 0.2,0.2, #friction, air control
                                 1,8,10) #jumps, jump height, air jump height
        self.current_action = actions.NeutralAction()
                         
    def keyPressed(self,key):
        fighter.Fighter.keyPressed(self,key)
        if key == pygame.K_RIGHT:
            if self.grounded:
                if self.change_x < 0:
                    self.doPivot(1)
                else:
                    self.doGroundMove(1)
        elif key == pygame.K_LEFT:
            if self.grounded:
                if self.change_x > 0:
                    self.doPivot(-1)
                else:
                    self.doGroundMove(-1)
        elif key == pygame.K_UP:
            self.doJump()
            
        elif key == pygame.K_z:
            if self.grounded:
                self.doNeutralAttack()
            else:
                self.doAirAttack()
                
    def keyReleased(self,key):
        if fighter.Fighter.keyReleased(self,key):
            if key == pygame.K_RIGHT:
                self.doStop()
            elif key == pygame.K_LEFT:
                self.doStop()
    
    def die(self):
        fighter.Fighter.die(self)
        self.current_action = actions.Fall()
    
    def applyKnockback(self,kb,kbg,trajectory):
        fighter.Fighter.applyKnockback(self, kb, kbg, trajectory)
        self.current_action = actions.HitStun(40,trajectory)
        
########################################################
#             BEGIN ACTION SETTERS                     #
########################################################
    
    def doIdle(self):
        self.current_action = actions.NeutralAction()
            
    def doLand(self):
        self.current_action = actions.Land()
        
    def doStop(self):
        if self.grounded:
            self.current_action = actions.Stop()
            
    def doGroundMove(self,direction):
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
        if not (self.keysContain(pygame.K_LEFT) or self.keysContain(pygame.K_RIGHT) 
                or self.keysContain(pygame.K_UP) or self.keysContain(pygame.K_DOWN)):
            self.current_action = actions.NeutralAir()
        
    