import settingsManager
import pygame
import re
from global_functions import *

class BaseController():
    def __init__(self,_bindings,_windows):
        self.key_bindings = _bindings
        self.windows = _windows
        self.type = 'Base'
        self.current = self.init_dict
        self.initials = self.init_dict
        self.state = self.init_state_dict
        self.buffer = list()
        self.frame_count = 0
    
    def flushInputs(self):
        self.current = self.init_dict
        self.initials = self.init_dict
        self.state = self.init_state_dict
        self.buffer = list()
        self.frame_count = 0

    def thresholdBucket(self,_primitive,_state):
        if _state < -self.windows[_primitive + 'Threshold6']: return -6
        elif _state < -self.windows[_primitive + 'Threshold5']: return -5
        elif _state < -self.windows[_primitive + 'Threshold4']: return -4
        elif _state < -self.windows[_primitive + 'Threshold3']: return -3
        elif _state < -self.windows[_primitive + 'Threshold2']: return -2
        elif _state < -self.windows[_primitive + 'Threshold1']: return -1
        elif _state <= self.windows[_primitive + 'Threshold1']: return 0
        elif _state <= self.windows[_primitive + 'Threshold2']: return 1
        elif _state <= self.windows[_primitive + 'Threshold3']: return 2
        elif _state <= self.windows[_primitive + 'Threshold4']: return 3
        elif _state <= self.windows[_primitive + 'Threshold5']: return 4
        elif _state <= self.windows[_primitive + 'Threshold6']: return 5
        else: return 6

    # Please call every time a primitive input state changes
    def pushPrimitive(self,_primitive,_state):
        if _primitive in ('moveHor', 'moveVert', 'actHor', 'actVert'):
            state_num = self.thresholdBucket(_primitive, _state)
        elif _primitive in ('attack', 'special', 'jump', 'shield', 'taunt'):
            state_num = 1 if _state > self.windows[_primitive+'Threshold'] else 0
        else:
            print("Primitive input does not exist: " + _primitive)
            return
        if state_num != self.current[_primitive]:
            self.buffer.append(self.states[(_primitive, state_num)])
            self.current[_primitive] = state_num

    def pumpBuffer(self):
        if 'bufferLength' in self.windows and self.frame_count > self.windows['bufferLength']:
            buffer_portion = list()
            try:
                while len(self.buffer) > 0:
                    checkval = self.buffer.pop(0)
                    buffer_portion.append(checkval)
                    if checkval == ' ': break
            except IndexError:
                pass
            else:
                self.frame_count -= 1
            self.initials = self.getInit(buffer_portion, self.initials)
        self.buffer.append(' ')
        self.frame_count += 1

    def pushInput(self,_event):
        raise NotImplementedError
    
    def getKeyaction(self,_key):
        return self.key_bindings.get(_key)

    def getactionKeys(self,_action):
        list_of_bindings = []
        for binding,name in self.key_bindings.items():
            if name == _action:
                list_of_bindings.append(settingsManager.getSetting().key_id_map[binding])
        return list_of_bindings

    def getWindow(self,_key):
        return self.windows.get(_key)

    def getState(self,_key):
        raise self.state.get(_key)

    def getInit(self,_removedBufferPortion,_init):
        actions_to_find = {'moveHor', 'moveVert', 'actHor', 'actVert', 'attack', 'special', 'jump', 'shield', 'taunt'}
        initials = _init.copy()
        for entry in _removedBufferPortion:
            if entry in self.codes:
                vals = self.codes[entry]
                if vals[0] in actions_to_find:
                    initials[vals[0]] = vals[1]
                    actions_to_find.remove(vals[0])
            if len(actions_to_find) == 0: break
        return initials
        
    def parseBuffer(self,_compiledRegexList,_from=None,_to=None):
        # Prune the buffer string so it meets our specifications 
        # The most recent is at the end, and the oldest is at the beginning
        buffer_list = self.buffer.copy()
        after_portion = list()
        to_count = 0
        if _to > 0:
            while len(buffer_list) > 0:
                if self.buffer_list.pop() == ' ': to_count += 1
                if to_count >= _to: break
        from_count = self.frame_count
        if _from < self.frame_count
            while len(buffer_list) > 0:
                check_val = self.buffer_list.pop(0)
                after_portion.append(check_val)
                if check_val == ' ': from_count -= 1
                if _from >= from_count: break

        # Construct the working initials
        working_initials = self.getInit(after_portion, self.initials)

        # Construct the matching string and match
        checkstring = ''.join(working_initials.values()) + '\n' + ''.join(buffer_list)
        matches = filter(None, map(lambda regex: regex.search(checkstring), _compiledRegexList))
        if len(matches) == 0: return -1 # No match
        
        # Modify buffer to remove the applicable match
        longest_match = max(matches, key=lambda match: match.end())
        max_len = longest_match.end() - 10 - len(after_portion)
        removed_portion = list()
        try:
            for i in range(0, max_len):
                check_val = self.buffer.pop(0)
                removed_portion.append(check_val)
                if checkval == ' ': self.frame_count -= 1
        except IndexError:
            pass
        self.initials = self.getInit(removed_portion, self.initials)
        return _compiledRegexList.index(longest_match.re)

    init_dict = {
        'moveHor': 'G',
        'moveVert': 'T',
        'actHor': 'g',
        'actVert': 't',
        'attack': '0',
        'special': '2',
        'jump': '4',
        'shield': '6',
        'taunt': '8'
    }

    init_state_dict = {
        'moveHor': 0,
        'moveVert': 0,
        'actHor': 0,
        'actVert': 0,
        'attack': 0,
        'special': 0,
        'jump': 0,
        'shield': 0,
        'taunt': 0
    }

    # Static dictionaries for lookups: 
    states = {
        ('attack', 0): '0', ('attack', 1): '1', ('special', 0): '2', ('special', 1): '3', ('jump', 0): '4', 
        ('jump', 1): '5', ('shield', 0): '6', ('shield', 1): '7', ('taunt', 0): '8', ('taunt', 1): '9', 

        ('moveHor', -6): 'A', ('moveHor', -5): 'B', ('moveHor', -4): 'C', ('moveHor', -3): 'D', 
        ('moveHor', -2): 'E', ('moveHor', -1): 'F', ('moveHor', 0): 'G', ('moveHor', 1): 'H', ('moveHor', 2): 'I', 
        ('moveHor', 3): 'J', ('moveHor', 4): 'K', ('moveHor', 5): 'L', ('moveHor', 6): 'M', 

        ('moveVert', -6): 'N', ('moveVert', -5): 'O', ('moveVert', -4): 'P', ('moveVert', -3): 'Q', 
        ('moveVert', -2): 'R', ('moveVert', -1): 'S', ('moveVert', 0): 'T', ('moveVert', 1): 'U', ('moveVert', 2): 'V', 
        ('moveVert', 3): 'W', ('moveVert', 4): 'X', ('moveVert', 5): 'Y', ('moveVert', 6): 'Z', 

        ('actHor', -6): 'a', ('actHor', -5): 'b', ('actHor', -4): 'c', ('actHor', -3): 'd', 
        ('actHor', -2): 'e', ('actHor', -1): 'f', ('actHor', 0): 'g', ('actHor', 1): 'h', ('actHor', 2): 'i', 
        ('actHor', 3): 'j', ('actHor', 4): 'k', ('actHor', 5): 'l', ('actHor', 6): 'm', 

        ('actVert', -6): 'n', ('actVert', -5): 'o', ('actVert', -4): 'p', ('actVert', -3): 'q', 

        ('actVert', -2): 'r', ('actVert', -1): 's', ('actVert', 0): 't', ('actVert', 1): 'u', ('actVert', 2): 'v', 
        ('actVert', 3): 'w', ('actVert', 4): 'x', ('actVert', 5): 'y', ('actVert', 6): 'z', 

        ('frame', 0): ' ', ('preframe', 0): '\n' #Just for completeness; this won't actually be looked up
    }

    codes = {
        '0': ('attack', 0), '1': ('attack', 1), '2': ('special', 0), '3': ('special', 1), '4': ('jump', 0), 
        '5': ('jump', 1), '6': ('shield', 0), '7': ('shield', 1), '8': ('taunt', 0), '9': ('taunt', 1), 

        'A': ('moveHor', -6), 'B': ('moveHor', -5), 'C': ('moveHor', -4), 'D': ('moveHor', -3), 
        'E': ('moveHor', -2), 'F': ('moveHor', -1), 'G': ('moveHor', 0), 'H': ('moveHor', 1), 'I': ('moveHor', 2), 
        'J': ('moveHor', 3), 'K': ('moveHor', 4), 'L': ('moveHor', 5), 'M': ('moveHor', 6), 

        'N': ('moveVert', -6), 'O': ('moveVert', -5), 'P': ('moveVert', -4), 'Q': ('moveVert', -3), 
        'R': ('moveVert', -2), 'S': ('moveVert', -1), 'T': ('moveVert', 0), 'U': ('moveVert', 1), 'V': ('moveVert', 2), 
        'W': ('moveVert', 3), 'X': ('moveVert', 4), 'Y': ('moveVert', 5), 'Z': ('moveVert', 6), 

        'a': ('actHor', -6), 'b': ('actHor', -5), 'c': ('actHor', -4), 'd': ('actHor', -3), 
        'e': ('actHor', -2), 'f': ('actHor', -1), 'g': ('actHor', 0), 'h': ('actHor', 1), 'i': ('actHor', 2), 
        'j': ('actHor', 3), 'k': ('actHor', 4), 'l': ('actHor', 5), 'm': ('actHor', 6), 

        'n': ('actVert', -6), 'o': ('actVert', -5), 'p': ('actVert', -4), 'q': ('actVert', -3), 
        'r': ('actVert', -2), 's': ('actVert', -1), 't': ('actVert', 0), 'u': ('actVert', 1), 'v': ('actVert', 2), 
        'w': ('actVert', 3), 'x': ('actVert', 4), 'y': ('actVert', 5), 'z': ('actVert', 6), 

        ' ': ('frame', 0), '\n': ('preframe', 0) #Just for completeness; this won't actually be looked up
    }
    
