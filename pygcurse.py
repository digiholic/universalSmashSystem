"""
Please forgive any typos or errors in the comments, I'll be cleaning them up as frequently as I can.


Pygcurse v0.1 alpha

Pygcurse (pronounced "pig curse") is a curses library emulator that runs on top of the Pygame framework. It provides an easy way to create text adventures, roguelikes, and console-style applications.

Unfortunately, the curses library that comes with the Python standard library does not work on Windows. The excellent Console module from effbot provides curses-like features, but it only runs on Windows and not Mac/Linux. By using Pygame, Pygcurse is able to run on all platforms.

Pygcurse provides several benefits over normal text-based stdio programs:

    1) Color text and background.
    2) The ability to move the cursor and print text anywhere in the console window.
    3) The ability to make console apps that make use of the mouse.
    4) The ability to have programs respond to individual key presses, instead of waiting for the user to type an entire string and press enter (as with input()/raw_input()).
    5) Since the console window that Pygcurse uses is just a Pygame surface object, additional drawing and transformations can be applied to it. Multiple consoles can also be used in the same program.

Pygcurse requires Pygame to be installed. Pygame can be downloaded from http://pygame.org

Pygcurse was developed by Al Sweigart (al@inventwithpython.com)
https://github.com/asweigart/pygcurse


Simplified BSD License:

Copyright 2011 Al Sweigart. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice, this list of
      conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice, this list
      of conditions and the following disclaimer in the documentation and/or other materials
      provided with the distribution.

THIS SOFTWARE IS PROVIDED BY Al Sweigart ''AS IS'' AND ANY EXPRESS OR IMPLIED
WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Al Sweigart OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the
authors and should not be interpreted as representing official policies, either expressed
or implied, of Al Sweigart.
"""

import copy
import time
import sys
import textwrap
import pygame
from pygame.locals import *

"""
Some nomenclature in this module's comments explained:

Cells:
The space for each character is called a cell in this module. Cells are all of an identical size, which is based on the font being used. (only a single font of a single size can be used in a PygcurseSurface object. Cell coordinates refer to the positions of characters on the surface. Pixel coordinates refer to the position of each pixel.

Scrolling:
The term "scrolling" refers to when a character is printed at the bottom right corner, which causes all the characters on the surface to be moved up and a blank row to be created at the bottom. The print() and write() functions causes scolls if it prints enough characters. The putchar() and putchars() functions do not.

Color parameters:
Several Pygcurse functions take colors for their parameters. These can almost always (there might be some exceptions) be:
    1) A pygame.Color object.
    2) An RGB tuple of three integers, 0 to 255 (like Pygame uses)
    3) An RGBA tuple of four integers, 0 to 255 (like Pygame uses)
    4) A string such as 'blue', 'lime', or 'gray' (or any of the strings listed in the colornames gloal dictionary. This dict can be updated with more colors if the user wants.)
    5) None, which means use whatever color the cell already uses.

Region parameters:
A "region" defines an area of the surface. It can be the following formats:
    1) Four-integer tuple (x, y, width, height)
    2) Four-integer tuple (x, y, None, None) which means x,y and extending to the right & bottom edge of the surface
    3) None or (None, None, None, None) which means the entire surface
    4) pygame.Rect object

Note about flickering: If your program is experiencing a lot of flicker, than you should disable the self._autoupdate member. By default, this is enabled and the screen is redrawn after each method call that makes a change to the screen.
"""


DEFAULTFGCOLOR = pygame.Color(164, 164, 164, 255) # default foreground color is gray (must be a pygame.Color object)
DEFAULTBGCOLOR = pygame.Color(0, 0, 0, 255) # default background color is black (must be a pygame.Color object)
ERASECOLOR = pygame.Color(0, 0, 0, 0) # erase color has 0 alpha level (must be a pygame.Color object)

# Internally used constants:
_NEW_WINDOW = 'new_window'
FULLSCREEN = 'full_screen'

# Directional constants:
NORTH = 'N'
EAST = 'E'
SOUTH = 'S'
WEST = 'W'
NORTHEAST = 'NE'
NORTHWEST = 'NW'
SOUTHEAST = 'SE'
SOUTHWEST = 'SW'

# A mapping of strings to color objects.
colornames = {'white':   pygame.Color(255, 255, 255),
              'yellow':  pygame.Color(255, 255,   0),
              'fuchsia': pygame.Color(255,   0, 255),
              'red':     pygame.Color(255,   0,   0),
              'silver':  pygame.Color(192, 192, 192),
              'gray':    pygame.Color(128, 128, 128),
              'olive':   pygame.Color(128, 128,   0),
              'purple':  pygame.Color(128,   0, 128),
              'maroon':  pygame.Color(128,   0,   0),
              'aqua':    pygame.Color(  0, 255, 255),
              'lime':    pygame.Color(  0, 255,   0),
              'teal':    pygame.Color(  0, 128, 128),
              'green':   pygame.Color(  0, 128,   0),
              'blue':    pygame.Color(  0,   0, 255),
              'navy':    pygame.Color(  0,   0, 128),
              'black':   pygame.Color(  0,   0,   0)}


