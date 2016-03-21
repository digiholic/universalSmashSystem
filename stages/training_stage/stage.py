import engine.stage as stage
import pygame
import spriteManager
import os
import settingsManager
import engine.article as article

def getStage():
    return TrainingStage()

def getStageName():
    return "Training Stage"

def getStageIcon():
    return spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","icon_training_stage.png"))

def getStagePreview():
    return None

def getMusicList():
    return [(os.path.join(os.path.dirname(__file__).replace('main.exe',''),'music','Character Lobby.ogg'),1,"Character Lobby")]

class TrainingStage(stage.Stage):
    def __init__(self):
        stage.Stage.__init__(self)
        
        self.size = pygame.Rect(0,0,960,720)
        self.camera_maximum = pygame.Rect(0,0,960,720)
        self.blast_line = pygame.Rect(-1,-1,961,721)
        
        self.platform_list = [stage.Platform([self.size.left+32,self.size.bottom - 32],[self.size.right-32,self.size.bottom-32]),
                              stage.Platform([self.size.left+32,self.size.top+32],[self.size.left+32,self.size.bottom+32]),
                              stage.Platform([self.size.left+32,self.size.top-32],[self.size.right-32,self.size.top-32]),
                              stage.Platform([self.size.right-32,self.size.top-32],[self.size.right-32,self.size.bottom+32])
                              ]
        
        self.spawnLocations = [[192,self.size.bottom-1],
                               [192 * 4,self.size.bottom-1],
                               [192 * 2,self.size.bottom-1],
                               [192 * 3,self.size.bottom-1],
                               ]
        
        backdrop = spriteManager.ImageSprite(os.path.join(os.path.dirname(__file__).replace('main.exe',''),"sprites","training_stage_bg.png"))
        backdrop.rect.topleft = [0,0]
        self.addToBackground(backdrop)
        
        self.backgroundColor = [100,100,100]
        self.getLedges()