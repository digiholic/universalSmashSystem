import settingsManager
import spriteManager
import os
import imp
import pygame

class CSSScreen():
    def __init__(self):
        settings = settingsManager.getSetting().setting
        
        self.height = settings['windowHeight']
        self.width = settings['windowWidth']
        
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(settings['windowName'])
    
        clock = pygame.time.Clock()
        self.playerPanel = PlayerPanel(0)
        
        offset = 0
        for portrait in self.playerPanel.portraitList:
            portrait.draw(screen, [offset,0], 2.0)
            offset += 256
            pygame.display.flip()
            
        
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                
class PlayerPanel():
    def __init__(self,playerNum):
        self.playerNum = playerNum
        self.active = False
        self.fighters = []
        self.portraitList = []
        
        # Load all files.
        directory = os.path.join(os.path.dirname(settingsManager.__file__),"fighters")
        fightercount = 0
        for subdir in next(os.walk(directory))[1]:
            fighter = importFromURI(directory, os.path.join(directory,subdir,"fighter.py"),suffix=str(fightercount))
            fightercount += 1
            self.fighters.append(fighter)
            portrait = fighter.cssIcon()
            if portrait == None: portrait = spriteManager.ImageSprite(os.path.join(os.path.dirname(settingsManager.__file__),"sprites","icon_unknown.png"))
            self.portraitList.append(portrait)
            print self.portraitList
            
        
            
def importFromURI(filePath, uri, absl=False, suffix=""):
    if not absl:
        uri = os.path.normpath(os.path.join(os.path.dirname(filePath), uri))
    path, fname = os.path.split(uri)
    mname, ext = os.path.splitext(fname)
    
    no_ext = os.path.join(path, mname)
         
    if os.path.exists(no_ext + '.py'):
        try:
            return imp.load_source((mname + suffix), no_ext + '.py')
        except Exception as e:
            print mname, e
        
        
if __name__  == '__main__': CSSScreen()