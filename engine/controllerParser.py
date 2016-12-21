import xml.etree.ElementTree as ElementTree
import engine.controller as controller
import xml.dom.minidom as minidom
import os
from ast import literal_eval as make_tuple


class ControllerParser():
    def __init__(self, _baseDir, _controls):
        self.controller_xml_data = os.path.join(_baseDir,_controls)
        self.base_dir = _baseDir
        self.controller_xml_full = ElementTree.parse(self.controller_xml_data)
        self.controller_xml = self.controller_xml_full.getroot()
        print('controller_parse: ' + str(self.controller_xml))
    
    def hasControls(self, _controlName):
        if self.controller_xml.find(_controlName) is None:
            return False
        return True
    
    def getAllControls(self):
        ret = []
        for item in list(self.controller_xml):
            ret.append(item.tag)
        return ret
    
    def saveControls(self,_path=None):
        if not _path: _path = self.controller_xml_data
        self.controller_xml_full.write(_path)
        
    def modifyControls(self,_controlName,_newControl):
        control_xml = self.controller_xml.find(_controlName)
        if control_xml is not None:self.controller_xml.remove(control_xml)
        
        if _newControl is not None: #if it's none, we just remove it and don't put anything back
            elem = ElementTree.Element(_actionName)

            if _newControl.windows:
                window_elem = ElementTree.Element('windows')
                for tag,val in _newAction.windows.iteritems():
                    new_elem = ElementTree.Element(tag)
                    new_elem.attrib['type'] = type(val).__name__
                    new_elem.text = str(val)
                    window_elem.append(new_elem)
                elem.append(window_elem)

            #inputs
            if len(_newControl.inputs) > 0:
                input_elem = ElementTree.Element('inputs')
                for input_case in _newControl.inputs:
                    input_elem.append(input_case.getXmlElement())
                elem.append(input_elem)
                    
            rough_string = ElementTree.tostring(elem, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            data = reparsed.toprettyxml(indent="\t")
            self.controller_xml.append(ElementTree.fromstring(data))
            
    def loadControls(self,_controlName):
        #Load the action XML
        control_xml = self.controller_xml.find(_controlName)
        print('loading controls',control_xml,_controlName)
        
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
           
        #Create and populate the Dynamic Action
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
