from engine.subaction import *

class modifyArmor(SubAction):
    subact_group = 'Armor'
    
    def __init__(self,_armorName='',_hurtbox='',_armorVars={}):
        SubAction.__init__(self)
        self.armor_name = _armorName
        self.hurtbox = _hurtbox
        self.armor_vars = _armorVars
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if _action.hurtboxes.has_key(self.hurtbox):  
            hurtbox = _action.hurtboxes[self.hurtbox]
            if hurtbox.armor.has_key(self.armor_name):
                armor = hurtbox.armor[self.armor_name]
                if armor:
                    for name,value in self.hitbox_vars.iteritems():
                        if hasattr(armor, name):
                            if isinstance(value, VarData) or isinstance(value, FuncData) or isinstance(value, EvalData):
                                setattr(armor, name, value.unpack(_action,_actor))
                                if name in armor.variable_dict:
                                    armor.variable_dict[name] = value.unpack(_action, _actor)
                            else: 
                                setattr(hitbox, name, value)
                                if name in armor.variable_dict:
                                    armor.variable_dict[name] = value
        else:
            if _actor.armor.has_key(self.armor_name):
                armor = _actor.armor[self.armor_name]
                for name,value in self.hitbox_vars.iteritems():
                    if hasattr(armor, name):
                        if isinstance(value, VarData) or isinstance(value, FuncData) or isinstance(value, EvalData):
                            setattr(armor, name, value.unpack(_action,_actor))
                            if name in armor.variable_dict:
                                armor.variable_dict[name] = value.unpack(_action, _actor)
                        else: 
                            setattr(hitbox, name, value)
                            if name in armor.variable_dict:
                                armor.variable_dict[name] = value
        
    def getDisplayName(self):
        return 'Modify Armor: ' + str(self.armor_name)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyArmorProperties(_root,self,newArmor=False)
        
    def getXmlElement(self):
        elem = ElementTree.Element('modifyArmor')
        elem.attrib['name'] = self.armor_name
        for tag,value in self.armor_vars.iteritems():
            new_elem = ElementTree.Element(tag)
            new_elem.text = str(value)
            elem.append(new_elem)
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        armor_name = _node.attrib['name']
        hurtbox = _node.attrib['hurtbox']
        armor_vars = {}
        #these lists let the code know which keys should be which types.
        float_type = ['num_hits', 'damage_threshold', 'knockback_threshold', 'armor_damage_multiplier', 'armor_knockback_multiplier', 'overflow_damage_multiplier', 'overflow_knockback_multiplier']
        
        for child in _node:
            tag = child.tag
            val = child.text
            
            #special cases
            if tag in float_type:
                _type = 'float'
            
            val = parseData(child, _type, None)
            armor_vars[tag] = val
            
        return modifyHitbox(armor_name,hurtbox,armor_vars)
