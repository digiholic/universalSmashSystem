from engine.subaction import *

class createArmor(SubAction):
    subact_group = 'Armor'
    
    def __init__(self, _name='', _armorType='hyper', _hurtbox='', _variables={}):
        SubAction.__init__(self)
        
        self.armor_name = _name
        self.armor_type = _armorType if _armorType is not None else "hyper"
        self.hurtbox = _hurtbox
        self.armor_vars = _variables
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)

        if self.armor_name == '': return
        
        #Create the armor of the right type    
        if self.armor_type == "hyper":
            armor = engine.hurtbox.HyperArmor(_actor,self.armor_vars)
        elif self.armor_type == "super":
            armor = engine.hurtbox.SuperArmor(_actor,self.armor_vars)
        elif self.armor_type == "heavy":
            armor = engine.hurtbox.HeavyArmor(_actor,self.armor_vars)
        elif self.armor_type == "invulnerable":
            armor = engine.hurtbox.Invulnerability(_actor,self.armor_vars)
        elif self.armor_type == "intangible":
            armor = engine.hurtbox.Intangibility(_actor,self.armor_vars)
        elif self.armor_type == "cumulative":
            armor = engine.hurtbox.CumulativeArmor(_actor,self.armor_vars)
        elif self.armor_type == "grabImmunity":
            armor = engine.hurtbox.GrabImmunity(_actor,self.armor_vars)
        elif self.armor_type == "crouchCancel":
            armor = engine.hurtbox.CrouchCancel(_actor,self.armor_vars)
            
        if self.hurtbox is not '' and _action is not None:
            _action.hurtbox[self.hurtbox_name].armor[self.armor_name] = armor
        else:
            _actor.armor[self.armor_name] = armor
    
    def getDisplayName(self):
        return 'Add ' + self.armor_type + ' armor to ' + self.hurtbox if self.hurtbox is not '' else 'the fighter'
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyArmorProperties(_root,self,newArmor=True)
       
    def getXmlElement(self):
        elem = ElementTree.Element('createArmor')
        elem.attrib['type'] = self.armor_type
        name_elem = ElementTree.Element('name')
        name_elem.text = self.armor_name
        elem.append(name_elem)
        hurtbox_elem = ElementTree.Element('hurtbox')
        hurtbox_elem.text = self.hurtbox
        elem.append(hurtbox_elem)
        for tag,value in self.armor_vars.iteritems():
            new_elem = ElementTree.Element(tag)
            new_elem.text = str(value)
            elem.append(new_elem)
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        #mandatory fields
        armor_type = _node.attrib['type'] if _node.attrib.has_key('type') else "hyper"
        
        #build the variable dict
        variables = {}
        #these lists let the code know which keys should be which types.
        float_type = ['num_hits', 'damage_threshold', 'knockback_threshold', 'armor_damage_multiplier', 'armor_knockback_multiplier', 'overflow_damage_multiplier', 'overflow_knockback_multiplier']
            
        for child in _node:
            tag = child.tag
            val = child.text
            
            owner_event = ''
            other_event = ''
            #special cases
            if tag == 'name':
                name = val
            elif tag == 'hurtbox':
                hurtbox = val
            elif tag in tuple_type:
                variables[tag] = make_tuple(val)
            elif tag in float_type:
                variables[tag] = float(val)
            elif tag in int_type:
                variables[tag] = int(val)
            else:
                variables[tag] = val
            
        return createArmor(name, armor_type, hurtbox, variables)