# This controller class is for keyboards. 
# To help players perform angled inputs, this controller smooths directional inputs automatically. 
class KeyboardController(BaseController):
    def __init__(self,_bindings,_windows):
        BaseController.__init__(self, _bindings, _windows)
        self.type = 'Keyboard'
        self.inputted = self.init_state_dict

    def flushInputs(self):
        BaseController.flushInputs(self)
        self.inputted = self.init_state_dict

    def pumpBuffer(self):
        BaseController.pumpBuffer(self)
        self.decay('moveHor')
        self.decay('moveVert')
        self.decay('actHor')
        self.decay('actVert')

    def decay(self, _primitive):
        if self.inputted[_primitive] == 0: 
            # Case one: current input is zero
            self.state[_primitive] = addFrom(self.state[_primitive], -self.windows['offDecay'])
        elif self.state[_primitive] == 0:
            # Case two: smoothed input is zero
            pass
        elif math.copysign(1, self.inputted[_primitive]) == math.copysign(1, self.state[_primitive]):
            if abs(self.inputted[_primitive]) > abs(self.state[_primitive]):
                # Case three: same direction, state is weaker
                self.state[_primitive] = addFrom(self.state[_primitive], -self.windows['onDecay'])
            else:
                # Case four: same direction, state is stronger
                self.state[_primitive] = addFrom(self.state[_primitive], -self.windows['offDecay'])
        elif abs(self.inputted[_primitive]) > abs(self.state[_primitive]):
            # Case five: opposite directions, state is weaker
            self.state[_primitive] = self.inputted[_primitive]
            self.pushPrimitive(_primitive, self.state[_primitive])
        else:
            # Case six: opposite directions, state is stronger
            self.state[_primitive] = addFrom(self.state[_primitive], -self.windows['againstDecay'])

    def acceptDirection(self, _primitive, _value):
        if _value == 0: 
            # Case one: current input is zero
            self.inputted[_primitive] = 0
            self.pushPrimitive(_primitive, 0)
        elif self.state[_primitive] == 0:
            # Case two: smoothed input is zero
            self.inputted[_primitive] = _value
            self.state[_primitive] = _value
            self.pushPrimitive(_primitive, _value)
        elif math.copysign(1, _value) == math.copysign(1, self.state[_primitive]):
            if abs(_value) > abs(self.state[_primitive]):
                # Case three: same direction, state is weaker
                self.inputted[_primitive] = _value+self.state[_primitive]
                self.state[_primitive] = self.inputted[_primitive]
                self.pushPrimitive(_primitive, self.state[_primitive])
            else:
                # Case four: same direction, state is stronger
                self.inputted[_primitive] = _value
                self.pushPrimitive(_primitive, _value)
        elif abs(_value) > abs(self.state[_primitive]):
            # Case five: opposite directions, state is weaker
            self.inputted[_primitive] = _value
            self.state[_primitive] = _value
            self.pushPrimitive(_primitive, _value)
        else:
            # Case six: opposite directions, state is stronger
            self.inputted[_primitive] = _value
            self.pushPrimitive(_primitive, _value)
    
    def pushInput(self,_event):
        if _event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
            return None
        k = self.key_bindings.get(_event.key)
        if k:
            if _event.type == pygame.KEYDOWN:
                for key in k[0]:
                    if key[0] in ('moveHor', 'moveVert', 'actHor', 'actVert'):
                        self.acceptDirection(key[0], key[1])
                    else: 
                        self.state[key[0]] = key[1]
                        self.pushPrimitive(key[0], key[1])
                return k
            elif _event.type == pygame.KEYUP:
                for key in k[1]:
                    if key[0] in ('moveHor', 'moveVert', 'actHor', 'actVert'):
                        self.acceptDirection(key[0], key[1])
                    else: 
                        self.state[key[0]] = key[1]
                        self.pushPrimitive(key[0], key[1])
        return None

    init_state_dict = {
        'moveHor': 0,
        'moveVert': 0,
        'actHor': 0,
        'actVert': 0,
        'attack': 0,
        'special': 0,
        'jump': 0,
        'shield': 0,
        'taunt': 0
    }

