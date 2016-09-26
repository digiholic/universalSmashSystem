import sys
import pdb
import io
import settingsManager
import spriteManager
import pygame
import pygcurse

class debugConsole(pdb.Pdb):
    def __init__(self, _surface, _font="joystix monospace", _size=12, _height=8):
        self.output_hold = io.StringIO()
        pdb.Pdb.__init__(self, stdout=self.output_hold)
        self.prompt = "> "
        text_dims = pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size).size(" ") #Used to determine how much space is available
        self.text_width = int(_surface.get_width()/text_dims[0])
        self.render_corner = [0, _surface.get_height()-text_dims[1]*_height]
        self.pyg_surface = pygcurse.PygcurseSurface(self.text_width, _height, pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size))
        self.pyg_input = pygcurse.PygcurseInput(self.pyg_surface, prompt = "> ")

    def acceptInput(self, _keyEvent):
        self.pyg_input.sendkeyevent(_keyEvent)
        if self.pyg_input.done:
            self.run(''.join(self.pyg_input.buffer))
            self.pyg_surface.pygprint(self.output_hold.getvalue())
            self.output_hold = io.StringIO() #Probably inefficient, but it works
            self.pyg_surface.pygprint("\n")
            self.pyg_input.update()
            self.pyg_input = pygcurse.PygcurseInput(self.pyg_surface, prompt = "> ")
        self.pyg_input.update()

    def display(self, _surface):
        self.pyg_surface.update()
        self.pyg_surface.blitto(_surface, self.render_corner)