class PygcurseSurface(object):

    """
    A PygcurseSurface object is the ascii-based analog of Pygame's Surface objects. It represents a 2D field of ascii characters, exactly like a console terminal. Each cell can have a different character, foreground color, background color, and RGB tint. The PygcurseSurface object also tracks the location of the cursor (where the print() and putchar() functions will output text) and the "input cursor" (the blinking cursor when the user is typing in characters.)

    Each xy position on the surface is called a "cell". A cell can hold one and only one character.

    The PygcurseSurface object contains a pygame.Surface object that it draws to. This pygame.Surface object in turn may have additional Pygame drawing functions called on it before being drawn to the screen with pygame.display.update().

    It should be noted that none of the code in the pygcurse module should at all be considered thread-safe.
    """
    _pygcurseClass = 'PygcurseSurface'

    def __init__(self, width=80, height=25, font=None, fgcolor=DEFAULTFGCOLOR, bgcolor=DEFAULTBGCOLOR, windowsurface=None):
        """
        Creates a new PygcurseSurface object.

        - width and height are the number of characters the the object can display.
        - font is a pygame.Font object used to display the characters. PygcurseSurface can only display one font of one size at a time. The size of the underlying pygame.Surface object is calculated from the font size and width/height accordingly. If None, then a default generic font is used.
        - fgcolor is the foreground color  (ie the color of the text). It is set to either a pygame.Color object, an RGB tuple, an RGBA tuple, or a string that is a key in the colornames dict.
        - bgcolor is the background color of the text.
        - windowSurface is optional. If None, than the user is responsible for calling the update() method on this object and blitting it's surface to the screen, and calling pygame.display.update(). If a pygame.Surface object is specified, then PygcurseSurface object handles updating automatically (unless disabled). (See the update() method for more details.)
        """
        pygame.init()
        self._cursorx = 0
        self._cursory = 0
        self._cursorstack = []
        self._width = width
        self._height = height

        # The self._screen* members are 2D lists that store data for each cell of the PygcurseSurface object. _screenchar[x][y] holds the character at cell x, y. _screenfgcolor and _screenbgcolor  stores the foreground/background color of the cell, etc.
        self._screenchar = [[None] * height for i in range(width)]

        # intialize the foreground and background colors of each cell
        self._fgcolor = fgcolor
        self._bgcolor = bgcolor
        # make sure the values in _screenfgcolor and _screenbgcolor are always pygame.Color objects, and not RGB/RGBA tuples or color strings like 'blue'. Use getpygamecolor().
        self._screenfgcolor = [[None] * height for i in range(width)]
        self._screenbgcolor = [[None] * height for i in range(width)]
        for x in range(width):
            for y in range(height):
                self._screenfgcolor[x][y] = fgcolor
                self._screenbgcolor[x][y] = bgcolor

        # intialize the dirty flag for each cell to True. If the cell's dirty flag is True, then update() needs to update this cell on the self._surfaceobj pygame.Surface object.
        self._screendirty = [[True] * height for i in range(width)]

        # initalize the tinting of each cell to 0. (255 is max, -255 is minimum)
        self._rdelta = 0
        self._gdelta = 0
        self._bdelta = 0
        self._screenRdelta = [[0] * height for i in range(width)]
        self._screenGdelta = [[0] * height for i in range(width)]
        self._screenBdelta = [[0] * height for i in range(width)]

        # The "input cursor" is a separate cursor used by the input() method (and PygcurseInput objects). It tracks where the typed characters should appear. This is separate from the regular cursor which tracks where print() and putchar() should output characters. The mode can be:
        # - None, meaning there is no visible cursor
        # - 'underline', meaning a generic underscore-looking cursor
        # - 'insert', meaning a small box cursor (used when the Insert key has been pressed.)
        # - 'box', which is a box that covers the entire cell, and inverts the foreground and background colors.
        # inputcursorblinking is a boolean variable that tracks if the input cursor should be blinking or stay solid.
        self._inputcursormode = None # either None, 'underline', 'insert' or 'box'
        self.inputcursorblinking = True
        self._inputcursorx = 0
        self._inputcursory = 0

        self._scrollcount = 0 # the number of times writing text to the bottom row has scrolled the screen up a line.

        if font is None:
            self._font = pygame.font.Font(None, 18)
        else:
            self._font = font

        # the width and height in pixels of each cell depends on the font used.
        self._cellwidth, self._cellheight = calcfontsize(self._font) # width and height of each cell in pixels

        self._autoupdate = True
        if windowsurface == _NEW_WINDOW:
            self._windowsurface = pygame.display.set_mode((self._cellwidth * width, self._cellheight * height))
            self._managesdisplay = True
        elif windowsurface == FULLSCREEN:
            self._windowsurface = pygame.display.set_mode((self._cellwidth * width, self._cellheight * height), pygame.FULLSCREEN)
            self._managesdisplay = True
        else:
            self._windowsurface = windowsurface
            self._managesdisplay = False
        self._autodisplayupdate = self._windowsurface is not None
        self._autoblit = self._windowsurface is not None

        self._tabsize = 8 # how many spaces a tab inserts.

        # width and height of the entire surface, in pixels.
        self._pixelwidth = self._width * self._cellwidth
        self._pixelheight = self._height * self._cellheight

        self._surfaceobj = pygame.Surface((self._pixelwidth, self._pixelheight))
        self._surfaceobj = self._surfaceobj.convert_alpha() # TODO - This is needed for erasing, but does this have a performance hit?


    def input(self, prompt='', x=None, y=None, maxlength=None, fgcolor=None, bgcolor=None, promptfgcolor=None, promptbgcolor=None, whitelistchars=None, blacklistchars=None, callbackfn=None, fps=None):
        """
        A pygcurse version of the input() and raw_input() functions. When called, it displays a cursor on the screen and lets the user type in a string. This function blocks until the user presses Enter, and it returns the string the user typed in.

        In fact, this function can be used as a drop-in replacement of Python's input() to convert a stdio text-based Python program to a graphical Pygcurse program. See the PygcurseWindow class for details.

        - prompt is a string that is displayed at the beginning of the input area
        - x and y are cell coordinates for where the beginning of the input area should be. By default it is where the cursor is.
        - maxlength is the maximum number of characters that the user can enter. By default it is 4094 characters if the keyboard input can span multiple lines, or to the end of the current row if the x value is specified.
        - fgcolor and bgcolor are the foreground and background colors of the text typed by the user.
        - promptfgcolor and promptbgcolor are the foreground and background colors of the prompt.
        - whitelistchars is a string of the characters that are allowed to be entered from the keyboard. If None, then all characters (except those in the blacklist, if one is specified) are allowed.
        - blacklistchars is a string of the characters that are prohibited to be entered from the keyboard. If None, then all characters (if they are in the whitelist, if one is specified) are allowed.
        - callbackfn is a function that is called during the input() method's loop. This can be used for any additional code that needs to be run while waiting for the user to enter text.
        - fps specifies how many times per second this function should update the screen (ie, frames per second). If left at None, then input() will simply try to update as fast as possible.
        """
        if fps is not None:
            clock = pygame.time.Clock()

        inputObj = PygcurseInput(self, prompt, x, y, maxlength, fgcolor, bgcolor, promptfgcolor, promptbgcolor, whitelistchars, blacklistchars)
        self.inputcursor = inputObj.startx, inputObj.starty

        while True: # the event loop
            self._inputcursormode = inputObj.insertMode and 'insert' or 'underline'

            for event in pygame.event.get((KEYDOWN, KEYUP, QUIT)): # TODO - handle holding down the keys
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type in (KEYDOWN, KEYUP):
                    inputObj.sendkeyevent(event)
                    if inputObj.done:
                        return ''.join(inputObj.buffer)

            if callbackfn is not None:
                callbackfn()

            inputObj.update()
            self.update()

            if fps is not None:
                clock.tick(fps)

    raw_input = input

    # This code makes my eyes (and IDEs) bleed (and maintenance a nightmare), but it's the only way to have syntactically correct code that is compatible with both Python 2 and Python 3:
    if sys.version.startswith('2.'): # for Python 2 version
        exec(r'''
def pygprint(self, *objs): # PY2
    """
    Displays text to the PygcurseSurface. The parameters work exactly the same as Python's textual print() function. It can take several arguments to display, each separated by the string in the sep parameter. The end parameter string is automatically added to the end of the displayed output.

    - fgcolor, bgcolor are colors for the text displayed by this call to print(). If None, then the PygcurseSurface object's fg and bg colors are used. These parameters only apply to the text printed by this function call, they do not change the PygcurseSurface's fg and bg color settings.

    This function can be used as a drop-in replacement of Python's print() to convert a stdio text-based Python program to a graphical Pygcurse program. See the PygcurseWindow class for details.
    """

    self.write(' '.join([str(x) for x in objs]) + '\n')
''')
    else: # for Python 3 version
        exec(r'''
def pygprint(self, obj='', *objs, sep=' ', end='\n', fgcolor=None, bgcolor=None, x=None, y=None):
    """
    Displays text to the PygcurseSurface. The parameters work exactly the same as Python's textual print() function. It can take several arguments to display, each separated by the string in the sep parameter. The end parameter string is automatically added to the end of the displayed output.

    - fgcolor, bgcolor are colors for the text displayed by this call to print(). If None, then the PygcurseSurface object's fg and bg colors are used. These parameters only apply to the text printed by this function call, they do not change the PygcurseSurface's fg and bg color settings.

    This function can be used as a drop-in replacement of Python's print() to convert a stdio text-based Python program to a graphical Pygcurse program. See the PygcurseWindow class for details.
    """

    writefgcolor = (fgcolor is not None) and getpygamecolor(fgcolor) or self._fgcolor
    writebgcolor = (bgcolor is not None) and getpygamecolor(bgcolor) or self._bgcolor
    if x is not None:
        self.cursorx = x
    if y is not None:
        self.cursory = y

    text = [str(obj)]
    if objs:
        text.append(str(sep) + str(sep).join([str(x) for x in objs]))
    text.append(str(end))

    self.write(''.join(text), writefgcolor, writebgcolor)
#print = pygprint # Actually, this line is a bad idea and only encourages non-compatibility. Leave it commented out.
''')


    def blitto(self, surfaceObj, dest=(0, 0)):
        """
        Copies this object's pygame.Surface to another surface object. (Usually, this surface object is the one returned by pygame.display.set_mode().)

        - surfaceObj is the pygame.Surface object to copy this PygcurseSurface's image to.
        - dest is a tuple of the xy pixel coordinates of the topleft corner where the image should be copied. By default, it is (0,0).
        """
        return surfaceObj.blit(self._surfaceobj, dest)


    def pushcursor(self):
        """Save the current cursor positions to a stack for them. This is useful when you need to modify the cursor position but want to restore it later."""
        self._cursorstack.append( (self._cursorx, self._cursory) )


    def popcursor(self):
        """Restore the cursor position from the cursor stack."""
        x, y = self._cursorstack.pop()
        self._cursorx = x
        self._cursory = y
        return x, y


    def getnthcellfrom(self, x, y, spaces):
        """
        Returns the xy cell coordinates of the nth cell after the position specified by the x and y parameters. This method accounts for wrapping around to the next row if it extends past the right edge of the surface. The returned coordinates can be past the bottom row of the pygcurse surface.
        """
        if x + spaces < self._width:
            return x + spaces, y
        spaces -= x
        y += 1
        return spaces % self._width, y + int(spaces / self._width)


    def update(self):
        """
        Update the encapsulated pygame.Surface object to match the state of this PygcurseSurface object. This needs to be done before the pygame.Surface object is blitted to the screen if you want the most up-to-date state displayed.

        There are three types of updating:
            1) Updating the PygcurseSurface surface object to match the backend data.
                (Enabled by default by setting self._autoupdate == True)
            2) Blitting the PygcurseSurface surface object to the main window
                (Enabled by setting self._windowsurface to the main window AND self._autoblit == True)
            3) Calling pygame.display.update()
                (Enabled by default if _windowsurface is set, self._autoblit == True, AND if _autodisplayupdate == True)
        """

        # TODO - None of this code is optimized yet.

        # "Dirty" means that the cell's state has been altered on the backend and it needs to be redrawn on pygame.Surface object (which will make the cell "clean").
        for x in range(self._width):
            for y in range(self._height):
                if self._screendirty[x][y]: # draw to surfaceobj all the dirty cells.
                    self._screendirty[x][y] = False

                    # modify the fg and bg color if there is a tint
                    cellfgcolor, cellbgcolor = self.getdisplayedcolors(x, y)

                    # fill in the entire background of the cell
                    cellrect = pygame.Rect(self._cellwidth * x, self._cellheight * y, self._cellwidth, self._cellheight)

                    if self._screenchar[x][y] is None:
                        self._surfaceobj.fill(ERASECOLOR, cellrect)
                        continue

                    self._surfaceobj.fill(cellbgcolor, cellrect)

                    if self._screenchar[x][y] == ' ':
                        continue # don't need to render anything if it is just a space character.

                    # render the character and draw it to the surface
                    charsurf = self._font.render(self._screenchar[x][y], 1, cellfgcolor, cellbgcolor)
                    charrect = charsurf.get_rect()
                    charrect.centerx = self._cellwidth * x + int(self._cellwidth / 2)
                    charrect.bottom = self._cellheight * (y + 1) # TODO - not correct, this would put stuff like g, p, q higher than normal.
                    self._surfaceobj.blit(charsurf, charrect)

        self._drawinputcursor()

        # automatically blit to "window surface" pygame.Surface object if it was set.
        if self._windowsurface is not None and self._autoblit:
            self._windowsurface.blit(self._surfaceobj, self._surfaceobj.get_rect())
            if self._autodisplayupdate:
                pygame.display.update()


    def _drawinputcursor(self):
        """Draws the input cursor directly onto the self._surfaceobj Surface object, if self._inputcursormode is not None."""
        if self._inputcursormode is not None and self._inputcursorx is not None and self._inputcursory is not None:
            x = self._inputcursorx # syntactic sugar
            y = self._inputcursory # syntactic sugar

            if not self.inputcursorblinking or int(time.time() * 2) % 2 == 0:
                cellfgcolor, cellbgcolor = self.getdisplayedcolors(x, y)

                if self._inputcursormode == 'underline':
                    # draw a simply underline cursor
                    pygame.draw.rect(self._surfaceobj, cellfgcolor, (self._cellwidth * x + 2, self._cellheight * (y+1) - 3, self._cellwidth - 4, 3))
                elif self._inputcursormode == 'insert':
                    # draw a cursor that takes up about half the cell
                    pygame.draw.rect(self._surfaceobj, cellfgcolor, (self._cellwidth * x + 2, self._cellheight * (y+1) - int(self._cellheight / 2.5), self._cellwidth - 4, int(self._cellheight / 2.5)))
                elif self._inputcursormode == 'box':
                    # draw the reverse the fg & bg colors of the cell (but don't actually modify the backend data)
                    # TODO - the following is copy pasta. Get rid of it when optimizing?
                    cellrect = pygame.Rect(self._cellwidth * x, self._cellheight * y, self._cellwidth, self._cellheight)
                    self._surfaceobj.fill(cellfgcolor, cellrect)
                    charsurf = self._font.render(self._screenchar[x][y], 1, cellbgcolor, cellfgcolor)
                    charrect = charsurf.get_rect()
                    charrect.centerx = self._cellwidth * x + int(self._cellwidth / 2)
                    charrect.bottom = self._cellheight * (y+1) # TODO - not correct, this would put stuff like g, p, q higher than normal.
                    self._surfaceobj.blit(charsurf, charrect)
            else:
                # need to blank out the cursor by simply redrawing the cell
                self._repaintcell(x, y)

    def getdisplayedcolors(self, x, y):
        """Returns the fg and bg colors of the given cell as pygame.Color objects, modified for the tint. If x and y is not on the surface, returns (None, None)"""

        if x < 0 or y < 0 or x >= self._width or y >= self._height:
            return None, None

        fgcolor = (self._screenfgcolor[x][y] is None) and (DEFAULTFGCOLOR) or (self._screenfgcolor[x][y])
        bgcolor = (self._screenbgcolor[x][y] is None) and (DEFAULTBGCOLOR) or (self._screenbgcolor[x][y])

        # NOTE - The ternary trick does work here, because the case where the wrong value of the two is used, both values are the same.
        rdelta = (self._screenRdelta[x][y] is not None) and (self._screenRdelta[x][y]) or (0)
        gdelta = (self._screenGdelta[x][y] is not None) and (self._screenGdelta[x][y]) or (0)
        bdelta = (self._screenBdelta[x][y] is not None) and (self._screenBdelta[x][y]) or (0)


        if rdelta or gdelta or bdelta:
            r, g, b, a = fgcolor.r, fgcolor.g, fgcolor.b, fgcolor.a
            r = getwithinrange(r + rdelta)
            g = getwithinrange(g + gdelta)
            b = getwithinrange(b + bdelta)
            displayedfgcolor = pygame.Color(r, g, b, a)

            r, g, b, a = self._screenbgcolor[x][y].r, self._screenbgcolor[x][y].g, self._screenbgcolor[x][y].b, self._screenbgcolor[x][y].a
            r = getwithinrange(r + rdelta)
            g = getwithinrange(g + gdelta)
            b = getwithinrange(b + bdelta)
            displayedbgcolor = pygame.Color(r, g, b, a)
        else:
            displayedfgcolor = fgcolor
            displayedbgcolor = bgcolor

        return displayedfgcolor, displayedbgcolor


    def _repaintcell(self, x, y):
        """Immediately updates the cell at xy. Use this method when you don't want to update the entire surface."""

        if x < 0 or y < 0 or x >= self._width or y >= self._height:
            return

        # modify the fg and bg color if there is a tint
        cellfgcolor, cellbgcolor = self.getdisplayedcolors(x, y)
        cellrect = pygame.Rect(self._cellwidth * x, self._cellheight * y, self._cellwidth, self._cellheight)
        self._surfaceobj.fill(cellbgcolor, cellrect)
        charsurf = self._font.render(self._screenchar[x][y], 1, cellfgcolor, cellbgcolor)
        charrect = charsurf.get_rect()
        charrect.centerx = self._cellwidth * x + int(self._cellwidth / 2)
        charrect.bottom = self._cellheight * (y+1) # TODO - not correct, this would put stuff like g, p, q higher than normal.
        self._surfaceobj.blit(charsurf, charrect)


    _debugcolorkey = {(255,0,0): 'R',
                      (0,255,0): 'G',
                      (0,0,255): 'B',
                      (0,0,0): 'b',
                      (255, 255, 255): 'w'}


    def _debug(self, returnstr=False, fn=None):
        text = ['+' + ('-' * self._width) + '+\n']
        for y in range(self._height):
            line = ['|']
            for x in range(self._width):
                line.append(fn(x, y))
            line.append('|\n')
            text.append(''.join(line))
        text.append('+' + ('-' * self._width) + '+\n')
        if returnstr:
            return ''.join(text)
        else:
            sys.stdout.write(''.join(text) + '\n')


    def _debugfgFn(self, x, y):
        r, g, b = self._screenfgcolor[x][y].r, self._screenfgcolor[x][y].g, self._screenfgcolor[x][y].b
        if (r, g, b) in PygcurseSurface._debugcolorkey:
            return PygcurseSurface._debugcolorkey[(r, g, b)]
        else:
            return'.'


    def _debugfg(self, returnstr=False):
        return self._debug(returnstr=returnstr, fn=self._debugfgFn)


    def _debugbgFn(self, x, y):
        r, g, b = self._screenbgcolor[x][y].r, self._screenbgcolor[x][y].g, self._screenbgcolor[x][y].b
        if (r, g, b) in PygcurseSurface._debugcolorkey:
            return PygcurseSurface._debugcolorkey[(r, g, b)]
        else:
            return '.'


    def _debugbg(self, returnstr=False):
        return self._debug(returnstr=returnstr, fn=self._debugbgFn)


    def _debugcharsFn(self, x, y):
        if self._screenchar[x][y] in (None, '\n', '\t'):
            return '.'
        else:
            return self._screenchar[x][y]


    def _debugchars(self, returnstr=False):
        return self._debug(returnstr=returnstr, fn=self._debugcharsFn)


    def _debugdirtyFn(self, x, y):
        if self._screendirty[x][y]:
            return 'D'
        else:
            return '.'


    def _debugdirty(self, returnstr=False):
        return self._debug(returnstr=returnstr, fn=self._debugdirtyFn)


    def gettopleftpixel(self, cellx, celly=None, onscreen=True):
        """Return a tuple of the pixel coordinates of the cell at cellx, celly."""
        if type(cellx) in (tuple, list):
            if type(celly) == bool: # shuffling around the parameters
                isonscreen = celly
            cellx, celly = cellx
        if onscreen and not self.isonscreen(cellx, celly):
            return (None, None)
        return (cellx * self._cellwidth, celly * self._cellheight)


    def gettoppixel(self, celly, onscreen=True):
        """Return the y pixel coordinate of the cells at row celly."""
        if onscreen and (celly < 0 or celly >= self.height):
            return None
        return celly * self._cellheight


    def getleftpixel(self, cellx, onscreen=True):
        """Return the x pixel coordinate of the cells at column cellx."""
        if onscreen and (cellx < 0 or cellx >= self.width):
            return None
        return cellx * self._cellwidth


    def getcoordinatesatpixel(self, pixelx, pixely=None, onscreen=True):
        """
        Given the pixel x and y coordinates relative to the PygCurse screen's origin, return the cell x and y coordinates that it is over. (Useful for finding what cell the mouse cursor is over.)

        Returns (None, None) if the pixel coordinates are not over the screen.
        """
        if type(pixelx) in (tuple, list):
            if type(pixely) == bool: # shuffling around the parameters
                onscreen = pixely
            pixelx, pixely = pixelx

        if onscreen and (pixelx < 0 or pixelx >= self._width * self._cellwidth) or (pixely < 0 or pixely >= self._height * self._cellheight):
            return (None, None)
        return int(pixelx / self._cellwidth), int(pixely / self._cellheight)


    def getcharatpixel(self, pixelx, pixely):
        """Returns the character in the cell located at the pixel coordinates pixelx, pixely."""
        x, y = self.getcoordinatesatpixel(pixelx, pixely)
        if (x, y) == (None, None):
            return (None, None)
        return self._screenchar[x][y]


    def resize(self, newwidth=None, newheight=None, fgcolor=None, bgcolor=None):
        """
        Resize the number of cells wide and tall the surface is. If we are expanding the size of the surface, specify the foreground/background colors of the new cells.
        """

        # TODO - Yipes. This function changes so many things, a lot of testing needs to be done.
        # For example, what happens if the input cursor is now off the screen?
        if newwidth == self._width and newheight == self._height:
            return
        if newwidth is None:
            newwidth = self._width
        if newheight is None:
            newheight = self._height
        if fgcolor is None:
            fgcolor = self._fgcolor
        fgcolor = getpygamecolor(fgcolor)

        if bgcolor is None:
            bgcolor = self._bgcolor
        bgcolor = getpygamecolor(bgcolor)

        # create new _screen* data structures
        newchars = [[None] * newheight for i in range(newwidth)]
        newfg = [[None] * newheight for i in range(newwidth)]
        newbg = [[None] * newheight for i in range(newwidth)]
        newdirty = [[True] * newheight for i in range(newwidth)]
        newRdelta = [[0] * newheight for i in range(newwidth)]
        newGdelta = [[0] * newheight for i in range(newwidth)]
        newBdelta = [[0] * newheight for i in range(newwidth)]
        for x in range(newwidth):
            for y in range(newheight):
                if x >= self._width or y >= self._height:
                    # Create new color objects
                    newfg[x][y] = fgcolor
                    newbg[x][y] = bgcolor
                    newRdelta[x][y] = self._rdelta
                    newGdelta[x][y] = self._gdelta
                    newBdelta[x][y] = self._bdelta
                else:
                    newchars[x][y] = self._screenchar[x][y]
                    newdirty[x][y] = self._screendirty[x][y]
                    # Copy over old color objects
                    newfg[x][y] = self._screenfgcolor[x][y]
                    newbg[x][y] = self._screenbgcolor[x][y]
                    newRdelta[x][y] = self._screenRdelta[x][y]
                    newGdelta[x][y] = self._screenGdelta[x][y]
                    newBdelta[x][y] = self._screenBdelta[x][y]

        # set new dimensions
        self._width = newwidth
        self._height = newheight
        self._pixelwidth = self._width * self._cellwidth
        self._pixelheight = self._height * self._cellheight
        self._cursorx = 0
        self._cursory = 0
        newsurf = pygame.Surface((self._pixelwidth, self._pixelheight))
        newsurf.blit(self._surfaceobj, (0, 0))
        self._surfaceobj = newsurf

        self._screenchar = newchars
        self._screenfgcolor = newfg
        self._screenbgcolor = newbg
        self._screendirty = newdirty

        if self._managesdisplay:
            # resize the pygame window itself
            self._windowsurface = pygame.display.set_mode((self._pixelwidth, self._pixelheight))
            self.update()
        elif self._autoupdate:
            self.update()


    def setfgcolor(self, fgcolor, region=None):
        """
        Sets the foreground color of a region of cells on this surface.

        - fgcolor is the color to set the foreground to.
        """
        if region == None:
            self._fgcolor = fgcolor
            return

        regionx, regiony, regionwidth, regionheight = self.getregion(region)
        if (regionx, regiony, regionwidth, regionheight) == (None, None, None, None):
            return

        for ix in range(regionx, regionx + regionwidth):
            for iy in range(regiony, regiony + regionheight):
                self._screenfgcolor[ix][iy] = fgcolor
                self._screendirty[ix][iy] = True
        if self._autoupdate:
            self.update()


    def setbgcolor(self, bgcolor, region=None):
        """
        Sets the background color of a region of cells on this surface.

        - bgcolor is the color to set the background to.
        """
        if region == None:
            self._fgcolor = fgcolor
            return

        regionx, regiony, regionwidth, regionheight = self.getregion(region)
        if (regionx, regiony, regionwidth, regionheight) == (None, None, None, None):
            return

        for ix in range(regionx, regionx + regionwidth):
            for iy in range(regiony, regiony + regionheight):
                self._screenbgcolor[ix][iy] = bgcolor
                self._screendirty[ix][iy] = True
        if self._autoupdate:
            self.update()


    def reversecolors(self, region=None):
        """
        Reverse the foreground/background colors of a region of cells on this surface with each other.
        """
        regionx, regiony, regionwidth, regionheight = self.getregion(region)
        if (regionx, regiony, regionwidth, regionheight) == (None, None, None, None):
            return

        for ix in range(regionx, regionx + regionwidth):
            for iy in range(regiony, regiony + regionheight):
                self._screenfgcolor[ix][iy], self._screenbgcolor[ix][iy] = self._screenbgcolor[ix][iy], self._screenfgcolor[ix][iy]
                self._screendirty[ix][iy] = True
        if self._autoupdate:
            self.update()


    def _invertfg(self, x, y):
        # NOTE - This function does not set the dirty flag.
        fgcolor = self._screenfgcolor[x][y]
        invR, invG, invB = 255 - fgcolor.r, 255 - fgcolor.g, 255 - fgcolor.b
        self._screenfgcolor[x][y] = pygame.Color(invR, invG, invB, fgcolor.a)


    def _invertbg(self, x, y):
        # NOTE - This function does not set the dirty flag.
        bgcolor = self._screenbgcolor[x][y]
        invR, invG, invB = 255 - bgcolor.r, 255 - bgcolor.g, 255 - bgcolor.b
        self._screenbgcolor[x][y] = pygame.Color(invR, invG, invB, bgcolor.a)


    def invertcolors(self, region=None):
        """
        Invert the colors of a region of cells on this surface. (For example, black and white are inverse of each other, as are blue and yellow.)
        """
        regionx, regiony, regionwidth, regionheight = self.getregion(region)
        if (regionx, regiony, regionwidth, regionheight) == (None, None, None, None):
            return

        for ix in range(regionx, regionx + regionwidth):
            for iy in range(regiony, regiony + regionheight):
                self._invertfg(ix, iy)
                self._invertbg(ix, iy)
                self._screendirty[ix][iy] = True
        if self._autoupdate:
            self.update()


    def invertfgcolor(self, region=None):
        """
        Invert the foreground color of a region of cells on this surface. (For example, black and white are inverse of each other, as are blue and yellow.)
        """
        regionx, regiony, regionwidth, regionheight = self.getregion(region)
        if (regionx, regiony, regionwidth, regionheight) == (None, None, None, None):
            return

        for ix in range(regionx, regionx + regionwidth):
            for iy in range(regiony, regiony + regionheight):
                self._invertfg(ix, iy)
                self._screendirty[ix][iy] = True
        if self._autoupdate:
            self.update()


    def invertbgcolor(self, region=None):
        """
        Invert the background color of a region of cells on this surface. (For example, black and white are inverse of each other, as are blue and yellow.)
        """
        regionx, regiony, regionwidth, regionheight = self.getregion(region)
        if (regionx, regiony, regionwidth, regionheight) == (None, None, None, None):
            return

        for ix in range(regionx, regionx + regionwidth):
            for iy in range(regiony, regiony + regionheight):
                self._invertbg(ix, iy)
                self._screendirty[ix][iy] = True
        if self._autoupdate:
            self.update()


    def paste(self, srcregion=None, dstsurf=None, dstregion=None, pastechars=True, pastefgcolor=True, pastebgcolor=True, pasteredtint=True, pastegreentint=True, pastebluetint=True):
        srcx, srcy, srcwidth, srcheight = self.getregion(srcregion)
        if (srcx, srcy, srcwidth, srcheight) == (None, None, None, None):
            return

        if dstsurf is None:
            # Create a new PygcurseSurface to paste to.
            dstsurf = PygcurseSurface(srcwidth, srcheight, font=self._font, fgcolor=self._fgcolor, bgcolor=self._bgcolor)
        elif dstsurf._pygcurseClass not in ('PygcurseSurface', 'PygcurseWindow'): # TODO - is this the right way to do this?
            return

        dstx, dsty, dstwidth, dstheight = dstsurf.getregion(dstregion)
        if (dstx, dsty, dstwidth, dstheight) == (None, None, None, None):
            return

        if self == dstsurf and regionsoverlap((srcx, srcy, srcwidth, srcheight), (dstx, dsty, dstwidth, dstheight)):
            # Since we are trying to copy/paste over the same region, in order to prevent any weird side effects, paste to a new surface object first
            tempsurf = self.paste((srcx, srcy, srcwidth, srcheight))
            tempsurf.paste(None, self, (dstx, dsty, dstwidth, dstheight))
            return

        for ix in range(srcx, srcx + srcwidth):
            for iy in range(srcy, srcy + srcheight):
                finx = dstx + (ix - srcx)
                finy = dsty + (iy - srcy)

                if not dstsurf.isonscreen(finx, finy) or ix - srcx >= dstwidth or iy - srcy >= dstheight:
                    continue

                if pastechars and self._screenchar[ix][iy] is not None:
                    dstsurf._screenchar[finx][finy] = self._screenchar[ix][iy]
                if pastefgcolor and self._screenfgcolor[ix][iy] is not None:
                    dstsurf._screenfgcolor[finx][finy] = self._screenfgcolor[ix][iy]
                if pastebgcolor and self._screenbgcolor[ix][iy] is not None:
                    dstsurf._screenbgcolor[finx][finy] = self._screenbgcolor[ix][iy]
                if pasteredtint and self._screenRdelta[ix][iy] is not None:
                    dstsurf._screenRdelta[finx][finy] = self._screenRdelta[ix][iy]
                if pastegreentint and self._screenGdelta[ix][iy] is not None:
                    dstsurf._screenGdelta[finx][finy] = self._screenGdelta[ix][iy]
                if pastebluetint and self._screenBdelta[ix][iy] is not None:
                    dstsurf._screenBdelta[finx][finy] = self._screenBdelta[ix][iy]
                dstsurf._screendirty[finx][finy] = True

        if dstsurf._autoupdate:
            dstsurf.update()


    def pastechars(self, srcregion=None, dstsurf=None, dstregion=None):
        return self.paste(srcregion, dstsurf, dstregion, True, False, False, False, False, False)


    def pastecolor(self, srcregion=None, dstsurf=None, dstregion=None, pastefgcolor=True, pastebgcolor=True):
        return self.paste(srcregion, dstsurf, dstregion, False, pastefgcolor, pastebgcolor, False, False, False)


    def pastetint(self, srcregion=None, dstsurf=None, dstregion=None, pasteredtint=True, pastegreentint=True, pastebluetint=True):
        return self.paste(srcregion, dstsurf, dstregion, False, False, False, pasteredtint, pastegreentint, pastebluetint)


    def lighten(self, amount=51, region=None):
        """
        Adds a highlighting tint to the region specified.

        - amount is the amount to lighten by. When the lightening is at 255, the cell will be completely white. A negative amount argument has the same effect as calling darken().
        """

        # NOTE - I chose 51 for the default amount because 51 is a fifth of 255.
        self.tint(amount, amount, amount, region)


    def darken(self, amount=51, region=None):
        """
        Adds a darkening tint to the region specified.

        - amount is the amount to darken by. When the lightening is at -255, the cell will be completely black. A negative amount argument has the same effect as calling lighten().
        """
        self.tint(-amount, -amount, -amount, region)


    def addshadow(self, amount=51, region=None, offset=None, direction=None, xoffset=1, yoffset=1):
        """
        Creates a shadow by darkening the cells around a rectangular region. For example, if the O characters represent the rectangular region, then the S characters represent the darkend cells to form the shadow:

          OOOO
          OOOOS
          OOOOS
          OOOOS
           SSSS

        - amount is the amount to darken the cells. 255 will make the cells completely black.
        - offset is how many cells the shadow is offset from the rectangular region. The example above has an offset of 1. An offset of 0 places no shadow, since it would be directly underneath the rectangular region. Specifying the offset parameter overrides the xoffset and yoffset parameters.
        - direction is used along with offset. This controls which direction the shadow is cast from the rectangular region. Specify one of the directional constants for this parameter (i.e. NORTH, NORTHWEST, EAST, SOUTHEAST, etc.) This parameter is ignored if offset is not specified.
        - xoffset, yoffset are ways to specify the offset directly. Positive values send the shadow to the right and down, negative values to the left and up.
        """
        x, y, width, height = self.getregion(region, False)
        if (x, y, width, height) == (None, None, None, None):
            return

        if offset is not None:
            xoffset = offset
            yoffset = offset

            if direction is not None:
                if direction in (NORTH, NORTHWEST, NORTHEAST):
                    yoffset = -yoffset
                if direction in (WEST, NORTHWEST, SOUTHWEST):
                    xoffset = -xoffset
                if direction in (NORTH, SOUTH):
                    xoffset = 0
                if direction in (WEST, EAST):
                    yoffset = 0

        # north shadow
        if yoffset < 0 and (-width < xoffset < width):
            self.darken(amount, (x + getwithinrange(xoffset, 0, width),
                                 y + yoffset,
                                 width-abs(xoffset),
                                 min(abs(yoffset), height)))

        # south shadow
        if yoffset > 0 and (-width < xoffset < width):
            self.darken(amount, (x + getwithinrange(xoffset, 0, width),
                            y+max(yoffset, height),
                            width-abs(xoffset),
                            min(abs(yoffset), height)))

        # west shadow
        if xoffset < 0 and (-height < yoffset < height):
            self.darken(amount, (x + xoffset,
                                 y + getwithinrange(yoffset, 0, height),
                                 getwithinrange(abs(xoffset), 0, width),
                                 height - abs(yoffset)))

        # east shadow
        if xoffset > 0 and (-height < yoffset < height):
            self.darken(amount, (x + max(xoffset, width),
                                 y + getwithinrange(yoffset, 0, height),
                                 min(abs(xoffset), width),
                                 height - abs(yoffset)))

        # northwest shadow
        if xoffset < 0 and yoffset < 0:
            self.darken(amount, (x + xoffset,
                                 y + yoffset,
                                 min(abs(xoffset), width),
                                 min(abs(yoffset), height)))

        # northeast shadow
        if xoffset > 0 and yoffset < 0:
            self.darken(amount, (x + getwithinrange(xoffset, width, xoffset),
                                 y + yoffset,
                                 min(abs(xoffset), width),
                                 min(abs(yoffset), height)))

        # southwest shadow
        if xoffset < 0 and yoffset > 0:
            self.darken(amount, (x + xoffset,
                                 y + getwithinrange(yoffset, height, yoffset),
                                 min(abs(xoffset), width),
                                 min(abs(yoffset), height)))

        # southeast shadow
        if xoffset > 0 and yoffset > 0:
            self.darken(amount, (x + getwithinrange(xoffset, width, xoffset),
                                 y + getwithinrange(yoffset, height, yoffset),
                                 getwithinrange(abs(xoffset), 0, width),
                                 getwithinrange(abs(yoffset), 0, height)))


    def tint(self, r=0, g=0, b=0, region=None):
        """
        Adjust the red, green, and blue tint of the cells in the specified region.

        - r, g, b are the amount of tint to add/subtract. A positive integer adds tint, negative removes it. At 255, there is maximum tint of that color. At -255 there will never be any amount of that color in the cell.
        """
        x, y, width, height = self.getregion(region)
        if (x, y, width, height) == (None, None, None, None):
            return

        for ix in range(x, x + width):
            for iy in range(y, y + height):
                self._screenRdelta[ix][iy] = getwithinrange(r + self._screenRdelta[ix][iy], min=-255)
                self._screenGdelta[ix][iy] = getwithinrange(g + self._screenGdelta[ix][iy], min=-255)
                self._screenBdelta[ix][iy] = getwithinrange(b + self._screenBdelta[ix][iy], min=-255)
                self._screendirty[ix][iy] = True
        if self._autoupdate:
            self.update()

    def setbrightness(self, amount=0, region=None):
        """
        Set the brightness level of a region of cells.

        - amount is the amount of brightness. 0 means a neutral amount, and the cells will be displayed as their true colors. 255 is maximum brightness, which turns all cells completely white, and -255 is maximum darkness, turning all cells completely black.
        """
        self.settint(amount, amount, amount, region)


    def settint(self, r=0, g=0, b=0, region=None):
        """
        Set the brightness level of a region of cells. The r, g, and b parameters are the amount of red, green, and blue tint used for the region of cells. 0 is no tint at all, whereas 255 is maximum tint and -255 is maximum removal of that color.
        """
        x, y, width, height = self.getregion(region)
        if (x, y, width, height) == (None, None, None, None):
            return

        for ix in range(x, x + width):
            for iy in range(y, y + height):
                self._screenRdelta[ix][iy] = getwithinrange(r, min=-255)
                self._screenGdelta[ix][iy] = getwithinrange(g, min=-255)
                self._screenBdelta[ix][iy] = getwithinrange(b, min=-255)
                self._screendirty[ix][iy] = True

        if self._autoupdate:
            self.update()

    def getchar(self, x, y):
        """Returns the character at cell x, y."""
        if x < 0 or y < 0 or x >= self._width or y >= self._height:
            return None
        return self._screenchar[x][y]


    def getchars(self, region=None, gapChar=' '):
        """
        Returns the a list of the characters in the specified region. Each item in the list is a string of the rows of characters.

        - gapChar is used whenever None is found as a cell. By default this is set to a space character. If gapChar is set to None, then the None characters in cells will be ignored (this could cause alignment issues in between the lines.)
        """
        x, y, width, height = self.getregion(region)
        if (x, y, width, height) == (None, None, None, None):
            return

        lines = []
        for iy in range(y, y + height):
            line = []
            for ix in range(x, x + width):
                if self._screenchar[ix][iy] is None and gapChar is not None:
                    line.append(gapChar)
                else:
                    line.append(self._screenchar[ix][iy])
            lines.append(''.join(line))
        return lines


    def putchar(self, char, x=None, y=None, fgcolor=None, bgcolor=None):
        """
        Print a single character to the coordinates on the surface. This function does not move the cursor.
        """
        if type(char) != str:
            raise Exception('Argument 1 must be str, not %s' % (str(type(char))))

        if char == '':
            return

        if x is None:
            x = self._cursorx
        if y is None:
            y = self._cursory

        if x < 0 or y < 0 or x >= self._width or y >= self._height:
            return None

        if fgcolor is not None:
            self._screenfgcolor[x][y] = getpygamecolor(fgcolor)
        if bgcolor is not None:
            self._screenbgcolor[x][y] = getpygamecolor(bgcolor)

        self._screenchar[x][y] = char[0]
        self._screendirty[x][y] = True

        if self._autoupdate:
            self.update()

        return char


    def putchars(self, chars, x=None, y=None, fgcolor=None, bgcolor=None, indent=False):
        # doc - does not modify the cursor. That's how putchars is different from print() or write()
        # doc - also, putchars does wrap but doesn't cause scrolls. (if you want a single line, just put putchar() calls in a loop)
        if type(chars) != str:
            raise Exception('Argument 1 must be str, not %s' % (str(type(chars))))

        if x is None:
            x = self._cursorx
        if y is None:
            y = self._cursory

        if type(chars) in (list, tuple):
            # convert a list/tuple of strings to a single string (this is so that putchars() can work with the return value of getchars())
            chars = '\n'.join(chars)

        if fgcolor is not None:
            fgcolor = getpygamecolor(fgcolor)
        if bgcolor is not None:
            bgcolor = getpygamecolor(bgcolor)

        tempcurx = x
        tempcury = y
        for i in range(len(chars)):
            if tempcurx >= self._width or chars[i] in ('\n', '\r'): # TODO - wait, this isn't right. We should be ignoring one of these newlines.
                tempcurx = indent and x or 0
                tempcury += 1
            if tempcury >= self._height: # putchars() does not cause a scroll.
                break

            self._screenchar[tempcurx][tempcury] = chars[i]
            self._screendirty[tempcurx][tempcury] = True
            if fgcolor is not None:
                self._screenfgcolor[tempcurx][tempcury] = fgcolor
            if bgcolor is not None:
                self._screenbgcolor[tempcurx][tempcury] = bgcolor
            tempcurx += 1

        if self._autoupdate:
            self.update()


    def setscreencolors(self, fgcolor=None, bgcolor=None, clear=False):
        """
        Sets the foreground and/or background color of the entire screen to the ones specified in the fgcolor and bgcolor parameters. Also sets the PygcurseSurface's default foreground and/or background colors. The brightness of all cells is reset back to 0. This is a good "clear screen" function to use.

        fgcolor - foreground color. If None, then the foreground color isn't changed.
        bgcolor - background color. If None, then the background color isn't changed.
        clear - If set to True, then all the characters on the surface will be erased so that the screen is just a solid fill of the background color. This parameter is False by default.
        """
        if fgcolor is not None:
            self.fgcolor = getpygamecolor(fgcolor)
        if bgcolor is not None:
            self.bgcolor = getpygamecolor(bgcolor)
        char = clear and ' ' or None
        self.fill(char, fgcolor, bgcolor)
        self.setbrightness()


    def erase(self, region=None):
        self.fill(None, None, None, region)


    def paint(self, x, y, bgcolor=None):
        self.putchar(' ', x, y, None, bgcolor)


    def fill(self, char=' ', fgcolor=None, bgcolor=None, region=None):
        x, y, width, height = self.getregion(region)
        if (x, y, width, height) == (None, None, None, None):
            return

        fgcolor = (fgcolor is not None) and (getpygamecolor(fgcolor)) or (self._fgcolor)
        bgcolor = (bgcolor is not None) and (getpygamecolor(bgcolor)) or (self._bgcolor)

        for ix in range(x, x + width):
            for iy in range(y, y + height):
                if char is not None:
                    self._screenchar[ix][iy] = char
                if fgcolor is not None:
                    self._screenfgcolor[ix][iy] = fgcolor
                if bgcolor is not None:
                    self._screenbgcolor[ix][iy] = bgcolor
                self._screendirty[ix][iy] = True

        if self._autoupdate:
            self.update()


    def _scroll(self):
        """Scroll the content of the entire screen up one row. This is done when characters are printed to the screen that go past the end of the last row."""
        for x in range(self._width):
            for y in range(self._height - 1):
                self._screenchar[x][y] = self._screenchar[x][y+1]
                self._screenfgcolor[x][y] = self._screenfgcolor[x][y+1]
                self._screenbgcolor[x][y] = self._screenbgcolor[x][y+1]
                self._screenRdelta[x][y] = self._screenRdelta[x][y+1]
                self._screenGdelta[x][y] = self._screenGdelta[x][y+1]
                self._screenBdelta[x][y] = self._screenBdelta[x][y+1]
            self._screenchar[x][self._height-1] = ' ' # bottom row is blanked
            self._screenfgcolor[x][self._height-1] = self._fgcolor
            self._screenbgcolor[x][self._height-1] = self._bgcolor
            self._screenRdelta[x][self._height-1] = self._rdelta
            self._screenGdelta[x][self._height-1] = self._gdelta
            self._screenBdelta[x][self._height-1] = self._bdelta
        self._screendirty = [[True] * self._height for i in range(self._width)]
        self._scrollcount += 1


    def getregion(self, region=None, truncate=True):
        if region is None:
            return (0, 0, self._width, self._height)
        elif type(region) in (tuple, list) and len(region) == 4:
            x, y, width, height = region
            if x == y == width == height == None:
                return (0, 0, self._width, self._height)
            elif width == height == None:
                width = self._width - x
                height = self._height - y
        elif str(type(region)) in ("<class 'pygame.Color'>", "<type 'pygame.Color'>"):
            x, y, width, heigh = region.x, region.y, region.width, region.height

        if width < 1 or height < 1:
            return None, None, None, None

        if not truncate:
            return x, y, width, height

        if x + width < 0 or y + height < 0 or x >= self._width or y >= self._height:
            # If the region is entirely outside the boundaries, then return None
            return None, None, None, None

        # Truncate width or height if they extend past the boundaries
        if x + width > self._width:
            width -= (x + width) - self._width
        if y + height > self._height:
            height -= (y + height) - self._height
        if x < 0:
            width += x # subtracts, since x is negative
            x = 0
        if y < 0:
            height += y # subtracts, since y is negative
            y = 0

        return x, y, width, height


    def isonscreen(self, x, y):
        """Returns True if the given xy cell coordinates are on the PygcurseSurface object, otherwise False."""
        return x >= 0 and y >= 0 and x < self.width and y < self.height


    def writekeyevent(self, keyevent, x=None, y=None, fgcolor=None, bgcolor=None):
        """
        Writes a character to the PygcurseSurface that the Pygame key event object represents. A foreground and background color can optionally be supplied. An xy cell coordinate can also be supplied, but the current cursor position is used by default.

        - keyevent is the KEYDOWN or KEYUP event that pygame.event.get() returns. This event object contains the key information.
        """
        if x is None or y is None:
            x = self._cursorx
            y = self._cursory
        if not self.isonscreen(x, y):
            return
        char = interpretkeyevent(keyevent)
        if char is not None:
            self.putchar(char, x=x, y=y, fgcolor=fgcolor, bgcolor=bgcolor)


    # File-like Object methods:
    def write(self, text, x=None, y=None, fgcolor=None, bgcolor=None):
        if x is not None:
            self.cursorx = x
        if y is not None:
            self.cursory = y

        fgcolor = (fgcolor is None) and (self._fgcolor) or (getpygamecolor(fgcolor))
        bgcolor = (bgcolor is None) and (self._bgcolor) or (getpygamecolor(bgcolor))

        # TODO - we can calculate in advance what how many scrolls to do.


        # replace tabs with appropriate number of spaces
        i = 0
        tempcursorx = self._cursorx - 1
        while i < len(text):
            if text[i] == '\n':
                tempcursorx = 0
            elif text[i] == '\t':
                numspaces = self._tabsize - ((i+1) + tempcursorx % self._tabsize)
                if tempcursorx + numspaces >= self._width:
                    # tabbed past the edge, just go to first
                    # TODO - this doesn't work at all.
                    text = text[:i] + (' ' * (self._width - tempcursorx + 1)) + text[i+1:]
                    tempcursorx += (self._width - tempcursorx + 1)
                else:
                    text = text[:i] + (' ' * numspaces) + text[i+1:]
                    tempcursorx += numspaces
            else:
                tempcursorx += 1

            if tempcursorx >= self._width:
                tempcursorx = 0
            i += 1

        """
        # create a cache of surface objects for each letter in text
        letterSurfs = {}
        for letter in text:
            if ord(letter) in range(33, 127) and letter not in letterSurfs:
                letterSurfs[letter] = self._font.render(letter, 1, fgcolor, bgcolor)
                #letterSurfs[letter] = letterSurfs[letter].convert_alpha() # TODO - wait a sec, I don't think pygame lets fonts have transparent backgrounds.
            elif letter == ' ':
                continue
            elif letter not in letterSurfs and '?' not in letterSurfs:
                letterSurfs['?'] = self._font.render('?', 1, fgcolor, bgcolor)
                #letterSurfs['?'] = letterSurfs['?'].convert_alpha()
        """

        for i in range(len(text)):
            if text[i] in ('\n', '\r'): # TODO - wait, this isn't right. We should be ignoring one of these newlines. Otherwise \r\n shows up as two newlines.
                self._cursory += 1
                self._cursorx = 0
            else:
                # set the backend data structures that track the screen state
                self._screenchar[self._cursorx][self._cursory] = text[i]
                self._screenfgcolor[self._cursorx][self._cursory] = fgcolor
                self._screenbgcolor[self._cursorx][self._cursory] = bgcolor
                self._screendirty[self._cursorx][self._cursory] = True

                """
                r = pygame.Rect(self._cellwidth * self._cursorx, self._cellheight * self._cursory, self._cellwidth, self._cellheight)
                self._surfaceobj.fill(bgcolor, r)
                charsurf = letterSurfs[text[i]]
                charrect = charsurf.get_rect()
                charrect.centerx = self._cellwidth * self._cursorx + int(self._cellwidth / 2)
                charrect.bottom = self._cellheight * (self._cursory+1)
                self._surfaceobj.blit(charsurf, charrect)
                self._screendirty[self._cursorx][self._cursory] = False
                """

                # Move cursor over (and to next line if it moves past the right edge)
                self._cursorx += 1
                if self._cursorx >= self._width:
                    self._cursorx = 0
                    self._cursory += 1
            if self._cursory >= self._height:
                # scroll up a line if we try to print on the line after the last one
                self._scroll()
                self._cursory = self._height - 1

        if self._autoupdate:
            self.update()


    def read(self): # TODO - this isn't right.
        return '\n'.join(self.getchars())


    # Properties:
    def _propgetcursorx(self):
        return self._cursorx


    def _propsetcursorx(self, value):
        x = int(value)
        if x >= self._width or x <= -self._width:
            return # no-op

        if x < 0:
            x = self._width - x

        self._cursorx = x


    def _propgetcursory(self):
        return self._cursory


    def _propsetcursory(self, value):
        y = int(value)
        if y >= self._height or y <= -self._height:
            return # no-op

        if y < 0:
            y = self._height - y

        self._cursory = y


    def _propgetcursor(self):
        return (self._cursorx, self._cursory)


    def _propsetcursor(self, value):
        x = int(value[0])
        y = int(value[1])
        if not self.isonscreen(x, y):
            return
        self._cursorx = x
        self._cursory = y


    def _propgetinputcursor(self):
        return (self._inputcursorx, self._inputcursory)


    def _propsetinputcursor(self, value):
        x = int(value[0])
        y = int(value[1])
        if not self.isonscreen(x, y):
            return
        if x != self._inputcursorx or y != self._inputcursory:
            self._repaintcell(self._inputcursorx, self._inputcursory) # blank out the old cursor position
        self._inputcursorx = x
        self._inputcursory = y


    def _propgetinputcursormode(self):
        return self._inputcursormode


    def _propsetinputcursormode(self, value):
        if value in (None, 'underline', 'insert', 'box'):
            self._inputcursormode = value
        elif value is False:
            self._inputcursormode = None
        elif value is True:
            self._inputcursormode = 'underline'
        else:
            self._inputcursormode = None


    def _propgetfont(self):
        return self._font


    def _propsetfont(self, value):
        self._font = value # TODO - a lot of this code is copy/paste
        self._cellwidth, self._cellheight = calcfontsize(self._font)
        if self._managesdisplay and self._fullscreen:
            self._windowsurface = pygame.display.set_mode((self._cellwidth * self.width, self._cellheight * self.height), pygame.FULLSCREEN)
        elif self._managesdisplay:
            self._windowsurface = pygame.display.set_mode((self._cellwidth * self.width, self._cellheight * self.height))
        self._pixelwidth = self._width * self._cellwidth
        self._pixelheight = self._height * self._cellheight
        self._surfaceobj = pygame.Surface((self._pixelwidth, self._pixelheight))
        self._surfaceobj = self._surfaceobj.convert_alpha() # TODO - This is needed for erasing, but does this have a performance hit?
        self._screendirty = [[True] * self._height for i in range(self._width)]

        if self._autoupdate:
            self.update()


    def _propgetfgcolor(self):
        return self._fgcolor


    def _propsetfgcolor(self, value):
        self._fgcolor = getpygamecolor(value)


    def _propgetbgcolor(self):
        return self._bgcolor


    def _propsetbgcolor(self, value):
        self._bgcolor = getpygamecolor(value)


    def _propgetcolors(self):
        return (self._fgcolor, self._bgcolor)


    def _propsetcolors(self, value):
        self._fgcolor = getpygamecolor(value[0])
        self._bgcolor = getpygamecolor(value[1])


    def _propgetautoupdate(self):
        return self._autoupdate


    def _propsetautoupdate(self, value):
        self._autoupdate = bool(value)


    def _propgetautoblit(self):
        return self._autoblit


    def _propsetautoblit(self, value):
        self._autoblit = bool(value)


    def _propgetautodisplayupdate(self):
        return self._autodisplayupdate


    def _propsetautodisplayupdate(self, value):
        if self._windowsurface is not None:
            self._autodisplayupdate = bool(value)
        elif bool(value):
            # TODO - this should be a raised exception, not an assertion.
            assert False, 'Window Surface object must be set to a surface before autodisplayupdate can be enabled.'


    def _propgetheight(self):
        return self._height


    def _propsetheight(self, value):
        newheight = int(value)
        if newheight != self._height:
            self.resize(newheight=newheight)


    def _propgetwidth(self):
        return self._width


    def _propsetwidth(self, value):
        newwidth = int(value)
        if newwidth != self._width:
            self.resize(newwidth=newwidth)


    def _propgetsize(self):
        return (self._width, self._height)


    def _propsetsize(self, value):
        newwidth = int(value[0])
        newheight = int(value[1])
        if newwidth != self._width or newheight != self._height:
            self.resize(newwidth, newheight)


    def _propgetpixelwidth(self):
        return self._width * self._cellwidth


    def _propsetpixelwidth(self, value):
        newwidth = int(int(value) / self._cellwidth)
        if newwidth != self._width:
            self.resize(newwidth=newwidth)


    def _propgetpixelheight(self):
        return self._height * self._cellheight


    def _propsetpixelheight(self, value):
        newheight = int(int(value) / self._cellheight)
        if newheight != self._height:
            self.resize(newheight=newheight)


    def _propgetpixelsize(self):
        return (self._width * self._cellwidth, self._height * self._cellheight)


    def _propsetpixelsize(self, value):
        newwidth = int(int(value) / self._cellwidth)
        newheight = int(int(value) / self._cellheight)
        if newwidth != self._width or newheight != self._height:
            self.resize(newwidth, newheight)


    def _propgetcellwidth(self):
        return self._cellwidth


    def _propgetcellheight(self):
        return self._cellheight


    def _propgetcellsize(self):
        return (self._cellwidth, self._cellheight)


    def _propgetsurface(self):
        return self._surfaceobj


    def _propgetleft(self):
        return 0


    def _propgetright(self):
        return self._width - 1 # note: this behavior is different from pygame Rect objects, which do not have the -1.


    def _propgettop(self):
        return 0


    def _propgetbottom(self):
        return self._height - 1 # note: this behavior is different from pygame Rect objects, which do not have the -1.


    def _propgetcenterx(self):
        return int(self._width / 2)


    def _propgetcentery(self):
        return int(self._height / 2)


    def _propgetcenter(self):
        return (int(self._width / 2), int(self._height / 2))


    def _propgettopleft(self):
        return (0, 0)


    def _propgettopright(self):
        return (self._width - 1, 0)


    def _propgetbottomleft(self):
        return (0, self._height - 1)


    def _propgetbottomright(self):
        return (self._width - 1, self._height - 1)


    def _propgetmidleft(self):
        return (0, int(self._height / 2))


    def _propgetmidright(self):
        return (self._width - 1, int(self._height / 2))


    def _propgetmidtop(self):
        return (int(self._width / 2), 0)


    def _propgetmidbottom(self):
        return (int(self._width / 2), self._height - 1)


    def _propgetrect(self):
        return pygame.Rect(0, 0, self._width, self._height)


    def _propgetpixelrect(self):
        return pygame.Rect(0, 0, self._width * self._cellwidth, self._height * self._cellheight)


    def _propgettabsize(self):
        return self._fgcolor


    def _propsettabsize(self, value):
        self._tabsize = max(1, int(value))


    cursorx           = property(_propgetcursorx, _propsetcursorx)
    cursory           = property(_propgetcursory, _propsetcursory)
    cursor            = property(_propgetcursor, _propsetcursor)
    inputcursor       = property(_propgetinputcursor, _propsetinputcursor)
    inputcursormode   = property(_propgetinputcursormode, _propsetinputcursormode)
    fgcolor           = property(_propgetfgcolor, _propsetfgcolor)
    bgcolor           = property(_propgetbgcolor, _propsetbgcolor)
    colors            = property(_propgetcolors, _propsetcolors)
    autoupdate        = property(_propgetautoupdate, _propsetautoupdate)
    autoblit          = property(_propgetautoblit, _propsetautoblit)
    autodisplayupdate = property(_propgetautodisplayupdate, _propsetautodisplayupdate)
    width             = property(_propgetwidth, _propsetwidth)
    height            = property(_propgetheight, _propsetheight)
    size              = property(_propgetsize, _propsetsize)
    pixelwidth        = property(_propgetpixelwidth, _propsetpixelwidth)
    pixelheight       = property(_propgetpixelheight, _propsetpixelheight)
    pixelsize         = property(_propgetpixelsize, _propsetpixelsize)
    font              = property(_propgetfont, _propsetfont)
    cellwidth         = property(_propgetcellwidth, None) # Set func will be in VER2
    cellheight        = property(_propgetcellheight, None) # Set func will be in VER2
    cellsize          = property(_propgetcellsize, None) # Set func will be in VER2
    surface           = property(_propgetsurface, None)
    tabsize           = property(_propgettabsize, _propsettabsize)

    left        = property(_propgetleft, None)
    right       = property(_propgetright, None) # TODO - need set functions for properties that cause a resize
    top         = property(_propgettop, None)
    bottom      = property(_propgetbottom, None)
    centerx     = property(_propgetcenterx, None)
    centery     = property(_propgetcentery, None)
    center      = property(_propgetcenter, None)
    topleft     = property(_propgettopleft, None)
    topright    = property(_propgettopright, None)
    bottomleft  = property(_propgetbottomleft, None)
    bottomright = property(_propgetbottomright, None)
    midleft     = property(_propgetmidleft, None)
    midright    = property(_propgetmidright, None)
    midtop      = property(_propgetmidtop, None)
    midbottom   = property(_propgetmidbottom, None)
    rect        = property(_propgetrect, None)
    pixelrect   = property(_propgetpixelrect, None)

    """
    TODO - ideas for new properties (are these worth it?)
    leftcolumn (0), rightcolumn (which is width - 1)
    toptrow (0), bottomrow (which is height - 1)

    setting rightcolumn and bottom row will call resize, just like setting the right and bottom properties.
    """

    # Primitive Drawing Functions
    def drawline(self, start_pos, end_pos, char=' ', fgcolor=None, bgcolor=None):
        if fgcolor is None:
            fgcolor = self._fgcolor
        else:
            fgcolor = getpygamecolor(fgcolor)

        if bgcolor is None:
            bgcolor = self._bgcolor
        else:
            bgcolor = getpygamecolor(bgcolor)
        # brensenham line algorithm
        x0, y0 = start_pos
        x1, y1 = end_pos
        isSteep = abs(y1 - y0) > abs(x1 - x0)
        if isSteep:
            # swap the x's and y's
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            # swap end points so that we always go left-to-right
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        if y0 < y1:
            ystep = 1
        else:
            ystep = -1
        xdelta = x1 - x0
        ydelta = abs(y1 - y0)
        error = -xdelta / 2 # TODO - float div or int div?
        y = y0
        for x in range(x0, x1+1): # +1 to include x1 in the range
            if isSteep:
                self.putchar(char, y, x, fgcolor, bgcolor)
            else:
                self.putchar(char, x, y, fgcolor, bgcolor)

            error = error + ydelta
            if error > 0:
                y = y + ystep
                error = error - xdelta


    def drawlines(self, pointlist, closed=False, char=' ', fgcolor=None, bgcolor=None):
        if len(pointlist) < 2:
            return
        for i in range(len(pointlist) - 1):
            self.drawline(pointlist[i], pointlist[i + 1], char, fgcolor, bgcolor)
        if closed:
            self.drawline(pointlist[-1], pointlist[0], char, fgcolor, bgcolor)


