from __future__ import print_function
import pygame.constants
import re
import os
import sys
import imp
import engine.controller
import math
try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser


settings = None
sfx_lib = None


########################################################
#                GLOBAL ACCESSORS                      #
########################################################
"""
These functions are called from other modules to give them access
to global values and functions.
"""

"""
Since the settingsManager is always going to be in the root directory,
this function is a great way for any file, no matter where it is,
to be able to get back to the root of the program.

It will use the proper os.join calls to build a platform-apropriate path
from the main game to whatever you pass in the path argument.
"""
def createPath(_path):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir.replace('main.exe',''),_path)

"""
This function imports a module from it's file path.
It returns the imported module.


"""
#TODO refactor the variables to make this less confusing
def importFromURI(_filePath, _uri, _absl=False, _suffix=""):
    if not _absl:
        _uri = os.path.normpath(os.path.join(os.path.dirname(_filePath).replace('main.exe',''), _uri))
    #print(_uri)
    path, fname = os.path.split(_uri)
    mname, ext = os.path.splitext(fname)
    
    no_ext = os.path.join(path, mname)

    #print ((mname + _suffix), no_ext + '.py')
    
    if os.path.exists(no_ext + '.py'):
        try:
            return imp.load_source((mname + _suffix), no_ext + '.py')
        except Exception as e:
            print(mname, e)
"""
Build the settings if they do not exist yet, otherwise, get a setting.

If a key is given, it will return the value of that setting. If no key is given,
it returns the setting dictionary in its entirety (to make using lots of settings in
another file a lot easier)
"""
def getSetting(_key = None):
    global settings
    if settings == None:
        settings = Settings()
        return settings
    if _key:
        return settings.setting[_key]
    else:
        return settings

"""
Gets the Keybindings object for the given player_num.

If it can't find those controls, it'll make a blank Keybinding
"""
def getControls(_playerNum):
    global settings
    if settings == None:
        settings = Settings()
    
    controls = None
    
    control_type = settings.setting['controlType_'+str(_playerNum)]  
    if not control_type == 'Keyboard':
        try:
            controls = settings.setting[control_type]
            #Move the timing windows from the default controls to the new one
            controls.timing_window = settings.setting['controls_' + str(_playerNum)].timing_window
        except:
            pass #Can't find controller, gonna load normal
    
    if not controls:
        try:
            controls = settings.setting['controls_' + str(_playerNum)]
        except:
            controls = engine.controller.Controller({})
    
    return controls

"""
Creates or returns the SFX Library.
"""
def getSfx():
    global sfx_lib
    if sfx_lib == None:
        sfx_lib = sfx_library()
    return sfx_lib
    

