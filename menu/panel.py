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
class panel(pygcurse.PygcurseSurface):
    def __init__(self, _surface, _parent=None, _width=20, _height=1, corner=(0, 0), _font="unifont-9.0.02", _size=16):
        self.surface = _surface
        self.parent = _parent
        self.corner = _corner
        if _parent is not None:
            _parent.children.append(self)
            bgcolor = _parent.bgcolor-pygame.Color(16, 16, 16)
        else:
            bgcolor = pygame.Color(255, 255, 255)
        pygcurse.PygcurseSurface.__init__(self, _width, _height, font=pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size), fgcolor=pygame.Color(0, 0, 0), bgcolor=bgcolor)
        self.children = []
        self.focused = None

    """
    Updates self, then updates all of its children so everything displays nicely. 
    Focused elements get priority so we don't get weird things like panels overwriting menus. 
    Yes, this method can (and probably should) be overwritten. 
    """
    def update(self):
        # Put overriding update code here. 
        pygcurse.PygcurseSurface.update(self)
        if self.children:
            for child in self.children:
                if child is not self.focused: child.update()
            if self.focused is not None:
                self.focused.update()

    """
    Blits self, then blits all of its children so everything displays nicely. 
    Focused elements get priority so we don't get weird things like panels overwriting menus. 
    I wouldn't suggest overwriting this method. 
    """
    def display(self, dx=0, dy=0):
        self.blitto(_surface, corner)
        if self.children:
            for child in self.children:
                if child is not self.focused: child.display(corner[0], corner[1])
            if self.focused is not None:
                self.focused.display(corner[0], corner[1])

    """
    Process an event we are given. True if focus is kept/gained, false if it is not. 
    By default the rules are:
    First, pass to the focused child if we have one. 
        If it retains focus, skip over everything else and return True. 
        However, if it loses focus or we have no focusing child, see if it should focus on us. 
            If it does, then determine if any of out children should gain focus. Return true if we give a child focus. 
            Otherwise, pass false, and let our parent decide. 
    If we have focus and none of our children returned True, run onEvent. By default, this is nothing. 
    Overriding this method is discouraged; if you want to customize event response, use the provided preFocus, refocus, keepFocus, gainFocus, and onEvent methods. 
    """
    def capture(self, _event):
        if self.focused is not None:
            if self.focused.capture(): return True
            else: self.focused = None
        return preFocus(self, _event)

    """
    A starting function into the recursive function refocus. 
    """
    def preFocus(self, _event):
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
    Can be overridden, but overriding gainFocus or preFocus should be enough. 
    """
    def refocus(self, _event):
        self.former_focused = self.focused
        self.focused = None
        if self.gainFocus(_event):
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
    Given the given event, returns if we should gain focus or not. 
    """
    def gainFocus(self, _event):
        return _event.type == pygame.MOUSEBUTTONUP and self.getcoordinatesatpixel(_event.pos[0]-self.corner[0]. _event.pos[1]-self.corner[1]) != (None, None)

    """
    Given the given event, returns if we should keep focus or not. 
    """
    def keepFocus(self, _event):
        return _event.type != pygame.MOUSEBUTTONUP or self.getcoordinatesatpixel(_event.pos[0]-self.corner[0]. _event.pos[1]-self.corner[1]) != (None, None)

    """
    While we are in focus, process the given event. 
    The default behavior is to remove self-focus. 
    """
    def onEvent(self, _event):
        if self.parent is not None:
            self.parent.focused = None

"""
A text button that displays feedback if clicked.
"""
class button(panel):
    def __init__(self, _surface, _parent=None, _width=20, _height=1, _corner=(0, 0), _font="unifont-9.0.02", _size=16, _optionDict=None):
        self.panel.__init__(self, _surface, _parent, _width, _height, _corner, _font, _size)
        self.putchars(_optionDict.keys[0], x=0, y=0)
        self.option_dict= _optionDict
        self.selection = 0
        self.button_down = False

    def update(self):
        if self.button_down:
            self.setfgcolor(self._bgcolor)
            self.setbgcolor(self._fgcolor)
            self.putchars(_optionDict.values[selection], x=0, y=0)
        else:
            self.setfgcolor(self._fgcolor)
            self.setbgcolor(self._bgcolor)
            self.putchars(_optionDict.keys[selection], x=0, y=0)
        panel.update(self)

    def setValue(self, _newSelect, _newDict=None):
        if _newDict is not None:
            self.option_dict = _newDict
        self.selection = _newSelect

    def getValue(self):
        return self.option_dict.keys()[selection]

    def gainFocus(self, _event):
        if _event.type == pygame.MOUSEBUTTONDOWN and self.getcoordinatesatpixel(_event.pos[0]-self.corner[0]. _event.pos[1]-self.corner[1]) != (None, None):
            return True
        else:
            return False

    def keepFocus(self, _event):
        if self.getcoordinatesatpixel(_event.pos[0]-self.corner[0]. _event.pos[1]-self.corner[1]) == (None, None) or not panel.keepFocus(self, _event):
            self.button_down = False
            return False
        else:
            return True

    def onEvent(self, _event):
        if _event.type = pygame.MOUSEBUTTONUP:
            if self.button_down:
                self.selection = (self.selection+1)%len(self.option_dict)
            self.button_down = False
        elif _event.type = pygame.MOUSEBUTTONDOWN:
            self.button_down = True
                