# This controller class is for controllers that have no analog inputs, such as arcade controllers. 
# To help players perform angled inputs, this controller smooths directional inputs automatically. 
class ArcadeController(BaseController):
    def __init__(self,_bindings,_windows):
        BaseController.__init__(self, _bindings, _windows)
        self.type = 'Arcade'
        self.inputted = self.init_state_dict

    def flushInputs(self):
        BaseController.flushInputs(self)

        self.inputted = self.init_state_dict

    def pumpBuffer(self):
        BaseController.pumpBuffer(self)
        self.decay('moveHor')
        self.decay('moveVert')
        self.decay('actHor')
        self.decay('actVert')

    def decay(self, _primitive):
        if self.inputted[_primitive] == 0: 
            # Case one: current input is zero
            self.state[_primitive] = addFrom(self.state[_primitive], -self.windows['offDecay'])
        elif self.state[_primitive] == 0:
            # Case two: smoothed input is zero
            pass
        elif math.copysign(1, self.inputted[_primitive]) == math.copysign(1, self.state[_primitive]):
            if abs(self.inputted[_primitive]) > abs(self.state[_primitive]):
                # Case three: same direction, state is weaker
                self.state[_primitive] = addFrom(self.state[_primitive], -self.windows['onDecay'])
            else:
                # Case four: same direction, state is stronger
                self.state[_primitive] = addFrom(self.state[_primitive], -self.windows['offDecay'])
        elif abs(self.inputted[_primitive]) > abs(self.state[_primitive]):
            # Case five: opposite directions, state is weaker
            self.state[_primitive] = self.inputted[_primitive]
            self.pushPrimitive(_primitive, self.state[_primitive])
        else:
            # Case six: opposite directions, state is stronger
            self.state[_primitive] = addFrom(self.state[_primitive], -self.windows['againstDecay'])

    def acceptDirection(self, _primitive, _value):
        if _value == 0: 
            # Case one: current input is zero
            self.inputted[_primitive] = 0
            self.pushPrimitive(_primitive, 0)
        elif self.state[_primitive] == 0:
            # Case two: smoothed input is zero
            self.inputted[_primitive] = _value
            self.state[_primitive] = _value
            self.pushPrimitive(_primitive, _value)
        elif math.copysign(1, _value) == math.copysign(1, self.state[_primitive]):
            if abs(_value) > abs(self.state[_primitive]):
                # Case three: same direction, state is weaker
                self.inputted[_primitive] = _value+self.state[_primitive]
                self.state[_primitive] = self.inputted[_primitive]
                self.pushPrimitive(_primitive, self.state[_primitive])
            else:
                # Case four: same direction, state is stronger
                self.inputted[_primitive] = _value
                self.pushPrimitive(_primitive, _value)
        elif abs(_value) > abs(self.state[_primitive]):
            # Case five: opposite directions, state is weaker
            self.inputted[_primitive] = _value
            self.state[_primitive] = _value
            self.pushPrimitive(_primitive, _value)
        else:
            # Case six: opposite directions, state is stronger
            self.inputted[_primitive] = _value
            self.pushPrimitive(_primitive, _value)
    
    def pushInput(self,_event):
        if _event.type not in [pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
            return None
        k = self.key_bindings.getButtonInput(_event.joy,_event.button)
        if k:
            if _event.type == pygame.JOYBUTTONDOWN:
                for key in k[0]:
                    if key[0] in ('moveHor', 'moveVert', 'actHor', 'actVert'):
                        self.acceptDirection(key[0], key[1])
                    else: 
                        self.state[key[0]] = key[1]
                        self.pushPrimitive(key[0], key[1])
                return k
            elif _event.type == pygame.JOYBUTTONUP:
                for key in k[1]:
                    if key[0] in ('moveHor', 'moveVert', 'actHor', 'actVert'):
                        self.acceptDirection(key[0], key[1])
                    else: 
                        self.state[key[0]] = key[1]
                        self.pushPrimitive(key[0], key[1])
        return None

    init_state_dict = {
        'moveHor': 0,
        'moveVert': 0,
        'actHor': 0,
        'actVert': 0,
        'attack': 0,
        'special': 0,
        'jump': 0,
        'shield': 0,
        'taunt': 0
    }
    
# This controller class is for controllers that have analog inputs, such as most home console 
# game controllers. Since analog sticks are available, this controller handles analog inputs 
# directly. Mapping buttons to directional inputs is possible, but no smoothing happens. 
class GamepadController(BaseController):
    def __init__(self,_padBindings):
        BaseController.__init__(self, _padBindings)
        self.type = 'Gamepad'

    def pushInput(self,_event):
        if _event.type not in [pygame.JOYAXISMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
            return None
        if _event.type == pygame.JOYAXISMOTION: 
            #getJoystickInput will get a pad and an axis, and return the value of that stick
            #by checking it along with the other axis of that joystick, if there is one.
            k = self.key_bindings.getJoystickInput(_event.joy,_event.axis,_event.value)
            if k:
                for key in k[0]:
                    self.state[key[0]] = key[1]
                    self.pushPrimitive(key[0], key[1])
                return k
        elif _event.type == pygame.JOYBUTTONDOWN:
            k = self.key_bindings.getButtonInput(_event.joy,_event.button)
            if k: 
                for key in k[0]:
                    self.state[key[0]] = key[1]
                    self.pushPrimitive(key[0], key[1])
                return k
        elif _event.type == pygame.JOYBUTTONUP: 
            k = self.key_bindings.getButtonInput(_event.joy,_event.button)
            if k: 
                for key in k[1]:
                    self.state[key[0]] = key[1]
                    self.pushPrimitive(key[0], key[1])
        return None
    
    def getKeysForaction(self,_action):
        return self.key_bindings.getKeysForaction(_action)
    
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
        return self.axis_bindings.get(_axis) 
            
    def getButtonInput(self,_joy,_button):
        if not _joy == self.joystick:
            return None
        return self.button_bindings.get(_button)
    
    def getKeysForaction(self,_action):
        list_of_bindings = []
        for button,actions in self.button_bindings.items():
            if _action in actions:
                list_of_bindings.append('Button ' + str(button))
        for axis,name in self.axis_bindings.items():
            if _action in actions:
                list_of_bindings.append('Axis ' + str(axis))
        return list_of_bindings