########################################################
#                 SETTINGS LOADER                      #
########################################################           
class Settings():
    def __init__(self):
        self.key_id_map = {}
        self.key_name_map = {}
        for name, value in vars(pygame.constants).items():
            if name.startswith("K_"):
                self.key_id_map[value] = name.lower()
                self.key_name_map[name.lower()] = value
        
        
        self.parser = SafeConfigParser()
        if getattr(sys, 'frozen', False):
            # The application is frozen
            self.datadir = os.path.dirname(sys.executable)
        else:
            # The application is not frozen
            # Change this bit to match where you store your data files:
            self.datadir = os.path.dirname(__file__)
        
        self.parser.read(os.path.join(os.path.join(self.datadir.replace('main.exe','').replace('main.exe',''),'settings'),'settings.ini'))
        
        self.setting = dict()
        
        # Getting the window information
        
        self.setting['windowName']    = getString(self.parser,'window','windowName')
        #self.setting['windowSize']    = getNumber(self.parser, 'window', 'windowSize',True)
        #self.setting['windowWidth']   = self.setting['windowSize'][0]
        #self.setting['windowHeight']  = self.setting['windowSize'][1]
        self.setting['windowWidth']   = getNumber(self.parser, 'window', 'windowWidth')
        self.setting['windowHeight']  = getNumber(self.parser, 'window', 'windowHeight')
        self.setting['frameCap']      = getNumber(self.parser, 'window', 'frameCap')
        self.setting['windowSize']    = [self.setting['windowWidth'], self.setting['windowHeight']]

        self.setting['music_volume']       = getNumber(self.parser, 'sound', 'music_volume') / 100.0
        self.setting['sfxVolume']         = getNumber(self.parser, 'sound', 'sfxVolume') / 100.0
        self.setting['showHitboxes']      = getBoolean(self.parser, 'graphics', 'displayHitboxes')
        self.setting['showHurtboxes']     = getBoolean(self.parser,'graphics','displayHurtboxes')
        self.setting['showSpriteArea']    = getBoolean(self.parser,'graphics','displaySpriteArea')
        self.setting['showPlatformLines'] = getBoolean(self.parser, 'graphics', 'displayPlatformLines')
        self.setting['showECB']           = getBoolean(self.parser, 'graphics', "displayECB")

        self.setting['playerColor0'] = getString(self.parser, 'playerColors', 'player0')
        self.setting['playerColor1'] = getString(self.parser, 'playerColors', 'player1')
        self.setting['playerColor2'] = getString(self.parser, 'playerColors', 'player2')
        self.setting['playerColor3'] = getString(self.parser, 'playerColors', 'player3')
        # Getting game information
        
        # The "preset" lets users define custom presets to switch between.
        # The "custom" preset is one that is modified in-game.
        
        
        presets = []
        for f in os.listdir(os.path.join(self.datadir.replace('main.exe','').replace('main.exe',''),'settings/rules')):
            fname, ext = os.path.splitext(f)
            if ext == '.ini':
                presets.append(fname)
                
        self.setting['presetLists'] = presets
        preset = self.parser.get('game','rulePreset')
        
        self.new_gamepads = []
        
        self.loadGameSettings(preset)
        self.loadControls()
        
        
    def loadGameSettings(self,_presetSuf):
        preset_parser = SafeConfigParser()
        preset_parser.read(os.path.join(os.path.join(self.datadir.replace('main.exe','').replace('main.exe',''),'settings/rules',),_presetSuf+'.ini'))
        
        preset = 'preset_' + _presetSuf
        self.setting['current_preset'] = _presetSuf
        
        self.setting['gravity'] = float(getNumber(preset_parser, preset, 'gravityMultiplier')) / 100.0
        self.setting['weight'] = float(getNumber(preset_parser, preset, 'weightMultiplier')) / 100.0
        self.setting['friction'] = float(getNumber(preset_parser, preset, 'frictionMultiplier')) / 100.0
        self.setting['airControl'] = float(getNumber(preset_parser, preset, 'airControlMultiplier')) / 100.0
        self.setting['hitstun'] = float(getNumber(preset_parser, preset, 'hitstunMultiplier')) / 100.0
        self.setting['hitlag'] = float(getNumber(preset_parser, preset, 'hitlagMultiplier')) / 100.0
        self.setting['shieldStun'] = float(getNumber(preset_parser, preset, 'shieldStunMultiplier')) / 100.0
        
        self.setting['ledgeConflict'] = getString(preset_parser, preset, 'ledgeConflict')
        sweetSpotDict = {'large': [128,128], 'medium': [64,64], 'small': [32,32]}
        self.setting['ledgeSweetspotSize'] = sweetSpotDict[getString(preset_parser, preset, 'ledgeSweetspotSize')]
        self.setting['ledgeSweetspotForwardOnly'] = getBoolean(preset_parser, preset, 'ledgeSweetspotForwardOnly')
        self.setting['teamLedgeConflict'] = getBoolean(preset_parser, preset, 'teamLedgeConflict')
        self.setting['ledgeInvincibilityTime'] = getNumber(preset_parser, preset, 'ledgeInvincibilityTime')
        self.setting['regrabInvincibility'] = getBoolean(preset_parser, preset, 'regrabInvincibility')
        self.setting['slowLedgeWakeupThreshold'] = getNumber(preset_parser, preset, 'slowLedgeWakeupThreshold')

        self.setting['respawnDowntime'] = int(getNumber(preset_parser, preset, 'respawnDowntime'))
        self.setting['respawnLifetime'] = int(getNumber(preset_parser, preset, 'respawnLifetime'))
        self.setting['respawnInvincibility'] = int(getNumber(preset_parser, preset, 'respawnInvincibility'))
        
        self.setting['airDodgeType'] = getString(preset_parser, preset, 'airDodgeType')
        self.setting['freeDodgeSpecialFall'] = getBoolean(preset_parser, preset, 'freeDodgeSpecialFall')
        self.setting['enableWavedash'] = getBoolean(preset_parser, preset, 'enableWavedash')     
        self.setting['airDodgeLag'] = int(getNumber(preset_parser, preset, 'airDodgeLag'))
        
        self.setting['lagCancel'] = getString(preset_parser, preset, 'lagCancel')
        
        print(self.setting)
    
    def loadControls(self):
        player_num = 0
        self.getGamepadList(True)
        while self.parser.has_section('controls_' + str(player_num)):
            bindings = {}
            group_name = 'controls_' + str(player_num)
            control_type = self.parser.get(group_name, 'controlType')
            
            self.setting['controlType_'+str(player_num)] = control_type
            try:
                self.setting[control_type]
            except:
                self.setting['controlType_'+str(player_num)] = 'Keyboard'
            
            timing_window = {'smash_window': 4,
                             'repeat_window': 8,
                             'buffer_window': 8,
                             'smoothing_window': 64
                             }
            
            for key in timing_window.keys():
                if self.parser.has_option(group_name, key):
                    timing_window[key] = int(self.parser.get(group_name,key))
            
            for opt in self.parser.options(group_name):
                if self.key_name_map.has_key(opt):
                    bindings[self.key_name_map[opt]] = self.parser.get(group_name, opt)
            
            self.setting[group_name] = engine.controller.Controller(bindings,timing_window)
            #self.setting[group_name] = engine.cpuPlayer.CPUplayer(bindings) #Here be CPU players
            
            player_num += 1
    
    """
    Check all connected gamepads and add them to the settings.
    """
    def loadGamepad(self,_controllerName):
        pygame.joystick.init()
        controller_parser = SafeConfigParser()
        controller_parser.read(os.path.join(os.path.join(self.datadir.replace('main.exe',''),'settings'),'gamepads.ini'))
        if controller_parser.has_section(_controllerName):
            joystick = None
            for pad in range(pygame.joystick.get_count()):
                joy = pygame.joystick.Joystick(pad)
                if joy.get_name() == _controllerName:
                    joystick = joy
                    joystick.init()
            
            if joystick:
                jid = joystick.get_id()
            else:
                jid = None
            
            axes = {}
            buttons = {}
            for opt in controller_parser.options(_controllerName):
                if opt[0] == 'a':
                    axes[int(opt[1:])] = tuple(controller_parser.get(_controllerName, opt)[1:-1].split(','))
                elif opt[0] == 'b':
                    buttons[int(opt[1:])] = controller_parser.get(_controllerName, opt)
        
            pad_bindings = engine.controller.PadBindings(_controllerName,jid,axes,buttons)
            
            return engine.controller.GamepadController(pad_bindings)
        else:
            joystick = None
            for pad in range(pygame.joystick.get_count()):
                joy = pygame.joystick.Joystick(pad)
                if joy.get_name() == _controllerName:
                    joystick = joy
                    joystick.init()
            
            if joystick:
                jid = joystick.get_id()
            else:
                jid = None
            
            axes = dict()
            buttons = dict()
            
            pad_bindings = engine.controller.PadBindings(_controllerName,jid,axes,buttons)
            self.setting[joystick.get_name()] = pad_bindings
            
            return engine.controller.GamepadController(pad_bindings)
    
    def getGamepadList(self,_store=False):
        controller_parser = SafeConfigParser()
        controller_parser.read(os.path.join(os.path.join(self.datadir.replace('main.exe',''),'settings'),'gamepads.ini'))
        controller_list = []
        
        for control in controller_parser.sections():
            controls = self.loadGamepad(control)
            controller_list.append(controls)
            if _store: self.setting[control] = controls
            
        retlist = controller_parser.sections()
        retlist.extend(self.new_gamepads)
        return retlist
    
    def getGamepadByName(self,_joyName):
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            if joystick.get_name() == _joyName:
                return joystick
        return None