class PygcurseWindow(PygcurseSurface):
    _pygcurseClass = 'PygcurseWindow'

    def __init__(self, width=80, height=25, caption=None, font=None, fgcolor=DEFAULTFGCOLOR, bgcolor=DEFAULTBGCOLOR, fullscreen=False):
        pygame.init()
        self._fullscreen = fullscreen
        fullscreen = fullscreen and FULLSCREEN or _NEW_WINDOW
        if sys.version.startswith('2.'):
            super(PygcurseWindow, self).__init__(width, height, font, fgcolor, bgcolor, fullscreen) # for Python 2
        else:
            super().__init__(width, height, font, fgcolor, bgcolor, fullscreen) # for Python 3 and later
        if caption is not None:
            pygame.display.set_caption(caption)


    def blittowindow(self, dest=(0,0), displayupdate=True):
        retval = self._windowsurface.blit(self._surfaceobj, dest)
        if displayupdate:
            pygame.display.update()
        return retval


    def _propgetfullscreen(self):
        return self._fullscreen


    def _propsetfullscreen(self, value):
        if value and not self._fullscreen:
            self._fullscreen = True
            self._windowsurface = pygame.display.set_mode((self.pixelwidth, self.pixelheight), pygame.FULLSCREEN)
        elif not value and self._fullscreen:
            self._fullscreen = False
            self._windowsurface = pygame.display.set_mode((self.pixelwidth, self.pixelheight))

    fullscreen = property(_propgetfullscreen, _propsetfullscreen)


