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
            if self.hurtbox in _action.hurtboxes:
                hurtbox = _action.hurtboxes[self.hurtbox]
                if self.armor_name is '':
                    hurtbox.armor.clear()
                elif self.armor_name in hurtbox.armor:
                    del hurtbox.armor[self.armor_name]
        else:
            if self.armor_name is '':
                _actor.armor.clear()
            elif self.armor_name in _actor.armor:
                del _actor.armor[self.armor_name]
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.UpdateHitboxProperties(_root,self)
    
    def getDisplayName(self):
        return 'Deactivate Armor: ' + self.armor_name