"""
Save a modified settings object to the settings.ini file.
"""
def saveSettings(_settings):
    key_id_map = {}
    key_nameMap = {}
    for name, value in vars(pygame.constants).items():
        if name.startswith("K_"):
            key_id_map[value] = name
            key_nameMap[name] = value
    
    parser = SafeConfigParser()
    
    parser.add_section('window')
    parser.set('window','windowName',str(_settings['windowName']))
    parser.set('window','windowSize',str(_settings['windowSize']))
    parser.set('window','windowWidth',str(_settings['windowSize'][0]))
    parser.set('window','windowHeight',str(_settings['windowSize'][1]))
    parser.set('window','frameCap',str(_settings['frameCap']))
    
    parser.add_section('sound')
    parser.set('sound','music_volume',str(_settings['music_volume'] * 100))
    parser.set('sound','sfxVolume',str(_settings['sfxVolume'] * 100))
    
    parser.add_section('graphics')
    parser.set('graphics','displayHitboxes',str(_settings['showHitboxes']))
    parser.set('graphics','displayHurtboxes',str(_settings['showHurtboxes']))
    parser.set('graphics','displaySpriteArea',str(_settings['showSpriteArea']))
    parser.set('graphics','displayPlatformLines',str(_settings['showPlatformLines']))
    parser.set('graphics','displayECB',str(_settings['showECB']))
    
    parser.add_section('playerColors')
    parser.set('playerColors','Player0',str(_settings['playerColor0']))
    parser.set('playerColors','Player1',str(_settings['playerColor1']))
    parser.set('playerColors','Player2',str(_settings['playerColor2']))
    parser.set('playerColors','Player3',str(_settings['playerColor3']))
    
    parser.add_section('game')
    parser.set('game','rulePreset',str(_settings['current_preset']))
    
    for i in range(0,4):
        sect = 'controls_'+str(i)
        parser.add_section(sect)
        parser.set(sect,'controlType',_settings['controlType_'+str(i)])
        for key in _settings[sect].key_bindings:
            parser.set(sect,'controlType',_settings['controlType_'+str(i)])
            parser.set(sect,key_id_map[key],str(_settings[sect].key_bindings[key]))
        for key,val in _settings[sect].timing_window.iteritems():
            parser.set(sect,key,str(val))
            
    with open(os.path.join(getSetting().datadir.replace('main.exe',''),'settings','settings.ini'), 'w') as configfile:
        parser.write(configfile)

    saveGamepad(_settings)

