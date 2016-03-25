import sys
import pygame
import settingsManager
import battle
import stages.true_arena
import stages.arena
import spriteManager
import os
import musicManager
import random

class StageScreen():
    def __init__(self,rules,characters,cpuPlayers):
        settings = settingsManager.getSetting().setting
        self.rules = rules
        self.fighters = characters
        self.cpuPlayers = cpuPlayers
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

        x = 0
        y = 0
        
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
                            if not self.grid.isStageStruckAt(self.grid.getXY()[0],self.grid.getXY()[1]):
                                #choose
                                if self.grid.getSelectedStage() == 'random':
                                    stage = self.grid.getRandomStage()
                                else:
                                    stage = self.grid.getSelectedStage()
                                
                                musicManager.getMusicManager().stopMusic(500)
                                #This will wait until the music fades out for cool effect
                                while musicManager.getMusicManager().isPlaying():
                                    pass
                                musicList = stage.getMusicList()
                                musicManager.getMusicManager().createMusicSet('stage', musicList)
                                musicManager.getMusicManager().rollMusic('stage')
                                currentBattle = battle.Battle(self.rules,self.fighters,stage.getStage(),self.cpuPlayers)
                                currentBattle.startBattle(screen)
                                status = 1
                                #do something with battle result
                                
                        #TODO: Fix this when special button is added
                        elif bindings.get(event.key) == 'jump':
                            x,y = self.grid.getXY()
                            self.grid.changeStageStruckAt(x,y)
                            
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
            if(subdir == '__pycache__'):
                continue
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
        self.stagesStriked = []
        x = 0
        y = 0
        maxX = settingsManager.getSetting('windowWidth') / 32 #the number of icons that'll fit on the screen horizontally
        print(maxX)
        stageRow = []
        strikingRow = []
        stages.append('random')
        for stage in stages:
            if x < maxX:
                stageRow.append(stage) #Put it in the row
                strikingRow.append(False)
                x += 1
            else:
                self.stageGrid.append(stageRow) #Add the row to the grid
                self.stagesStriked.append(strikingRow)
                stageRow = [] #Clear the row
                strikingRow = []
                y += 1
                stageRow.append(stage)
                strikingRow.append(False)
                x = 1
        #End of stages
        self.stageGrid.append(stageRow) #Put the last row onto the grid
        self.stagesStriked.append(strikingRow)
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
        
    def getXY(self):
        return self.selectedStage

    def getSelectedStage(self):
        x,y = self.selectedStage
        return self.stageGrid[y][x]
    
    def getStageAt(self,x,y):
        return self.stageGrid[y][x]

    def isStageStruckAt(self,x,y):
        return self.stagesStriked[y][x]

    def changeStageStruckAt(self,x,y):
        if self.getStageAt(x,y) != 'random':
            self.stagesStriked[y][x] = not self.stagesStriked[y][x]
    
    def getStagePortrait(self,stage):
        portrait = stage.getStageIcon()
        if portrait == None:
            portrait = spriteManager.ImageSprite(settingsManager.createPath(os.path.join("sprites","icon_blank.png")))
        return portrait

    def getRandomStage(self):
        randomStages = []
        stageCount = 0
        for row in range(0,len(self.stageGrid)):
            for stage in range(0,row+3):
                if (not self.isStageStruckAt(stage,row)) and self.getStageAt(stage,row) != 'random':
                    randomStages.append(self.getStageAt(stage,row))
                    stageCount += 1
        print(randomStages)
        if stageCount == 0:
            print('Why did you strike all of the stages')
            for row in range(0,len(self.stageGrid)):
                for stage in range(0,row+3):
                    if self.getStageAt(stage,row) != 'random':
                        randomStages.append(self.getStageAt(stage,row))
                        stageCount += 1
                    
        return randomStages[random.randint(0, stageCount-1)]
    
    def drawScreen(self,screen):
        top_pos = 0
        left_pos = 0
        
        for row in range(0,len(self.stageGrid)):
            for stage in range(0,len(self.stageGrid[row])):
                if self.getStageAt(stage,row) == 'random':
                    sprite = spriteManager.ImageSprite(settingsManager.createPath(os.path.join("sprites","icon_unknown.png")))
                else:
                    sprite = self.getStagePortrait(self.getStageAt(stage,row))
                if self.isStageStruckAt(stage,row):
                    sprite.alpha(48)
                    if self.getStageAt(stage,row) == self.getSelectedStage():
                        sprite.alpha(64)
                elif self.getStageAt(stage,row) == self.getSelectedStage():
                    sprite.alpha(255)
                else:
                    sprite.alpha(128)
                sprite.draw(screen,(left_pos,top_pos),1)
                left_pos += 32
                
            left_pos = 0
            top_pos += 32
