import settingsManager
import pygame
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
#
# 

class BaseController:
    def __init__(self,_bindings,_windows):
        self.key_bindings = _bindings
        self.windows = _windows
        self.initials = self.init_dict
        self.state = self.init_state_dict
        self.buffer = list()
        self.frame_count = 0
    
    def flushInputs(self):
        self.initials = self.init_dict
        self.state = self.init_state_dict
        self.buffer = list()
        self.frame_count = 0

    def bucket(self,_input,_state):
        key_candidates = sorted(filter(lambda k: k is not None, self.key_bindings[_input].keys()))
        for candidate in key_candidates:
            if _state <= candidate:
                return candidate
        return None

    # Please call every time a primitive input state changes
    def pushState(self,_input,_state):
        now_state = self.bucket(_input,_state)
        if self.bucket(_input,self.state[_input]) != now_state: 
            push_states = self.key_bindings[_input][now_state].lookup(self.bucket(_input, _state))
            if push_states is not None:
                for key,val in push_states:
                    self.pushState(key,val)
            if _input in {'moveHor', 'moveVert', 'actHor', 'actVert', 
                    'attack', 'special', 'jump', 'shield', 'taunt', 'pause'}:
                if now_state is not None: self.buffer.append(states[_input, int(math.floor(now_state))])
                else: self.buffer.append(states[_input, None])
                   
        self.state[_input] = _state

    def pumpBuffer(self):
        if 'bufferLength' in self.windows and self.frame_count > self.windows['bufferLength']:
            buffer_portion = list()
            try:
                while len(self.buffer) > 0:
                    check_val = self.buffer.pop(0)
                    buffer_portion.append(check_val)
                    if check_val == ' ': break
            except IndexError:
                pass
            else: self.frame_count -= 1
            self.initials = self.getInit(buffer_portion, self.initials)
        self.buffer.append(' ')
        self.frame_count += 1
        for input_val in self.state:
            self.decay(input_val)

    def decay(self, _input):
        if 'decay' not in self.key_bindings[_input]:
            return
        decay_dict = self.key_bindings[_input]['decay'].lookup(self.state)
        if decay_dict is None: 
            return
        self.pushState(_input, dictDecay(self.state[_input], decay_dict))

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

    def getBucketedState(self,_action):
        return self.bucket(_action, self.state.get(_action))

    def getInit(self,_removedBufferPortion,_init):
        actions_to_find = {'moveHor', 'moveVert', 'actHor', 'actVert', 
                'attack', 'special', 'jump', 'shield', 'taunt', 'pause'}
        initials = _init.copy()
        for entry in _removedBufferPortion:
            if entry in codes:
                vals = codes[entry]
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
                if buffer_list.pop() == ' ': to_count += 1
                if to_count >= _to: break
        from_count = self.frame_count
        if _from < self.frame_count:
            while len(buffer_list) > 0:
                check_val = buffer_list.pop(0)
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
                if check_val == ' ': self.frame_count -= 1
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

class PhysicalController(BaseController):
    def __init__(self,_bindings,_windows,_joy):
        BaseController.__init__(self, _bindings, _windows)
        self.joystick = _joy

    def pushInput(self,_event):
        if _event.type not in {pygame.KEYDOWN, pygame.KEYUP}:
            if self.joystick is None or _event.type not in {pygame.JOYAXISMOTION, pygame.JOYBALLMOTION, \
                    pygame.JOYHATMOTION, pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP}:
                return None
        if _event.type == pygame.KEYDOWN:
            self.pushState('key_'+_event.key, 1)
        elif _event.type == pygame.KEYUP:
            self.pushState('key_'+_event.key, 0)
        elif _event.type == pygame.JOYAXISMOTION:
            self.pushState('axis_'+_event.axis, _event.value)
        elif _event.type == pygame.JOYBALLMOTION:
            self.pushState('ball_'+_event.ball, _event.rel)
        elif _event.type == pygame.JOYHATMOTION: 
            self.pushState('hat_x_'+_event.hat, _event.value[0])
            self.pushState('hat_y_'+_event.hat, _event.value[1])
        elif _event.type == pygame.JOYBUTTONDOWN: 
            self.pushState('button_'+_event.button, 1)
        elif _event.type == pygame.JOYBUTTONUP:
            self.pushState('button_'+_event.button, 0)
    
    def getKeysForaction(self,_action):
        list_of_bindings = []
        for key,actions in self.key_bindings.items():
            if _action in actions:
                list_of_bindings.append(str(key))
        return list_of_bindings
    
class RangeCheckTree():
    def __init__(self, _entryName=None, _default=None):
        self.entry_name = _entryName
        self.default = _default
        self.entries = list()
        
    def addEntry(self, _range, _entry):
        self.entries.append((_range, _entry))

    def lookup(self, _dict):
        return_node = None
        if self.entry_name in _dict:
            for entry in self.entries:
                val = _dict[self.entry_name]
                if entry[0][0] <= val < entry[0][1]:
                    return_node = entry
                    break
        if return_node is None: return_node = self.default
        if isinstance(return_node, RangeCheckTree): return return_node.lookup(_dict)
        else: return return_node