class PygcurseInput():
    """
    A PygcurseInput object keeps track of the state of a string of text being entered, identical to the behavior of raw_input()/input().

    Keypress events are sent to the object, which tracks the characters entered (in self.buffer) and the position of the cursor. The update() function draws the current state of the input to the PygcurseSurface object associated with it. (This is set in the constructor with the pygsurf parameter.)

    The design of this class is that it is meant to be polled. It does not use callbacks or multithreading or an event loop.
    """


    def __init__(self, pygsurf=None, prompt='', x=None, y=None, maxlength=None, fgcolor=None, bgcolor=None, promptfgcolor=None, promptbgcolor=None, whitelistchars=None, blacklistchars=None):
        self.buffer = []
        self.prompt = prompt
        self.pygsurf = pygsurf
        if maxlength is None and pygsurf is None:
            self._maxlength = 4094 # NOTE - Python's input()/raw_input() functions let you enter at most 4094 characters. PygcurseInput has this as a default unless you specify otherwise
        elif maxlength is None and x is not None and y is not None:
            self._maxlength = pygsurf.width - x
        else:
            self._maxlength = (maxlength is not None and maxlength > 0) and (maxlength) or (4094)
        self.cursor = 0
        self.showCursor = True
        self.blinkingCursor = True
        self.eraseBufferSize = None # when set to None, nothing needs to be erased. When the buffer decreases in size, we need to remember how big it was so that we can paint blank space characters.

        self.insertMode = False
        self.done = False # when True, the enter key has been pressed.

        if pygsurf is not None:
            if x is None:
                self.startx = pygsurf.cursorx
            else:
                self.startx = x
            if y is None:
                self.starty = pygsurf.cursory
            else:
                self.starty = y
            self.lastScrollCount = pygsurf._scrollcount
        else:
            if x is None:
                self.startx = 0
            else:
                self.startx = x
            if y is None:
                self.starty = 0
            else:
                self.starty = y
            self.lastScrollCount = 0

        self._fgcolor = (fgcolor is not None) and (getpygamecolor(fgcolor)) or (None)
        self._bgcolor = (bgcolor is not None) and (getpygamecolor(bgcolor)) or (None)
        self._promptfgcolor = (promptfgcolor is not None) and (getpygamecolor(promptfgcolor)) or (None)
        self._promptbgcolor = (promptbgcolor is not None) and (getpygamecolor(promptbgcolor)) or (None)

        self.whitelistchars = whitelistchars
        self.blacklistchars = blacklistchars

        self.multiline = True # if True, then wrap to next line (scrolling the PygcurseSurface if needed.)

        self.KEYMAPPING = {K_LEFT:      self.leftarrow,
                           K_RIGHT:     self.rightarrow,
                           K_HOME:      self.home,
                           K_END:       self.end,
                           K_BACKSPACE: self.backspace,
                           K_DELETE:    self.delete,
                           K_INSERT:    self.insert}

        if pygsurf._pygcurseClass == 'PygcurseWindow': # TODO - need a better way to identify the object
            self.pygsurface = pygsurf.surface
        elif pygsurf._pygcurseClass == 'PygcurseSurface': # TODO - need a better way to identify the object
            self.pygsurface = pygsurf
        else:
            raise Exception('Invalid argument passed for pygsurf parameter.')


    def updateerasebuffersize(self):
        """
        This method must be called whenever a character is deleted from the buffer. The eraseBufferSize member tracks how many characters have been deleted so that the next time this PygcurseInput object is drawn to the PygcurseSurface, it will erase the additional leftover characters.
        """
        # NOTE - don't update if the current buffer size is smaller than the current erase buffer size (two backspaces in a row without calling update() to reset erasebuffersize)
        if self.eraseBufferSize is None or len(self.buffer) > self.eraseBufferSize:
            self.eraseBufferSize = len(self.buffer)


    def backspace(self):
        """Perform the action that happens when the backspac key is pressed."""
        if self.cursor == 0:
            return
        self.cursor -= 1
        self.updateerasebuffersize()
        del self.buffer[self.cursor]


    def insert(self):
        """Perform the action that happens when the insert key is pressed."""
        self.insertMode = not self.insertMode


    def delete(self):
        """Perform the action that happens when the delete key is pressed."""
        if self.cursor == len(self.buffer):
            return
        self.updateerasebuffersize()
        del self.buffer[self.cursor]


    def home(self):
        """Perform the action that happens when the home key is pressed."""
        self.cursor = 0


    def end(self):
        """Perform the action that happens when the end key is pressed."""
        self.cursor = len(self.buffer)


    def leftarrow(self):
        """Perform the action that happens when the left arrow key is pressed."""
        if self.cursor > 0:
            self.cursor -= 1


    def rightarrow(self):
        """Perform the action that happens when the right arrow key is pressed."""
        if self.cursor < len(self.buffer):
            self.cursor += 1


    def paste(text):
        """
        Inserts the string text into the buffer at the position of the cursor. This does not actually use the system's clipboard, it only pastes from the text parameter.
        """
        text = str(text)
        if not self.insertMode and len(text) + len(self.buffer) > self._maxlength:
            text = text[:self._maxlength - len(self.buffer)] # truncate the pasted text (this is what web browsers do, so I'm copying that behavior)

        if self.cursor == len(self.buffer):
            # append to end
            self.buffer.extend(list(text))
        elif self.cursor == 0:
            # prepend to beginning
            self.buffer = list(text) + self.buffer
        else:
            if self.insertMode:
                # Overwrite characters
                self.buffer = self.buffer[:self.cursor] + list(text) + self.buffer[self.cursor + len(text):]
            else:
                self.buffer = self.buffer[:self.cursor] + list(text) + self.buffer[self.cursor:]


    def update(self, pygsurfObj=None):
        """
        Draw the PygcurseInput object to the PygcurseSurface object associated with it (in the self.pygsurf member) or to the pygsurfObj argument.

        This method handles drawing the prompt, typed in text, and cursor of this object.
        """
        if pygsurfObj is not None and pygsurfObj._pygcurseClass in ('PygcurseWindow', 'PygcurseSurface'): # TODO - need a better way to identify the object
            pygsurfObj = pygsurfObj.surface
        elif self.pygsurf is not None:
            pygsurfObj = self.pygsurf
        else:
            raise Exception('No PygcurseSurface object specified to draw the PygcurseWindow object to.')

        if self.lastScrollCount < pygsurfObj._scrollcount:
            # pygsurf has scrolled up since the last time this was drawn, move the input up.
            self.starty -= pygsurfObj._scrollcount - self.lastScrollCount
            # TODO - need to handle the case where the starty is now negative

        if self.multiline:
            pygsurfObj.pushcursor()
            if self.eraseBufferSize is not None:
                # need to blank out the previous drawn, longer string.
                pygsurfObj.write(self.prompt + (' ' * self.eraseBufferSize))
                pygsurfObj.popcursor() # revert to the original cursor before proceeding
                pygsurfObj.pushcursor()
                self.eraseBufferSize = None
            pygsurfObj.write(self.prompt, fgcolor=self._promptfgcolor, bgcolor=self._promptbgcolor)
            pygsurfObj.write(''.join(self.buffer) + ' ', fgcolor=self._fgcolor, bgcolor=self._bgcolor) # the space at the end is to change the color of the cursor
            afterPromptX, afterPromptY = pygsurfObj.getnthcellfrom(self.startx, self.starty, len(self.prompt))
            pygsurfObj.inputcursor = pygsurfObj.getnthcellfrom(afterPromptX, afterPromptY, self.cursor)
            pygsurfObj._drawinputcursor() # TODO - there's a bug if the prompt goes past the right edge, the screen cursor is in a weird place.
            pygsurfObj.popcursor() # restore previous cursor position that print() moved.
        else:
            # all this must fit on one line, with any excess text truncated
            if self.eraseBufferSize is not None:
                # need to blank out the previous drawn, longer string.
                tempcursorx = self.startx
                while tempcursorx < pygsurfObj.width and tempcursorx < self.startx + len(self.prompt) + eraseBufferSize:
                    pygsurfObj.putchar(' ', tempcursorx, self.starty)
                    tempcursorx += 1
                self.eraseBufferSize = None
            numToPrint = self._width - self.startx - 1
            # TODO - implement prompt colors, but keep in mind that this all has to be on one line.
            pygsurfObj.putchars((self.prompt + ''.join(self.buffer))[:numToPrint], self.startx, self.starty, fgcolor=self._fgcolor, bgcolor=self._bgcolor)
            pygsurfObj.inputcursor = pygsurfObj.getnthcellfrom(self.startx, self.starty, self.cursor)
            pygsurfObj._drawinputcursor()


    def enter(self):
        """Sets self.done to True, which means that the user has intended to enter the currently typed in text as their complete response. While self.done is True, this object will no longer process additional keyboard events."""
        self.done = True


    def sendkeyevent(self, keyEvent):
        """Interpret the character that the pygame.event.Event object passed as keyEvent represents, and perform the associated action. These actions could be adding another character to the buffer, or manipulating the cursor position (such as when the arrow keys are pressed)."""

        # TODO - how should we handle tab key presses? For now, we just treat it as a space.
        if self.done:
            return

        char = interpretkeyevent(keyEvent)
        if char in ('\r', '\n') and keyEvent.type == KEYUP: # TODO - figure out which is the right one
            self.done = True
            self.pygsurf.inputcursormode = None
            x, y = self.pygsurf.getnthcellfrom(self.startx, self.starty, self.cursor)
            self.pygsurf.write('\n') # print a newline to move the pygcurse surface object's cursor.
            self.pygsurf._repaintcell(x, y)
        elif char not in ('\r', '\n') and keyEvent.type == KEYDOWN:
            if char is None and keyEvent.key in self.KEYMAPPING:
                (self.KEYMAPPING[keyEvent.key])() # call the related method
            elif char is not None:
                if (self.whitelistchars is not None and char not in self.whitelistchars) or (self.blacklistchars is not None and char in self.blacklistchars):
                    return # filter out based on white and black list

                if char == '\t':
                    char = ' '
                if (not self.insertMode and len(self.buffer) < self._maxlength) or (self.insertMode and self.cursor == len(self.buffer)):
                    self.buffer.insert(self.cursor, char)
                    self.cursor += 1
                elif len(self.buffer) < self._maxlength:
                    self.buffer[self.cursor] = char
                    self.cursor += 1
        self.pygsurf.inputcursor = self.pygsurf.getnthcellfrom(self.startx, self.starty, self.cursor)


    def _debug(self):
        """Print out the current state of the PygcurseInput object to stdout."""
        print(self.prompt + ''.join(self.buffer) + '\t(%s length)' % len(self.buffer))
        print('.' * len(self.prompt) + '.' * self.cursor + '^')


    def __len__(self):
        """Returns the length of the buffer. This does not include the length of the prompt."""
        return len(self.buffer)


    # Properties
    def _propgetfgcolor(self):
        return self._fgcolor

    def _propsetfgcolor(self, value):
        self._fgcolor = getpygamecolor(value)


    def _propgetbgcolor(self):
        return self._bgcolor

    def _propsetbgcolor(self, value):
        self._bgcolor = getpygamecolor(value)

    def _propgetcolors(self):
        return (self._fgcolor, self._bgcolor)

    def _propsetcolors(self, value):
        self._fgcolor = getpygamecolor(value[0])
        self._bgcolor = getpygamecolor(value[1])


    def _propgetpromptfgcolor(self):
        return self._promptfgcolor

    def _propsetpromptfgcolor(self, value):
        self._promptfgcolor = getpygamecolor(value)


    def _propgetpromptbgcolor(self):
        return self._promptbgcolor

    def _propsetpromptbgcolor(self, value):
        self._promptbgcolor = getpygamecolor(value)

    def _propgetpromptcolors(self):
        return (self._promptfgcolor, self._promptbgcolor)

    def _propsetpromptcolors(self, value):
        self._promptfgcolor = getpygamecolor(value[0])
        self._promptbgcolor = getpygamecolor(value[1])

    fgcolor = property(_propgetfgcolor, _propsetfgcolor)
    bgcolor = property(_propgetbgcolor, _propsetbgcolor)
    colors = property(_propgetcolors, _propsetcolors)
    promptfgcolor = property(_propgetpromptfgcolor, _propsetpromptfgcolor)
    promptbgcolor = property(_propgetpromptbgcolor, _propsetpromptbgcolor)
    promptcolors = property(_propgetpromptcolors, _propsetpromptcolors)



