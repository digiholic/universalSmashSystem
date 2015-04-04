import pygame.constants
import re
from ConfigParser import SafeConfigParser

settings = None

def getSetting(key = None):
    global settings
    if settings == None:
        settings = Settings()
    
    if key:
        return settings.setting[key]
    else:
        return settings

def main():
    print getSetting().setting
    
def getNumbersFromString(string, many = False):
    if many:
        return map(int, re.findall(r'\d+', string))
    else:
        return int(re.search(r'\d+', string).group())

class Settings():
    def __init__(self):
        self.KeyIdMap = {}
        self.KeyNameMap = {}
        for name, value in vars(pygame.constants).iteritems():
            if name.startswith("K_"):
                self.KeyIdMap[value] = name
                self.KeyNameMap[name] = value
        
        
        parser = SafeConfigParser()
        parser.read('settings.ini')
        
        self.setting = {}
        
        # Getting the window information
        size = parser.get('window', 'windowSize')
        
        self.setting['windowName']   = parser.get('window', 'windowName')
        self.setting['windowSize']   = getNumbersFromString(size,True)
        self.setting['windowWidth']  = self.setting['windowSize'][0]
        self.setting['windowHeight'] = self.setting['windowSize'][1]
        self.setting['frameCap']     = getNumbersFromString(parser.get('window', 'frameCap'))
        
        # Getting game information
        
        # The "preset" lets users define custom presets to switch between.
        # The "custom" preset is one that is modified in-game.
        preset = parser.get('game','rulePreset')
        self.loadGameSettings(parser,preset)
        self.loadControls(parser)
        
    def loadGameSettings(self,parser,preset):
        self.setting['gravityMultiplier'] = parser.get(preset, 'gravityMultiplier')
        self.setting['weightMultiplier'] = parser.get(preset, 'weightMultiplier')
        
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

        
if __name__  == '__main__': main()