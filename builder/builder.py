import pygame

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480),pygame.HWACCEL | pygame.DOUBLEBUF | pygame.RESIZABLE)
    pygame.display.set_caption('Character Builder')
    
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((128, 128, 128))
    
    appPanels = []
    

#The base Panel Class, which the others inherit from. Will handle drawing, porting on the screen, resizing, etc.    
class Panel():
    def __init__(self):
        self.rect = pygame.Rect()
        self.port_on_screen = pygame.Rect()
        self.parent = None
        
    def draw(self,screen):
        screen.blit(self.image,self.rect)

#The header panel will handle things like saving/loading, reading images, etc.
class HeaderPanel(Panel):
    pass

#The ImagePanel shows the current sprite and image, as well as hitboxes and hurtboxes if they are being inspected.
#Also includes a grid, as well as a text line that shows the xy coordinates from topleft, as well as from center.
class ImagePanel(Panel):
    pass

#The ActionPanel shows the current action being worked on. Each subaction is listed here, in order.
class ActionPanel(Panel):
    pass

#This changes depending on what subaction is selected in the ActionPanel. It contains options for the subaction,
#like setting the "andReleased" value in a buffer key check.
class SubActionSettings(Panel):
    pass

#The timing panel is used to switch between frames as well as play out the animation.
class TimingPanel(Panel):
    pass

#Settings panel changes settings of the application. like displaying the grid or hitboxes.
class SettingsPanel(Panel):
    pass