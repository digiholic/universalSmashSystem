from engine.subaction import *

class removeArmor(SubAction):
    subact_group = 'Armor'
    fields = [NodeMap('armor_name','string','removeArmor',''),
              NodeMap('hurtbox','string','removeArmor|hurtbox','')
              ]
    
    def __init__(self,_armorName='',_hurtbox=''):
        SubAction.__init__(self)
        self.armor_name = _armorName
        self.hurtbox = _hurtbox
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.hurtbox is not '':
            if _action.hurtboxes.has_key(self.hurtbox):
                hurtbox = _action.hurtboxes[self.hurtbox]
                if self.armor_name is '':
                    hurtbox.armor.clear()
                elif hurtbox.armor.has_key(self.armor_name):
                    del hurtbox.armor[self.armor_name]
        else:
            if self.armor_name is '':
                _actor.armor.clear()
            elif _actor.armor.has_key(self.armor_name):
                del _actor.armor[self.armor_name]
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.UpdateHitboxProperties(_root,self)
    
    def getDisplayName(self):
        return 'Deactivate Armor: ' + self.armor_name
