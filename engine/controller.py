import settingsManager
import pygame

class Controller():
    def __init__(self,bindings):
        self.keysToPass = []
        self.keysToRelease = []
        self.keysHeld = []
        self.keyBindings = bindings
        self.type = 'Keyboard'
    
    def loadFighter(self,fighter):
        self.fighter = fighter
    
    def flushInputs(self):
        self.keysToPass = []
        self.keysToRelease = []
        self.keysHeld = []
        
    def getInputs(self,event,push = True, outputOnRelease = True):
        if event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
            return None
        output = True
        k = self.keyBindings.get(event.key)
        if k:
            if event.type == pygame.KEYDOWN:
                if push: self.keysToPass.append(k)
                if k not in self.keysHeld: self.keysHeld.append(k)
            elif event.type == pygame.KEYUP:
                output = outputOnRelease and output
                if push: self.keysToRelease.append(k)
                if k in self.keysHeld: self.keysHeld.remove(k)
        if output: return k
        return None
    
    def get(self,key):
        return self.keyBindings.get(key)
    
    def passInputs(self):
        for key in self.keysToPass:
            self.fighter.keyPressed(key)
        for key in self.keysToRelease:
            self.fighter.keyReleased(key)
        self.keysToPass = []
        self.keysToRelease = []
    
    def getKeysForAction(self,action):
        listOfBindings = []
        for binding,name in self.keyBindings.items():
            if name == action:
                listOfBindings.append(settingsManager.getSetting().KeyIdMap[binding])
        return listOfBindings
    
class GamepadController():
    def __init__(self,padBindings):
        self.keysToPass = []
        self.keysToRelease = []
        self.keysHeld = []
        self.padBindings = padBindings
        self.type = 'Gamepad'
    
    def loadFighter(self,fighter):
        self.fighter = fighter
    
    def flushInputs(self):
        self.keysToPass = []
        self.keysToRelease = []
        self.keysHeld = []
    
    def getInputs(self,event,push = True, outputOnRelease = True):
        if event.type not in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
            return None
        k = None
        output = True
        if event.type == pygame.JOYAXISMOTION:
            #getJoystickInput will get a pad and an axis, and return the value of that stick
            #by checking it along with the other axis of that joystick, if there is one.
            k = self.padBindings.getJoystickInput(event.joy,event.axis,event.value)
            if k and k in self.keysHeld: k = None
            if k and k not in self.keysHeld:
                self.keysHeld.append(k)
            if k and push:
                self.keysToPass.append(k)
                
            if k == 0:
                output = output and outputOnRelease
                a, b = self.padBindings.axisBindings.get(event.axis)
                if a in self.keysHeld: self.keysHeld.remove(a)
                if b in self.keysHeld: self.keysHeld.remove(b)
                if push:
                    self.keysToRelease.extend([a,b])
        elif event.type == pygame.JOYBUTTONDOWN:
            #getButtonInput is much more simple. It gets the key that button is mapped to
            k = self.padBindings.getButtonInput(event.joy,event.button)
        elif event.type == pygame.JOYBUTTONUP:
            output = output and outputOnRelease
            k = self.padBindings.getButtonInput(event.joy,event.button)
        
        if k:
            if event.type == pygame.JOYBUTTONDOWN:
                if k not in self.keysHeld: self.keysHeld.append(k)
                if push: self.keysToPass.append(k)
                
            elif event.type == pygame.JOYBUTTONUP:
                if k in self.keysHeld: self.keysHeld.remove(k)
                if push: self.keysToRelease.append(k)
        if output: return k
        return None
    
    def get(self,key):
        return self.keyBindings.get(key)
    
    def passInputs(self):
        for key in self.keysToPass:
            self.fighter.keyPressed(key)
        for key in self.keysToRelease:
            self.fighter.keyReleased(key)
        self.keysToPass = []
        self.keysToRelease = []
    
    def getKeysForAction(self,action):
        return self.padBindings.getKeysForAction(action)
    
class PadBindings():
    def __init__(self,joyName,joystick,axisBindings,buttonBindings):
        self.name = joyName
        self.joystick = joystick
        #Each axis is bound to a tuple of what a negative value is, and what a positive value is.
        #So, in this hard-coded example, axis 0 is left when negative, right when positive.
        self.axisBindings = axisBindings
        self.buttonBindings = buttonBindings
        
    def getJoystickInput(self,joy,axis,value):
        if not joy == self.joystick:
            return None
        axisTuple = self.axisBindings.get(axis) 
        if axisTuple:
            #if the value is above deadzone
            if value > 0.2750:
                return axisTuple[1]
            elif value < -0.2750:
                return axisTuple[0]
            else:
                return 0
            
    def getButtonInput(self,joy,button):
        if not joy == self.joystick:
            return None
        return self.buttonBindings.get(button)
    
    def getKeysForAction(self,action):
        listOfBindings = []
        for button,name in self.buttonBindings.items():
            if name == action:
                listOfBindings.append('Button ' + str(button))
        for axis,(neg,pos) in self.axisBindings.items():
            if pos == action:
                listOfBindings.append('Axis ' + str(axis) + ' Positive')
            if neg == action:
                listOfBindings.append('Axis ' + str(axis) + ' Negative')
        return listOfBindings