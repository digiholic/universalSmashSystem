import engine.action as action
import engine.baseActions as baseActions
import xml.etree.ElementTree as ElementTree
import engine.subaction as subaction
import engine.action as action
import settingsManager
import os

class ActionLoader():
    def __init__(self,baseDir, actions):
        actionsXMLdata = os.path.join(baseDir,actions)
        self.baseDir = baseDir
        self.actionsXML = ElementTree.parse(actionsXMLdata).getroot()
        print('actionsXML: ' + str(self.actionsXML))
    
    def hasAction(self, actionName):
        if self.actionsXML.find(actionName) is None:
            return False
        return True
    
    def getAllActions(self):
        ret = []
        for item in list(self.actionsXML):
            ret.append(item.tag)
        return ret
            
    def loadAction(self,actionName):
        #Load the action XML
        actionXML = self.actionsXML.find(actionName)
        
        #Check if it's a Python action
        if actionXML is not None and actionXML.find('loadCodeAction') is not None:
            fileName = actionXML.find('loadCodeAction').find('file').text
            actionName = actionXML.find('loadCodeAction').find('action').text
            newaction = settingsManager.importFromURI(os.path.join(self.baseDir,fileName), fileName)
            return getattr(newaction, actionName)()
        
        
        #Get the baseClass
        class_ = None
        if (actionXML is not None) and (actionXML.find('base') is not None):
            if hasattr(baseActions, actionXML.find('base')): 
                class_ = getattr(baseActions, actionXML.find('base'))
        else:
            if hasattr(baseActions, actionName):
                class_ = getattr(baseActions,actionName)
        
        if class_: base = class_
        else: base = action.Action
        if actionXML is None:
            return base()
        
        #Get the action variables
        length = int(self.loadNodeWithDefault(actionXML, 'length', 1))
        startingFrame = int(self.loadNodeWithDefault(actionXML, 'startingFrame', 0))
        spriteName = self.loadNodeWithDefault(actionXML, 'sprite', None)
        spriteRate = int(self.loadNodeWithDefault(actionXML, 'spriteRate', 1))
        loop = bool(self.loadNodeWithDefault(actionXML, 'loop', False))
        
        actionvars = {}
        if actionXML.find('vars') is not None:
            for var in actionXML.find('vars'):
                t = var.attrib['type'] if var.attrib.has_key('type') else None
                if t and t == 'int':
                    actionvars[var.tag] = int(var.text)
                elif t and t == 'float':
                    actionvars[var.tag] = float(var.text)
                else: actionvars[var.tag] = var.text
        
        #Load the SetUp subactions
        setUpActions = []
        if actionXML.find('setUp') is not None:
            for subact in actionXML.find('setUp'):
                if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                    setUpActions.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
                    
        #Load the tearDown subactions
        tearDownActions = []
        if actionXML.find('tearDown') is not None:
            for subact in actionXML.find('tearDown'):
                if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                    tearDownActions.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
        
        #Load the stateTransition subactions
        stateTransitionActions = []
        if actionXML.find('transitions') is not None:
            for subact in actionXML.find('transitions'):
                if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                    stateTransitionActions.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
        
        #Load all of the frames
        frames = actionXML.findall('frame')
        subactionsBeforeFrame = []
        subactionsAfterFrame = []
        subactionsAtLastFrame = []
        
        for frame in frames:
            if frame.attrib['number'] == 'before':
                for subact in frame:
                    if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                        subactionsBeforeFrame.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
                frames.remove(frame)
            if frame.attrib['number'] == 'after':
                for subact in frame:
                    if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                        subactionsAfterFrame.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
                frames.remove(frame)
            if frame.attrib['number'] == 'last':
                for subact in frame:
                    if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                        subactionsAtLastFrame.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
                frames.remove(frame)
            
        subactionsAtFrame = []
                        
        #Iterate through every frame possible (not just the ones defined)
        for frameNo in range(0,length+1):
            sublist = []
            if frames:
                for frame in frames:
                    if frame.attrib['number'] == str(frameNo): #If this frame matches the number we're on
                        for subact in frame:
                            if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                                sublist.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
                                
                        frames.remove(frame) #Done with this one
                         
            subactionsAtFrame.append(sublist) #Put the list in, whether it's empty or not
        
        
        #Create and populate the Dynamic Action
        dynAction = action.DynamicAction(length, base, actionvars, startingFrame)
        dynAction.actionsBeforeFrame = subactionsBeforeFrame
        dynAction.actionsAtFrame = subactionsAtFrame
        dynAction.actionsAfterFrame = subactionsAfterFrame
        dynAction.actionsAtLastFrame = subactionsAtLastFrame
        dynAction.stateTransitionActions = stateTransitionActions
        dynAction.setUpActions = setUpActions
        dynAction.tearDownActions = tearDownActions
        if spriteName: dynAction.spriteName = spriteName
        if spriteRate: dynAction.spriteRate = spriteRate
        dynAction.loop = loop
        return dynAction
    
    @staticmethod
    def loadNodeWithDefault(node,subnode,default):
        if node is not None:
            if node.find(subnode) is not None:
                return node.find(subnode).text
            else:
                return default
        else:
            return default