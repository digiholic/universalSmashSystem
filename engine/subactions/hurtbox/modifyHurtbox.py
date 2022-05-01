from engine.subaction import *

# Change the properties of an existing hurtbox
class modifyHurtbox(SubAction):
    subact_group = 'Hurtbox'
    
    def __init__(self,_hurtboxName='',_hurtboxVars={}):
        SubAction.__init__(self)
        self.hurtbox_name = _hurtboxName
        self.hurtbox_vars = _hurtboxVars
        
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        if self.hurtbox_name in _action.hurtboxes:
            hurtbox = _action.hurtboxes[self.hurtbox_name]
            if hurtbox:
                for name,value in self.hurtbox_vars.items():
                    if hasattr(hurtbox, name):
                        if isinstance(value, VarData) or isinstance(value, FuncData) or isinstance(value, EvalData):
                            setattr(hurtbox, name, value.unpack(_action,_actor))
                        else: setattr(hurtbox, name, value)
        
    def getDisplayName(self):
        return 'Modify Hurtbox: ' + str(self.hurtbox_name)
    
    def getPropertiesPanel(self, _root):
        #return subactionSelector.ModifyHurtboxProperties(_root,self,newHurtbox=False)
        return None
        
    def getXmlElement(self):
        elem = ElementTree.Element('modifyHurtbox')
        elem.attrib['name'] = self.hurtbox_name
        for tag,value in self.hurtbox_vars.items():
            new_elem = ElementTree.Element(tag)
            new_elem.text = str(value)
            elem.append(new_elem)
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        hurtbox_name = loadNodeWithDefault(_node, 'name', 'auto')
        hurtbox_vars = {}
        
        tuple_type = ['center','size','fix_size_multiplier','self_size_multiplier']
        
        for child in _node:
            tag = child.tag
            val = child.text
            
            #special cases
            if tag in tuple_type:
                _type = 'tuple'
            else: _type = 'string'
            val = parseData(child, _type, None)
            hurtbox_vars[tag] = val
            
        return modifyHurtbox(hurtbox_name,hurtbox_vars)
