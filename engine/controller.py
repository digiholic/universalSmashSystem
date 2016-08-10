import settingsManager
import pygame

class Controller():
    def __init__(self,bindings):
        self.keys_to_pass = []
        self.keys_to_release = []
        self.keys_held = []
        self.key_bindings = bindings
        self.type = 'Keyboard'
    
    def loadFighter(self,fighter):
        self.fighter = fighter
    
    def flushInputs(self):
        self.keys_to_pass = []
        self.keys_to_release = []
        self.keys_held = []
        
    def getInputs(self,event,push = True, outputOnRelease = True):
        if event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
            return None
        output = True
        k = self.key_bindings.get(event.key)
        if k:
            if event.type == pygame.KEYDOWN:
                if push: self.keys_to_pass.append(k)
                if k not in self.keys_held: self.keys_held.append(k)
            elif event.type == pygame.KEYUP:
                output = outputOnRelease and output
                if push: self.keys_to_release.append(k)
                if k in self.keys_held: self.keys_held.remove(k)
        if output: return k
        return None
    
    def get(self,key):
        return self.key_bindings.get(key)
    
    def passInputs(self):
        for key in self.keys_to_pass:
            self.fighter.keyPressed(key)
        for key in self.keys_to_release:
            self.fighter.key_released(key)
        self.keys_to_pass = []
        self.keys_to_release = []
    
    def getKeysForAction(self,action):
        list_of_bindings = []
        for binding,name in self.key_bindings.items():
            if name == action:
                list_of_bindings.append(settingsManager.getSetting().KeyIdMap[binding])
        return list_of_bindings
    
class GamepadController():
    def __init__(self,pad_bindings):
        self.keys_to_pass = []
        self.keys_to_release = []
        self.keys_held = []
        self.pad_bindings = pad_bindings
        self.type = 'Gamepad'
    
    def loadFighter(self,fighter):
        self.fighter = fighter
    
    def flushInputs(self):
        self.keys_to_pass = []
        self.keys_to_release = []
        self.keys_held = []
    
    def getInputs(self,event,push = True, outputOnRelease = True):
        if event.type not in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
            return None
        k = None
        output = True
        if event.type == pygame.JOYAXISMOTION:
            #getJoystickInput will get a pad and an axis, and return the value of that stick
            #by checking it along with the other axis of that joystick, if there is one.
            k = self.pad_bindings.getJoystickInput(event.joy,event.axis,event.value)
            if k and k in self.keys_held: k = None
            if k and k not in self.keys_held:
                self.keys_held.append(k)
            if k and push:
                self.keys_to_pass.append(k)
                
            if k == 0:
                output = output and outputOnRelease
                a, b = self.pad_bindings.axis_bindings.get(event.axis)
                if a in self.keys_held: self.keys_held.remove(a)
                if b in self.keys_held: self.keys_held.remove(b)
                if push:
                    self.keys_to_release.extend([a,b])
        elif event.type == pygame.JOYBUTTONDOWN:
            #getButtonInput is much more simple. It gets the key that button is mapped to
            k = self.pad_bindings.getButtonInput(event.joy,event.button)
        elif event.type == pygame.JOYBUTTONUP:
            output = output and outputOnRelease
            k = self.pad_bindings.getButtonInput(event.joy,event.button)
        
        if k:
            if event.type == pygame.JOYBUTTONDOWN:
                if k not in self.keys_held: self.keys_held.append(k)
                if push: self.keys_to_pass.append(k)
                
            elif event.type == pygame.JOYBUTTONUP:
                if k in self.keys_held: self.keys_held.remove(k)
                if push: self.keys_to_release.append(k)
        if output: return k
        return None
    
    def get(self,key):
        return self.key_bindings.get(key)
    
    def passInputs(self):
        for key in self.keys_to_pass:
            self.fighter.keyPressed(key)
        for key in self.keys_to_release:
            self.fighter.key_released(key)
        self.keys_to_pass = []
        self.keys_to_release = []
    
    def getKeysForAction(self,action):
        return self.pad_bindings.getKeysForAction(action)
    
class PadBindings():
    def __init__(self,joyName,joystick,axis_bindings,button_bindings):
        self.name = joyName
        self.joystick = joystick
        #Each axis is bound to a tuple of what a negative value is, and what a positive value is.
        #So, in this hard-coded example, axis 0 is left when negative, right when positive.
        self.axis_bindings = axis_bindings
        self.button_bindings = button_bindings
        
    def getJoystickInput(self,joy,axis,value):
        if not joy == self.joystick:
            return None
        axis_tuple = self.axis_bindings.get(axis) 
        if axis_tuple:
            #if the value is above deadzone
            if value > 0.2750:
                return axis_tuple[1]
            elif value < -0.2750:
                return axis_tuple[0]
            else:
                return 0
            
    def getButtonInput(self,joy,button):
        if not joy == self.joystick:
            return None
        return self.button_bindings.get(button)
    
    def getKeysForAction(self,action):
        list_of_bindings = []
        for button,name in self.button_bindings.items():
            if name == action:
                list_of_bindings.append('Button ' + str(button))
        for axis,(neg,pos) in self.axis_bindings.items():
            if pos == action:
                list_of_bindings.append('Axis ' + str(axis) + ' Positive')
            if neg == action:
                list_of_bindings.append('Axis ' + str(axis) + ' Negative')
        return list_of_bindings