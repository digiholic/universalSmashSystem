from __future__ import print_function
import pygame.constants
import re
import os
import sys
import imp
import engine.controller
try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser


settings = None
sfxLib = None


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
def createPath(path):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(__file__)
    return os.path.join(datadir.replace('main.exe',''),path)

"""
This function imports a module from it's file path.
It returns the imported module.


"""
#TODO refactor the variables to make this less confusing
def importFromURI(filePath, uri, absl=False, suffix=""):
    if not absl:
        uri = os.path.normpath(os.path.join(os.path.dirname(filePath).replace('main.exe',''), uri))
    #print(uri)
    path, fname = os.path.split(uri)
    mname, ext = os.path.splitext(fname)
    
    no_ext = os.path.join(path, mname)

    #print ((mname + suffix), no_ext + '.py')
    
    if os.path.exists(no_ext + '.py'):
        try:
            return imp.load_source((mname + suffix), no_ext + '.py')
        except Exception as e:
            print(mname, e)
"""
Build the settings if they do not exist yet, otherwise, get a setting.

If a key is given, it will return the value of that setting. If no key is given,
it returns the setting dictionary in its entirety (to make using lots of settings in
another file a lot easier)
"""
def getSetting(key = None):
    global settings
    if settings == None:
        settings = Settings()
        return settings
    if key:
        return settings.setting[key]
    else:
        return settings

"""
Gets the Keybindings object for the given player_num.

If it can't find those controls, it'll make a blank Keybinding
"""
def getControls(player_num):
    global settings
    if settings == None:
        settings = Settings()
    
    controls = None
    
    controlType = settings.setting['controlType_'+str(player_num)]  
    if not controlType == 'Keyobard':
        try:
            controls = settings.setting[controlType]
        except:
            pass #Can't find controller, gonna load normal
    
    if not controls:
        try:
            controls = settings.setting['controls_' + str(player_num)]
        except:
            controls = engine.controller.Controller({})
    
    return controls

"""
Creates or returns the SFX Library.
"""
def getSfx():
    global sfxLib
    if sfxLib == None:
        sfxLib = sfxLibrary()
    return sfxLib
    

