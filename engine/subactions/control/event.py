from engine.subaction import *

class Event(SubAction):
    subact_group = 'Control'
    
    def __init__(self,_eventSubactions):
        SubAction.__init__(self)
        self.event_subactions = _eventSubactions
    
    def execute(self, _action, _actor):
        SubAction.execute(self, _action, _actor)
        for subact in self.event_subactions:
            subact.execute(_action,_actor)
    
    def getPropertiesPanel(self, _root):
        return None
                    
    def getDisplayName(self):
        return ''
    
    def getXmlElement(self):
        elem = ElementTree.Element('Event')
        for subact in self.event_subactions:
            elem.append(subact.getXmlElement())
        return elem
    
    @staticmethod
    def customBuildFromXml(_node):
        event_actions = []
        for subact in _node:
            if subact.tag in subactionFactory.subaction_dict: 
                event_actions.append(subactionFactory.buildFromXml(subact.tag,subact))
        return Event(event_actions)
