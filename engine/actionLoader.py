import engine.action as action
import engine.baseActions as baseActions
import xml.etree.ElementTree as ElementTree
import engine.subaction as subaction
import engine.action as action

actionsXML = None

subActionDict = {
                 'changeSprite': subaction.changeFighterSprite,
                 'changeSubimage': subaction.changeFighterSubimage,
                 'setFrame': subaction.changeActionFrame
                 }

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
            vars[var.tag] = var.text
    
    #Load the SetUp subactions
    setUpActions = []
    if actionXML.find('setUp') is not None:
        for subact in actionXML.find('setUp'):
            if subActionDict.has_key(subact.tag): #Subactions string to class dict
                setUpActions.append(subActionDict[subact.tag].buildFromXml(subact))
                
    #Load the tearDown subactions
    tearDownActions = []
    if actionXML.find('tearDown') is not None:
        for subact in actionXML.find('tearDown'):
            if subActionDict.has_key(subact.tag): #Subactions string to class dict
                tearDownActions.append(subActionDict[subact.tag].buildFromXml(subact))
    
    #Load the stateTransition subactions
    stateTransitionActions = []
    if actionXML.find('transitions') is not None:
        for subact in actionXML.find('transitions'):
            if subActionDict.has_key(subact.tag): #Subactions string to class dict
                stateTransitionActions.append(subActionDict[subact.tag].buildFromXml(subact))
    
    #Load all of the frames
    frames = actionXML.findall('frame')
    subactionsBeforeFrame = []
    subactionsAfterFrame = []
    subactionsAtLastFrame = []
    
    for frame in frames:
        if frame.attrib['number'] == 'before':
            for subact in frame:
                if subActionDict.has_key(subact.tag): #Subactions string to class dict
                    subactionsBeforeFrame.append(subActionDict[subact.tag].buildFromXml(subact))
            frames.remove(frame)
        if frame.attrib['number'] == 'after':
            for subact in frame:
                if subActionDict.has_key(subact.tag): #Subactions string to class dict
                    subactionsAfterFrame.append(subActionDict[subact.tag].buildFromXml(subact))
            frames.remove(frame)
        if frame.attrib['number'] == 'last':
            for subact in frame:
                if subActionDict.has_key(subact.tag): #Subactions string to class dict
                    subactionsAtLastFrame.append(subActionDict[subact.tag].buildFromXml(subact))
            frames.remove(frame)
        
    subactionsAtFrame = []
                    
    #Iterate through every frame possible (not just the ones defined)
    for frameNo in range(0,length+1):
        sublist = []
        if frames:
            for frame in frames:
                if frame.attrib['number'] == str(frameNo): #If this frame matches the number we're on
                    for subact in frame:
                        if subActionDict.has_key(subact.tag): #Subactions string to class dict
                            sublist.append(subActionDict[subact.tag].buildFromXml(subact))
                            
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
    
    class Move(baseActions.Move):
        def __init__(self,accel = True):
            baseActions.Move.__init__(self)

    class Dash(baseActions.Dash):
        def __init__(self,accel = True):
            baseActions.Dash.__init__(self)
            self.accel = accel
            
    class Run(baseActions.Run):
        def __init__(self):
            baseActions.Run.__init__(self)
                       
    class Pivot(baseActions.Pivot):
        def __init__(self):
            baseActions.Pivot.__init__(self)
    
    class RunPivot(baseActions.RunPivot):
        def __init__(self):
            baseActions.RunPivot.__init__(self)
    
    class Grabbing(baseActions.Grabbing):
        def __init__(self):
            baseActions.Grabbing.__init__(self)
            
    class Stop(baseActions.Stop):
        def __init__(self):
            baseActions.Stop.__init__(self)
    
    class RunStop(baseActions.RunStop):
        def __init__(self):
            baseActions.RunStop.__init__(self)
    
    class CrouchGetup(baseActions.CrouchGetup):
        def __init__(self):
            baseActions.CrouchGetup.__init__(self)
            
    class HitStun(baseActions.HitStun):
        def __init__(self,hitstun,direction,hitstop):
            baseActions.HitStun.__init__(self, hitstun, direction,hitstop)
            
    class TryTech(baseActions.TryTech):
        def __init__(self,hitstun,direction,hitstop):
            baseActions.TryTech.__init__(self, hitstun, direction, hitstop)
                 
    class Jump(baseActions.Jump):
        def __init__(self):
            baseActions.Jump.__init__(self)
    
    class AirJump(baseActions.AirJump):
        def __init__(self):
            baseActions.AirJump.__init__(self)
                
    class Fall(baseActions.Fall):
        def __init__(self):
            baseActions.Fall.__init__(self)
    
    class Helpless(baseActions.Helpless):
        def __init__(self):
            baseActions.Helpless.__init__(self)
                
    class Land(baseActions.Land):
        def __init__(self):
            baseActions.Land.__init__(self)
    
    class HelplessLand(baseActions.HelplessLand):
        def __init__(self):
            baseActions.HelplessLand.__init__(self)
    
    class Trip(baseActions.Trip):
        def __init__(self, length, direction):
            baseActions.Trip.__init__(self, length, direction)
    
    class Getup(baseActions.Getup):
        def __init__(self, direction):
            baseActions.Getup.__init__(self, direction)
    
    class GetupAttack(action.Action):
        def __init__(self):
            action.Action.__init__(self)
    
    class PlatformDrop(baseActions.PlatformDrop):
        def __init__(self):
            baseActions.PlatformDrop.__init__(self, 12, 6, 9)
            
    class PreShield(baseActions.PreShield):
        def __init__(self):
            baseActions.PreShield.__init__(self)
            
    class Shield(baseActions.Shield):
        def __init__(self):
            baseActions.Shield.__init__(self)
    
    class ShieldStun(baseActions.ShieldStun):
        def __init__(self, length):
            baseActions.ShieldStun.__init__(self, length)
    
    class Stunned(baseActions.Stunned):
        def __init__(self, length):
            baseActions.Stunned.__init__(self, length)
            
    class ForwardRoll(baseActions.ForwardRoll):
        def __init__(self):
            baseActions.ForwardRoll.__init__(self)
            
    class BackwardRoll(baseActions.BackwardRoll):
        def __init__(self):
            baseActions.BackwardRoll.__init__(self)
            
    class SpotDodge(baseActions.SpotDodge):
        def __init__(self):
            baseActions.SpotDodge.__init__(self)
            
    class AirDodge(baseActions.AirDodge):
        def __init__(self):
            baseActions.AirDodge.__init__(self)
    
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