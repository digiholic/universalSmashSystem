import engine.abstractFighter as abstractFighter
import spriteObject
import main

class Fighter(abstractFighter.AbstractFighter):
    def __init__(self,playerNum):
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
        sprite = spriteObject.SheetSprite("hitboxie_idle",[0,0],92,generateAlpha= False,file = __file__)
        abstractFighter.AbstractFighter.__init__(self,
                                 playerNum,
                                 sprite, #Start Sprite
                                 "HBoxie", #Name
                                 var)
        
        self.actions = main.importFromURI(__file__,'hitboxie_actions.py')
        
        self.current_action = self.actions.NeutralAction()
        
########################################################
#                  ACTION SETTERS                      #
########################################################
    
    def doIdle(self):
        self.changeAction(self.actions.NeutralAction())
            
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
        #if self.current_action.canBeInterrupted(newAction):
        self.flip()
        self.changeAction(newAction)
    
    def doJump(self):
        if self.grounded:
            self.changeAction(self.actions.Jump())
        else:
            if self.jumps > 0:
                self.changeAction(self.actions.AirJump())
    
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
    
    def applyKnockback(self,kb,kbg,trajectory):
        abstractFighter.AbstractFighter.applyKnockback(self, kb, kbg, trajectory)
        self.changeAction(self.actions.HitStun(40,trajectory))
        
########################################################
#                 ENGINE FUNCTIONS                     #
########################################################

    def keyPressed(self,key):
        abstractFighter.AbstractFighter.keyPressed(self,key)