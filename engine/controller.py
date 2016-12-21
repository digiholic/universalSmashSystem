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
        if self.bucket(_input,self.state[_input]) != now_state and now_state is not None: 
            push_states = self.key_bindings[_input][now_state].lookup(self.bucket(_input, _state))
            if push_states is not None:
                for key,val in push_states:
                    self.pushState(key,val)
            if _input in {'moveHor', 'moveVert', 'actHor', 'actVert', 
                    'attack', 'special', 'jump', 'shield', 'taunt', 'pause'}:
                self.buffer.append(states[(_input, now_state)])
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
        scale = self.key_bindings[_input]['decay'].lookup(self.state)
        if scale is None: 
            return
        self.pushState(_input, addFrom(self.state[_input], scale[0], scale[1]))

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
    ('attack', 0): '!',  ('attack', 1): '"',   ('attack', 2): '#',  ('attack', 3): '%',  
    ('special', 0): '&', ('special', 1): '\'', ('special', 2): ',', ('special', 3): '-',
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

    ' ': ('frame', 0), '\n': ('preframe', 0) #Just for completeness; this shouldn't actually be looked up
}