class PygcurseTextbox:
    def __init__(self, pygsurf, region=None, fgcolor=None, bgcolor=None, text='', wrap=True, border='basic', caption='', margin=0, marginleft=None, marginright=None, margintop=None, marginbottom=None, shadow=None, shadowamount=51):
        self.pygsurf = pygsurf
        self.x, self.y, self.width, self.height = pygsurf.getregion(region, False)

        self.fgcolor = (fgcolor is None) and (pygsurf.fgcolor) or (getpygamecolor(fgcolor))
        self.bgcolor = (bgcolor is None) and (pygsurf.bgcolor) or (getpygamecolor(bgcolor))
        self.text = text
        self.wrap = wrap
        self.border = border # value is one of 'basic', 'rounded', or a single character
        self.caption = caption

        self.margintop = margin
        self.marginbottom = margin
        self.marginleft = margin
        self.marginright = margin
        if margintop is not None:
            self.margintop = margintop
        if marginbottom is not None:
            self.marginbottom = marginbottom
        if marginright is not None:
            self.marginright = marginright
        if marginleft is not None:
            self.marginleft = marginleft
        self.shadow = shadow # value is a None or directional constant, e.g. NORTHWEST
        self.shadowamount = shadowamount

        # not included in the parameters, because the number of parameters is getting ridiculous. The user can always change these later.
        self.shadowxoffset = 1
        self.shadowyoffset = 1

    def update(self, pygsurf=None):
        # NOTE - border of 'basic' uses +,-,| scheme. A single letter can be used to use that character for a border. None means no border. '' means an empty border (same as border of None and margin of 1)
        # NOTE - this function does not create scrollbars, any excess characters are just truncated.

        if pygsurf is None:
            pygsurf = self.pygsurf

        x, y, width, height = pygsurf.getregion((self.x, self.y, self.width, self.height))
        if (x, y, width, height) == (None, None, None, None):
            return

        fgcolor = (self.fgcolor is None) and pygsurf.fgcolor or self.fgcolor
        bgcolor = (self.bgcolor is None) and pygsurf.bgcolor or self.bgcolor

        # blank out space for box
        for ix in range(x, x + width):
            for iy in range(y, y + height):
                pygsurf._screenfgcolor[ix][iy] = fgcolor
                pygsurf._screenbgcolor[ix][iy] = bgcolor
                pygsurf._screenchar[ix][iy] = ' '
                pygsurf._screendirty[ix][iy] = True

        # Recalculate dimensions, this time including if they are off the surface.
        x, y, width, height = pygsurf.getregion((self.x, self.y, self.width, self.height), False)
        if (x, y, width, height) == (None, None, None, None):
            return

        # draw border
        if self.border in ('basic', 'rounded'):
            # corners
            if pygsurf.isonscreen(x, y):
                pygsurf._screenchar[x][y] = (self.border == 'basic') and '+' or '/'
            if pygsurf.isonscreen(x + width - 1, y):
                pygsurf._screenchar[x + width - 1][y] = (self.border == 'basic') and '+' or '\\'
            if pygsurf.isonscreen(x, y + height - 1):
                pygsurf._screenchar[x][y + height - 1] = (self.border == 'basic') and '+' or '\\'
            if pygsurf.isonscreen(x + width - 1, y + height - 1):
                pygsurf._screenchar[x + width - 1][y + height - 1] = (self.border == 'basic') and '+' or '/'

            # top/bottom side
            for ix in range(x + 1, x + width - 1):
                if pygsurf.isonscreen(ix, y):
                    pygsurf._screenchar[ix][y] = '-'
                if pygsurf.isonscreen(ix, y + height-1):
                    pygsurf._screenchar[ix][y + height-1] = '-'

            # left/right side
            for iy in range(y+1, y + height-1):
                if pygsurf.isonscreen(x, iy):
                    pygsurf._screenchar[x][iy] = '|'
                if pygsurf.isonscreen(x + width - 1, iy):
                    pygsurf._screenchar[x + width - 1][iy] = '|'
        elif self.border is not None and len(self.border) == 1:
            # use a single character to draw the entire border
            # top/bottom side
            for ix in range(x, x + width):
                if pygsurf.isonscreen(ix, y):
                    pygsurf._screenchar[ix][y] = self.border
                if pygsurf.isonscreen(ix, y + height-1):
                    pygsurf._screenchar[ix][y + height-1] = self.border

            # left/right side
            for iy in range(y+1, y + height-1):
                if pygsurf.isonscreen(x, iy):
                    pygsurf._screenchar[x][iy] = border
                if pygsurf.isonscreen(x + width - 1, iy):
                    pygsurf._screenchar[x + width - 1][iy] = border

        # draw caption:
        if self.caption:
            for i in range(len(self.caption)):
                if i + 2 > self.width - 2 or not pygsurf.isonscreen(x + i + 2, y):
                    continue
                pygsurf._screenchar[x + i + 2][y] = self.caption[i]

        # draw the textbox shadow
        if self.shadow is not None:
            pygsurf.addshadow(x=x, y=y, width=width, height=height, amount=self.shadowamount, direction=self.shadow, xoffset=self.shadowxoffset, yoffset=self.shadowyoffset)


        if self.text == '':
            return # There's no text to display, so return after drawing the background and border.
        text = self.getdisplayedtext()
        if text == '':
            return

        if self.border is not None:
            x += 1
            y += 1
            width -= 2
            height -= 2
        if not self.border and self.caption:
            y += 1
            height -= 1
        x += self.marginleft
        y += self.margintop
        width -= (self.marginleft + self.marginright)
        height -= (self.margintop + self.marginbottom)

        if y < 0: # if the top row of text is above the top edge of the surface, then truncate
            text = text[abs(y):]
            y = 0
        maxDisplayedLines = (y + height < pygsurf._height) and (height) or (max(0, pygsurf._height - y))

        truncateLeftChars = (x < 0) and abs(x) or 0
        maxDisplayedLength = (x + width < pygsurf._width) and (width) or (max(0, pygsurf._width - x))
        iy = 0
        for line in text:
            if y + iy >= pygsurf._height:
                break
            for ix in range(truncateLeftChars, min(len(line), maxDisplayedLength)):
                pygsurf._screenchar[x + ix][y + iy] = line[ix]
            iy += 1


    def getdisplayedtext(self):
    # returns the text that can be displayed given the box's current width, height, border, and margins
        margintop = self.margintop
        marginbottom = self.marginbottom
        marginright = self.marginright
        marginleft = self.marginleft

        # calculate margin & text layout
        if self.border is not None:
            margintop += 1
            marginbottom += 1
            marginleft += 1
            marginright += 1
        elif self.caption:
            margintop += 1

        width = self.width - marginleft - marginright
        height = self.height - margintop - marginbottom

        if width < 1 or height < 1:
            return '' # no room for text

        # handle word wrapping
        if self.wrap:
            text = textwrap.wrap(self.text, width=width)
        else:
            text = spitintogroupsof(width, self.text) # TODO - slight bug where if a line ends with \n, it could show an additional character. (this is the behavior of textwrap.wrap())

        return text[:height]


    def erase(self):
        # a convenience function, more than anything. Does the same thing as fill except for just the area of this text box.
        self.pygsurf.fill(x=self.x, y=self.y, width=self.width, height=self.height)

    # TODO - make properties for magins, shadowxoffset, etc.

    def _propgetleft(self):
        return self.x
    def _propgetright(self):
        return self.x + self.width - 1 # note: this behavior is different from pygame Rect objects, which do not have the -1.
    def _propgettop(self):
        return self.y
    def _propgetbottom(self):
        return self.y + self.height - 1 # note: this behavior is different from pygame Rect objects, which do not have the -1.
    def _propgetcenterx(self):
        return self.x + int(self.width / 2)
    def _propgetcentery(self):
        return self.y + int(self.height / 2)
    def _propgettopleft(self):
        return (self.x, self.y)
    def _propgettopright(self):
        return (self.x + self.width - 1, self.y)
    def _propgetbottomleft(self):
        return (self.x, self.y + self.height - 1)
    def _propgetbottomright(self):
        return (self.x + self.width - 1, self.y + self.height - 1)
    def _propgetmidleft(self):
        return (self.x, self.y + int(self.height / 2))
    def _propgetmidright(self):
        return (self.x + self.width - 1, self.y + int(self.height / 2))
    def _propgetmidtop(self):
        return (self.x + int(self.width / 2), self.y)
    def _propgetmidbottom(self):
        return (self.x + int(self.width / 2), self.y + self.height - 1)
    def _propgetcenter(self):
        return (self.x + int(self.width / 2), self.y + int(self.height / 2))
    def _propgetregion(self):
        return (self.x, self.y, self.width, self.height)

    def _propsetleft(self, value):
        self.x = value
    def _propsetright(self, value):
        self.x = value - self.width
    def _propsettop(self, value):
        self.y = value
    def _propsetbottom(self, value):
        self.y = value - self.height
    def _propsetcenterx(self, value):
        self.x = value - int(self.width / 2)
    def _propsetcentery(self, value):
        self.y = value - int(self.height / 2)
    def _propsetcenter(self, value):
        self.x = value[0] - int(self.width / 2)
        self.y = value[1] - int(self.height / 2)
    def _propsettopleft(self, value):
        self.x = value[0]
        self.y = value[1]
    def _propsettopright(self, value):
        self.x = value[0] - self.width
        self.y = value[1]
    def _propsetbottomleft(self, value):
        self.x = value[0]
        self.y = value[1] - self.height
    def _propsetbottomright(self, value):
        self.x = value[0] - self.width
        self.y = value[1] - self.height
    def _propsetmidleft(self, value):
        self.x = value[0]
        self.y = value[1] - int(self.height / 2)
    def _propsetmidright(self, value):
        self.x = value[0] - self.width
        self.y = value[1] - int(self.height / 2)
    def _propsetmidtop(self, value):
        self.x = value[0] - int(self.width / 2)
        self.y = value[1]
    def _propsetmidbottom(self, value):
        self.x = value[0] - int(self.width / 2)
        self.y = value[1] - self.height
    def _propsetcenter(self, value):
        self.x = value[0] - int(self.width / 2)
        self.y = value[1] - int(self.height / 2)
    def _propsetregion(self, value):
        self.x, self.y, self.width, self.height = pygsurf.getregion(value, False)

    def _propgetsize(self):
        return (self.width, self.height)
    def _propsetsize(self, value):
        newwidth = int(value[0])
        newheight = int(value[1])
        if newwidth != self.width or newheight != self.height:
            self.resize(newwidth, newheight)
    def _propgetpixelwidth(self):
        return self.width * self._cellwidth
    def _propsetpixelwidth(self, value):
        newwidth = int(int(value) / self._cellwidth)
        if newwidth != self.width:
            self.resize(newwidth=newwidth)
    def _propgetpixelheight(self):
        return self.height * self._cellheight
    def _propsetpixelheight(self, value):
        newheight = int(int(value) / self._cellheight)
        if newheight != self.height:
            self.resize(newheight=newheight)
    def _propgetpixelsize(self):
        return (self.width * self._cellwidth, self.height * self._cellheight)
    def _propsetpixelsize(self, value):
        newwidth = int(int(value) / self._cellwidth)
        newheight = int(int(value) / self._cellheight)
        if newwidth != self.width or newheight != self.height:
            self.resize(newwidth, newheight)

    left        = property(_propgetleft, _propsetleft)
    right       = property(_propgetright, _propsetright)
    top         = property(_propgettop, _propsettop)
    bottom      = property(_propgetbottom, _propsetbottom)
    centerx     = property(_propgetcenterx, _propsetcenterx)
    centery     = property(_propgetcentery, _propsetcentery)
    center      = property(_propgetcenter, _propsetcenter)
    topleft     = property(_propgettopleft, _propsettopleft)
    topright    = property(_propgettopright, _propsettopright)
    bottomleft  = property(_propgetbottomleft, _propsetbottomleft)
    bottomright = property(_propgetbottomright, _propsetbottomright)
    midleft     = property(_propgetmidleft, _propsetmidleft)
    midright    = property(_propgetmidright, _propsetmidright)
    midtop      = property(_propgetmidtop, _propsetmidtop)
    midbottom   = property(_propgetmidbottom, _propsetmidbottom)
    region      = property(_propgetregion, _propsetregion)

    pixelwidth  = property(_propgetsize, _propsetsize)
    pixelheight = property(_propgetsize, _propsetsize)
    pixelsize   = property(_propgetsize, _propsetsize)
    size        = property(_propgetsize, _propsetsize)

