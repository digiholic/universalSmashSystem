import main

"""
This method returns an instance of the fighter.
"""
def getFighter(playerNum):
    fight = main.importFromURI(__file__,'hitboxie.py')
    
    return fight.Hitboxie(playerNum)

"""
The ColorMap class is used to dictate all of the possible palette swaps of a fighter.

colorDict is a Dictionary mapping a color in the original sprite sheet to a color that it
should be changed to. As an example here, Hitboxie only has one color to change, and that
is black (0,0,0), so a dict can easily be defined in one line. For a more complicated
color map, you could break it up into multiple lines. For example, to change all of Hitboxie's
colors, including his border, it would be something like this:

{(0,0,0}       : (0,0,255),
 (128,128,128) : (0,0,128),
 (166,166,166) : (0,0,200)}

keyColor is simply the color that shows on the CSS screen when selecting your palette.
This color should be indicative of the overall color of the palette, so players can
easily coordinate team colors or pick their favorite color without needed to know what
the palette looks like.

newCSSImg is a path to the character select screen portrait for that palette. It is not
necessary, and if None is given, it will simply use the normal portrait. The CSS Images
are likely not quite as simple as the sprites, so doing a color replace on that with the
same map will often lead to undesirable results.
"""
class ColorMap():
    def __ini__(self,colorDict,keyColor,newCSSImg = None):
        self.colorDict = colorDict
        self.keyColor = keyColor
        self.newCSSImg = newCSSImg
        
colorMaps = [ColorMap({(0,0,0) : (0,0,0)      }, (0,0,0),       None),
             ColorMap({(0,0,0) : (0,0,255)    }, (0,0,255),     None),
             ColorMap({(0,0,0) : (0,255,0)    }, (0,255,0),     None),
             ColorMap({(0,0,0) : (255,0,0)    }, (255,0,0),     None),
             ColorMap({(0,0,0) : (255,255,0)  }, (255,255,0),   None),
             ColorMap({(0,0,0) : (0,255,255)  }, (0,255,255),   None),
             ColorMap({(0,0,0) : (255,0,255)  }, (255,0,255),   None),
             ColorMap({(0,0,0) : (255,255,255)}, (255,255,255), None),
             ]

def getColor(n):
    global colorMaps
    return colorMaps[n]


"""
This function is called when the character is clicked on in the CSS.
This is where you can select variant costumes, colors, and whatever
else you want to make selectable at the screen, such as variant
ultimate attacks, special moves, or even physics tweaks.
"""
def onCSSClick():
    pass