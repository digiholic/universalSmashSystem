from engine.subaction import *

# Create a new hurtbox
class createHurtbox(SubAction):
    subact_group = 'Hurtbox'
    
    def __init__(self, _name='', _variables={}):
        SubAction.__init__(self)
        self.hurtbox_name = _name
        self.hurtbox_vars = _variables
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.hurtbox_name == '': return 
        
        hurtbox = engine.hurtbox.Hurtbox(_actor,self.hurtbox_vars)
        _action.hurtboxes[self.hurtbox_name] = hurtbox
        _actor.activateHurtbox(_action.hurtboxes[self.hurtbox_name])
    
    def getDisplayName(self):
        return 'Create New Hurtbox: ' + self.hurtbox_name
    
    def getPropertiesPanel(self, _root):
        #return subactionSelector.ModifyHurtboxProperties(_root,self,newHurtbox=True)
        return None
       
    def getXmlElement(self):
        elem = ElementTree.Element('createHurbox')
        name_elem = ElementTree.Element('name')
        name_elem.text = self.hurtbox_name
        elem.append(name_elem)
        for tag,value in self.hurtbox_vars.items():
            new_elem = ElementTree.Element(tag)
            new_elem.text = str(value)
            elem.append(new_elem)
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        #build the variable dict
        variables = {}
        #these lists let the code know which keys should be which types.
        tuple_type = ['center','size','fix_size_multiplier','self_size_multiplier']
            
        for child in _node:
            tag = child.tag
            val = child.text

            if tag == 'name':
                name = val
            elif tag in tuple_type:
                variables[tag] = make_tuple(val)
            else:
                print('string variable',tag,val)
                variables[tag] = val
            
        return createHurtbox(name, variables)