_shiftchars = {'`':'~', '1':'!', '2':'@', '3':'#', '4':'$', '5':'%', '6':'^', '7':'&', '8':'*', '9':'(', '0':')', '-':'_', '=':'+', '[':'{', ']':'}', '\\':'|', ';':':', "'":'"', ',':'<', '.':'>', '/':'?'}

def interpretkeyevent(keyEvent):
    """Returns the character represented by the pygame.event.Event object in keyEvent. This makes adjustments for the shift key and capslock."""
    key = keyEvent.key
    if (key >= 32 and key < 127) or key in (ord('\n'), ord('\r'), ord('\t')):
        caps = bool(keyEvent.mod & KMOD_CAPS)
        shift = bool(keyEvent.mod & KMOD_LSHIFT or keyEvent.mod & KMOD_RSHIFT)
        char = chr(key)
        if char.isalpha() and (caps ^ shift):
            char = char.upper()
        elif shift and char in _shiftchars:
            char = _shiftchars[char]
        return char
    return None # None means that there is no printable character corresponding to this keyEvent


def spitintogroupsof(groupSize, theList):
    # splits a sequence into a list of sequences, where the inner lists have at
    # most groupSize number of items.
    result = []
    for i in range(0, len(theList), groupSize):
        result.append(theList[i:i+groupSize])
    return result


