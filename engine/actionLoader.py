import engine.action as action
import engine.baseActions as baseActions
import xml.etree.ElementTree as ElementTree
import engine.subaction as subaction
import engine.action as action

actionsXML = None

def loadAction(actionName):
    global actionsXML
    
    #Load the action XML
    actionXML = actionsXML.find(actionName)
    #Get the baseClass
    base = baseActions.nameToClass[actionName] if baseActions.nameToClass.has_key(actionName) else action.Action
    
    #Get the action variables
    length = int(actionXML.find('length').text) if actionXML.find('length') is not None else 0
    startingFrame = int(actionXML.find('startingFrame').text) if actionXML.find('startingFrame') is not None else 0
    vars = {}
    if actionXML.find('vars') is not None:
        for var in actionXML.find('vars'):
            t = var.attrib['type']
            if t and t == 'int':
                vars[var.tag] = int(var.text)
            elif t and t == 'float':
                vars[var.tag] = float(var.text)
            else: vars[var.tag] = var.text
    
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
    dynAction = action.DynamicAction(length, base, vars, startingFrame)
    dynAction.actionsBeforeFrame = subactionsBeforeFrame
    dynAction.actionsAtFrame = subactionsAtFrame
    dynAction.actionsAfterFrame = subactionsAfterFrame
    dynAction.actionsAtLastFrame = subactionsAtLastFrame
    dynAction.setUpActions = setUpActions
    dynAction.tearDownActions = tearDownActions
    return dynAction
    
class ActionLoader():
    def __init__(self,actionsXMLdata):
        global actionsXML
        actionsXML = ElementTree.parse(actionsXMLdata).getroot()
    
    def NeutralAction(self):
        return loadAction('NeutralAction')
        
    def Crouch(self):
        return loadAction('Crouch')
    
    def CrouchGetup(self):
        return loadAction('CrouchGetup')
    
    def Stop(self):
        return loadAction('Stop')
    
    def RunStop(self):
        return loadAction('RunStop')
    
    def Fall(self):
        return loadAction('Fall')
    
    """
    def Land(self):
        #TODO rework landing, does not work in current system
        pass
    """
    class Land(baseActions.Land):
        def __init__(self):
            baseActions.Land.__init__(self)
            
    def Jump(self):
        return loadAction('Jump')
    
    def AirJump(self):
        return loadAction('AirJump')
    
    def Helpless(self):
        return loadAction('Helpless')
    
    def PlatformDrop(self):
        return loadAction('PlatformDrop')
    
    def Move(self):
        return loadAction('Move')
        
    def Dash(self):
        return loadAction('Dash')
    
    def Run(self):
        return loadAction('Run')
    
    def Pivot(self):
        return loadAction('Pivot')
    
    def RunPivot(self):
        return loadAction('RunPivot')
    
    def Grabbing(self):
        return loadAction('Grabbing')
    
    def Getup(self):
        return loadAction('Getup')
    
    def PreShield(self):
        return loadAction('PreShield')
    
    def Shield(self):
        return loadAction('Shield')
    
    def ForwardRoll(self):
        return loadAction('ForwardRoll')
    
    def BackwardRoll(self):
        return loadAction('BackwardRoll')
    
    def SpotDodge(self):
        return loadAction('SpotDodge')
    
    def AirDodge(self):
        return loadAction('AirDodge')
    
    ###############################################
    #           UNIMPLEMENTED ACTIONS             #
    ###############################################           
    class HitStun(baseActions.HitStun):
        def __init__(self,hitstun,direction,hitstop):
            baseActions.HitStun.__init__(self, hitstun, direction,hitstop)
            
    class TryTech(baseActions.TryTech):
        def __init__(self,hitstun,direction,hitstop):
            baseActions.TryTech.__init__(self, hitstun, direction, hitstop)
    
    class HelplessLand(baseActions.HelplessLand):
        def __init__(self):
            baseActions.HelplessLand.__init__(self)
    
    class Trip(baseActions.Trip):
        def __init__(self, length, direction):
            baseActions.Trip.__init__(self, length, direction)
    
    class GetupAttack(action.Action):
        def __init__(self):
            action.Action.__init__(self)
            
    class ShieldStun(baseActions.ShieldStun):
        def __init__(self, length):
            baseActions.ShieldStun.__init__(self, length)
    
    class Stunned(baseActions.Stunned):
        def __init__(self, length):
            baseActions.Stunned.__init__(self, length)
            
    class TechDodge(baseActions.TechDodge):
        def __init__(self):
            baseActions.TechDodge.__init__(self)
    
    class Trapped(baseActions.Trapped):
        def __init__(self, length):
            baseActions.Trapped.__init__(self, length)
    
    class Grabbed(baseActions.Grabbed):
        def __init__(self,height):
            baseActions.Grabbed.__init__(self, height)
    
    class Release(baseActions.Release):
        def __init__(self,height):
            baseActions.Release.__init__(self)
    
    class Released(baseActions.Released):
        def __init__(self):
            baseActions.Released.__init__(self)
    
    class LedgeGrab(baseActions.LedgeGrab):
        def __init__(self,ledge):
            baseActions.LedgeGrab.__init__(self, ledge)
    
    class LedgeGetup(baseActions.LedgeGetup):
        def __init__(self):
            baseActions.LedgeGetup.__init__(self)
    
    class LedgeAttack(baseActions.LedgeGetup):
        def __init__(self):
            baseActions.LedgeGetup.__init__(self)
    
    class LedgeRoll(baseActions.LedgeGetup):
        def __init__(self):
            baseActions.LedgeGetup.__init__(self)
            
    class NeutralGroundSpecial(action.Action):
        def __init__(self):
            action.Action.__init__(self)
        
    class NeutralAirSpecial(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class ForwardSpecial(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class DownSpecial(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class UpSpecial(action.Action):
        def __init__(self):
            action.Action.__init__(self)
            
    class NeutralAttack(action.Action):
        def __init__(self):
            action.Action.__init__(self)
        
    class UpAttack(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class UpSmash(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class DashAttack(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class DownAttack(action.Action):
        def __init__(self):
            action.Action.__init__(self)
        
    class DownSmash(action.Action):
        def __init__(self):
            action.Action.__init__(self)
            
    class ForwardAttack(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class ForwardSmash(action.Action):
        def __init__(self):
            action.Action.__init__(self)
            self.chargeLevel = 0
    
    class NeutralAir(action.Action):
        def __init__(self):
            action.Action.__init__(self)

    class BackAir(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class ForwardAir(action.Action):
        def __init__(self):
            action.Action.__init__(self)
            
    class DownAir(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class UpAir(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class GroundGrab(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class DashGrab(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class Pummel(baseActions.BaseGrabbing):
        def __init__(self):
            baseActions.BaseGrabbing.__init__(self)
            
    class ForwardThrow(baseActions.BaseGrabbing):
        def __init__(self):
            baseActions.BaseGrabbing.__init__(self)
    
    class DownThrow(baseActions.BaseGrabbing):
        def __init__(self):
            baseActions.BaseGrabbing.__init__(self)
    
    class UpThrow(baseActions.BaseGrabbing):
        def __init__(self):
            baseActions.BaseGrabbing.__init__(self)
    
    class BackThrow(baseActions.BaseGrabbing):
        def __init__(self):
            baseActions.BaseGrabbing.__init__(self)