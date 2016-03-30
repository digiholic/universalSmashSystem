import settingsManager
import pygame

class Controller():
    def __init__(self,bindings):
        self.keysToPass = []
        self.keysToRelease = []
        self.keysHeld = []
        self.keyBindings = bindings
    
    def loadFighter(self,fighter):
        self.fighter = fighter
    
    def flushInputs(self):
        self.keysToPass = []
        self.keysToRelease = []
        self.keysHeld = []
        
    def getInputs(self,event):
        if event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
            return None
        k = self.keyBindings.get(event.key)
        if k:
            if event.type == pygame.KEYDOWN:
                self.keysToPass.append(k)
                if k not in self.keysHeld: self.keysHeld.append(k)
            elif event.type == pygame.KEYUP:
                self.keysToRelease.append(k)
                if k in self.keysHeld: self.keysHeld.remove(k)
        return k
    
    def get(self,key):
        return self.keyBindings.get(key)
    
    def passInputs(self):
        for key in self.keysToPass:
            self.fighter.keyPressed(key)
        for key in self.keysToRelease:
            self.fighter.keyReleased(key)
        self.keysToPass = []
        self.keysToRelease = []
        
class GamepadController():
    def __init__(self,padBindings):
        self.keysToPass = []
        self.keysToRelease = []
        self.keysHeld = []
        self.padBindings = padBindings
    
    def loadFighter(self,fighter):
        self.fighter = fighter
    
    def flushInputs(self):
        self.keysToPass = []
        self.keysToRelease = []
        self.keysHeld = []
    
    def getInputs(self,event):
        if event.type not in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
            return None
        k = None
        if event.type == pygame.JOYAXISMOTION:
            #getJoystickInput will get a pad and an axis, and return the value of that stick
            #by checking it along with the other axis of that joystick, if there is one.
            k = self.padBindings.getJoystickInput(event.joy,event.axis,event.value)
            if k:
                self.keysToPass.append(k)
                if k not in self.keysHeld: self.keysHeld.append(k)
            if k == 0:
                a, b = self.padBindings.axisBindings.get(event.axis)
                self.keysToRelease.extend([a,b])
                if a in self.keysHeld: self.keysHeld.remove(a)
                if b in self.keysHeld: self.keysHeld.remove(b)
        elif event.type == pygame.JOYBUTTONDOWN:
            #getButtonInput is much more simple. It gets the key that button is mapped to
            k = self.padBindings.getButtonInput(event.joy,event.button)
        elif event.type == pygame.JOYBUTTONUP:
            k = self.padBindings.getButtonInput(event.joy,event.button)
        
        if k:
            if event.type == pygame.JOYBUTTONDOWN:
                self.keysToPass.append(k)
                if k not in self.keysHeld: self.keysHeld.append(k)
            elif event.type == pygame.JOYBUTTONUP:
                self.keysToRelease.append(k)    
                if k in self.keysHeld: self.keysHeld.remove(k)
        return k
    
    def get(self,key):
        return self.keyBindings.get(key)
    
    def passInputs(self):
        for key in self.keysToPass:
            self.fighter.keyPressed(key)
        for key in self.keysToRelease:
            self.fighter.keyReleased(key)
        self.keysToPass = []
        self.keysToRelease = []

class PadBindings():
    def __init__(self,joystick,axisBindings,buttonBindings):
        self.joystick = joystick
        #Each axis is bound to a tuple of what a negative value is, and what a positive value is.
        #So, in this hard-coded example, axis 0 is left when negative, right when positive.
        self.axisBindings = axisBindings
        
        self.buttonBindings = buttonBindings
        
        print(axisBindings)
        print(buttonBindings)
        
    def getJoystickInput(self,joy,axis,value):
        if not joy == self.joystick:
            return None
        axisTuple = self.axisBindings.get(axis) 
        if axisTuple:
            #if the value is above deadzone
            if value > 0.1:
                return axisTuple[1]
            elif value < -0.1:
                return axisTuple[0]
            else:
                return 0
            
    def getButtonInput(self,joy,button):
        if not joy == self.joystick:
            return None
        return self.buttonBindings.get(button)
    