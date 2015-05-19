import pygame.constants
import re
import os
import imp
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
    return os.path.join(os.path.dirname(__file__),path)

"""
This function imports a module from it's file path.
It returns the imported module.


"""
#TODO refactor the variables to make this less confusing
def importFromURI(filePath, uri, absl=False, suffix=""):
    if not absl:
        uri = os.path.normpath(os.path.join(os.path.dirname(filePath), uri))
    path, fname = os.path.split(uri)
    mname, ext = os.path.splitext(fname)
    
    no_ext = os.path.join(path, mname)
         
    if os.path.exists(no_ext + '.py'):
        try:
            return imp.load_source((mname + suffix), no_ext + '.py')
        except Exception as e:
            print mname, e

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
Gets the Keybindings object for the given playerNum.

If it can't find those controls, it'll make a blank Keybinding
"""
def getControls(playerNum):
    global settings
    if settings == None:
        settings = Settings()
    
    try:
        return settings.setting['controls_' + str(playerNum)]
    except:
        settings.setting['controls_' + str(playerNum)] = Keybindings({
                                                          'left': None,
                                                          'right': None,
                                                          'up': None,
                                                          'down': None,
                                                          'jump': None,
                                                          'attack': None,
                                                          'shield': None
                                                          })
        
        return settings.setting['controls_' + str(playerNum)]
        
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
        for name, value in vars(pygame.constants).iteritems():
            if name.startswith("K_"):
                self.KeyIdMap[value] = name
                self.KeyNameMap[name] = value
        
        
        parser = SafeConfigParser()
        parser.read(os.path.join(os.path.dirname(__file__),'settings.ini'))
        
        self.setting = {}
        
        # Getting the window information
        
        self.setting['windowName']    = getString(parser,'window','windowName')
        self.setting['windowSize']    = getNumber(parser, 'window', 'windowSize',True) 
        self.setting['windowWidth']   = self.setting['windowSize'][0]
        self.setting['windowHeight']  = self.setting['windowSize'][1]
        self.setting['frameCap']      = getNumber(parser, 'window', 'frameCap')
        
        self.setting['showHitboxes']  = getBoolean(parser, 'graphics', 'displayHitboxes')
        self.setting['showHurtboxes'] = getBoolean(parser,'graphics','displayHurtboxes')
        self.setting['showSpriteArea'] = getBoolean(parser,'graphics','displaySpriteArea')
        
        self.setting['playerColor0'] = getString(parser, 'playerColors', 'player0')
        self.setting['playerColor1'] = getString(parser, 'playerColors', 'player1')
        self.setting['playerColor2'] = getString(parser, 'playerColors', 'player2')
        self.setting['playerColor3'] = getString(parser, 'playerColors', 'player3')
        # Getting game information
        
        # The "preset" lets users define custom presets to switch between.
        # The "custom" preset is one that is modified in-game.
        preset = parser.get('game','rulePreset')
        self.loadGameSettings(parser,preset)
        self.loadGamepads()
        self.loadControls(parser)
        
    def loadGameSettings(self,parser,preset):
        self.setting['gravity'] = float(getNumber(parser, preset, 'gravityMultiplier'))
        self.setting['weight'] = float(getNumber(parser, preset, 'weightMultiplier'))
        self.setting['friction'] = float(getNumber(parser, preset, 'frictionMultiplier'))
        self.setting['airControl'] = float(getNumber(parser, preset, 'airControlMultiplier'))
        self.setting['hitstun'] = float(getNumber(parser, preset, 'hitstunMultiplier'))
        self.setting['hitlag'] = float(getNumber(parser, preset, 'hitlagMultiplier'))
        
        self.setting['ledgeConflict'] = getString(parser, preset, 'ledgeConflict')
        sweetSpotDict = {'large': [128,128], 'medium': [64,64], 'small': [32,32]}
        self.setting['ledgeSweetspotSize'] = sweetSpotDict[getString(parser, preset, 'ledgeSweetspotSize')]
        self.setting['ledgeSweetspotForwardOnly'] = getBoolean(parser, preset, 'ledgeSweetspotForwardOnly')
        self.setting['teamLedgeConflict'] = getBoolean(parser, preset, 'teamLedgeConflict')
        self.setting['ledgeInvincibilityTime'] = getNumber(parser, preset, 'ledgeInvincibilityTime')
        self.setting['regrabInvincibility'] = getBoolean(parser, preset, 'regrabInvincibility')
        self.setting['slowLedgeWakeupThreshold'] = getNumber(parser, preset, 'slowLedgeWakeupThreshold')
        
        self.setting['airDodgeType'] = getString(parser, preset, 'airDodgeType')
        self.setting['freeDodgeSpecialFall'] = getBoolean(parser, preset, 'freeDodgeSpecialFall')
        self.setting['enableWavedash'] = getBoolean(parser, preset, 'enableWavedash')        
    
    def loadControls(self,parser):
        playerNum = 0
        while parser.has_section('controls_' + str(playerNum)):
            bindings = {}
            groupName = 'controls_' + str(playerNum)
            controlType = parser.get(groupName, 'controlType')
            if controlType == 'gamepad': # If the controls are set to Gamepad
                gamepadName = parser.get(groupName, 'gamepad')
                if gamepadName in self.setting['controllers']: # Check if that Gamepad is connected
                    print "okay", gamepadName
                    bindings = {
                        getGamepadTuple(parser, gamepadName, 'left') : 'left',
                        getGamepadTuple(parser, gamepadName, 'right') : 'right',
                        getGamepadTuple(parser, gamepadName, 'up') : 'up',
                        getGamepadTuple(parser, gamepadName, 'down') : 'down',
                        getGamepadTuple(parser, gamepadName, 'attack') : 'attack',
                        getGamepadTuple(parser, gamepadName, 'special') : 'special',
                        getGamepadTuple(parser, gamepadName, 'jump') : 'jump',
                        getGamepadTuple(parser, gamepadName, 'shield') : 'shield',
                        }
                else: # If it is not connected, use the buttons instead.
                    print "error", gamepadName
                    bindings = {}
            
            # If the bindings are empty (as in, not set by the Gamepad)
            if bindings == {}:
                bindings = {
                        self.KeyNameMap[parser.get(groupName, 'left')] : 'left',
                        self.KeyNameMap[parser.get(groupName, 'right')] : 'right',
                        self.KeyNameMap[parser.get(groupName, 'up')] : 'up',
                        self.KeyNameMap[parser.get(groupName, 'down')] : 'down',
                        self.KeyNameMap[parser.get(groupName, 'jump')] : 'jump',
                        self.KeyNameMap[parser.get(groupName, 'attack')] : 'attack',
                        self.KeyNameMap[parser.get(groupName, 'shield')] : 'shield'
                        }
            self.setting[groupName] = Keybindings(bindings)
            playerNum += 1
    
    """
    Check all connected gamepads and add them to the settings.
    """
    def loadGamepads(self):
        pygame.joystick.init()
        self.joysticks = []
        for i in range(0, pygame.joystick.get_count()):
            self.joysticks.append(pygame.joystick.Joystick(i).get_name())
        self.setting['controllers'] = self.joysticks



"""
The Keybindings object is just a shorthand for looking up
the keys in the game settings. A dictionary is passed
that maps the action to the key that does it.
"""
class Keybindings():
    
    def __init__(self,keyBindings):
        self.keyBindings = keyBindings
        
    def get(self,key):
        return self.keyBindings.get(key)
    

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
        self.sounds[category + "_" + name].play()
    
    """
    This is called to add a directory of sound effects to the library.
    It is usually called when loading a fighter or a stage.
    """
    def addSoundsFromDirectory(self,path,category):
        for f in os.listdir(path):
            fname, ext = os.path.splitext(f)
            if self.supportedFileTypes.count(ext):
                self.sounds[category + "_" + fname] = pygame.mixer.Sound(os.path.join(path,f))
        
    
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
        return map(int, re.findall(r'\d+', string))
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
        return parser.get(preset,key).lower()
    except Exception,e:
        print e
        return ""

"""
A wrapper that'll get a boolean from the parser, or return gracefully with an error.
"""
def getBoolean(parser,preset,key):
    try:
        return boolean(parser.get(preset,key))
    except Exception,e:
        print e
        return False

"""
A wrapper that'll get a number from the parser, or return gracefully with an error.
"""    
def getNumber(parser,preset,key,islist = False):
    try:
        return getNumbersFromString(parser.get(preset,key),islist)
    except Exception,e:
        print e
        return 0

"""
A wrapper that'll get a Gamepad Tuple from the parser, or return gracefully with an error.

A Gamepad Tuple is in the form of (type, id[, value])
If type is button, id is the number of the button on that pad.
If type is axis, the id is that axis, and value is + or - depending on which direction
corresponds to that item.
"""
def getGamepadTuple(parser,preset,key):
    try:
        joyInfo = parser.get(preset,key).split(' ')
        if len(joyInfo) < 3: joyInfo.append('')
        return (joyInfo[0], getNumbersFromString(joyInfo[1],False),joyInfo[2]) 
    except Exception,e:
        print e
        return ("",0)

"""
Main method for debugging purposes
"""
def test():
    print getSetting().setting
    

if __name__  == '__main__': test()