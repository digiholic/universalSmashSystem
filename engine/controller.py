import settingsManager
import pygame
import re
from global_functions import *

# This is the base class of Project TUSSLE's controller abstraction. Each controller is reduced to 
# ten "primitive inputs", four that can take on integer values from -6 to 6, and six that can take 
# on integer values from 0 to 3. These are the values that are returned in state queries, and the 
# values that are parsed over in buffer queries. 
#
# Applicable windows:
#     
#     bufferLength: The maximum frame length of the buffer. Smaller buffers may (and probably 
#         will) be queried if applicable, but automatic buffer pruning ensures that the buffer can 
#         be no longer than the max buffer length. 

class BaseController():
    def __init__(self,_bindings,_windows):
        self.key_bindings = _bindings
        self.windows = _windows
        self.current = self.init_dict
        self.initials = self.init_dict
        self.state = self.init_dict
        self.buffer = list()
        self.frame_count = 0
    
    def flushInputs(self):
        self.current = self.init_dict
        self.initials = self.init_dict
        self.state = self.init_dict
        self.buffer = list()
        self.frame_count = 0

    # Please call every time a primitive input state changes
    def pushPrimitive(self,_primitive,_state):
        if _primitive in self.current and _state != self.current[_primitive]:
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
        actions_to_find = {'moveHor', 'moveVert', 'actHor', 'actVert', 'attack', 'special', 'jump', 'shield', 'taunt', 'pause'}
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
        'attack': '!',
        'special': '&',
        'jump': '/',
        'shield': '3',
        'taunt': '7',
        'pause': ';'
    }

    # Static dictionaries for lookups: 
    states = {
        ('attack', 0): '!',  ('attack', 1): '"',   ('attack', 2): '#',  ('attack', 3): '%',  
        ('special', 0): '&', ('special', 1): '\'', ('special', 2): ',', ('special', 3): '-'
        ('jump', 0): '/',    ('jump', 1): '0',     ('jump', 2): '1',    ('jump', 3): '2', 
        ('shield', 0): '3',  ('shield', 1): '4',   ('shield', 2): '5',  ('shield', 3): '6', 
        ('taunt', 0): '7',   ('taunt', 1): '8',    ('taunt', 2): '9',   ('taunt', 3): ':', 
        ('pause', 0): ';',   ('pause', 1): '<',    ('pause', 2): '=',   ('pause', 3): '>', 

        ('moveHor', -6): 'A', ('moveHor', -5): 'B', ('moveHor', -4): 'C', ('moveHor', -3): 'D', 
        ('moveHor', -2): 'E', ('moveHor', -1): 'F', ('moveHor', 0): 'G',  ('moveHor', 1): 'H',  ('moveHor', 2): 'I', 
        ('moveHor', 3): 'J',  ('moveHor', 4): 'K',  ('moveHor', 5): 'L',  ('moveHor', 6): 'M', 

        ('moveVert', -6): 'N', ('moveVert', -5): 'O', ('moveVert', -4): 'P', ('moveVert', -3): 'Q', 
        ('moveVert', -2): 'R', ('moveVert', -1): 'S', ('moveVert', 0): 'T',  ('moveVert', 1): 'U',  ('moveVert', 2): 'V', 
        ('moveVert', 3): 'W',  ('moveVert', 4): 'X',  ('moveVert', 5): 'Y',  ('moveVert', 6): 'Z', 

        ('actHor', -6): 'a', ('actHor', -5): 'b', ('actHor', -4): 'c', ('actHor', -3): 'd', 
        ('actHor', -2): 'e', ('actHor', -1): 'f', ('actHor', 0): 'g',  ('actHor', 1): 'h',  ('actHor', 2): 'i', 
        ('actHor', 3): 'j',  ('actHor', 4): 'k',  ('actHor', 5): 'l',  ('actHor', 6): 'm', 

        ('actVert', -6): 'n', ('actVert', -5): 'o', ('actVert', -4): 'p', ('actVert', -3): 'q', 
        ('actVert', -2): 'r', ('actVert', -1): 's', ('actVert', 0): 't',  ('actVert', 1): 'u',  ('actVert', 2): 'v', 
        ('actVert', 3): 'w',  ('actVert', 4): 'x',  ('actVert', 5): 'y',  ('actVert', 6): 'z', 

        ('frame', 0): ' ', ('preframe', 0): '\n' #Just for completeness; this won't actually be looked up
    }

    codes = {
        '!': ('attack', 0),  '"': ('attack', 1),   '#': ('attack', 2),  '%': ('attack', 3),  
        '&': ('special', 0), '\'': ('special', 1), ',': ('special', 2), '-': ('special', 3), 
        '/': ('jump', 0),    '0': ('jump', 1),     '1': ('jump', 2),    '2': ('jump', 3), 
        '3': ('shield', 0),  '4': ('shield', 1),   '5': ('shield', 2),  '6': ('shield', 3), 
        '7': ('taunt', 0),   '8': ('taunt', 1),    '9': ('taunt', 2),   ':': ('taunt', 3), 
        ';': ('pause', 0),   '<': ('pause', 1),    '=': ('pause', 2),   '>': ('pause', 3), 

        'A': ('moveHor', -6), 'B': ('moveHor', -5), 'C': ('moveHor', -4), 'D': ('moveHor', -3), 
        'E': ('moveHor', -2), 'F': ('moveHor', -1), 'G': ('moveHor', 0), 'H':  ('moveHor', 1),  'I': ('moveHor', 2), 
        'J': ('moveHor', 3), 'K':  ('moveHor', 4), 'L':  ('moveHor', 5), 'M':  ('moveHor', 6), 

        'N': ('moveVert', -6), 'O': ('moveVert', -5), 'P': ('moveVert', -4), 'Q': ('moveVert', -3), 
        'R': ('moveVert', -2), 'S': ('moveVert', -1), 'T': ('moveVert', 0),  'U': ('moveVert', 1),  'V': ('moveVert', 2), 
        'W': ('moveVert', 3),  'X': ('moveVert', 4),  'Y': ('moveVert', 5),  'Z': ('moveVert', 6), 

        'a': ('actHor', -6), 'b': ('actHor', -5), 'c': ('actHor', -4), 'd': ('actHor', -3), 
        'e': ('actHor', -2), 'f': ('actHor', -1), 'g': ('actHor', 0),  'h': ('actHor', 1),  'i': ('actHor', 2), 
        'j': ('actHor', 3),  'k': ('actHor', 4),  'l': ('actHor', 5),  'm': ('actHor', 6), 

        'n': ('actVert', -6), 'o': ('actVert', -5), 'p': ('actVert', -4), 'q': ('actVert', -3), 
        'r': ('actVert', -2), 's': ('actVert', -1), 't': ('actVert', 0),  'u': ('actVert', 1),  'v': ('actVert', 2), 
        'w': ('actVert', 3),  'x': ('actVert', 4),  'y': ('actVert', 5),  'z': ('actVert', 6), 

        ' ': ('frame', 0), '\n': ('preframe', 0) #Just for completeness; this won't actually be looked up
    }