# Static dictionaries for lookups: 
states = {
    ('attack', 0): '!',  ('attack', 1): '"',   ('attack', 2): '#',  ('attack', None): '%',  
    ('special', 0): '&', ('special', 1): '\'', ('special', 2): ',', ('special', None): '-',
    ('jump', 0): '/',    ('jump', 1): '0',     ('jump', 2): '1',    ('jump', None): '2', 
    ('shield', 0): '3',  ('shield', 1): '4',   ('shield', 2): '5',  ('shield', None): '6', 
    ('taunt', 0): '7',   ('taunt', 1): '8',    ('taunt', 2): '9',   ('taunt', None): ':', 
    ('pause', 0): ';',   ('pause', 1): '<',    ('pause', 2): '=',   ('pause', None): '>', 
    
    ('moveHor', 0): 'A', ('moveHor', 1): 'B',  ('moveHor', 2): 'C',  ('moveHor', 3): 'D', 
    ('moveHor', 4): 'E', ('moveHor', 5): 'F',  ('moveHor', 6): 'G',  ('moveHor', 7): 'H', ('moveHor', 8): 'I', 
    ('moveHor', 9): 'J', ('moveHor', 10): 'K', ('moveHor', 11): 'L', ('moveHor', None): 'M', 
    
    ('moveVert', 0): 'N', ('moveVert', 1): 'O',  ('moveVert', 2): 'P',  ('moveVert', 3): 'Q', 
    ('moveVert', 4): 'R', ('moveVert', 5): 'S',  ('moveVert', 6): 'T',  ('moveVert', 7): 'U', ('moveVert', 8): 'V', 
    ('moveVert', 9): 'W', ('moveVert', 10): 'X', ('moveVert', 11): 'Y', ('moveVert', None): 'Z',

    ('actHor', 0): 'a', ('actHor', 1): 'b',  ('actHor', 2): 'c',  ('actHor', 3): 'd',
    ('actHor', 4): 'e', ('actHor', 5): 'f',  ('actHor', 6): 'g',  ('actHor', 7): 'h', ('actHor', 8): 'i', 
    ('actHor', 9): 'j', ('actHor', 10): 'k', ('actHor', 11): 'l', ('actHor', None): 'm', 
    
    ('actVert', 0): 'n', ('actVert', 1): 'o',  ('actVert', 2): 'p',  ('actVert', 3): 'q', 
    ('actVert', 4): 'r', ('actVert', 5): 's',  ('actVert', 6): 't',  ('actVert', 7): 'u', ('actVert', 8): 'v', 
    ('actVert', 9): 'w', ('actVert', 10): 'x', ('actVert', 11): 'y', ('actVert', None): 'z', 
    
    ('frame', 0): ' ', ('preframe', 0): '\n' #Just for completeness; this won't actually be looked up
}

codes = {
    '!': ('attack', 0),  '"': ('attack', 1),   '#': ('attack', 2),  '%': ('attack', None),  
    '&': ('special', 0), '\'': ('special', 1), ',': ('special', 2), '-': ('special', None), 
    '/': ('jump', 0),    '0': ('jump', 1),     '1': ('jump', 2),    '2': ('jump', None), 
    '3': ('shield', 0),  '4': ('shield', 1),   '5': ('shield', 2),  '6': ('shield', None), 
    '7': ('taunt', 0),   '8': ('taunt', 1),    '9': ('taunt', 2),   ':': ('taunt', None), 
    ';': ('pause', 0),   '<': ('pause', 1),    '=': ('pause', 2),   '>': ('pause', None), 

    'A': ('moveHor', 0), 'B': ('moveHor', 1),  'C': ('moveHor', 2),  'D': ('moveHor', 3), 
    'E': ('moveHor', 4), 'F': ('moveHor', 5),  'G': ('moveHor', 6),  'H': ('moveHor', 7), 'I': ('moveHor', 8), 
    'J': ('moveHor', 9), 'K': ('moveHor', 10), 'L': ('moveHor', 11), 'M': ('moveHor', None), 

    'N': ('moveVert', 0), 'O': ('moveVert', 1),  'P': ('moveVert', 2),  'Q': ('moveVert', 3), 
    'R': ('moveVert', 4), 'S': ('moveVert', 5),  'T': ('moveVert', 6),  'U': ('moveVert', 7), 'V': ('moveVert', 8), 
    'W': ('moveVert', 9), 'X': ('moveVert', 10), 'Y': ('moveVert', 11), 'Z': ('moveVert', None), 

    'a': ('actHor', 0), 'b': ('actHor', 1),  'c': ('actHor', 2),  'd': ('actHor', 3), 
    'e': ('actHor', 4), 'f': ('actHor', 5),  'g': ('actHor', 6),  'h': ('actHor', 7), 'i': ('actHor', 8), 
    'j': ('actHor', 9), 'k': ('actHor', 10), 'l': ('actHor', 11), 'm': ('actHor', None), 

    'n': ('actVert', 0), 'o': ('actVert', 1),  'p': ('actVert', 2),  'q': ('actVert', 3), 
    'r': ('actVert', 4), 's': ('actVert', 5),  't': ('actVert', 6),  'u': ('actVert', 7), 'v': ('actVert', 8), 
    'w': ('actVert', 9), 'x': ('actVert', 10), 'y': ('actVert', 11), 'z': ('actVert', None), 

    ' ': ('frame', 0), '\n': ('preframe', 0) #Just for completeness; this shouldn't actually be looked up
}
