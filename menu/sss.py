import sys
import pygame
import settingsManager
import battle
import spriteManager
import os
import musicManager
import random

class StageScreen():
    def __init__(self,_rules,_characters):
        settings = settingsManager.getSetting().setting
        self.rules = _rules
        self.fighters = _characters
        self.stages = []
        self.getStages()
        self.grid = StageGrid(self.stages)
        
        self.height = settings['windowHeight']
        self.width = settings['windowWidth']
        
        pygame.init()
        screen = pygame.display.get_surface()
        
        background = pygame.Surface(screen.get_size())
        background = background.convert()
    
        clock = pygame.time.Clock()
        self.player_controls = []
        self.player_panels = []

        x = 0
        y = 0
        
        for i in range(0,4):
            self.player_controls.append(settingsManager.getControls(i))
            
        status = 0
        
        while status == 0:
            music = musicManager.getMusicManager()
            music.doMusicEvent()
            #Start event loop
            for event in pygame.event.get():
                
                for bindings in self.player_controls:
                    k = bindings.getInputs(event,False,False)
                    if k == 'left':
                        self.grid.updateSelection(-1, 0)    
                    elif k == 'right':
                        self.grid.updateSelection(1, 0)
                    elif k == 'up':
                        self.grid.updateSelection(0, -1)  
                    elif k == 'down':
                        self.grid.updateSelection(0, 1) 
                    elif k == 'attack':
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
                            music_list = stage.getMusicList()
                            musicManager.getMusicManager().createMusicSet('stage', music_list)
                            musicManager.getMusicManager().rollMusic('stage')
                            bindings.flushInputs()
                            current_battle = battle.Battle(self.rules,self.fighters,stage.getStage())
                            current_battle.startBattle(screen)
                            status = 1
                            #do something with battle result
                    
                    elif k == 'jump':
                        x,y = self.grid.getXY()
                        self.grid.changeStageStruckAt(x,y)
                        
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        status = 1
                    
            #End event loop
            screen.fill((0,0,0))
            self.grid.drawScreen(screen)
            
            pygame.display.flip()
            clock.tick(60)
        
    def getStages(self):
        # Load all files.
        directory = settingsManager.createPath("stages")
        stage_count = 0
        for subdir in next(os.walk(directory))[1]:
            if(subdir == '__pycache__'):
                continue
            stage = settingsManager.importFromURI(directory, os.path.join(directory,subdir,"stage.py"),suffix=str(stage_count))
            if (stage == None):
                raise ValueError("No stages found at " + os.path.join(directory,subdir,"stage.py"))
            stage_count += 1
            self.stages.append(stage)
    
class StageGrid():
    def __init__(self,_stages):
        self.stage_grid = []
        self.selected_stage = (0,0)
        self.stages_striked = []
        x = 0
        y = 0
        max_x = settingsManager.getSetting('windowWidth') / 32 #the number of icons that'll fit on the screen horizontally
        print(max_x)
        stage_row = []
        striking_row = []
        _stages.append('random')
        for stage in _stages:
            if x < max_x:
                stage_row.append(stage) #Put it in the row
                striking_row.append(False)
                x += 1
            else:
                self.stage_grid.append(stage_row) #Add the row to the grid
                self.stages_striked.append(striking_row)
                stage_row = [] #Clear the row
                striking_row = []
                y += 1
                stage_row.append(stage)
                striking_row.append(False)
                x = 1
        #End of stages
        self.stage_grid.append(stage_row) #Put the last row onto the grid
        self.stages_striked.append(striking_row)
        
    def updateSelection(self,_deltaX,_deltaY):
        x,y = self.selected_stage
        max_y = len(self.stage_grid) - 1
        y = y + _deltaY
        x = x + _deltaX
        
        if (y < 0):
            y = max_y
        if (y > max_y):
            y = 0
        max_x = len(self.stage_grid[y]) - 1
        if (x < 0):
            x = max_x
        if (x > max_x):
            x = 0
        self.selected_stage = (x,y)
        print(x,y)
        
    def getXY(self):
        return self.selected_stage

    def getSelectedStage(self):
        x,y = self.selected_stage
        return self.stage_grid[y][x]
    
    def getStageAt(self,_x,_y):
        return self.stage_grid[_y][_x]

    def isStageStruckAt(self,_x,_y):
        return self.stages_striked[_y][_x]

    def changeStageStruckAt(self,_x,_y):
        if self.getStageAt(_x,_y) != 'random':
            self.stages_striked[_y][_x] = not self.stages_striked[_y][_x]
    
    def getStagePortrait(self,_stage):
        portrait = _stage.getStageIcon()
        if portrait == None:
            portrait = spriteManager.ImageSprite(settingsManager.createPath(os.path.join("sprites","icon_blank.png")))
        return portrait

    def getRandomStage(self):
        random_stages = []
        stage_count = 0
        for row in range(0,len(self.stage_grid)):
            for stage in range(0,row+3):
                if (not self.isStageStruckAt(stage,row)) and self.getStageAt(stage,row) != 'random':
                    random_stages.append(self.getStageAt(stage,row))
                    stage_count += 1
        print(random_stages)
        if stage_count == 0:
            print('Can\'t select a random stage out of no available stages')
            for row in range(0,len(self.stage_grid)):
                for stage in range(0,row+3):
                    if self.getStageAt(stage,row) != 'random':
                        random_stages.append(self.getStageAt(stage,row))
                        stage_count += 1
                    
        return random_stages[random.randint(0, stage_count-1)]
    
    def drawScreen(self,_screen):
        top_pos = 0
        left_pos = 0
        
        for row in range(0,len(self.stage_grid)):
            for stage in range(0,len(self.stage_grid[row])):
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
                sprite.draw(_screen,(left_pos,top_pos),1)
                left_pos += 32
                
            left_pos = 0
            top_pos += 32
