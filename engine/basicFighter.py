import settingsManager
import vector2D

class BasicFighter():
    def __init__(self,
                 playerNum,
                 sprite,
                 attributes):
        
        self.attr = attributes
        self.vars = {}
        self.flags = {}
        self.functionHooks = {
                              'beforeUpdate': [],
                              'afterUpdate' : []
                              }
        
        self.sprite = sprite
        self.current_action = None
        
        self.velocity = vector2D.Vec2d()
        self.actions = settingsManager.importFromURI(__file__,'baseActions.py')
        
    def update(self):
        for func in self.functionHooks['beforeUpdate']:
            func(self)
            
        for func in self.functionHooks['afterUpdate']:
            func(self)
########################################################
#                  ACTION SETTERS                      #
########################################################
    
    """
    These functions are meant to be overridden. They are
    provided so the baseActions can change the AbstractFighter's
    actions. If you've changed any of the base actions
    for the fighter (including adding a sprite change)
    override the corresponding method and have it set
    an instance of your overridden action.
    """

    def changeAction(self,newAction):
        newAction.setUp(self,self.current_action)
        self.current_action.tearDown(self,newAction)
        self.current_action = newAction
        
    def doIdle(self):
        self.changeAction(self.actions.NeutralAction())
        
    def doGroundMove(self,direction,run=False):
        if run: self.current_action = self.actions.Run()
        else: self.changeAction(self.actions.Move())

    def doHitStun(self,hitstun,trajectory):
        self.changeAction(self.actions.HitStun(hitstun,trajectory))
    
    def doPivot(self):
        self.changeAction(self.actions.Pivot())
    
    def doStop(self):
        self.changeAction(self.actions.NeutralAction())
    
    def doLand(self):
        self.current_action = self.actions.Land()
    
    def doFall(self):
        self.changeAction(self.actions.Fall())
        
    def doGroundJump(self):
        self.current_action = self.actions.Jump()
    
    def doAirJump(self):
        self.current_action = self.actions.AirJump()
    
    def doGroundAttack(self):
        return None
    
    def doAirAttack(self):
        return None

    def doGroundGrab(self):
        return None

    def doAirGrab(self):
        return None

    def doGrabbed(self,height):
        self.changeAction(self.actions.Grabbed(height))

    def doRelease(self):
        self.changeAction(self.actions.Release())

    def doGrabbing(self):
        self.changeAction(self.actions.Grabbing())

    def doPummel(self):
        return None

    def doThrow(self):
        return None
   
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
        
    def doLedgeGetup(self):
        self.changeAction(self.actions.LedgeGetup())
        
    def doGetTrumped(self):
        print("trumped")
        
########################################################
#                  STATE CHANGERS                      #
########################################################
    

########################################################
#                 ENGINE FUNCTIONS                     #
########################################################
    
    def registerFunction(self,hook,func):
        self.functionHooks[hook].append(func)
        
    def unregisterFunction(self,hook,func):
        self.functionHooks[hook].remove(func)
    
