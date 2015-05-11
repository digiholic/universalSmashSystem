import engine.abstractFighter as abstractFighter
import spriteObject
import spriteManager
import main

class Hitboxie(abstractFighter.AbstractFighter):
    def __init__(self,playerNum,sprites):
        var = {
                'weight': 100,
                'gravity': .5,
                'maxFallSpeed': 20,
                'maxGroundSpeed': 6,
                'maxAirSpeed': 6,
                'friction': 0.2,
                'airControl': 0.6,
                'jumps': 1,
                'jumpHeight': 12,
                'airJumpHeight':14
                }
        abstractFighter.AbstractFighter.__init__(self,
                                 playerNum,
                                 sprites, #Start Sprite
                                 "HBoxie", #Name
                                 var)
        
        self.actions = main.importFromURI(__file__,'hitboxie_actions.py')
        
        self.current_action = self.actions.NeutralAction()
        
########################################################
#                  ACTION SETTERS                      #
########################################################
    
    def doIdle(self):
        self.changeAction(self.actions.NeutralAction())
    
    def doFall(self):
        self.changeAction(self.actions.Fall())
                
    def doLand(self):
        self.changeAction(self.actions.Land())
        
    def doStop(self):
        if self.grounded:
            self.changeAction(self.actions.Stop())
            
    def doGroundMove(self,direction,run=False):
        if run: newAction = self.actions.Run()
        else: newAction = self.actions.Move()
        if (self.facing == 1 and direction == 180) or (self.facing == -1 and direction == 0):
            self.flip()
        self.changeAction(newAction)
        
    def doPivot(self):
        newAction = self.actions.Pivot()
        self.flip()
        self.changeAction(newAction)
    
    def doJump(self):
        if self.grounded:
            self.changeAction(self.actions.Jump())
        else:
            if self.jumps > 0:
                self.changeAction(self.actions.AirJump())
                
    def doShield(self):
        self.changeAction(self.actions.Shield())
    
    def doShieldBreak(self):
        self.changeAction(self.actions.ShieldBreak())
        
    def doForwardRoll(self):
        self.changeAction(self.actions.ForwardRoll())
    
    def doBackwardRoll(self):
        self.changeAction(self.actions.BackwardRoll())
        
    def doSpotDodge(self):
        self.changeAction(self.actions.SpotDodge())
        
    def doAirDodge(self):
        self.changeAction(self.actions.AirDodge())
     
    def doLedgeGrab(self,ledge):
        self.changeAction(self.actions.LedgeGrab(ledge))
        
    def doGroundAttack(self):
        (key, invkey) = self.getForwardBackwardKeys()
        if self.keysContain(key):
            self.changeAction(self.actions.ForwardAttack())
        elif self.keysContain(invkey):
            self.flip()
            self.changeAction(self.actions.ForwardAttack())
        elif self.keysContain(self.keyBindings.k_up):
            pass
        elif self.keysContain(self.keyBindings.k_down):
            self.changeAction(self.actions.DownAttack())
        else:
            self.changeAction(self.actions.NeutralAttack())   
    
    def doAirAttack(self):
        (forward, backward) = self.getForwardBackwardKeys()
        if (self.keysContain(forward)):
            pass
        elif (self.keysContain(backward)):
            pass
        elif(self.keysContain(self.keyBindings.k_up)):
            pass
        elif (self.keysContain(self.keyBindings.k_down)):
            pass
        else: self.changeAction(self.actions.NeutralAir())
            
########################################################
#                  STATE CHANGERS                      #
########################################################
        
    def die(self):
        abstractFighter.AbstractFighter.die(self)
        self.changeAction(self.actions.Fall())
    
    def applyKnockback(self,damage,kb,kbg,trajectory):
        abstractFighter.AbstractFighter.applyKnockback(self, damage, kb, kbg, trajectory)
        self.changeAction(self.actions.HitStun(40,trajectory))
        
########################################################
#                 ENGINE FUNCTIONS                     #
########################################################

    def keyPressed(self,key):
        abstractFighter.AbstractFighter.keyPressed(self,key)