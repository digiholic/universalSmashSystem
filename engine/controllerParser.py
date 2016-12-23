import xml.etree.ElementTree as ElementTree
import engine.controller as controller
from ast import literal_eval as make_tuple
            
def loadControls(_controllerXML):
    #Load the action XML
    control_xml = _controllerXML
    print('loading controls',control_xml)
        
    windows = {}
    if control_xml.find('windows') is not None:
        for var in control_xml.find('windows'):
            t = var.attrib['type'] if var.attrib.has_key('type') else None
            if t and t == 'int':
                windows[var.tag] = int(var.text)
            elif t and t == 'float':
                windows[var.tag] = float(var.text)
            elif t and t == 'bool':
                windows[var.tag] = (var.text == 'True')
            elif t and t == 'tuple':
                windows[var.tag] = make_tuple(var.text)
            else: windows[var.tag] = var.text
    
    #Load the stateTransition subactions
    inputs = {}
    if control_xml.find('inputs') is not None:
        for input_case in control_xml.find('inputs'):
            entry_dict = {}

            #Parse decays
            decay_dict = {}
            if control_xml.find('decay') is not None: 
                for val in control_xml.iter():
                    decay_dict[val.tag] = val.text
            entry_dict['decay'] = decay_dict

            #Parse threshold crossovers
            for val in control_xml.iter():
                try:
                    tag_num = int(val.tag)
                    entry_dict[tag_num] = constructRangeTree(val)
                except ValueError: 
                    try:
                        tag_num = float(val.tag)
                        entry_dict[tag_num] = constructRangeTree(val)
                    except ValueError: 
                        pass

            inputs[input_case.tag] = entry_dict
            
    return controller.physicalController(inputs, windows)

def constructRangeTree(_element):
    if len(list(_element.findall("condition"))) == 0:
        return_dict = dict()
        for val in _element.iter():
            try: return_dict[val.tag] = int(val.text)
            except ValueError:
                try: return_dict[val.tag] = float(val.text)
                except ValueError: 
                    try: return_dict[val.tag] = make_tuple(val.text)
                    except ValueError: pass
        return return_dict
    else:
        return_tree = controller.RangeCheckTree(_element.attrib['input'], _element.attrib['default'])
        for val in _element.iter():
            return_tree[val.tag] = constructRangeTree(val)
        return return_tree
