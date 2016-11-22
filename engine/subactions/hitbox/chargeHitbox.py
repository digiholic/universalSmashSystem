from engine.subaction import *

class charge(SubAction):
    subact_group = 'Hitbox'
    fields = [NodeMap('max_charge','int','charge|maxCharge',10),
              NodeMap('start_charge_frame','int','charge',0),
              NodeMap('supress_mask','bool','charge|noMask',False),
              NodeMap('charge_deposit','string','charge|chargeDeposit','charge'),
              NodeMap('button_check','string','charge|buttonCheck','attack')
              ]
    
    def __init__(self,_max=10,_chargeFrame=0,_noMask=False,_chargeDeposit='charge',_buttonCheck='attack'):
        SubAction.__init__(self)
        self.max_charge = _max
        self.start_charge_frame = _chargeFrame
        self.supress_mask = _noMask
        self.charge_deposit = _chargeDeposit
        self.button_check = _buttonCheck
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if hasattr(_action, self.charge_deposit):
            setattr(_action, self.charge_deposit, getattr(_action, self.charge_deposit)+1)
        else:
            setattr(_action, self.charge_deposit, 1)
            #If we're starting out, start flashing unless asked not to
            if not self.supress_mask:
                _actor.createMask([255,255,0],72,True,32)
        
        if _actor.keysContain(self.button_check) and getattr(_action, self.charge_deposit) <= self.max_charge:
            _action.frame = self.start_charge_frame
        else:
            #We're moving on. Turn off the flashing
            _actor.mask = None