def saveGamepad(_settings):
    parser = SafeConfigParser()
    for controller_name in getSetting().getGamepadList():
        gamepad = getSetting(controller_name)
        if not parser.has_section(controller_name):
            parser.add_section(controller_name)
        
        for key,value in gamepad.key_bindings.axis_bindings.iteritems():
            neg,pos = value
            if not neg: neg = 'none'
            if not pos: pos = 'none'
            parser.set(controller_name,'a'+str(key),'('+str(neg)+','+str(pos)+')' )
        
        for key,value in gamepad.key_bindings.button_bindings.iteritems():
            parser.set(controller_name,'b'+str(key),str(value))
            
    with open(os.path.join(getSetting().datadir.replace('main.exe',''),'settings','gamepads.ini'), 'w') as configfile:
        parser.write(configfile)

        
def savePreset(_settings, _preset):
    parser = SafeConfigParser()
    
    parser.set(_preset,'gravityMultiplier',_settings['gravity'] * 100)
    parser.set(_preset,'weightMultiplier',_settings['weight'] * 100)
    parser.set(_preset,'frictionMultiplier',_settings['friction'] * 100)
    parser.set(_preset,'airControlMultiplier',_settings['airControl'] * 100)
    parser.set(_preset,'hitstunMultiplier',_settings['hitstun'] * 100)
    parser.set(_preset,'hitlagMultiplier',_settings['hitlag'] * 100)
    parser.set(_preset,'shieldStunMultiplier',_settings['shieldStun'] * 100)
    
    parser.set(_preset,'ledgeConflict',_settings['ledgeConflict'])
    sweetSpotDict = {[128,128]: 'large', [64,64]: 'medium', [32,32]: 'small'}
    parser.set(_preset,'ledgeSweetspotSize',sweetSpotDict[_settings['ledgeSweetspotSize']])
    parser.set(_preset,'ledgeSweetspotForwardOnly',_settings['ledgeSweetspotForwardOnly'])
    parser.set(_preset,'teamLedgeConflict',_settings['teamLedgeConflict'])
    parser.set(_preset,'ledgeInvincibilityTime',_settings['ledgeInvincibilityTime'])
    parser.set(_preset,'regrabInvincibility',_settings['regrabInvincibility'])
    parser.set(_preset,'slowLedgeWakeupThreshold',_settings['slowLedgeWakeupThreshold'])
    
    parser.set(_preset,'airDodgeType',_settings['airDodgeType'])
    parser.set(_preset,'freeDodgeSpecialFall',_settings['freeDodgeSpecialFall'])
    parser.set(_preset,'enableWavedash',_settings['enableWavedash'])
    
    parser.write(os.path.join(_settings.datadir.replace('main.exe',''),'settings.ini'))
    
