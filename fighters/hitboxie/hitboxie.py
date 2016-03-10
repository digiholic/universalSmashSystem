import engine.abstractFighter as abstractFighter
import settingsManager
import os

class Hitboxie(abstractFighter.AbstractFighter):
    def __init__(self,playerNum,sprites):
        var = {
                'weight': 100,
                'gravity': .5,
                'maxFallSpeed': 20,
                'maxGroundSpeed': 6,
                'runSpeed': 9,
                'maxAirSpeed': 6,
                'friction': 0.2,
                'staticGrip': 0.1,
                'airControl': 0.6,
                'jumps': 1,
                'jumpHeight': 12,
                'airJumpHeight': 14,
                'heavyLandLag': 4
                }
        abstractFighter.AbstractFighter.__init__(self,
                                 playerNum,
                                 sprites, #Start Sprite
                                 "HBoxie", #Name
                                 var)
        self.actions = settingsManager.importFromURI(__file__,'hitboxie_actions.py',suffix=str(playerNum))
        
        #try:
        self.current_action = self.actions.NeutralAction()
        #except:
        #    raise ValueError(os.path.normpath(os.path.join(os.path.dirname(__file__).replace('main.exe',''), 'hitboxie_actions.py')))
        
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
            
    def doGroundMove(self,direction):
        if (self.facing == 1 and direction == 180) or (self.facing == -1 and direction == 0):
            self.flip()
        self.changeAction(self.actions.Move())

    def doDash(self,direction):
        if (self.facing == 1 and direction == 180) or (self.facing == -1 and direction == 0):
            self.flip()
        self.changeAction(self.actions.Dash())
        
    def doRun(self,direction):
        if (self.facing == 1 and direction == 180) or (self.facing == -1 and direction == 0):
            self.flip()
        self.changeAction(self.actions.Run())
        
    def doPivot(self):
        newAction = self.actions.Pivot()
        self.flip()
        self.changeAction(newAction)
    
    def doJump(self):
        self.changeAction(self.actions.Jump())

    def doAirJump(self):
        self.changeAction(self.actions.AirJump())

    def doPreShield(self):
        self.changeAction(self.actions.PreShield())
                
    def doShield(self):
        self.changeAction(self.actions.Shield())

    def doShieldStun(self, length):
        self.changeAction(self.actions.ShieldStun(length))
    
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

    def doLedgeGetup(self):
        self.changeAction(self.actions.LedgeGetup())

    def doGroundGrab(self):
        self.changeAction(self.actions.GroundGrab())

    def doGrabbing(self):
        self.changeAction(self.actions.Grabbing())

    def doGrabbed(self, height):
        self.changeAction(self.actions.Grabbed(height))

    def doPummel(self):
        self.changeAction(self.actions.Pummel())

    def doThrow(self):
        (key, invkey) = self.getForwardBackwardKeys()
        if self.keysContain(key):
            self.changeAction(self.actions.ForwardThrow())
        elif self.keysContain(invkey):
            self.changeAction(self.actions.DownThrow())
        elif self.keysContain('up'):
            self.changeAction(self.actions.ForwardThrow())
        elif self.keysContain('down'):
            self.changeAction(self.actions.DownThrow())
        else: # How did we get here? 
            self.changeAction(self.actions.ForwardThrow())
        
    def doGroundAttack(self):
        print('player ', self.playerNum, ' attacking')
        (key, invkey) = self.getForwardBackwardKeys()
        if self.keysContain(key):
            if self.checkSmash(key):
                print("SMASH!")
                self.changeAction(self.actions.ForwardSmash())
            else:
                self.changeAction(self.actions.ForwardAttack())
        elif self.keysContain(invkey):
            self.flip()
            self.changeAction(self.actions.ForwardAttack())
        elif self.keysContain('up'):
            pass
        elif self.keysContain('down'):
            self.changeAction(self.actions.DownAttack())
        else:
            self.changeAction(self.actions.NeutralAttack())

    def doDashAttack(self):
        self.changeAction(self.actions.DashAttack())
    
    def doAirAttack(self):
        (forward, backward) = self.getForwardBackwardKeys()
        if (self.keysContain(forward)):
            pass
        elif (self.keysContain(backward)):
            pass
        elif(self.keysContain('up')):
            pass
        elif (self.keysContain('down')):
            self.changeAction(self.actions.DownAir())
        else: self.changeAction(self.actions.NeutralAir())

    def doGetupAttack(self, direction):
        self.changeAction(self.actions.NeutralAttack())
    
    def doGroundSpecial(self):
        (forward, backward) = self.getForwardBackwardKeys()
        if self.keysContain(forward):
            self.changeAction(self.actions.ForwardSpecial())
        elif self.keysContain(backward):
            self.flip()
            self.changeAction(self.actions.ForwardSpecial())
        elif (self.keysContain('up')):
            pass
        elif (self.keysContain('down')):
            pass
        else: 
            self.changeAction(self.actions.NeutralGroundSpecial())

    def doAirSpecial(self):
        (forward, backward) = self.getForwardBackwardKeys()
        if self.keysContain(forward):
            self.changeAction(self.actions.ForwardSpecial())
        elif self.keysContain(backward):
            self.flip()
            self.changeAction(self.actions.ForwardSpecial())
        elif (self.keysContain('up')):
            pass
        elif (self.keysContain('down')):
            pass
        else: 
            self.changeAction(self.actions.NeutralAirSpecial())

    def doHitStun(self,hitstun,trajectory):
        self.changeAction(self.actions.HitStun(hitstun,trajectory))

    def doTrip(self, length, direction):
        self.changeAction(self.actions.Trip(length, direction))

    def doGetup(self, direction):
        self.changeAction(self.actions.Getup(direction))
                
########################################################
#                  STATE CHANGERS                      #
########################################################

    def setGrabbing(self, other):
        self.grabbing = other
        
    def die(self,respawn = True):
        abstractFighter.AbstractFighter.die(self,respawn)
        self.changeAction(self.actions.Fall())
    
    def applyKnockback(self,damage,kb,kbg,trajectory,weight_influence=1,hitstun_multiplier=1):
        abstractFighter.AbstractFighter.applyKnockback(self, damage, kb, kbg, trajectory,weight_influence,hitstun_multiplier)
        
########################################################
#                 ENGINE FUNCTIONS                     #
########################################################

    def keyPressed(self,key):
        abstractFighter.AbstractFighter.keyPressed(self,key)
