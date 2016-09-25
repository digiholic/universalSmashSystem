import sys
import pdb
import io
import StringIO
import settingsManager
import spriteManager
import pygame

class debugConsole(pdb.Pdb):
    def __init__(self, _font="joystix monospace", _size=12, _height=8):
        self.input_hold = StringIO.StringIO()
        self.output_hold = StringIO.StringIO()
        pdb.Pdb.__init__(self, stdout=self.output_hold)
        self.prompt = "> "
        text_dims = pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size).size(" ") #Used to determine how much space is available
        self.backing = settingsManager.rectSprite([0, pygame.display.get_height()-int(_height*text_dims[1])], [pygame.display.get_width(), int(_height*text_dims[1]]), [0,0,0])
        self.display_text = [spriteManager.TextSprite("", _font, _size, [255, 255, 255])]*_height
        self.text_width = int(pygame.display.get_width()/self.text_dims[0])

    def acceptInput(self, _keyName):
        mods = pygame.key.get_mods()
        char_to_write = '\0'
        if len(_keyName) == 1:
            if _keyName in string.letters:
                if mods & (pygame.key.KMOD_SHIFT ^ pygame.key.KMOD_CAPS): # != 0
                    char_to_write = string.upper(_keyName)
                else:
                    char_to_write = _keyName
            elif _keyName in string.numbers:
                if mods & (pygame.key.KMOD_SHIFT): # != 0
                    if _keyName == '1': char_to_write = '!'
                    elif _keyName == '2': char_to_write = '@'
                    elif _keyName == '3': char_to_write = '#'
                    elif _keyName == '4': char_to_write = '$'
                    elif _keyName == '5': char_to_write = '%'
                    elif _keyName == '6': char_to_write = '^'
                    elif _keyName == '7': char_to_write = '&'
                    elif _keyName == '8': char_to_write = '*'
                    elif _keyName == '9': char_to_write = '('
                    elif _keyName == '0': char_to_write = ')'
                else:
                    char_to_write = _keyName
            
            