def getwithinrange(value, min=0, max=255):
    """
    Returns value if it is between the min and max number arguments. If value is greater than max, then max is returned. If value is less than min, then min is returned. If min and/or max is not specified, then the value is not limited in that direction.
    """
    if min is not None and value < min:
        return min
    elif max is not None and value > max:
        return max
    else:
        return value


def calcfontsize(font):
    """Returns the maximum width and maximum height used by any character in this font. This function is used to calculate the cell size."""
    maxwidth = 0
    maxheight = 0
    for i in range(32, 127):
        surf = font.render(chr(i), True, (0,0,0))
        if surf.get_width() > maxwidth:
            maxwidth = surf.get_width()
        if surf.get_height() > maxheight:
            maxheight = surf.get_height()

    return maxwidth, maxheight


def _ismonofont(font):
    """Returns True if all the characters in the font are of the same width, indicating that this is a monospace font.

    TODO - Not sure what I was planning to use this function for. I'll leave it in here for now.
    """
    minwidth = 0
    minheight = 0
    for i in range(32, 127):
        surf = font.render(chr(i), True, (0,0,0))
        if surf.get_width() < minwidth:
            minwidth = surf.get_width()
        if surf.get_height() < minheight:
            minheight = surf.get_height()

    maxwidth, maxheight = calcfontsize(font)
    return maxwidth - minwidth <= 3 and maxheight - minheight <= 3


