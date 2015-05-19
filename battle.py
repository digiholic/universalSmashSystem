import random
import pygame
import settingsManager

import fighters.hitboxie.fighter
import fighters.sandbag.fighter
import stages.true_arena
import stages.arena

"""
The battle object actually creates the fight and plays it out on screen.
It calls the update function of all of the fighters and the stage, and draws them.
It takes a Rules object (see below), a list of players, and a stage.


"""
class Battle():
    def __init__(self,rules,players,stage):
        self.settings = settingsManager.getSetting().setting
        
        if rules == None: rules = Rules()
        
        self.rules = rules
        self.players = players
        self.stage = stage
        self.inputBuffer = None
        #TODO bring over InputBuffer from fighter.
        random.seed
        self.randomstate = random.getstate
        
    def startBattle(self,screen):
        
        # Fill background
        background = pygame.Surface(screen.get_size())
        background = background.convert()
        background.fill((128, 128, 128))
        current_stage = self.stage
        active_hitboxes = pygame.sprite.Group()
    
        #gameObjects
        currentFighters = self.players
        gameObjects = []
        gameObjects.extend(currentFighters)
        
        for fighter in currentFighters:
            fighter.rect.midbottom = current_stage.spawnLocations[fighter.playerNum]
            fighter.gameState = current_stage
            current_stage.follows.append(fighter.rect)
        
        current_stage.initializeCamera()
            
        clock = pygame.time.Clock()
        
        """
        ExitStatus breaks us out of the loop. The battle loop can end in many ways, which is reflected here.
        In general, ExitStatus positive means that the game was supposed to end, while a negative value indicates an error.
        
        ExitStatus == 1: Battle ended early by user. No Contest.
        ExitStatus == 2: Battle ended by time or stock, decide winner, show victory screen
        ExitStatus == -1: Battle ended in error.
        """
        exitStatus = 0
        while exitStatus == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return -1
                if event.type == pygame.KEYDOWN:
                    for fight in currentFighters:
                        fight.keyPressed(event.key)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exitStatus = 1
                    for fight in currentFighters:
                        fight.keyReleased(event.key)
                if event.type == pygame.JOYAXISMOTION:
                    for fight in currentFighters:
                        fight.joyAxisMotion(event.joy, event.axis)
                if event.type == pygame.JOYBUTTONDOWN:
                    print "joybuttondown"
                if event.type == pygame.JOYBUTTONUP:
                    print "joybuttonup"
            # End pygame event loop
                                   
            screen.fill([100, 100, 100])
            
            current_stage.update()
            current_stage.cameraUpdate()
            current_stage.drawBG(screen)
            for obj in gameObjects:
                obj.update()
                if hasattr(obj,'active_hitboxes'):
                    active_hitboxes.add(obj.active_hitboxes)
                
                offset = current_stage.stageToScreen(obj.rect)
                scale =  current_stage.getScale()
                obj.draw(screen,offset,scale)
                if hasattr(obj, 'hurtbox'):
                    if (self.settings['showHurtboxes']): 
                        offset = current_stage.stageToScreen(obj.hurtbox.rect)
                        obj.hurtbox.draw(screen,offset,scale)
                    
                    hitbox_collisions = pygame.sprite.spritecollide(obj.hurtbox, active_hitboxes, False)
                    for hbox in hitbox_collisions:
                        if hbox.owner != obj:
                            hbox.onCollision(obj)
                if (self.settings['showHitboxes']):
                    for hbox in active_hitboxes:
                        hbox.draw(screen,current_stage.stageToScreen(hbox.rect),scale)
            
            # End object updates
            
            current_stage.drawFG(screen)      
            clock.tick(60)    
            pygame.display.flip()
        # End while loop
        
        self.doExitStatus(exitStatus)
        return # This'll pop us back to the character select screen.
    
    def doExitStatus(self,exitStatus):
        if exitStatus == 1:
            print "NO CONTEST"
        elif exitStatus == 2:
            print "GAME SET"
        elif exitStatus == -1:
            print "ERROR!"
         
    """
    In a normal game, the frame input won't matter.
    It will matter in replays and (eventually) online.
    """
    def getInputsforFrame(self,frame):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pass
            if event.type == pygame.KEYUP:
                pass
             
    def saveReplay(self,path):
        pass
    
    """
    Ends the battle and goes to a relevant menu or error page depending on how the
    battle ended.
    """    
    def endBattle(self,exitStatus):
        if exitStatus == "Error":
            pass
        
        
"""
The rules object determines the battle's rules.
By default it's 3 stock, 8 minute, free for all.
If stocks is set to 0, infinite stocks are used.
If time is set to 0, infinite time is used.
Self.teams is a list of tuples. Each tuple is in the form of (teamNumber, [playerNumbers]).
For example, if players 1 and 4 were on a team against players 2 and 3, the variable would look like this:

self.teams = [(0, [0,3]), (1, [1,2])]

Remember that PlayerNum is zero-indexed, so player 1 is PlayerNum 0, and so on.
"""
class Rules():
    def __init__(self,stocks=3,time=480,teams=[]):
        self.stocks = stocks #default to 3 stock
        self.time = time #default to 8 minutes
        self.teams = teams #teams off
    
class Replay(Battle):
    def __init__(self):
        pass
    

if __name__  == '__main__':
    settings = settingsManager.getSetting().setting
    
    height = settings['windowHeight']
    width = settings['windowWidth']
        
    pygame.init()
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(settings['windowName'])
    
    """
    Battle(None, 
           [fighters.hitboxie.fighter.getFighter(0, 0),fighters.sandbag.fighter.getFighter(1, 0),fighters.sandbag.fighter.getFighter(2, 0),fighters.sandbag.fighter.getFighter(3, 0)],
           stages.arena.getStage()).startBattle(screen)
    """    
    Battle(None, 
           [fighters.hitboxie.fighter.getFighter(0, 0)],
           stages.arena.getStage()).startBattle(screen)
    
    