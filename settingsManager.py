import pygame
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
    
class Settings():
    def __init__(self):
        parser = SafeConfigParser()
        parser.read('settings.ini')
        
        self.setting = {}
        
        # Getting the window information
        size = parser.get('window', 'windowSize')
        
        self.setting['windowName']   = parser.get('window', 'windowName')
        self.setting['windowSize']   = self.getNumbersFromString(size,True)
        self.setting['windowWidth']  = self.setting['windowSize'][0]
        self.setting['windowHeight'] = self.setting['windowSize'][1]
        self.setting['frameCap']     = self.getNumbersFromString(parser.get('window', 'frameCap'))
        
        # Getting game information
        
        # The "preset" lets users define custom presets to switch between.
        # The "custom" preset is one that is modified in-game.
        preset = parser.get('game','rulePreset')
        
        self.setting['gravityMultiplier'] = parser.get(preset, 'gravityMultiplier')
        self.setting['weightMultiplier'] = parser.get(preset, 'weightMultiplier')
        
        
        
    def getNumbersFromString(self,string, many = False):
        if many:
            return map(int, re.findall(r'\d+', string))
        else:
            return int(re.search(r'\d+', string).group())
        
if __name__  == '__main__': main()