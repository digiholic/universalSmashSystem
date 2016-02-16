import random
import pygame
import settingsManager
import spriteManager
import sys
import musicManager
import fighters.hitboxie.fighter
import fighters.sandbag.fighter
import stages.true_arena
import stages.arena
from cgi import log

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
        self.dataLogs = []
        
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
        currentFighters = self.players[:] #We have to slice this list so it passes by value instead of reference
        gameObjects = []
        gameObjects.extend(currentFighters)
        
        trackStocks = True
        trackTime = True
        if self.rules.stocks == 0:
            trackStocks = False
        if self.rules.time == 0:
            trackTime = False
            
        clockTime = self.rules.time * 60
        
        guiObjects = []
        if trackTime:
            pygame.time.set_timer(pygame.USEREVENT+2, 1000)
            countdownSprite = spriteManager.TextSprite('5','full Pack 2025',128,[0,0,0])
            countdownSprite.rect.center = screen.get_rect().center
            countAlpha = 0
            countdownSprite.alpha(countAlpha)
            guiObjects.append(countdownSprite)
            
            clockSprite = spriteManager.TextSprite('8:00','rexlia rg',32,[0,0,0])
            clockSprite.rect.topright = screen.get_rect().topright
            clockSprite.changeText(str(clockTime / 60)+':'+str(clockTime % 60).zfill(2))
            guiObjects.append(clockSprite)
        
        for fighter in currentFighters:
            fighter.rect.midbottom = current_stage.spawnLocations[fighter.playerNum]
            fighter.gameState = current_stage
            current_stage.follows.append(fighter.rect)
            log = DataLog()
            self.dataLogs.append(log)
            fighter.dataLog = log
            if trackStocks: fighter.stocks = self.rules.stocks
        
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
        
        dataLog = DataLog();
        dataLog.addSection('test', 1)
        dataLog.setData('test', 3, (lambda x,y: x + y))
        while exitStatus == 0:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                    return -1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print("saving screenshot")
                        pygame.image.save(screen,settingsManager.createPath('screenshot.jpg'))
                    
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
                    for fight in currentFighters:
                        fight.joyButtonPressed(event.joy, event.button)
                if event.type == pygame.JOYBUTTONUP:
                    for fight in currentFighters:
                        fight.joyButtonReleased(event.joy, event.button)
                if event.type == pygame.USEREVENT+2:
                    pygame.time.set_timer(pygame.USEREVENT+2, 1000)
                    clockSprite.changeText(str(clockTime / 60)+':'+str(clockTime % 60).zfill(2))
                    clockTime -= 1
                    print(clockTime)
                    if clockTime <= 5 and clockTime > 0:
                        countdownSprite.changeText(str(clockTime))
                        countAlpha = 255
                    if clockTime == 0:
                        exitStatus = 2
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
            for fight in currentFighters:
                if fight.rect.right < current_stage.blast_line.left or fight.rect.left > current_stage.blast_line.right or fight.rect.top > current_stage.blast_line.bottom or fight.rect.bottom < current_stage.blast_line.top:
                    if not trackStocks:
                        # Get score
                        fight.die()
                    else:
                        fight.stocks -= 1
                        print fight.stocks
                        if fight.stocks == 0:
                            fight.die(False)
                            currentFighters.remove(fight)
                            current_stage.follows.remove(fight.rect)
                            #If someon's eliminated and there's 1 or fewer people left
                            if len(currentFighters) < 2:
                                exitStatus = 2 #Game set
                        else: fight.die()
            for obj in guiObjects:
                obj.draw(screen, obj.rect.topleft,1)
            if trackTime and clockTime <= 5:
                countAlpha = max(0,countAlpha - 5)
                countdownSprite.alpha(countAlpha)
                
            # End object updates
            
            current_stage.drawFG(screen)    
            clock.tick(60)  
            pygame.display.flip()
        # End while loop
        
        if exitStatus == 1:
            print("NO CONTEST")
        elif exitStatus == 2:
            musicManager.getMusicManager().stopMusic()
            frameHold = 0
            gameSprite = spriteManager.TextSprite('GAME!','full Pack 2025',128,[0,0,0])
            gameSprite.rect.center = screen.get_rect().center
            while frameHold < 150:
                gameSprite.draw(screen, gameSprite.rect.topleft, 1)
                clock.tick(60)
                pygame.display.flip()
                frameHold += 1
            print("GAME SET")
        elif exitStatus == -1:
            print("ERROR!")
        
        self.endBattle(exitStatus,screen)    
        return exitStatus # This'll pop us back to the character select screen.
        
         
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
    def endBattle(self,exitStatus,screen):
        if exitStatus == -1:
            #Don't show a results screen on error
            return
        elif exitStatus == 2:
            resultSprites = []
            width = settingsManager.getSetting('windowWidth')
            height = settingsManager.getSetting('windowHeight')
            for i in range(0,len(self.players)):
                print(self.players)
                print("player"+str(i))
                fighter = self.players[i]
                resultSprite = spriteManager.RectSprite(pygame.Rect((width / 4) * i,0,(width / 4),height), pygame.Color(settingsManager.getSetting('playerColor'+str(i))))
                nameSprite = spriteManager.TextSprite(fighter.name,size=24)
                nameSprite.rect.midtop = (resultSprite.rect.width / 2,0)
                resultSprite.image.blit(nameSprite.image,nameSprite.rect.topleft)
                
                score = fighter.dataLog.getData('KOs') - fighter.dataLog.getData('Falls')
                text = spriteManager.TextSprite('Score: ' + str(score))
                resultSprite.image.blit(text.image,(0,32))
                    
                dist = 48
                
                print(fighter.dataLog.data)
                for item,val in fighter.dataLog.data.iteritems():
                    text = spriteManager.TextSprite(str(item) + ': ' + str(val))
                    resultSprite.image.blit(text.image,(0,dist))
                    dist += 16
                resultSprites.append(resultSprite)
                confirmedList = [False] * len(resultSprites) #This pythonic hacking will make a list of falses equal to the result panels
           
            while 1:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                        return -1
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            print("saving screenshot")
                            pygame.image.save(screen,settingsManager.createPath('screenshot.jpg'))
                        if event.key == pygame.K_ESCAPE:
                            return
                        for i in range(0,len(self.players)):
                            if event.key in settingsManager.getControls(i).getAction('attack'):
                                resultSprites[i].image.set_alpha(0)
                                confirmedList[i] = True
                            if event.key in settingsManager.getControls(i).getAction('shield'):
                                resultSprites[i].image.set_alpha(255)
                                confirmedList[i] = False
                screen.fill((0,0,0))
                for sprite in resultSprites:
                    sprite.draw(screen, sprite.rect.topleft, 1.0)
                
                if all(confirmedList):
                    return
                pygame.display.flip()
            return
        elif exitStatus == 1:
            #Game ended in no contest
            return
        
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
    
"""
The Data Log object keeps track of information that happens in-game, such as score, deaths, total damage dealt/received, etc.

A log will be made for each character, and it will be given to them on load. They will keep track of updating their logs,
and characters are free to give it new information as they see fit. For example, you could make a character like Game & Watch log
how many of each number he scored.
"""
class DataLog():
    def __init__(self):
        self.data = {
                     'KOs'          : 0,
                     'Falls'        : 0,
                     'Damage Dealt' : 0,
                     'Damage Taken' : 0
                     }
        
    def addSection(self,section,initial):
        self.data[section] = initial
            
    def getData(self,section):
        return self.data[section]
    
    # If this last function looks scary to you, don't worry. Leave it out, and it changes the value at section to value.
    # You can pass a function to it to apply to section and value and it'll do a cool thing!
    def setData(self,section,value,function = (lambda x,y: y)):
        self.data[section] = function(self.getData(section),value)
        print(str(section) + ": " + str(self.data[section]))