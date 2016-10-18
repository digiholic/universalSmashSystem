import sys
import io
import settingsManager
import spriteManager
import pygame
import pygcurse
import difflib

"""A persistent text box object, which can be inputted to."""
class textEntry(pygcurse.PygcurseSurface):
    def __init__(self, _surface, _font="unifont-9.0.02", _size=16, _length=20, _corner = (0, 0)):
        self.screen = _surface
        self.corner = _corner
        pygcurse.PygcurseSurface.__init__(self, _length, 1, pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size))
        self.setscreencolors(fgcolor='black', bgcolor='white', clear=True)
        self.input_obj = pygcuse.PygcurseInput(self)
        self.input_obj.multiline = False
        self.active = True

    def display(self):
        self.input_obj.update()
        self.update()
        self.blitto(self.screen, self.corner)

    def setValue(self, _value):
        self.input_obj.buffer = list(_value)

    def getValue(self, _value):
        return "".join(input_obj.buffer)

    def deactivate(self):
        self.active = False
        self.setfgcolor(pygame.Color(63, 63, 63))

    def reactivate(self):
        self.active = True
        self.setfgcolor()

    def keyCapture(self, _event):
        """Process a key event. Returns true if focus should be maintained, false if it should be lost"""
        if not self.active:
            return False
        elif _event.type == pygame.KEYDOWN and _event.key in [pygame.key.K_ESCAPE, pygame.key.K_UP, pygame.key.K_DOWN, pygame.key.K_HOME, pygame.key.K_END, pygame.key.K_PAGEUP, pygame.key.K_PAGEDOWN]:
            return False
        elif _event.type == pygame.KEYUP and _event.key == pygame.key.K_RETURN:
            return False
        else:
            self.input_obj.sendkeyevent(_event)
            return True

    def mouseCapture(self, _event):
        """Process a mouse event. Returns true if focus should be maintained, false if it should be lost"""
        if not self.active:
            return False
        elif _event.type == pygame.MOUSEBUTTONDOWN and self._windowsurface.get_rect(topleft=self.corner).collidepoint(_event.get_pos):
            #TODO: Add code to adjust cursor position based on mouse position
            return True
        elif _event.type == pygame.MOUSEBUTTONDOWN
            return False
        else
            return True
            
"""A temporary drop-down menu. Appears when created, should disappear when a choice is made"""
class searchOption(pygcurse.PygcurseSurface):
    def __init__(self, _surface, _parent, _font="unifont-9.0.02", _size=16, _length=20, _height=29, _corner=(0, 0), _options=None):
        self.screen = _surface
        self.parent = _parent
        self.corner = _corner
        self.selection_height = _height-2
        pygcurse.PygcurseSurface.__init__(self, _length, _height, pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size))
        self.setscreencolors(fgcolor='black', bgcolor='white', clear=True)
        self.current_selection = 0
        if _options is not None:
            self.options = _options
        else
            self.options = list()

    def display(self):
        # The design of the display is that the current selection is centered whenever possible. 
        # The selection view ranges from 0 to self.selection_height-1, and we want to position
        # the selection at self.selection_height//2. 
        if len(self.options) == 0:
            self.setscreencolors(clear=True)
            self.putchars(("▲"*self._width)[:self._width], x=0, y=0)
            self.putchars(("▼"*self._width)[:self._width], x=0, y=self.selection_height+1)
            self.setfgcolor(pygame.Color(63, 63, 63), region=(0, 0, self._width, 1)
            self.setfgcolor(pygame.color(63, 63, 63), region=(0, self.selection_height+1, self._width, 1)
            
        else:
            self.uppermargin = self.current_selection-self.selection_height//2
            self.lowermargin = self.current_selection-self.selection_height+self.selection_height//2
            if self.uppermargin < 0:
                select_pos = self.current_selection
                lowest_index = 0
                topped_out = True
                if len(self.options) == 1: bottomed_out = True
                else: bottomed_out = False
            elif self.lowermargin >= self.selection_height:
                select_pos = self.current_selection-len(self.options)+self.selection_height
                lowest_index = len(self.options)-self.selection_height
                topped_out = False
                bottomed_out = True
            else
                select_pos = self.selection_height//2
                lowest_index = self.current_selection-self.selection_height//2
            
            #Now actually place chars
            self.setscreencolors(clear=True)
            
            self.putchars(("▲"*self._width)[:self._width], x=0, y=0)
            for line in range(self.selection_height):
                if (line+lowest_index) >= 0 and (line+lowest_index) < len(self.options):
                    for index in range(len(self.options[line+lowest_index])):
                        self.putchar(self.options[line+lowest_index][index], x=index, y=line+lowest_index+1)
            self.putchars(("▼"*self._width)[:self._width], x=0, y=self.selection_height+1)

            if topped_out: self.setfgcolor(pygame.Color(63, 63, 63), region=(0, 0, self._width, 1)
            if bottomed_out: self.setfgcolor(pygame.color(63, 63, 63), region=(0, self.selection_height+1, self._width, 1)
            self.reversecolors(self, region=(0, select_pos+1, self._width, 1)
        
        self.update()
        self.blitto(self.screen, self.corner)

    """
    Returns the closest match in options to the given key. 
    Probably should be overridden if needed. 
    """
    def autoSelect(self, _key=""):
        wordlist = difflib.get_close_matches(_key, self.options, n=1, cuttoff=0)
        if len(wordlist) == 0:
            return 0
        else
            return self.options.index(wordlist[0])

    def updateList(self, _newOptions=None):
        #Try to preserve current selection positioning
        current_selection_text = self.options[self.current_selection]
        if _newOptions is not None:
            self.options = _newOptions
        else
            self.options = list()
        if current_selection_text not in self.options:
            self.current_selection = self.autoSelect(current_selection_text)

    #cdef keyCapture(self, _event):
    