"""
The SFXLibrary object contains a dict of all sound effects that are being used.
It handles the playing of the sounds.
"""                    
class sfx_library():
    def __init__(self):
        self.sounds = {}
        self.supported_file_types = ['.wav', '.ogg']
        self.initializeLibrary()
    
    """
    Rebuilds the library from scratch. This is used to clear out unnecessary sounds, for example,
    after a fight is over, the fighter's SFX are no longer needed.
    """        
    def initializeLibrary(self):
        self.sounds = {}
        directory = createPath("sfx")
        
        for f in os.listdir(directory):
            fname, ext = os.path.splitext(f)
            if self.supported_file_types.count(ext):
                self.sounds["base_" + fname] = pygame.mixer.Sound(os.path.join(directory,f)) 
                
    def playSound(self,_name,_category = "base"):
        self.sounds[_category + "_" + _name].set_volume(getSetting().setting['sfxVolume'])
        self.sounds[_category + "_" + _name].play()
    
    """
    Check if a sound exists.
    @_name - the name of the sound to play
    @_category - the category of the sound
    """
    def hasSound(self,_name,_category):
        return self.sounds.has_key(_category+"_"+_name)
                
    """
    This is called to add a directory of sound effects to the library.
    It is usually called when loading a fighter or a stage.
    """
    def addSoundsFromDirectory(self,_path,_category):
        for f in os.listdir(_path):
            fname, ext = os.path.splitext(f)
            if self.supported_file_types.count(ext):
                self.sounds[_category + "_" + fname] = pygame.mixer.Sound(os.path.join(_path,f))
                
    
########################################################
#             STATIC HELPER FUNCTIONS                  #
########################################################
"""
When given a string representation of numbers, parse it and return
the actual numbers. If Many is given, the parser will look
for all numbers and return them in a list, otherwise, it will get the
first number.
"""
def getNumbersFromString(_string, _many = False):
    if _many:
        return list(map(int, re.findall(r'\d+', _string)))
    else:
        return int(re.search(r'\d+', _string).group())

"""
Convert basically whatever stupid thing people could possibly think to mean "yes" into
a True boolean. If it's not True, it's false, so feel free to set some of those debug
options to "Eat a dick" if you want to, it'll read as False
"""
def boolean(_string):
    # Well, I already have the function made, might as well cover all the bases.
    return _string in ['true', 'True', 't', 'T', '1', '#T', 'y', 'yes', 'on', 'enabled']

"""
A wrapper that'll get a lowercase String from the parser, or return gracefully with an error.
"""    
def getString(_parser,_preset,_key):
    try:
        return str(_parser.get(_preset,_key).lower())
    except Exception as e:
        print(e)
        return ""

"""
A wrapper that'll get a boolean from the parser, or return gracefully with an error.
"""
def getBoolean(_parser,_preset,_key):
    try:
        return boolean(_parser.get(_preset,_key))
    except Exception as e:
        print(e)
        return False

"""
A wrapper that'll get a number from the parser, or return gracefully with an error.
"""    
def getNumber(_parser,_preset,_key,_islist = False):
    try:
        return getNumbersFromString(_parser.get(_preset,_key),_islist)
    except Exception as e:
        print(e)
        return 0

"""
Main method for debugging purposes
"""
def test():
    print(getSetting().setting)
    

"""
A helper function to get the X and Y magnitudes from the Direction and Magnitude of a trajectory
"""
def getXYFromDM(_direction,_magnitude):
    rad = math.radians(_direction)
    x = round(math.cos(rad) * _magnitude,5)
    y = -round(math.sin(rad) * _magnitude,5)
    return (x,y)


if __name__  == '__main__': test()

