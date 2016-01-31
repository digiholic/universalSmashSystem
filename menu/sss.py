import sys
import pygame
import settingsManager
import battle
import stages.true_arena
import spriteManager
import os

class StageScreen():
    def __init__(self,characters):
        settings = settingsManager.getSetting().setting
        self.fighters = characters
        self.stages = []
        self.getStages()
        self.grid = StageGrid(self.stages)
        
        self.height = settings['windowHeight']
        self.width = settings['windowWidth']
        
        pygame.init()
        screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(settings['windowName'])
        
        background = pygame.Surface(screen.get_size())
        background = background.convert()
    
        clock = pygame.time.Clock()
        self.playerControls = []
        self.playerPanels = []
        
        for i in range(0,4):
            self.playerControls.append(settingsManager.getControls(i))
        
        status = 0
        
        while status == 0:
            #Start event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        status = 1
                    
                    for i,bindings in enumerate(self.playerControls):
                        if bindings.get(event.key) == 'left':
                            self.grid.updateSelection(-1, 0)
                                
                        elif bindings.get(event.key) == 'right':
                            self.grid.updateSelection(1, 0)
                        
                        elif bindings.get(event.key) == 'up':
                            self.grid.updateSelection(0, -1)
                            
                        elif bindings.get(event.key) == 'down':
                            self.grid.updateSelection(0, 1)
                            
                        elif bindings.get(event.key) == 'attack':
                            #choose
                            stage = self.grid.getSelectedStage().getStage()
                            currentBattle = battle.Battle(battle.Rules(),self.fighters,stage)
                            currentBattle.startBattle(screen)
                            status = 1
                            #do something with battle result
                                
                        #TODO: Fix this when special button is added
                        elif bindings.get(event.key) == 'shield':
                            status = 1
                            
                elif event.type == pygame.KEYUP:
                    pass
                    #I shouldn't actually need this, but just in case.
                    
            #End event loop
            screen.fill((0,0,0))
            self.grid.drawScreen(screen)
            
            pygame.display.flip()
            clock.tick(60)
        
    def getStages(self):
        # Load all files.
        directory = settingsManager.createPath("stages")
        stagecount = 0
        for subdir in next(os.walk(directory))[1]:
            stage = settingsManager.importFromURI(directory, os.path.join(directory,subdir,"stage.py"),suffix=str(stagecount))
            print(stage)
            if (stage == None):
                raise ValueError("No stages found at " + os.path.join(directory,subdir,"stage.py"))
            stagecount += 1
            self.stages.append(stage)
    
class StageGrid():
    def __init__(self,stages):
        self.stageGrid = []
        self.selectedStage = (0,0)
        x = 0
        y = 0
        maxX = settingsManager.getSetting('windowWidth') / 32 #the number of icons that'll fit on the screen horizontally
        print(maxX)
        stageRow = []
        for stage in stages:
            if x < maxX:
                stageRow.append(stage) #Put it in the row
                x += 1
            else:
                self.stageGrid.append(stageRow) #Add the row to the grid
                stageRow = [] #Clear the row
                y += 1
                stageRow.append(stage)
                x = 1
        #End of stages
        self.stageGrid.append(stageRow) #Put the last row onto the grid
        print(self.stageGrid)
        
    def updateSelection(self,delta_x,delta_y):
        x,y = self.selectedStage
        maxY = len(self.stageGrid) - 1
        y = y + delta_y
        x = x + delta_x
        
        if (y < 0):
            y = maxY
        if (y > maxY):
            y = 0
        maxX = len(self.stageGrid[y]) - 1
        if (x < 0):
            x = maxX
        if (x > maxX):
            x = 0
        self.selectedStage = (x,y)
        print(x,y)
    
    def getSelectedStage(self):
        x,y = self.selectedStage
        return self.stageGrid[y][x]
    
    def getStageAt(self,x,y):
        return self.stageGrid[y][x]
    
    def getStagePortrait(self,stage):
        portrait = stage.getStageIcon()
        if portrait == None:
            portrait = spriteManager.ImageSprite(settingsManager.createPath(os.path.join("sprites","icon_unknown.png")))
        return portrait
    
    def drawScreen(self,screen):
        top_pos = 0
        left_pos = 0
        for row in self.stageGrid:
            for stage in row:
                sprite = self.getStagePortrait(stage)
                if stage == self.getSelectedStage():
                    sprite.alpha(255)
                else:
                    sprite.alpha(128)
                sprite.draw(screen,(left_pos,top_pos),1)
                left_pos += 32
                
            left_pos = 0
            top_pos += 32