# This is a class for abstractions of physical controllers, derived from the base controller 
# class. On top of the base controller, it provides input addition, input smoothing, and input 
# decay, all of which may be helpful with physical controllers. 
#
# Applicable windows:
#
#     (.+)Threshold[1-6]: Analog input thresholds. The parenthesized group is the name of the 
#         input. This is used as the threshold of bucket division when divvying up the named 
#         analog input. Not all threshold windows need to exist for a particular input, but any 
#         particular bucket is possible only if the corresponding window is set. This means that 
#         an analog input with no thresholds set can only return zero. 
#     
#     (.+)((OffDecay)|(OnDecay)|(AgainstDecay)): The per-frame decays. The first parenthesized 
#         group is the name of the primitive to be decayed, and the second parenthesized group 
#         is the type of decay. Each turn, the primitive input is added to or subtracted from to 
#         make it closer to zero. This value is OnDecay if the input is in the same direction as 
#         the currently held input and stronger, OffDecay if the input is zero or in the same 
#         direction but weaker, or againstDecay if the input is in the opposite direction and 
#         weaker. (If the input is in the opposite direction and stronger, the current state 
#         immediately changes to that of the input.) All three must be set for a particular 
#         primitive to cause the input to decay. 
#         

class PhysicalController(BaseController):
    def __init__(self,_bindings,_windows):
        BaseController.__init__(self, _bindings, _windows)
        self.smoothed = self.init_state_dict
        self.inputs = self.init_state_dict

    def flushInputs(self):
        BaseController.flushInputs(self)
        self.smoothed = self.init_state_dict
        self.inputs = self.init_state_dict

    def pumpBuffer(self):
        BaseController.pumpBuffer(self)
        for primitive in smoothed:
            self.decay(primitive)

    def analogBucket(self,_input,_state):
        if _input +'Threshold6' in self.windows:
            if _state < -self.windows[_input + 'Threshold6']: return -6
            elif _state > self.windows[_input + 'Threshold6']: return 6
        if _input +'Threshold5' in self.windows:
            if _state < -self.windows[_input + 'Threshold5']: return -5
            elif _state > self.windows[_input + 'Threshold5']: return 5
        if _input +'Threshold4' in self.windows:
            if _state < -self.windows[_input + 'Threshold4']: return -4
            elif _state > self.windows[_input + 'Threshold4']: return 4
        if _input +'Threshold3' in self.windows:
            if _state < -self.windows[_input + 'Threshold3']: return -3
            elif _state > self.windows[_input + 'Threshold3']: return 3
        if _input +'Threshold2' in self.windows:
            if _state < -self.windows[_input + 'Threshold2']: return -2
            elif _state > self.windows[_input + 'Threshold2']: return 2
        if _input +'Threshold1' in self.windows:
            if _state < -self.windows[_input + 'Threshold1']: return -1
            elif _state > self.windows[_input + 'Threshold1']: return 1
        return 0

    def decay(self, _primitive):
        if not all(lambda k: _primitive+k+'Decay' in self.windows for k in ['Off', 'On', 'Against']):
            self.smoothed[_primitive] = self.inputs[_primitive]
        elif self.inputs[_primitive] == 0: 
            # Case one: current input is zero
            self.smoothed[_primitive] = addFrom(self.smoothed[_primitive], -self.windows[_primitive+'OffDecay'])
        elif self.smoothed[_primitive] == 0:
            # Case two: smoothed input is zero
            pass
        elif math.copysign(1, self.inputs[_primitive]) == math.copysign(1, self.smoothed[_primitive]):
            if abs(self.inputs[_primitive]) > abs(self.inputs[_primitive]):
                # Case three: same direction, state is weaker
                self.smoothed[_primitive] = addFrom(self.smoothed[_primitive], -self.windows[_primitive+'OnDecay'])
            else:
                # Case four: same direction, state is stronger
                self.smoothed[_primitive] = addFrom(self.smoothed[_primitive], -self.windows[_primitive+'OffDecay'])
        elif abs(self.inputs[_primitive]) > abs(self.smoothed[_primitive]):
            # Case five: opposite directions, state is weaker
            self.smoothed[_primitive] = self.inputs[_primitive]
        else:
            # Case six: opposite directions, state is stronger
            self.smoothed[_primitive] = addFrom(self.smoothed[_primitive], -self.windows[_primitive+'AgainstDecay'])
        self.pushPrimitive(_primitive, self.analogBucket('decay'+_primitive, self.smoothed[_primitive]))

    def acceptInput(self, _primitive, _input, _value, _maxValue = None):
        if _maxValue is None:
            self.inputs[_primitive] = _value
            self.smoothed[_primitive] = _value
        elif _value == 0: 
            # Case one: current input is zero
            self.inputs[_primitive] = 0
        elif self.smoothed[_primitive] == 0:
            # Case two: smoothed input is zero
            self.inputs[_primitive] = _value
            self.smoothed[_primitive] = _value
        elif math.copysign(1, _value) == math.copysign(1, self.smoothed[_primitive]):
            if abs(_value) > abs(self.state[_primitive]):
                # Case three: same direction, state is weaker
                self.inputs[_primitive] = bounded(_value+self.smoothed[_primitive], -_maxValue, _maxValue)
                self.smoothed[_primitive] = self.inputs[_primitive]
            else:
                # Case four: same direction, state is stronger
                self.inputs[_primitive] = _value
        elif abs(_value) > abs(self.smoothed[_primitive]):
            # Case five: opposite directions, state is weaker
            self.inputs[_primitive] = _value
            self.smoothed[_primitive] = _value
        else:
            # Case six: opposite directions, state is stronger
            self.inputs[_primitive] = _value
        self.pushPrimitive(_primitive, self.analogBucket(_input+_primitive, self.smoothed[_primitive]))

    init_state_dict = {
        'moveHor': 0,
        'moveVert': 0,
        'actHor': 0,
        'actVert': 0,
        'attack': 0,
        'special': 0,
        'jump': 0,
        'shield': 0,
        'taunt': 0,
        'pause': 0
    }

