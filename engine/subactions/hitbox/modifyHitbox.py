from engine.subaction import *

# Change the properties of an existing hitbox, such as position, or power
class modifyHitbox(SubAction):
    subact_group = 'Hitbox'
    
    def __init__(self,_hitboxName='',_hitboxVars={}):
        SubAction.__init__(self)
        self.hitbox_name = _hitboxName
        self.hitbox_vars = _hitboxVars
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.hitbox_name in _action.hitboxes:
            hitbox = _action.hitboxes[self.hitbox_name]
            if hitbox:
                for name,value in self.hitbox_vars.items():
                    if hasattr(hitbox, name):
                        if isinstance(value, VarData) or isinstance(value, FuncData) or isinstance(value, EvalData):
                            setattr(hitbox, name, value.unpack(_action,_actor))
                            if name in hitbox.variable_dict:
                                hitbox.variable_dict[name] = value.unpack(_action, _actor)
                        else: 
                            setattr(hitbox, name, value)
                            if name in hitbox.variable_dict:
                                hitbox.variable_dict[name] = value
        
    def getDisplayName(self):
        return 'Modify Hitbox: ' + str(self.hitbox_name)
    
    def getPropertiesPanel(self, _root):
        return subactionSelector.ModifyHitboxProperties(_root,self,newHitbox=False)
        
    def getXmlElement(self):
        elem = ElementTree.Element('modifyHitbox')
        elem.attrib['name'] = self.hitbox_name
        for tag,value in self.hitbox_vars.items():
            new_elem = ElementTree.Element(tag)
            new_elem.text = str(value)
            elem.append(new_elem)
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        hitbox_name = _node.attrib['name']
        hitbox_vars = {}
        
        tuple_type = ['center','size','color']
        float_type = ['damage','base_knockback','knockback_growth','hitsun','damageMultiplier','velocityMultiplier',
                     'weightInfluence','shieldMultiplier','priorityDiff','charge_damage','charge_base_knockback','charge_knockback_growth',
                     'x_bias','y_bias','x_multiplier','y_multiplier','hitlag_multiplier']
        int_type = ['trajectory','hp','transcendence','base_hitstun','x_offset','y_offset','width','height']
        boolean_type = ['ignore_shields', 'ignore_armor']
        
        for child in _node:
            tag = child.tag
            val = child.text
            
            #special cases
            if tag in tuple_type:
                _type = 'tuple'
            elif tag in float_type:
                _type = 'float'
            elif tag in int_type:
                _type = 'int'
            elif tag in boolean_type:
                _type = 'bool'
            
            val = parseData(child, _type, None)
            hitbox_vars[tag] = val
            
        return modifyHitbox(hitbox_name,hitbox_vars)
