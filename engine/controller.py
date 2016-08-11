import settingsManager
import pygame

class Controller():
    def __init__(self,_bindings):
        self.keys_to_pass = []
        self.keys_to_release = []
        self.keys_held = []
        self.key_bindings = _bindings
        self.type = 'Keyboard'
    
    def loadFighter(self,_fighter):
        self.fighter = _fighter
    
    def flushInputs(self):
        self.keys_to_pass = []
        self.keys_to_release = []
        self.keys_held = []
        
    def getInputs(self,_event,_push = True, _outputOnRelease = True):
        if _event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
            return None
        output = True
        k = self.key_bindings.get(_event.key)
        if k:
            if _event.type == pygame.KEYDOWN:
                if _push: self.keys_to_pass.append(k)
                if k not in self.keys_held: self.keys_held.append(k)
            elif _event.type == pygame.KEYUP:
                output = _outputOnRelease and output
                if _push: self.keys_to_release.append(k)
                if k in self.keys_held: self.keys_held.remove(k)
        if output: return k
        return None
    
    def get(self,_key):
        return self.key_bindings.get(_key)
    
    def passInputs(self):
        for key in self.keys_to_pass:
            self.fighter.keyPressed(key)
        for key in self.keys_to_release:
            self.fighter.key_released(key)
        self.keys_to_pass = []
        self.keys_to_release = []
    
    def getKeysForAction(self,_action):
        list_of_bindings = []
        for binding,name in self.key_bindings.items():
            if name == _action:
                list_of_bindings.append(settingsManager.getSetting().KeyIdMap[binding])
        return list_of_bindings
    
class GamepadController():
    def __init__(self,_padBindings):
        self.keys_to_pass = []
        self.keys_to_release = []
        self.keys_held = []
        self.pad_bindings = _padBindings
        self.type = 'Gamepad'
    
    def loadFighter(self,_fighter):
        self.fighter = _fighter
    
    def flushInputs(self):
        self.keys_to_pass = []
        self.keys_to_release = []
        self.keys_held = []
    
    def getInputs(self,_event,_push = True, _outputOnRelease = True):
        if _event.type not in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
            return None
        k = None
        output = True
        if _event.type == pygame.JOYAXISMOTION:
            #getJoystickInput will get a pad and an axis, and return the value of that stick
            #by checking it along with the other axis of that joystick, if there is one.
            k = self.pad_bindings.getJoystickInput(_event.joy,_event.axis,_event.value)
            if k and k in self.keys_held: k = None
            if k and k not in self.keys_held:
                self.keys_held.append(k)
            if k and push:
                self.keys_to_pass.append(k)
                
            if k == 0:
                output = output and _outputOnRelease
                a, b = self.pad_bindings.axis_bindings.get(_event.axis)
                if a in self.keys_held: self.keys_held.remove(a)
                if b in self.keys_held: self.keys_held.remove(b)
                if _push:
                    self.keys_to_release.extend([a,b])
        elif _event.type == pygame.JOYBUTTONDOWN:
            #getButtonInput is much more simple. It gets the key that button is mapped to
            k = self.pad_bindings.getButtonInput(_event.joy,_event.button)
        elif _event.type == pygame.JOYBUTTONUP:
            output = output and _outputOnRelease
            k = self.pad_bindings.getButtonInput(_event.joy,_event.button)
        
        if k:
            if _event.type == pygame.JOYBUTTONDOWN:
                if k not in self.keys_held: self.keys_held.append(k)
                if _push: self.keys_to_pass.append(k)
                
            elif _event.type == pygame.JOYBUTTONUP:
                if k in self.keys_held: self.keys_held.remove(k)
                if _push: self.keys_to_release.append(k)
        if output: return k
        return None
    
    def get(self,_key):
        return self.key_bindings.get(_key)
    
    def passInputs(self):
        for key in self.keys_to_pass:
            self.fighter.keyPressed(key)
        for key in self.keys_to_release:
            self.fighter.key_released(key)
        self.keys_to_pass = []
        self.keys_to_release = []
    
    def getKeysForAction(self,_action):
        return self.pad_bindings.getKeysForAction(_action)
    
class PadBindings():
    def __init__(self,_joyName,_joystick,_axisBindings,_buttonBindings):
        self.name = _joyName
        self.joystick = _joystick
        #Each axis is bound to a tuple of what a negative value is, and what a positive value is.
        #So, in this hard-coded example, axis 0 is left when negative, right when positive.
        self.axis_bindings = _axisBindings
        self.button_bindings = _buttonBindings
        
    def getJoystickInput(self,_joy,_axis,_value):
        if not _joy == self.joystick:
            return None
        axis_tuple = self.axis_bindings.get(_axis) 
        if axis_tuple:
            #if the value is above deadzone
            if value > 0.2750:
                return axis_tuple[1]
            elif value < -0.2750:
                return axis_tuple[0]
            else:
                return 0
            
    def getButtonInput(self,_joy,_button):
        if not _joy == self.joystick:
            return None
        return self.button_bindings.get(_button)
    
    def getKeysForAction(self,_action):
        list_of_bindings = []
        for button,name in self.button_bindings.items():
            if name == _action:
                list_of_bindings.append('Button ' + str(button))
        for axis,(neg,pos) in self.axis_bindings.items():
            if pos == _action:
                list_of_bindings.append('Axis ' + str(axis) + ' Positive')
            if neg == _action:
                list_of_bindings.append('Axis ' + str(axis) + ' Negative')
        return list_of_bindings