class KeyboardController(PhysicalController):
    def __init__(self,_bindings,_windows):
        DigitalController.__init__(self, _bindings, _windows)
        self.type = "Keyboard"
    
    def pushInput(self,_event):
        if _event.type not in [pygame.KEYDOWN, pygame.KEYUP]:
            return None
        k = self.key_bindings.get(_event.key)
        if k:
            if _event.type == pygame.KEYDOWN:
                for key in k[1]:
                    if len(key) == 3: self.acceptInput(key[0], _event.key.name(), key[1], key[2])
                    else: self.acceptInput(key[0], _event.key.name(), key[1])
                return k[1][0] # Return the first associated primitive input
            elif _event.type == pygame.KEYUP:
                for key in k[0]:
                    if len(key) == 3: self.acceptInput(key[0], _event.key.name(), key[1], key[2])
                    else: self.acceptInput(key[0], _event.key.name(), key[1])
        return None
    
class GamepadController(PhysicalController):
    def __init__(self,_padBindings,_windows):
        PhysicalController.__init__(self, _padBindings,_windows)
        self.type = 'Gamepad'

    def pushInput(self,_event):
        if _event.type not in [pygame.JOYAXISMOTION, pygame.JOYBALLMOTION, pygame.JOYHATMOTION, \
        pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP]:
            return None
        if _event.type == pygame.JOYAXISMOTION: 
            #getAxiInput will get a pad and an axis, and return the value of that stick
            #by checking it along with the other axis of that joystick, if there is one.
            k = self.key_bindings.getAxisInput(_event.joy,_event.axis)
            if k:
                bucket = self.analogBucket(_event.axis,_event.value)
                for key in k[bucket]:
                    if len(key) == 3: self.acceptInput(key[0], 'axis'+_event.axis, key[1], key[2])
                    else: self.acceptInput(key[0], _event.axis, key[1])
                if bucket != 0:
                    return k[bucket][0]
        elif _event.type == pygame.JOYBALLMOTION: 
            k = self.key_bindings.getBallInput(_event.joy,_event.ball)
            if k:
                bucket = self.analogBucket(_event.ball,_event.rel)
                for key in k[bucket]:
                    if len(key) == 3: self.acceptInput(key[0], 'ball'+_event.ball, key[1], key[2])
                    else: self.acceptInput(key[0], _event.ball, key[1])
                if bucket != 0:
                    return k[bucket][0]
        elif _event.type == pygame.JOYHATMOTION: 
            k = self.key_bindings.getHatInput(_event.joy,_event.hat)
            if k:
                bucket = self.analogBucket(_event.hat,_event.value)
                for key in k[bucket]:
                    if len(key) == 3: self.acceptInput(key[0], 'hat'+_event.hat, key[1], key[2])
                    else: self.acceptInput(key[0], _event.hat, key[1])
                if bucket != 0:
                    return k[bucket][0]
        elif _event.type == pygame.JOYBUTTONDOWN:
            k = self.key_bindings.getButtonInput(_event.joy,_event.button)
            if k: 
                for key in k[1]:
                    if len(key) == 3: self.acceptInput(key[0], 'button'+_event.button, key[1], key[2])
                    else: self.acceptInput(key[0], _event.button, key[1])
                return k[1][0]
        elif _event.type == pygame.JOYBUTTONUP: 
            k = self.key_bindings.getButtonInput(_event.joy,_event.button)
            if k: 
                for key in k[0]:
                    if len(key) == 3: self.acceptInput(key[0], 'button'+_event.button, key[1], key[2])
                    else: self.acceptInput(key[0], _event.button, key[1])
        return None
    
    def getKeysForaction(self,_action):
        return self.key_bindings.getKeysForaction(_action)
    
