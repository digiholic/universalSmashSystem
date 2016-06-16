import engine.abstractFighter as abstractFighter
import spriteManager
import os
import settingsManager

class Fighter(abstractFighter.AbstractFighter):
    def __init__(self,baseDir,playerNum):
        var = {
                'weight': 200,
                'gravity': 1.0,
                'maxFallSpeed': 20,
                'maxGroundSpeed': 5,
                'runSpeed': 5,
                'maxAirSpeed': 4,
                'friction': 1.0,
                'dashGrip': 1.0,
                'airControl': 0.2,
                'jumps': 1,
                'jumpHeight': 8,
                'airJumpHeight':10,
                'heavyLandLag': 4
                }
        path = os.path.join(os.path.dirname(__file__),"sprites")
        sprite = spriteManager.SpriteHandler(path,"sandbag_","idle",128,{})
        
        abstractFighter.AbstractFighter.__init__(self,baseDir,playerNum)
        
        self.actions = settingsManager.importFromURI(__file__,'sandbag_actions.py')
        
        self.current_action = self.actions.NeutralAction()
    
    
    def doIdle(self):
        self.changeAction(self.actions.NeutralAction())

    def doCrouch(self):
        pass

    def doCrouchGetup(self):
        pass
    
    def doFall(self):
        self.changeAction(self.actions.Fall())

    def doHelpless(self):
        pass
    
    def doPlatformDrop(self):
        pass
          
    def doLand(self):
        pass

    def doHelplessLand(self):
        pass
        
    def doStop(self):
        pass

    def doRunStop(self):
        pass
            
    def doGroundMove(self,direction):
        pass

    def doDash(self,direction):
        pass
        
    #def doRun(self,direction):
    #    pass
        
    def doPivot(self):
        pass

    def doRunPivot(self):
        pass
    
    def doJump(self):
        pass

    def doAirJump(self):
        pass

    def doPreShield(self):
        pass
                
    def doShield(self):
        pass

    def doShieldStun(self, length):
        pass
        
    def doForwardRoll(self):
        pass
    
    def doBackwardRoll(self):
        pass
        
    def doSpotDodge(self):
        pass
        
    def doAirDodge(self):
        pass

    def doTechDodge(self):
        pass
     
    def doLedgeGrab(self,ledge):
        pass

    def doLedgeGetup(self):
        pass

    def doLedgeAttack(self):
        pass

    def doLedgeRoll(self):
        pass

    def doGroundGrab(self):
        pass

    def doGrabbing(self):
        pass

    def doTrapped(self, length):
        pass

    def doStunned(self, length):
        pass

    def doGrabbed(self, height):
        pass

    def doPummel(self):
        pass

    def doThrow(self):
        pass
        
    def doGroundAttack(self):
        pass

    def doDashAttack(self):
        pass

    def doDashGrab(self):
        pass
    
    def doAirAttack(self):
        pass

    def doGetupAttack(self, direction):
        pass
    
    def doGroundSpecial(self):
        pass

    def doAirSpecial(self):
        pass

    def doHitStun(self,hitstun,trajectory,hitstop):
        pass

    def doTryTech(self, hitstun, trajectory, hitstop):
        pass

    def doTrip(self, length, direction):
        pass

    def doGetup(self, direction):
        pass    
def cssIcon(): return None

def getFighter(baseDir,playerNum):
    return Fighter(baseDir,playerNum)
