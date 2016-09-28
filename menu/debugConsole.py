import sys
import cmd
import io
import settingsManager
import spriteManager
import pygame
import pygcurse

class debugConsole(cmd.Cmd):
    def __init__(self, _surface, _gameEnv, _font="joystix monospace", _size=12, _height=8):
        self.game_env = _gameEnv
        text_dims = pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size).size(" ") #Used to determine how much space is available
        self.text_width = int(_surface.get_width()/text_dims[0])
        self.render_corner = [0, _surface.get_height()-text_dims[1]*_height]
        self.pyg_surface = pygcurse.PygcurseSurface(self.text_width, _height, pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size))
        self.pyg_input = pygcurse.PygcurseInput(self.pyg_surface, prompt = "> ")
        self.pyg_input.update()
        cmd.Cmd.__init__(self, stdout=self.pyg_surface) #Yay for duck typing

    def acceptInput(self, _keyEvent):
        self.pyg_input.sendkeyevent(_keyEvent)
        if self.pyg_input.done:
            self.pyg_surface.pygprint(self.onecmd((''.join(self.pyg_input.buffer))))
            self.pyg_surface.pygprint("\n")
            self.pyg_input.update()
            self.pyg_input = pygcurse.PygcurseInput(self.pyg_surface, prompt = "> ")
        self.pyg_input.update()

    def display(self, _surface):
        self.pyg_surface.update()
        self.pyg_surface.blitto(_surface, self.render_corner)

    def emptyline(self):
        pass #Don't want to cause problems
        

    


