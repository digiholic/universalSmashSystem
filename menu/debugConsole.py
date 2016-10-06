import sys
import cmd
import pdb
import io
import settingsManager
import spriteManager
import pygame
import pygcurse

class debugConsole(pdb.Pdb):
    def __init__(self, _surface, _gameEnv, _font="unifont-9.0.02", _size=16, _height=24):
        self.game_env = _gameEnv
        text_dims = pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size).size(" ") #Used to determine how much space is available
        self.text_width = int(_surface.get_width()/text_dims[0])
        self.render_corner = [0, _surface.get_height()-text_dims[1]*_height]
        self.pyg_surface = pygcurse.PygcurseSurface(self.text_width, _height, pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size))
        self.pyg_surface.setscreencolors(fgcolor=None, bgcolor=None, clear=True)
        pdb.Pdb.__init__(self, stdin=self, stdout=self.pyg_surface) #Yay for duck typing
        self.use_rawinput = False
        self.prompt = "> "

    def display(self):
        self.game_env.draw()
        self.pyg_surface.update()
        self.pyg_surface.blitto(self.game_env.screen, self.render_corner)
        pygame.display.update()

    def postcmd(self, _stop, _line):
        self.display()
        return pdb.Pdb.postcmd(self, _stop, _line)

    def interaction(self, frame, traceback):
        self.setup(frame, traceback)
        self.cmdloop("Welcome to the debug console. For help, type '?'. ")
        self.forget()

    #Shamelessly copied and modified from pygcurses. See pygcurse.py for license details. 
    def readline(self):
        clock = pygame.time.Clock()
        inputObj = pygcurse.PygcurseInput(self.pyg_surface)
        self.pyg_surface.inputcursor = inputObj.startx, inputObj.starty

        while True: # the event loop
            self.pyg_surface._inputcursormode = inputObj.insertMode and 'insert' or 'underline'

            for event in pygame.event.get((pygame.KEYDOWN, pygame.KEYUP, pygame.QUIT)): # TODO - handle holding down the keys
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                    inputObj.sendkeyevent(event)
                    if inputObj.done:
                        return ''.join(inputObj.buffer)

            inputObj.update()
            self.display()

            clock.tick(60)

    def emptyline(self):
        pass #Don't want to cause problems

    def do_setdamage(self, _args):
        """Sets the damage of a fighter to a value.\nSyntax: setdamage <player_num> <value>\nNote that player_num is zero indexed."""
        split_args = _args.split(' ')
        if len(self.game_env.current_fighters) > int(split_args[0]):
            dmg = max(0,min(999,int(split_args[1]))) #clamp it between 0 and 999
            self.game_env.current_fighters[int(split_args[0])].damage = dmg 
            self.pyg_surface.write('Setting player '+split_args[0]+' damage to '+str(dmg)+'\n')
        else: self.pyg_surface.write('Could not find player '+split_args[0]+'\n')
        return False

    def do_advance(self, _args):
        """Advances the game the given number of frames.\nSyntax: advance <num_frames>"""
        #TODO: Allow stepping without an argument
        split_args = _args.split(' ')
        num_frames = int(split_args[0])
        frames_advanced = 0
        if num_frames > 0:
            for frame in range(num_frames):
                self.game_env.debug_mode = False
                self.game_env.gameEventLoop()
                frames_advanced += 1
                if self.game_env.exit_status != 0:
                    break
            self.game_env.debug_mode = True
            self.pyg_surface.write('Advanced '+split_args[0]+' frames\n')
            return self.game_env.exit_status != 0
        elif num_frames == 0:
            self.pyg_surface.write('Advanced 0 frames\n')
            return False
        elif num_frames < 0:
            self.pyg_surface.write('Can\'t advance negative frames\n')
            return False