def getpygamecolor(value):
    """Returns a pygame.Color object of the argument passed in. The argument can be a RGB/RGBA tuple, pygame.Color object, or string in the colornames dict (such as 'blue' or 'gray')."""
    if type(value) in (tuple, list):
        alpha = len(value) > 3 and value[3] or 255
        return pygame.Color(value[0], value[1], value[2], alpha)
    elif str(type(value)) in ("<class 'pygame.Color'>", "<type 'pygame.Color'>"):
        return value
    elif value in colornames:
        return colornames[value]
    else:
        raise Exception('Color set to invalid value: %s' % (repr(value)))

    if type(color) in (tuple, list):
        return pygame.Color(*color)
    return color

def waitforkeypress(fps=None):
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    if fps is not None:
        clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get([KEYDOWN, KEYUP, QUIT]):
            if event.type == KEYDOWN:
                continue
            elif event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYUP:
                return interpretkeyevent(event)
        pygame.display.update()
        if fps is not None:
            clock.tick(fps)

def regionsoverlap(region1, region2):
    return withinregion(region1[0], region1[1], region2) or \
           withinregion(region1[0] + region1[2], region1[1], region2) or \
           withinregion(region1[0], region1[1] + region1[3], region2) or \
           withinregion(region1[0] + region1[2], region1[1] + region1[3], region2) or \
           withinregion(region2[0], region2[1], region1) or \
           withinregion(region2[0] + region2[2], region2[1], region1) or \
           withinregion(region2[0], region2[1] + region2[3], region1) or \
           withinregion(region2[0] + region2[2], region2[1] + region2[3], region1)

def withinregion(x, y, region):
    return x > region[0] and x < region[0] + region[2] and y > region[1] and y < region[1] + region[3]
