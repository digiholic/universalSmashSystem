import settingsManager
import pygame

class Controller():
    def __init__(self,bindings):
        self.keysToPass = []
        self.keysToRelease = []
        self.keyBindings = bindings
    
    def loadFighter(self,fighter):
        self.fighter = fighter
    
    def flushInputs(self):
        self.keysToPass = []
        self.keysToRelease = []
        
    def getInputs(self,event):
        k = self.keyBindings.get(event.key)
        if k:
            if event.type == pygame.KEYDOWN:
                self.keysToPass.append(k)
            elif event.type == pygame.KEYUP:
                self.keysToRelease.append(k)
        return k
    
    def get(self,key):
        return self.keyBindings.get(key)
    
    def passInputs(self):
        for key in self.keysToPass:
            self.fighter.keyPressed(key)
        for key in self.keysToRelease:
            self.fighter.keyReleased(key)
        self.keysToPass = []
        
class GamepadController():
    def __init__(self,fighter):
        self.keysToPass = []
        self.padBindings = settingsManager.getControls(fighter.playerNum)
        self.fighter = fighter
    
    def getInputs(self,event):
        if event.type == pygame.JOYAXISMOTION:
            #getJoystickInput will get a pad and an axis, and return the value of that stick
            #by checking it along with the other axis of that joystick, if there is one.
            k = self.padBindings.getJoystickInput(event.joy,event.axis,event.value)
        elif event.type == pygame.JOYBUTTONDOWN:
            #getButtonInput is much more simple. It gets the key that button is mapped to
            k = self.padBindings.getButtonInput(event.joy,event.button)
        if k:
            self.keysToPass.append(k)
        return k
    
    def passInputs(self):
        for key in self.keysToPass:
            self.fighter.keyPressed(key)
        self.keysToPass = []

class PadBindings():
    def __init__(self,joystick,axisBindings,buttonBindings):
        self.joystick = joystick
        
        #Each axis is bound to a tuple of what a negative value is, and what a positive value is.
        #So, in this hard-coded example, axis 0 is left when negative, right when positive.
        self.axisBindings = {
                             0: ('left','right'),
                             1: ('up','down'),
                             2: ('grab','shield')
                             }
        
        self.buttonBindings = {
                               0: 'attack',
                               1: 'special',
                               2: 'jump',
                               3: 'jump'
                               }
        
    def getJoystickInput(self,joy,axis,value):
        if not joy == self.joystick:
            return None
        axisTuple =self.axisBindings.get(axis) 
        if axisTuple:
            #if the value is above deadzone
            if value > 10:
                return axisTuple[1]
            elif value < -10:
                return axisTuple[0]
            else:
                return None
        
        
    def getButtonInput(self,joy,button):
        if not joy == self.joystick:
            return None
        return self.buttonBindings.get(button)
    