"""
A persistent text box object, which can be inputted to if active. 
"""
class textEntry(panel):
    def __init__(self, _surface, _parent=None, _width=20, _height=1, _corner=(0, 0), _font="unifont-9.0.02", _size=16, _initText='', _active=False):
        self.panel.__init__(self, _surface, _parent, _width, _height, _corner, _font, _size)
        self.input_obj = pygcuse.PygcurseInput(self)
        self.input_obj.multiline = _height > 1 #If it's a single line, don't scroll
        self.input_obj.buffer = list(_initText)
        self.active = _active

    def update(self):
        self.input_obj.update()
        panel.update(self)

    def setValue(self, _value):
        self.input_obj.buffer = list(_value)

    def getValue(self, _value):
        return "".join(input_obj.buffer)

    def deactivate(self):
        self.active = False
        self._inputcursormode = None

    def activate(self):
        self.active = True
        self._inputcursormode = input_obj.insertMode and 'insert' or 'underline'
        
    def keepFocus(self, _event):
        if not panel.keepFocus(self, _event):
            return False
        elif _event.type in [pygame.KEYDOWN, pygame.KEYUP] and not input_obj.multiline and _event.key == pygame.key.K_RETURN:
            return False
        elif _event.type in [pygame.KEYDOWN, pygame.KEYUP] and _event.key in [pygame.key.K_ESCAPE, pygame.key.K_UP, pygame.key.K_DOWN, pygame.key.K_HOME, pygame.key.K_END, pygame.key.K_PAGEUP, pygame.key.K_PAGEDOWN]:
            return False
        elif _event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            return False
        else:
            return True

    def onEvent(self, _event):
        if self.active and _event.type in [pygame.KEYDOWN, pygame.KEYUP]:
            input_obj.sendkeyevent(event)

"""
A panel for holding interrelated panels, which can be switched between with the arrow keys. No scrolling capability. 
"""
class panelGrid(panel):
    def __init__(self, _surface, _parent=None, _width=20, _height=10, corner=(0, 0), _font="unifont-9.0.02", _size=16):
        self.panel.__init__(self, _surface, _parent, _width, _height, _corner, _font, _size)

    def preFocus(self, _event):
        if _event.type in [pygame.KEYUP, pygame.KEYDOWN]:
            focus_index = self.children.index(self.focused)
            if _event.type == pygame.KEYUP and _event.key == pygame.key.K_RETURN:
                focus_index = (focus_index+1)%len(self.children)
            elif _event.type == pygame.KEYDOWN and _event.key == pygame.key.K_UP:
                if focus_index > 0: focus_index -= 1
            elif _event.type == pygame.KEYDOWN and _event.key == pygame.key.K_DOWN:
                if focus_index <= len(self.children): focus_index += 1
            elif _event.type == pygame.KEYDOWN and _event.key == pygame.key.K_PAGEUP:
                focus_index = min(0, focus_index-5)
            elif _event.type == pygame.KEYDOWN and _event.key == pygame.key.K_PAGEDOWN:
                focus_index = max(focus_index+5, len(self.children)-1)
            elif _event.type == pygame.KEYDOWN and _event.key == pygame.key.K_HOME:
                focus_index = 0
            elif _event.type == pygame.KEYDOWN and _event.key == pygame.key.K_END:
                focus_index = len(self.children)-1
            elif _event.type == pygame.KEYDOWN and _event.key == pygame.key.K_ESCAPE:
                self.focused = None
                return False
            self.focused = self.children[focus_index]
            return True
        else return panel.preFocus(self, _event)
            
"""
A panel that tries to keep the focused child object in view. 
TODO: Finish
"""
class viewPanel(panel):
    def __init__(self, _surface, _parent=None, _width=20, _height=10, corner=(0, 0), _font="unifont-9.0.02", _size=16):
        self.panel.__init__(self, _surface, _parent, _width, _height, _corner, _font, _size)

"""
#A temporary drop-down menu. Appears when created, should disappear when a choice is made
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

    def update(self):
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
    
"""
