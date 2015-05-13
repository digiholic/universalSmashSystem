import pygame.constants
import re
import os
import imp
from ConfigParser import SafeConfigParser

settings = None
sfxLib = None

def getSetting(key = None):
    global settings
    if settings == None:
        settings = Settings()
        return settings
    if key:
        return settings.setting[key]
    else:
        return settings

def getControls(playerNum):
    global settings
    if settings == None:
        settings = Settings()
    
    try:
        return settings.setting['controls_' + str(playerNum)]
    except:
        settings.setting['controls_' + str(playerNum)] = {
                                                          'left': None,
                                                          'right': None,
                                                          'up': None,
                                                          'down': None,
                                                          'jump': None,
                                                          'attack': None,
                                                          'shield': None
                                                          }
        
        return settings.setting['controls_' + str(playerNum)]
        
def getSfx():
    global sfxLib
    if sfxLib == None:
        sfxLib = sfxLibrary()
    return sfxLib
    
def createPath(path):
    return os.path.join(os.path.dirname(__file__),path)

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
        
        self.setting['windowName']    = self.getString(parser,'window','windowName')
        self.setting['windowSize']    = self.getNumber(parser, 'window', 'windowSize',True) 
        self.setting['windowWidth']   = self.setting['windowSize'][0]
        self.setting['windowHeight']  = self.setting['windowSize'][1]
        self.setting['frameCap']      = self.getNumber(parser, 'window', 'frameCap')
        
        self.setting['showHitboxes']  = self.getBoolean(parser, 'graphics', 'displayHitboxes')
        self.setting['showHurtboxes'] = self.getBoolean(parser,'graphics','displayHurtboxes')
        self.setting['showSpriteArea'] = self.getBoolean(parser,'graphics','displaySpriteArea')
        
        self.setting['playerColor0'] = self.getString(parser, 'playerColors', 'player0')
        self.setting['playerColor1'] = self.getString(parser, 'playerColors', 'player1')
        self.setting['playerColor2'] = self.getString(parser, 'playerColors', 'player2')
        self.setting['playerColor3'] = self.getString(parser, 'playerColors', 'player3')
        # Getting game information
        
        # The "preset" lets users define custom presets to switch between.
        # The "custom" preset is one that is modified in-game.
        preset = parser.get('game','rulePreset')
        self.loadGameSettings(parser,preset)
        self.loadGamepads()
        self.loadControls(parser)
        
    def loadGameSettings(self,parser,preset):
        self.setting['gravity'] = float(self.getNumber(parser, preset, 'gravityMultiplier'))
        self.setting['weight'] = float(self.getNumber(parser, preset, 'weightMultiplier'))
        self.setting['friction'] = float(self.getNumber(parser, preset, 'frictionMultiplier'))
        self.setting['airControl'] = float(self.getNumber(parser, preset, 'airControlMultiplier'))
        self.setting['hitstun'] = float(self.getNumber(parser, preset, 'hitstunMultiplier'))
        self.setting['hitlag'] = float(self.getNumber(parser, preset, 'hitlagMultiplier'))
        
        self.setting['ledgeConflict'] = self.getString(parser, preset, 'ledgeConflict')
        sweetSpotDict = {'large': [128,128], 'medium': [64,64], 'small': [32,32]}
        self.setting['ledgeSweetspotSize'] = sweetSpotDict[self.getString(parser, preset, 'ledgeSweetspotSize')]
        self.setting['ledgeSweetspotForwardOnly'] = self.getBoolean(parser, preset, 'ledgeSweetspotForwardOnly')
        self.setting['teamLedgeConflict'] = self.getBoolean(parser, preset, 'teamLedgeConflict')
        self.setting['ledgeInvincibilityTime'] = self.getNumber(parser, preset, 'ledgeInvincibilityTime')
        self.setting['regrabInvincibility'] = self.getBoolean(parser, preset, 'regrabInvincibility')
        self.setting['slowLedgeWakeupThreshold'] = self.getNumber(parser, preset, 'slowLedgeWakeupThreshold')
        
        self.setting['airDodgeType'] = self.getString(parser, preset, 'airDodgeType')
        self.setting['freeDodgeSpecialFall'] = self.getBoolean(parser, preset, 'freeDodgeSpecialFall')
        self.setting['enableWavedash'] = self.getBoolean(parser, preset, 'enableWavedash')
    
    def getString(self,parser,preset,key):
        try:
            return parser.get(preset,key).lower()
        except Exception,e:
            print e
            return ""
    
    def getBoolean(self,parser,preset,key):
        try:
            return boolean(parser.get(preset,key))
        except Exception,e:
            print e
            return False
        
    def getNumber(self,parser,preset,key,islist = False):
        try:
            return getNumbersFromString(parser.get(preset,key),islist)
        except Exception,e:
            print e
            return 0
        
    def loadControls(self,parser):
        playerNum = 0
        while parser.has_section('controls_' + str(playerNum)):
            groupName = 'controls_' + str(playerNum)
            controlType = self.getString(parser, groupName, 'controlType')
            if controlType == 'gamepad':
                gamepadName = self.getString(parser, groupName, 'gamepad')
                if gamepadName in self.setting['controllers']:
                    print "okay", gamepadName
                else:
                    print "error", gamepadName
        
            bindings = {
                'left': self.KeyNameMap[parser.get(groupName, 'left')],
                'right': self.KeyNameMap[parser.get(groupName, 'right')],
                'up': self.KeyNameMap[parser.get(groupName, 'up')],
                'down': self.KeyNameMap[parser.get(groupName, 'down')],
                'jump': self.KeyNameMap[parser.get(groupName, 'jump')],
                'attack': self.KeyNameMap[parser.get(groupName, 'attack')],
                'shield': self.KeyNameMap[parser.get(groupName, 'shield')]
                }
            self.setting[groupName] = Keybindings(bindings)
            playerNum += 1
            
    def loadGamepads(self):
        pygame.joystick.init()
        self.joysticks = []
        for i in range(0, pygame.joystick.get_count()):
            self.joysticks.append(pygame.joystick.Joystick(i).get_name().lower())
        self.setting['controllers'] = self.joysticks

