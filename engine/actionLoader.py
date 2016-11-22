import engine.action as action
import engine.baseActions as baseActions
import xml.etree.ElementTree as ElementTree
import engine.subaction as subaction
import engine.action as action
import settingsManager
import xml.dom.minidom as minidom
import os
import traceback
from ast import literal_eval as make_tuple

class ActionLoader():
    def __init__(self, _baseDir, _actions):
        self.actions_xml_data = os.path.join(_baseDir,_actions)
        self.base_dir = _baseDir
        self.actions_xml_full = ElementTree.parse(self.actions_xml_data)
        self.actions_xml = self.actions_xml_full.getroot()
        print('actions_xml: ' + str(self.actions_xml))
    
    def hasAction(self, _actionName):
        if self.actions_xml.find(_actionName) is None:
            return False
        return True
    
    def getAllActions(self):
        ret = []
        for item in list(self.actions_xml):
            ret.append(item.tag)
        return ret
    
    def saveActions(self,_path=None):
        if not _path: _path = self.actions_xml_data
        self.actions_xml_full.write(_path)
    
    def getGlobalEvents(self):
        """ Grabs all event subactions at the top level and returns
        them into a dict."""
        retDict = dict()
        
        for eventNode in self.actions_xml.findall('event'):
            event = subaction.subactionFactory.buildFromXml('event',eventNode)
            retDict[eventNode.attrib['name']] = event
        return retDict
    
    """
    This function will take an action name, and a dynamicAction object,
    and rebuild the XML of that action, and then modify that in the actions_xml
    object of the fighter.
    """
    def modifyAction(self,_actionName,_newAction):
        action_xml = self.actions_xml.find(_actionName)
        if action_xml is not None:self.actions_xml.remove(action_xml)
        
        if _newAction is not None: #if it's none, we just remove it and don't put anything back
            elem = ElementTree.Element(_actionName)
            
            """
            This isn't working. Find a way to populate the base value from the object hierarchy.
            
            #Set the base if it's different from normal
            if _newAction.parent:
                #if it's base is different than its name, set base. Otherwise, no need.
                if not _newAction.parent.__name__ == _actionName:
                    baseElem = ElementTree.Element('base')
                    baseElem.text = _newAction.parent.__name__
                    elem.append(baseElem)
            """
            
            #action variables
            #length
            length_elem =  ElementTree.Element('length')
            length_elem.text = str(_newAction.last_frame)
            elem.append(length_elem)
            #sprite_name
            s_name_elem =  ElementTree.Element('sprite')
            s_name_elem.text = str(_newAction.sprite_name)
            elem.append(s_name_elem)
            #sprite_rate
            s_rate_elem =  ElementTree.Element('sprite_rate')
            s_rate_elem.text = str(_newAction.base_sprite_rate)
            elem.append(s_rate_elem)
            #loop
            loop_elem =  ElementTree.Element('loop')
            loop_elem.text = str(_newAction.loop)
            elem.append(loop_elem)
            
            if _newAction.default_vars:
                vars_elem = ElementTree.Element('vars')
                for tag,val in _newAction.default_vars.iteritems():
                    new_elem = ElementTree.Element(tag)
                    new_elem.attrib['type'] = type(val).__name__
                    new_elem.text = str(val)
                    vars_elem.append(new_elem)
                elem.append(vars_elem)
            
            if len(_newAction.set_up_actions) > 0:
                set_up_elem = ElementTree.Element('setUp')
                for subact in _newAction.set_up_actions:
                    set_up_elem.append(subact.getXmlElement())
                elem.append(set_up_elem)
            if len(_newAction.tear_down_actions) > 0:
                tear_down_elem = ElementTree.Element('tearDown')
                for subact in _newAction.tear_down_actions:
                    tear_down_elem.append(subact.getXmlElement())
                elem.append(tear_down_elem)
            if len(_newAction.state_transition_actions) > 0:
                transition_elem = ElementTree.Element('transitions')
                for subact in _newAction.state_transition_actions:
                    transition_elem.append(subact.getXmlElement())
                elem.append(transition_elem)
            if len(_newAction.actions_on_clank) > 0:
                clank_elem = ElementTree.Element('onClank')
                for subact in _newAction.actions_on_clank:
                    clank_elem.append(subact.getXmlElement())
                elem.append(clank_elem)
            if len(_newAction.actions_on_prevail) > 0:
                prevail_elem = ElementTree.Element('onPrevail')
                for subact in _newAction.actions_on_prevail:
                    prevail_elem.append(subact.getXmlElement())
                elem.append(prevail_elem)
            if len(_newAction.actions_before_frame) > 0:
                before_elem = ElementTree.Element('frame')
                before_elem.attrib['number'] = 'before'
                for subact in _newAction.actions_before_frame:
                    before_elem.append(subact.getXmlElement())
                elem.append(before_elem)
            if len(_newAction.actions_after_frame) > 0:
                after_elem = ElementTree.Element('frame')
                after_elem.attrib['number'] = 'after'
                for subact in _newAction.actions_after_frame:
                    after_elem.append(subact.getXmlElement())
                elem.append(after_elem)
            if len(_newAction.actions_at_last_frame) > 0:
                last_elem = ElementTree.Element('frame')
                last_elem.attrib['number'] = 'last'
                for subact in _newAction.actions_at_last_frame:
                    last_elem.append(subact.getXmlElement())
                elem.append(last_elem)
            
            for i,frameList in enumerate(_newAction.actions_at_frame):
                if len(frameList) > 0:
                    frameElem = ElementTree.Element('frame')
                    frameElem.attrib['number'] = str(i)
                    for subact in frameList:
                        frameElem.append(subact.getXmlElement())
                    elem.append(frameElem)
            
            for event_name,event in _newAction.events.iteritems():
                if len(event) > 0:
                    event_elem = ElementTree.Element('Event')
                    event_elem.attrib['name'] = str(event_name)
                    for subact in event:
                        event_elem.append(subact.getXmlElement())
                    elem.append(event_elem)
                    
            rough_string = ElementTree.tostring(elem, 'utf-8')
            reparsed = minidom.parseString(rough_string)
            data = reparsed.toprettyxml(indent="\t")
            self.actions_xml.append(ElementTree.fromstring(data))
            
    def loadAction(self,_actionName):
        #Load the action XML
        action_xml = self.actions_xml.find(_actionName)
        print('loading action',action_xml,_actionName)
        #Check if it's a Python action
        if action_xml is not None and action_xml.find('loadCodeAction') is not None:
            file_name = action_xml.find('loadCodeAction').find('file').text
            action_name = action_xml.find('loadCodeAction').find('action').text
            new_action = settingsManager.importFromURI(os.path.join(self.base_dir,file_name), file_name)
            return getattr(new_action, action_name)()
        
        #Get the baseClass
        class_ = None
        if (action_xml is not None) and (action_xml.find('base') is not None):
            if hasattr(baseActions, action_xml.find('base').text): 
                class_ = getattr(baseActions, action_xml.find('base').text)
        else:
            if hasattr(baseActions, _actionName):
                class_ = getattr(baseActions,_actionName)
        
        if class_: base = class_
        else: base = action.Action
        if action_xml is None:
            return base()
        
        #Get the action variables
        length = int(self.loadNodeWithDefault(action_xml, 'length', 1))
        starting_frame = int(self.loadNodeWithDefault(action_xml, 'starting_frame', 0))
        sprite_name = self.loadNodeWithDefault(action_xml, 'sprite', None)
        sprite_rate = int(self.loadNodeWithDefault(action_xml, 'sprite_rate', 1))
        loop = self.loadNodeWithDefault(action_xml, 'loop', False) == 'True'
        
        action_vars = {}
        if action_xml.find('vars') is not None:
            for var in action_xml.find('vars'):
                t = var.attrib['type'] if var.attrib.has_key('type') else None
                if t and t == 'int':
                    action_vars[var.tag] = int(var.text)
                elif t and t == 'float':
                    action_vars[var.tag] = float(var.text)
                elif t and t == 'bool':
                    action_vars[var.tag] = (var.text == 'True')
                elif t and t == 'tuple':
                    action_vars[var.tag] = make_tuple(var.text)
                else: action_vars[var.tag] = var.text
                
        #Load the SetUp subactions
        set_up_actions = []
        if action_xml.find('setUp') is not None:
            for subact in action_xml.find('setUp'):
                print('loading setup actions',subaction.subactionFactory, subact, subact.tag)
                if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                    set_up_actions.append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
                    
        #Load the tearDown subactions
        tear_down_actions = []
        if action_xml.find('tearDown') is not None:
            for subact in action_xml.find('tearDown'):
                if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                    tear_down_actions.append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
        
        #Load the stateTransition subactions
        state_transition_actions = []
        if action_xml.find('transitions') is not None:
            for subact in action_xml.find('transitions'):
                if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                    state_transition_actions.append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
        
        actions_on_clank = []
        if action_xml.find('onClank') is not None:
            for subact in action_xml.find('onClank'):
                if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                    actions_on_clank.append(subaction.subactionFactory.buildFromXml(subact.tag,subact))

        actions_on_prevail = []
        if action_xml.find('onPrevail') is not None:
            for subact in action_xml.find('onPrevail'):
                if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                    actions_on_prevail.append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
        
        #Load all of the frames
        frames = action_xml.findall('frame')
        subactions_before_frame = []
        subactions_after_frame = []
        subactions_at_last_frame = []
        
        for frame in frames:
            if frame.attrib['number'] == 'before':
                for subact in frame:
                    if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                        subactions_before_frame.append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
                frames.remove(frame)
            if frame.attrib['number'] == 'after':
                for subact in frame:
                    if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                        subactions_after_frame.append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
                frames.remove(frame)
            if frame.attrib['number'] == 'last':
                for subact in frame:
                    if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                        subactions_at_last_frame.append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
                frames.remove(frame)

        subactions_at_frame = []            
                        
        #Iterate through every frame possible (not just the ones defined)
        for frame_number in range(0,length+1):
            sublist = []
            if frames:
                for frame in frames:
                    if frame.attrib['number'] == str(frame_number): #If this frame matches the number we're on
                        for subact in frame:
                            if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                                sublist.append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
                                
                        frames.remove(frame) #Done with this one
                         
            subactions_at_frame.append(sublist) #Put the list in, whether it's empty or not

        #Interpret frame ranges
        for frame in frames:
            if "," in frame.attrib['number'] and frame.attrib['number'].replace(",","").replace(" ","").isdigit():
                for subact in frame:
                    if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                        for frame_num in make_tuple(frame.attrib['number']):
                            subactions_at_frame[frame_num].append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
                frames.remove(frame)

        for frame in frames:
            if "-" in frame.attrib['number'] and frame.attrib['number'].replace("-","").replace(" ","").isdigit():
                ends = frame.attrib['number'].split("-")
                for subact in frame:
                    if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                        for frame_num in range(int(ends[0]), int(ends[1])+1):
                            subactions_at_frame[frame_num].append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
                frames.remove(frame)
                    
        conditional_actions = dict()
        conds = action_xml.findall('conditional')
        for cond in conds:
            conditional_list = []
            for subact in cond:
                if subaction.subactionFactory.subaction_dict.has_key(subact.tag): #Subactions string to class dict
                    conditional_list.append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
            conditional_actions[cond.attrib['name']] = conditional_list
        
        event_actions = dict()
        events = action_xml.findall('event')
        #Because we're merging events and conditionals, this checks for either.
        events.extend(action_xml.findall('conditional'))
        for event in events:
            event_list = []
            for subact in event:
                if subaction.subactionFactory.subaction_dict.has_key(subact.tag):
                    event_list.append(subaction.subactionFactory.buildFromXml(subact.tag,subact))
            event_actions[event.attrib['name']] = event_list
            
        #Create and populate the Dynamic Action
        dyn_action = base()
        dyn_action.frame = starting_frame
        dyn_action.last_frame = length
        dyn_action.name = _actionName
        dyn_action.actions_before_frame = subactions_before_frame
        dyn_action.actions_at_frame = subactions_at_frame
        dyn_action.actions_after_frame = subactions_after_frame
        dyn_action.actions_at_last_frame = subactions_at_last_frame
        dyn_action.state_transition_actions = state_transition_actions
        dyn_action.set_up_actions = set_up_actions
        dyn_action.tear_down_actions = tear_down_actions
        dyn_action.actions_on_clank = actions_on_clank
        dyn_action.actions_on_prevail = actions_on_prevail
        dyn_action.events = event_actions
        if sprite_name: dyn_action.sprite_name = sprite_name
        if sprite_rate: dyn_action.base_sprite_rate = sprite_rate
        dyn_action.loop = loop
        
        dyn_action.default_vars = action_vars
        for key,val in action_vars.iteritems():
            setattr(dyn_action,key,val)
        
        return dyn_action
    
    @staticmethod
    def loadNodeWithDefault(_node,_subnode,_default):
        if _node is not None:
            if _node.find(_subnode) is not None:
                return _node.find(_subnode).text
            else:
                return _default
        else:
            return _default
