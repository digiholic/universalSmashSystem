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
                for val in control_xml.find('decay').iter():
                    decay_dict[float(val.tag)] = constructRangeTree(val)
            entry_dict['decay'] = decay_dict

            #Parse threshold crossovers
            for val in control_xml.findall('threshold'):
                if 'value' in val.attrib:
                    entry_dict[float(val.attrib['value'])] = constructRangeTree(val)
                else: entry_dict[None] = constructRangeTree(val)

            inputs[input_case.tag] = entry_dict
            
    return controller.physicalController(inputs, windows)

def constructRangeTree(_element):
    default_dict = dict()
    for val in _element.findall('key'):
        if 'name' in val.attrib:
            try: default_dict[float(val.attrib['name'])] = float(val.text)
            except ValueError: default_dict[val.attrib['name']] = float(val.text)
        else:
            default_dict[None] = float(val.text)
    if 'input' in _element.attrib:
        return_tree = controller.RangeCheckTree(_element.attrib['input'], default_dict)
    else:
        return_tree = controller.RangeCheckTree(None, default_dict)
    for val in _element.findall('condition'):
        for case in val.findall('threshold'):
            if 'value' in case.attrib:
                return_tree.addEntry(case.attrib['value'], constructRangeTree(case))
            else:
                return_tree.addEntry(None, constructRangeTree(case))
    return return_tree









