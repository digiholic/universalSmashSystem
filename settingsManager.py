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
        size = parser.get('window', 'windowSize')
        
        self.setting['windowName']    = parser.get('window', 'windowName')
        self.setting['windowSize']    = getNumbersFromString(size,True)
        self.setting['windowWidth']   = self.setting['windowSize'][0]
        self.setting['windowHeight']  = self.setting['windowSize'][1]
        self.setting['frameCap']      = getNumbersFromString(parser.get('window', 'frameCap'))
        
        self.setting['showHitboxes']  = boolean(parser.get('graphics','displayHitboxes'))
        self.setting['showHurtboxes'] = boolean(parser.get('graphics','displayHurtboxes'))
        self.setting['showSpriteArea'] = boolean(parser.get('graphics','displaySpriteArea'))
        
        # Getting game information
        
        # The "preset" lets users define custom presets to switch between.
        # The "custom" preset is one that is modified in-game.
        preset = parser.get('game','rulePreset')
        self.loadGameSettings(parser,preset)
        self.loadControls(parser)
        
    def loadGameSettings(self,parser,preset):
        self.setting['gravity'] = parser.get(preset, 'gravityMultiplier')
        self.setting['weight'] = parser.get(preset, 'weightMultiplier')
        self.setting['friction'] = parser.get(preset, 'frictionMultiplier')
        self.setting['airControl'] = parser.get(preset, 'airControlMultiplier')
        self.setting['hitstun'] = parser.get(preset, 'hitstunMultiplier')
        self.setting['hitlag'] = parser.get(preset, 'hitlagMultiplier')
        
        self.setting['ledgeConflict'] = parser.get(preset, 'ledgeConflict')
        self.setting['ledgeSweetspotSize'] = parser.get(preset, 'ledgeSweetspotSize')
        self.setting['ledgeSweetspotForwardOnly'] = boolean(parser.get(preset, 'ledgeSweetspotForwardOnly'))
        self.setting['teamLedgeConflict'] = boolean(parser.get(preset, 'teamLedgeConflict'))
        self.setting['ledgeInvincibilityTime'] = getNumbersFromString(parser.get(preset, 'ledgeInvincibilityTime'))
        self.setting['regrabInvincibility'] = boolean(parser.get(preset, 'regrabInvincibility'))
        self.setting['slowLedgeWakeupThreshold'] = getNumbersFromString(parser.get(preset, 'slowLedgeWakeupThreshold'))
        
        self.setting['airDodgeType'] = parser.get(preset, 'airDodgeType')
        self.setting['freeDodgeSpecialFall'] = boolean(parser.get(preset, 'freeDodgeSpecialFall'))
        self.setting['directionalDodgeWavedash'] = boolean(parser.get(preset, 'directionalDodgeWavedash'))


        
    def loadControls(self,parser):
        playerNum = 0
        while parser.has_section('controls_' + str(playerNum)):
            groupName = 'controls_' + str(playerNum)
            bindings = {
                'left': self.KeyNameMap[parser.get(groupName, 'left')],
                'right': self.KeyNameMap[parser.get(groupName, 'right')],
                'up': self.KeyNameMap[parser.get(groupName, 'up')],
                'down': self.KeyNameMap[parser.get(groupName, 'down')],
                'jump': self.KeyNameMap[parser.get(groupName, 'jump')],
                'attack': self.KeyNameMap[parser.get(groupName, 'attack')],
                'shield': self.KeyNameMap[parser.get(groupName, 'shield')]
                }
            self.setting[groupName] = bindings
            playerNum += 1

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
        

        
if __name__  == '__main__': main()