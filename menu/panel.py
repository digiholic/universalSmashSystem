import sys
import io
import settingsManager
import spriteManager
import pygame
import pygcurse
import difflib

"""
This is the base UI element that everything else is based upon. It can also be initialized directly to obtain a boring ol' rectangle, with or without text. 
"""
class panel(pygcurse.PygcurseTextbox):
    def __init__(self, _surface, _parent=None, _region=(0,0,0,0), **kwargs):
        self.parent = _parent
        if _parent is not None:
            _region = (_region[0]+_parent.x, _region[1]+_parent.y, _region[2], _region[3])
            _parent.children.append(self)
            bgcolor = _parent.bgcolor-pygame.Color(16, 16, 16)
        else:
            bgcolor = _surface._bgcolor-pygame.Color(16, 16, 16)
        if bgcolor.r+bgcolor.g+bgcolor.b <= 381:
            fgcolor = pygame.Color(255, 255, 255)
        else:
            fgcolor = pygame.Color(0, 0, 0)
        pygcurse.PygcurseTextbox.__init__(self, _surface, _region, border=None, fgcolor=fgcolor, bgcolor=bgcolor, **kwargs) #Who knows? Maybe we want captions, or margins, or what. 
        self.children = []
        self.focused = None

    """
    Updates self, then updates all of its children so everything displays nicely. 
    Focused elements get priority so we don't get weird things like panels overwriting menus. 
    Yes, this method can (and probably should) be overwritten. 
    """
    def update(self):
        # Put overriding update code here. 
        pygcurse.PygcurseTextbox.update(self)
        if self.children:
            for child in self.children:
                if child is not self.focused: child.update()
            if self.focused is not None:
                self.focused.update()

    """
    Process an event we are given. True if focus is kept/gained, false if it is not. 
    By default the rules are:
    First, pass to the focused child if we have one. 
        If it retains focus, skip over everything else and return True. 
        However, if it loses focus or we have no focusing child, see if it should focus on us. 
            If it does, then determine if any of out children should gain focus. Return true if we give a child focus. 
            Otherwise, pass false, and let our parent decide. 
    If we have focus and none of our children returned True, run onMouseEvent. By default, this is nothing. 
    Overriding this method is discouraged; if you want to customize event response, use the provided refocus, keepFocus, gainFocus, and onEvent methods. 
    """
    def capture(self, _event):
        if self.focused is not None:
            if self.focused.capture(): return True
            else: 
                self.focused = None
        if self.keepFocus(_event):
            if self.children:
                for child in self.children:
                    if child.refocus(self, _event):
                        self.focused = child
                        return True
            # If we got here, either we have no children, or none of our children gained focus. So let's run our event! 
            self.onEvent(_event)
            return True
        else: return False

    """
    Recursive method to determine which child should gain focus if we need to switch focus. 
    Can be overridden, but usally, overriding gainFocus should be enough. 
    """
    def refocus(self, _event):
        self.focused = None
        if self.gainFocus(_event):
            if self.children:
                for child in self.children:
                    if child.refocus(self, _event):
                        self.focused = child
                        return True
            # If we got here, either we have no children, or none of our children gained focus. So let's run our mouse event! 
            self.onEvent(_event)
            return True
        else: return False

    """
    Given the given event, returns if we should gain focus or not. 
    """
    def gainFocus(self, _event):
        return _mouseEvent.type == pygame.MOUSEBUTTONUP and pygame.Rect(self.x, self.y, self.width, self.height).collidepoint(_mouseEvent.pos)

    """
    Given the given event, returns if we should keep focus or not. 
    """
    def keepFocus(self, _event):
        return _mouseEvent.type != pygame.MOUSEBUTTONUP or pygame.Rect(self.x, self.y, self.width, self.height).collidepoint(_mouseEvent.pos)

    """
    While we are in focus, process the given event. 
    The default behavior is to remove self-focus and pass the event to a parent. 
    """
    def onEvent(self, _event):
        if self.parent is not None:
            self.parent.focused = None
            self.parent.onEvent(_event)

"""A persistent text box object, which can be inputted to."""
class textEntry(panel):
    def __init__(self, _surface, _parent, _region=(0, 0, 0, 0), _active=True, **kwargs):
        self.panel.__init__(_surface, _parent, _region, **kwargs)
        self.input_obj = pygcuse.PygcurseInput(self)
        self.input_obj.multiline = _region[3] > 1 #If it's a single line, don't scroll
        self.active = _active

    def display(self):
        self.input_obj.update()
        self.update()

    def setValue(self, _value):
        self.input_obj.buffer = list(_value)

    def getValue(self, _value):
        return "".join(input_obj.buffer)

    def deactivate(self):
        self.active = False
        #Modify colors

    def reactivate(self):
        self.active = True
        #Modify colors

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
    def __init__(self, _surface, _font="unifont-9.0.02", _size=16, _length=20, _height=29, _corner=(0, 0), _options=None):
        self.screen = _surface
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
    