########################################################
#                 SETTINGS LOADER                      #
########################################################           
class Settings():
    def __init__(self):
        self.KeyIdMap = {}
        self.KeyNameMap = {}
        for name, value in vars(pygame.constants).items():
            if name.startswith("K_"):
                self.KeyIdMap[value] = name.lower()
                self.KeyNameMap[name.lower()] = value
        
        
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

        self.setting['musicVolume']       = getNumber(self.parser, 'sound', 'musicVolume') / 100.0
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
        
        self.newGamepads = []
        
        self.loadGameSettings(preset)
        self.loadControls()
        
        
    def loadGameSettings(self,preset_suf):
        preset_parser = SafeConfigParser()
        preset_parser.read(os.path.join(os.path.join(self.datadir.replace('main.exe','').replace('main.exe',''),'settings/rules',),preset_suf+'.ini'))
        
        preset = 'preset_' + preset_suf
        self.setting['current_preset'] = preset_suf
        
        self.setting['gravity'] = float(getNumber(preset_parser, preset, 'gravityMultiplier')) / 100
        self.setting['weight'] = float(getNumber(preset_parser, preset, 'weightMultiplier')) / 100
        self.setting['friction'] = float(getNumber(preset_parser, preset, 'frictionMultiplier')) / 100
        self.setting['airControl'] = float(getNumber(preset_parser, preset, 'airControlMultiplier')) / 100
        self.setting['hitstun'] = float(getNumber(preset_parser, preset, 'hitstunMultiplier')) / 100
        self.setting['hitlag'] = float(getNumber(preset_parser, preset, 'hitlagMultiplier')) / 100
        self.setting['shieldStun'] = float(getNumber(preset_parser, preset, 'shieldStunMultiplier')) / 100
        
        self.setting['ledgeConflict'] = getString(preset_parser, preset, 'ledgeConflict')
        sweetSpotDict = {'large': [128,128], 'medium': [64,64], 'small': [32,32]}
        self.setting['ledgeSweetspotSize'] = sweetSpotDict[getString(preset_parser, preset, 'ledgeSweetspotSize')]
        self.setting['ledgeSweetspotForwardOnly'] = getBoolean(preset_parser, preset, 'ledgeSweetspotForwardOnly')
        self.setting['teamLedgeConflict'] = getBoolean(preset_parser, preset, 'teamLedgeConflict')
        self.setting['ledgeInvincibilityTime'] = getNumber(preset_parser, preset, 'ledgeInvincibilityTime')
        self.setting['regrabInvincibility'] = getBoolean(preset_parser, preset, 'regrabInvincibility')
        self.setting['slowLedgeWakeupThreshold'] = getNumber(preset_parser, preset, 'slowLedgeWakeupThreshold')
        
        self.setting['airDodgeType'] = getString(preset_parser, preset, 'airDodgeType')
        self.setting['freeDodgeSpecialFall'] = getBoolean(preset_parser, preset, 'freeDodgeSpecialFall')
        self.setting['enableWavedash'] = getBoolean(preset_parser, preset, 'enableWavedash')        
    
        print(self.setting)
    
    def loadControls(self):
        player_num = 0
        self.getGamepadList(True)
        while self.parser.has_section('controls_' + str(player_num)):
            bindings = {}
            groupName = 'controls_' + str(player_num)
            controlType = self.parser.get(groupName, 'controlType')
            
            self.setting['controlType_'+str(player_num)] = controlType
            try:
                self.setting[controlType]
            except:
                self.setting['controlType_'+str(player_num)] = 'Keyboard'
            
            for opt in self.parser.options(groupName):
                if self.KeyNameMap.has_key(opt):
                    bindings[self.KeyNameMap[opt]] = self.parser.get(groupName, opt)
            self.setting[groupName] = engine.controller.Controller(bindings)
            #self.setting[groupName] = engine.cpuPlayer.CPUplayer(bindings) #Here be CPU players
                    
            player_num += 1
    
    """
    Check all connected gamepads and add them to the settings.
    """
    def loadGamepad(self,controllerName):
        pygame.joystick.init()
        controllerParser = SafeConfigParser()
        controllerParser.read(os.path.join(os.path.join(self.datadir.replace('main.exe',''),'settings'),'gamepads.ini'))
        if controllerParser.has_section(controllerName):
            joystick = None
            for pad in range(pygame.joystick.get_count()):
                joy = pygame.joystick.Joystick(pad)
                if joy.get_name() == controllerName:
                    joystick = joy
                    joystick.init()
            
            if joystick:
                jid = joystick.get_id()
            else:
                jid = None
            
            axes = {}
            buttons = {}
            for opt in controllerParser.options(controllerName):
                if opt[0] == 'a':
                    axes[int(opt[1:])] = tuple(controllerParser.get(controllerName, opt)[1:-1].split(','))
                elif opt[0] == 'b':
                    buttons[int(opt[1:])] = controllerParser.get(controllerName, opt)
        
            pad_bindings = engine.controller.PadBindings(controllerName,jid,axes,buttons)
            return engine.controller.GamepadController(pad_bindings)
        else:
            joystick = None
            for pad in range(pygame.joystick.get_count()):
                joy = pygame.joystick.Joystick(pad)
                if joy.get_name() == controllerName:
                    joystick = joy
                    joystick.init()
            
            if joystick:
                jid = joystick.get_id()
            else:
                jid = None
            
            axes = dict()
            buttons = dict()
            
            pad_bindings = engine.controller.PadBindings(controllerName,jid,axes,buttons)
            self.setting[joystick.get_name()] = pad_bindings
            
            return engine.controller.GamepadController(pad_bindings)
    
    def getGamepadList(self,store=False):
        controllerParser = SafeConfigParser()
        controllerParser.read(os.path.join(os.path.join(self.datadir.replace('main.exe',''),'settings'),'gamepads.ini'))
        controllerList = []
        
        for control in controllerParser.sections():
            controls = self.loadGamepad(control)
            controllerList.append(controls)
            if store: self.setting[control] = controls
            
        retlist = controllerParser.sections()
        retlist.extend(self.newGamepads)
        return retlist
    
    def getGamepadByName(self,joyName):
        for i in range(pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            if joystick.get_name() == joyName:
                return joystick
        return None
"""
Save a modified settings object to the settings.ini file.
"""
def saveSettings(settings):
    keyIdMap = {}
    keyNameMap = {}
    for name, value in vars(pygame.constants).items():
        if name.startswith("K_"):
            keyIdMap[value] = name
            keyNameMap[name] = value
    
    parser = SafeConfigParser()
    
    parser.add_section('window')
    parser.set('window','windowName',str(settings['windowName']))
    parser.set('window','windowSize',str(settings['windowSize']))
    parser.set('window','windowWidth',str(settings['windowSize'][0]))
    parser.set('window','windowHeight',str(settings['windowSize'][1]))
    parser.set('window','frameCap',str(settings['frameCap']))
    
    parser.add_section('sound')
    parser.set('sound','musicVolume',str(settings['sfxVolume'] * 100))
    parser.set('sound','sfxVolume',str(settings['musicVolume'] * 100))
    
    parser.add_section('graphics')
    parser.set('graphics','displayHitboxes',str(settings['showHitboxes']))
    parser.set('graphics','displayHurtboxes',str(settings['showHurtboxes']))
    parser.set('graphics','displaySpriteArea',str(settings['showSpriteArea']))
    parser.set('graphics','displayPlatformLines',str(settings['showPlatformLines']))
    parser.set('graphics','displayECB',str(settings['showECB']))
    
    parser.add_section('playerColors')
    parser.set('playerColors','Player0',str(settings['playerColor0']))
    parser.set('playerColors','Player1',str(settings['playerColor1']))
    parser.set('playerColors','Player2',str(settings['playerColor2']))
    parser.set('playerColors','Player3',str(settings['playerColor3']))
    
    parser.add_section('game')
    parser.set('game','rulePreset',str(settings['current_preset']))
    
    for i in range(0,4):
        sect = 'controls_'+str(i)
        parser.add_section(sect)
        parser.set(sect,'controlType',settings['controlType_'+str(i)])
        for key in settings[sect].key_bindings:
            parser.set(sect,'controlType',settings['controlType_'+str(i)])
            parser.set(sect,keyIdMap[key],str(settings[sect].key_bindings[key]))
            
    with open(os.path.join(getSetting().datadir.replace('main.exe',''),'settings','settings.ini'), 'w') as configfile:
        parser.write(configfile)

    saveGamepad(settings)

def saveGamepad(settings):
    parser = SafeConfigParser()
    for controllerName in getSetting().getGamepadList():
        gamepad = getSetting(controllerName)
        if not parser.has_section(controllerName):
            parser.add_section(controllerName)
        
        for key,value in gamepad.pad_bindings.axis_bindings.iteritems():
            neg,pos = value
            if not neg: neg = 'none'
            if not pos: pos = 'none'
            parser.set(controllerName,'a'+str(key),'('+str(neg)+','+str(pos)+')' )
        
        for key,value in gamepad.pad_bindings.button_bindings.iteritems():
            parser.set(controllerName,'b'+str(key),str(value))
            
    with open(os.path.join(getSetting().datadir.replace('main.exe',''),'settings','gamepads.ini'), 'w') as configfile:
        parser.write(configfile)

        
def savePreset(settings, preset):
    parser = SafeConfigParser()
    
    parser.set(preset,'gravityMultiplier',settings['gravity'] * 100)
    parser.set(preset,'weightMultiplier',settings['weight'] * 100)
    parser.set(preset,'frictionMultiplier',settings['friction'] * 100)
    parser.set(preset,'airControlMultiplier',settings['airControl'] * 100)
    parser.set(preset,'hitstunMultiplier',settings['hitstun'] * 100)
    parser.set(preset,'hitlagMultiplier',settings['hitlag'] * 100)
    parser.set(preset,'shieldStunMultiplier',settings['shieldStun'] * 100)
    
    parser.set(preset,'ledgeConflict',settings['ledgeConflict'])
    sweetSpotDict = {[128,128]: 'large', [64,64]: 'medium', [32,32]: 'small'}
    parser.set(preset,'ledgeSweetspotSize',sweetSpotDict[settings['ledgeSweetspotSize']])
    parser.set(preset,'ledgeSweetspotForwardOnly',settings['ledgeSweetspotForwardOnly'])
    parser.set(preset,'teamLedgeConflict',settings['teamLedgeConflict'])
    parser.set(preset,'ledgeInvincibilityTime',settings['ledgeInvincibilityTime'])
    parser.set(preset,'regrabInvincibility',settings['regrabInvincibility'])
    parser.set(preset,'slowLedgeWakeupThreshold',settings['slowLedgeWakeupThreshold'])
    
    parser.set(preset,'airDodgeType',settings['airDodgeType'])
    parser.set(preset,'freeDodgeSpecialFall',settings['freeDodgeSpecialFall'])
    parser.set(preset,'enableWavedash',settings['enableWavedash'])
    
    parser.write(os.path.join(settings.datadir.replace('main.exe',''),'settings.ini'))
    
"""
The SFXLibrary object contains a dict of all sound effects that are being used.
It handles the playing of the sounds.
"""                    
class sfxLibrary():
    def __init__(self):
        self.sounds = {}
        self.supportedFileTypes = ['.wav', '.ogg']
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
            if self.supportedFileTypes.count(ext):
                self.sounds["base_" + fname] = pygame.mixer.Sound(os.path.join(directory,f)) 
                
    def playSound(self,name,category = "base"):
        print(category,name,getSetting().setting['sfxVolume'])
        self.sounds[category + "_" + name].set_volume(getSetting().setting['sfxVolume'])
        self.sounds[category + "_" + name].play()
    
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
    def addSoundsFromDirectory(self,path,category):
        for f in os.listdir(path):
            fname, ext = os.path.splitext(f)
            if self.supportedFileTypes.count(ext):
                self.sounds[category + "_" + fname] = pygame.mixer.Sound(os.path.join(path,f))
                print(category + "_" + fname,self.sounds[category + "_" + fname])
                
    
########################################################
#             STATIC HELPER FUNCTIONS                  #
########################################################
"""
When given a string representation of numbers, parse it and return
the actual numbers. If Many is given, the parser will look
for all numbers and return them in a list, otherwise, it will get the
first number.
"""
def getNumbersFromString(string, many = False):
    if many:
        return list(map(int, re.findall(r'\d+', string)))
    else:
        return int(re.search(r'\d+', string).group())

"""
Convert basically whatever stupid thing people could possibly think to mean "yes" into
a True boolean. If it's not True, it's false, so feel free to set some of those debug
options to "Eat a dick" if you want to, it'll read as False
"""
def boolean(string):
    # Well, I already have the function made, might as well cover all the bases.
    return string in ['true', 'True', 't', 'T', '1', '#T', 'y', 'yes', 'on', 'enabled']

"""
A wrapper that'll get a lowercase String from the parser, or return gracefully with an error.
"""    
def getString(parser,preset,key):
    try:
        return str(parser.get(preset,key).lower())
    except Exception as e:
        print(e)
        return ""

"""
A wrapper that'll get a boolean from the parser, or return gracefully with an error.
"""
def getBoolean(parser,preset,key):
    try:
        return boolean(parser.get(preset,key))
    except Exception as e:
        print(e)
        return False

"""
A wrapper that'll get a number from the parser, or return gracefully with an error.
"""    
def getNumber(parser,preset,key,islist = False):
    try:
        return getNumbersFromString(parser.get(preset,key),islist)
    except Exception as e:
        print(e)
        return 0

"""
Main method for debugging purposes
"""
def test():
    print(getSetting().setting)
    

if __name__  == '__main__': test()

