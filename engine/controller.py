import settingsManager
import pygame

class BaseController():
    def __init__(self,_bindings):
        self.keys_to_pass = []
        self.keys_to_release = []
        self.keys_held = []
        self.key_bindings = _bindings
        self.type = 'Keyboard'
        self.target = None
        
        self.buffer = [[]]
        self.last_index = 0
      
      
    def linkObject(self,_object):
        self.target = _object
    
    def flushInputs(self):
        self.keys_to_pass = []
        self.keys_to_release = []
        self.keys_held = []
        
        self.buffer = [[]]
        self.last_index = 0
        
    def getInputs(self,_event,_push=True, _outputOnRelease=True):
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
        if self.target:
            for key in self.keys_to_pass:
                self.target.keyPressed(key)
            for key in self.keys_to_release:
                self.target.keyReleased(key)
        self.keys_to_pass = []
        self.keys_to_release = []
        
    def getKeysForAction(self,_action):
        list_of_bindings = []
        for binding,name in list(self.key_bindings.items()):
            if name == _action:
                list_of_bindings.append(settingsManager.getSetting().key_id_map[binding])
        return list_of_bindings
    
    
class Controller(BaseController):
    def __init__(self,_bindings,_timing_window = dict()):
        BaseController.__init__(self, _bindings)
        self.timing_window = _timing_window
        print(self.timing_window)
    
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
    
class GamepadController(BaseController):
    def __init__(self,_padBindings):
        BaseController.__init__(self, _padBindings)
        self.type = 'Gamepad'
    
    def getInputs(self,_event,_push = True, _outputOnRelease = True):
        if _event.type not in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
            return None
        k = None
        output = True
        if _event.type == pygame.JOYAXISMOTION:
            #getJoystickInput will get a pad and an axis, and return the value of that stick
            #by checking it along with the other axis of that joystick, if there is one.
            k = self.key_bindings.getJoystickInput(_event.joy,_event.axis,_event.value)
            if k and k in self.keys_held: k = None
            if k and k not in self.keys_held:
                self.keys_held.append(k)
            if k and _push:
                self.keys_to_pass.append(k)
                
            if k == 0:
                output = output and _outputOnRelease
                a, b = self.key_bindings.axis_bindings.get(_event.axis)
                if a in self.keys_held: self.keys_held.remove(a)
                if b in self.keys_held: self.keys_held.remove(b)
                if _push:
                    self.keys_to_release.extend([a,b])
        elif _event.type == pygame.JOYBUTTONDOWN:
            #getButtonInput is much more simple. It gets the key that button is mapped to
            k = self.key_bindings.getButtonInput(_event.joy,_event.button)
        elif _event.type == pygame.JOYBUTTONUP:
            output = output and _outputOnRelease
            k = self.key_bindings.getButtonInput(_event.joy,_event.button)
        
        if k:
            if _event.type == pygame.JOYBUTTONDOWN:
                if k not in self.keys_held: self.keys_held.append(k)
                if _push: self.keys_to_pass.append(k)
                
            elif _event.type == pygame.JOYBUTTONUP:
                if k in self.keys_held: self.keys_held.remove(k)
                if _push: self.keys_to_release.append(k)
        if output: return k
        return None
    
    def getKeysForAction(self,_action):
        return self.key_bindings.getKeysForAction(_action)
    
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
            if _value > 0.2750:
                return axis_tuple[1]
            elif _value < -0.2750:
                return axis_tuple[0]
            else:
                return 0
            
    def getButtonInput(self,_joy,_button):
        if not _joy == self.joystick:
            return None
        return self.button_bindings.get(_button)
    
    def getKeysForAction(self,_action):
        list_of_bindings = []
        for button,name in list(self.button_bindings.items()):
            if name == _action:
                list_of_bindings.append('Button ' + str(button))
        for axis,(neg,pos) in list(self.axis_bindings.items()):
            if pos == _action:
                list_of_bindings.append('Axis ' + str(axis) + ' Positive')
            if neg == _action:
                list_of_bindings.append('Axis ' + str(axis) + ' Negative')
        return list_of_bindings
    
    
"""
The input buffer is a list of all of the buttons pressed and released,
and the frames they're put in on. It's used to check for buttons that
were pressed in the past, such as for a wall tech, or a buffered jump,
but can also be used to re-create the entire battle (once a replay manager
is set up)
"""
class InputBuffer():
    def __init__(self):
        self.buffer = [[]]
        self.working_buff = []
        self.last_index = 0
      
    """
    Pushes the buttons for the frame into the buffer, then extends the index by one.
    """
    def push(self):
        self.buffer.append(dict(self.working_buff))
        self.working_buff = []
        self.last_index += 1
        
    """
    Get a sub-buffer of N frames
    """
    def getLastNFrames(self,_from,_to=0):
        ret_buffer = []
        if _from > self.last_index: _from = self.last_index
        if _to > self.last_index: _to = self.last_index
        for i in range(self.last_index - _to,self.last_index - _from,-1):
            ret_buffer.append(self.buffer[i - _to])
        return ret_buffer
    
    """
    put a key into the current working buffer. The working buffer is all of the inputs for
    one frame, before the frame is actually executed.
    """
    def append(self,_key):
        self.working_buff.append(_key)