class PadBindings():
    def __init__(self,_joyName,_joystick,_axisBindings,_buttonBindings,_ballBindings,_hatBindings):
        self.name = _joyName
        self.joystick = _joystick
        self.axis_bindings = _axisBindings
        self.button_bindings = _buttonBindings
        self.ball_bindings = _ballBindings
        self.hat_bindings = _hatBindings
        
    def getAxisInput(self,_joy,_axis):
        if not _joy == self.joystick:
            return None
        return self.axis_bindings.get(_axis)
            
    def getButtonInput(self,_joy,_button):
        if not _joy == self.joystick:
            return None
        return self.button_bindings.get(_button)

    def getBallInput(self,_joy,_ball):
        if not _joy == self.joystick:
            return None
        return self.ball_bindings.get(_ball)

    def getHatInput(self,_joy,_hat):
        if not _joy == self.joystick:
            Return None
        return self.hat_bindings.get(_hat)
    
    def getKeysForaction(self,_action):
        list_of_bindings = []
        for button,actions in self.button_bindings.items():
            if _action in actions:
                list_of_bindings.append('Button ' + str(button))
        for axis,actions in self.axis_bindings.items():
            if _action in actions:
                list_of_bindings.append('Axis ' + str(axis))
        for ball,actions in self.ball_bindings.items():
            if _action in actions:
                list_of_bindings.append('Ball ' + str(ball))
        for hat,actions in self.hat_bindings.items():
            if _action in actions:
                list_of_bindigns.append('Hat ' + str(hat))
        return list_of_bindings