"""
The Keybindings object is just a shorthand for looking up
the keys in the game settings. A dictionary is passed
that maps the action to the key that does it.
"""
class Keybindings():
    
    def __init__(self,keyBindings):
        self.keyBindings = keyBindings
        self.k_left = self.keyBindings.get('left')
        self.k_right = self.keyBindings.get('right')
        self.k_up = self.keyBindings.get('up')
        self.k_down = self.keyBindings.get('down')
        self.k_jump = self.keyBindings.get('jump')
        self.k_attack = self.keyBindings.get('attack')
        self.k_shield = self.keyBindings.get('shield')
        
                    
class sfxLibrary():
    def __init__(self):
        self.sounds = {}
        supportedFileTypes = ['.wav', '.ogg']
        directory = createPath("sfx")
        
        for f in os.listdir(directory):
            fname, ext = os.path.splitext(f)
            if supportedFileTypes.count(ext):
                self.sounds[fname] = pygame.mixer.Sound(os.path.join(directory,f))
        print "sounds: ", self.sounds
                
    def playSound(self,name):
        self.sounds[name].play()
        
def main():
    print getSetting().setting
    
def getNumbersFromString(string, many = False):
    if many:
        return map(int, re.findall(r'\d+', string))
    else:
        return int(re.search(r'\d+', string).group())

def boolean(string):
    # Well, I already have the function made, might as well cover all the bases.
    return string in ['true', 'True', 't', 'T', '1', '#T', 'y', 'yes', 'on', 'enabled']
    
        
if __name__  == '__main__': main()