import sys
import io
import settingsManager
import spriteManager
import pygame
import pygcurse

class textEntry(pygcurse.PygcurseSurface):
    def __init__(self, _surface, _font="unifont-9.0.02", _size=16, _length=10, _corner = (0, 0)):
        text_dims = pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size).size(" ") #Used to determine how much space is available
        self.text_height = int(_surface.get_width()/text_dims[1])
        self.corner = _corner
        pygcurse.PygcurseSurface.__init__(self, _length, 1, pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size))
        self.setscreencolors(fgcolor='black', bgcolor='white', clear=True)
        self.input_obj = pygcuse.PygcurseInput(self, maxlength=_length)

    def display(self):
        self.update()
        self.blitto(self.game_env.screen, self.corner)

    def setValue(self, _value):
        self.input_obj.buffer = list(_value)
        self.input_obj.update()

    def getValue(self, _value):
        return "".join(input_obj.buffer)

    def keyCapture(self, _keyEvent):
        """Obtain a key event. Returns true if focus should be maintained, false if it should be lost"""
        if _keyEvent.type == pygame.key.KEY_DOWN and _keyEvent.key in [pygame.key.K_ESCAPE, pygame.key.K_UP, pygame.key.K_DOWN, pygame.key.K_HOME, pygame.key.K_END, pygame.key.K_PAGEUP, pygame.key.K_PAGEDOWN]:
            return False
        elif _keyEvent.type == pygame.key.KEY_UP and _keyEvent.key == pygame.key.K_RETURN:
            return False
        else:
            self.input_obj.sendkeyevent(_keyEvent)
            return True
            

