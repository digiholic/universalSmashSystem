import engine.action as action
import engine.baseActions as baseActions
import xml.etree.ElementTree as ElementTree
import engine.subaction as subaction
import engine.action as action
import settingsManager
import xml.dom.minidom as minidom
import os

class ActionLoader():
    def __init__(self, baseDir, actions):
        self.actionsXMLdata = os.path.join(baseDir,actions)
        self.baseDir = baseDir
        self.actionsXMLFull = ElementTree.parse(self.actionsXMLdata)
        self.actionsXML = self.actionsXMLFull.getroot()
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
    
    def saveActions(self,path=None):
        if not path: path = self.actionsXMLdata
        self.actionsXMLFull.write(path)
    
    """
    This function will take an action name, and a dynamicAction object,
    and rebuild the XML of that action, and then modify that in the actionsXML
    object of the fighter.
    """
    def modifyAction(self,actionName,newAction):
        actionXML = self.actionsXML.find(actionName)
        if actionXML is not None:self.actionsXML.remove(actionXML)
        
        elem = ElementTree.Element(actionName)
        
        #Set the base if it's different from normal
        if newAction.parent:
            #if it's base is different than its name, set base. Otherwise, no need.
            if not newAction.parent.__name__ == actionName:
                baseElem = ElementTree.Element('base')
                baseElem.text = newAction.parent.__name__
                elem.append(baseElem)
        
        #action variables
        #length
        lengthElem =  ElementTree.Element('length')
        lengthElem.text = str(newAction.lastFrame)
        elem.append(lengthElem)
        #spriteName
        sNameElem =  ElementTree.Element('sprite')
        sNameElem.text = str(newAction.spriteName)
        elem.append(sNameElem)
        #spriteRate
        sRateElem =  ElementTree.Element('spriteRate')
        sRateElem.text = str(newAction.baseSpriteRate)
        elem.append(sRateElem)
        #loop
        loopElem =  ElementTree.Element('loop')
        loopElem.text = str(newAction.loop)
        elem.append(loopElem)
        
        if newAction.defaultVars:
            varsElem = ElementTree.Element('vars')
            for tag,val in newAction.defaultVars.iteritems():
                newElem = ElementTree.Element(tag)
                newElem.attrib['type'] = type(val).__name__
                newElem.text = str(val)
                varsElem.append(newElem)
            elem.append(varsElem)
        
        if len(newAction.setUpActions) > 0:
            setUpElem = ElementTree.Element('setUp')
            for subact in newAction.setUpActions:
                setUpElem.append(subact.getXmlElement())
            elem.append(setUpElem)
        if len(newAction.tearDownActions) > 0:
            tearDownElem = ElementTree.Element('tearDown')
            for subact in newAction.tearDownActions:
                tearDownElem.append(subact.getXmlElement())
            elem.append(tearDownElem)
        if len(newAction.stateTransitionActions) > 0:
            transitionElem = ElementTree.Element('transitions')
            for subact in newAction.stateTransitionActions:
                transitionElem.append(subact.getXmlElement())
            elem.append(transitionElem)
        if len(newAction.actionsOnClank) > 0:
            clankElem = ElementTree.Element('onClank')
            for subact in newAction.actionsOnClank:
                clankElem.append(subact.getXmlElement())
            elem.append(clankElem)
        if len(newAction.actionsBeforeFrame) > 0:
            beforeElem = ElementTree.Element('frame')
            beforeElem.attrib['number'] = 'before'
            for subact in newAction.actionsBeforeFrame:
                beforeElem.append(subact.getXmlElement())
            elem.append(beforeElem)
        if len(newAction.actionsAfterFrame) > 0:
            afterElem = ElementTree.Element('frame')
            afterElem.attrib['number'] = 'after'
            for subact in newAction.actionsAfterFrame:
                afterElem.append(subact.getXmlElement())
            elem.append(afterElem)
        if len(newAction.actionsAtLastFrame) > 0:
            lastElem = ElementTree.Element('frame')
            lastElem.attrib['number'] = 'last'
            for subact in newAction.actionsAtLastFrame:
                lastElem.append(subact.getXmlElement())
            elem.append(lastElem)
        
        for i,frameList in enumerate(newAction.actionsAtFrame):
            if len(frameList) > 0:
                frameElem = ElementTree.Element('frame')
                frameElem.attrib['number'] = str(i)
                for subact in frameList:
                    frameElem.append(subact.getXmlElement())
                elem.append(frameElem)
        
        for cond,condList in newAction.conditionalActions.iteritems():
            if len(condList) > 0:
                condElem = ElementTree.Element('conditional')
                condElem.attrib['name'] = str(cond)
                for subact in condList:
                    condElem.append(subact.getXmlElement())
                elem.append(condElem)
        
        rough_string = ElementTree.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        data = reparsed.toprettyxml(indent="\t")
        self.actionsXML.append(ElementTree.fromstring(data))
            
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
            if hasattr(baseActions, actionXML.find('base').text): 
                class_ = getattr(baseActions, actionXML.find('base').text)
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
        
        actionsOnClank = []
        if actionXML.find('onClank') is not None:
            for subact in actionXML.find('onClank'):
                if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                    actionsOnClank.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
        
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
        
        conditionalActions = dict()
        conds = actionXML.findall('conditional')
        for cond in conds:
            conditionalList = []
            for subact in cond:
                if subaction.subActionDict.has_key(subact.tag): #Subactions string to class dict
                    conditionalList.append(subaction.subActionDict[subact.tag].buildFromXml(subact))
            conditionalActions[cond.attrib['name']] = conditionalList
         
        #Create and populate the Dynamic Action
        dynAction = action.DynamicAction(length, base, actionvars, startingFrame)
        dynAction.actionsBeforeFrame = subactionsBeforeFrame
        dynAction.actionsAtFrame = subactionsAtFrame
        dynAction.actionsAfterFrame = subactionsAfterFrame
        dynAction.actionsAtLastFrame = subactionsAtLastFrame
        dynAction.stateTransitionActions = stateTransitionActions
        dynAction.setUpActions = setUpActions
        dynAction.tearDownActions = tearDownActions
        dynAction.actionsOnClank = actionsOnClank
        dynAction.conditionalActions = conditionalActions
        if spriteName: dynAction.spriteName = spriteName
        if spriteRate: dynAction.baseSpriteRate = spriteRate
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