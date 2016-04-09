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
import colorsys
import engine.hitbox as hitbox
import engine.controller as controller
from cgi import log

"""
The battle object actually creates the fight and plays it out on screen.
It calls the update function of all of the fighters and the stage, and draws them.
It takes a Rules object (see below), a list of players, and a stage.


"""
class Battle():
    def __init__(self,rules,players,stage):
        self.settings = settingsManager.getSetting().setting
        
        if rules is None: rules = Rules()
        
        self.rules = rules
        self.players = players
        self.nullLock = hitbox.HitboxLock()
        self.controllers = []
        for player in players:
            player.hitboxLock.add(self.nullLock)
            self.controllers.append(player.keyBindings)
            
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
        
        screen.fill(self.stage.backgroundColor)
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
        
        guiOffset = screen.get_rect().width / (len(self.players) + 1)
        for fighter in currentFighters:
            fighter.rect.midbottom = current_stage.spawnLocations[fighter.playerNum]
            fighter.gameState = current_stage
            fighter.players = self.players
            current_stage.follows.append(fighter.rect)
            log = DataLog()
            self.dataLogs.append(log)
            fighter.dataLog = log
            if trackStocks: fighter.stocks = self.rules.stocks
            
            percentSprite = HealthTracker(fighter)
            
            percentSprite.rect.bottom = screen.get_rect().bottom
            percentSprite.rect.centerx = guiOffset

            guiOffset += screen.get_rect().width / (len(self.players) + 1)
            
            guiObjects.append(percentSprite)
            
        current_stage.initializeCamera()
            
        clock = pygame.time.Clock()
        clock_speed = 60
        debug_mode = False
        debug_pass = False
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
        self.dirty_rects = [pygame.Rect(0,0,self.settings['windowWidth'],self.settings['windowHeight'])]
        while exitStatus == 0:
            for cont in self.controllers:
                cont.passInputs()
                
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                    return -1
                
                for cont in self.controllers:
                    cont.getInputs(event)
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print("saving screenshot")
                        pygame.image.save(screen,settingsManager.createPath('screenshot.jpg'))
                    elif event.key == pygame.K_RSHIFT:
                        debug_mode = not debug_mode
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_ESCAPE:
                        exitStatus = 1
                            
                if event.type == pygame.USEREVENT+2:
                    pygame.time.set_timer(pygame.USEREVENT+2, 1000)
                    clockSprite.changeText(str(clockTime / 60)+':'+str(clockTime % 60).zfill(2))
                    clockTime -= 1
                    if clockTime <= 5 and clockTime > 0:
                        countdownSprite.changeText(str(clockTime))
                        countAlpha = 255
                    if clockTime == 0:
                        exitStatus = 2
            # End pygame event loop
                                   
            screen.fill(self.stage.backgroundColor)
            
            current_stage.update()
            current_stage.cameraUpdate()
            drawRects = current_stage.drawBG(screen)
            self.dirty_rects.extend(drawRects)
            
            for hbox in active_hitboxes:
                hitbox_clank = pygame.sprite.spritecollide(hbox,active_hitboxes, False)
                for other in hitbox_clank:
                    if other is not hbox:
                        if not hbox.compareTo(other):
                            if hasattr(hbox.owner,'current_action') and hbox.article == None:
                                hbox.owner.current_action.onClank(hbox.owner)
                            print("CLANK!")
                            hbox.hitbox_lock = self.nullLock
                        if not other.compareTo(hbox):
                            if hasattr(other.owner,'current_action') and hbox.article == None:
                                other.owner.current_action.onClank(other.owner)
                            print("CLANK!")
                            other.hitbox_lock = self.nullLock
            
            for obj in gameObjects:
                obj.update()
                if hasattr(obj,'active_hitboxes'):
                    active_hitboxes.add(obj.active_hitboxes)
                
                offset = current_stage.stageToScreen(obj.rect)
                scale =  current_stage.getScale()
                drawRect = obj.draw(screen,offset,scale)
                if drawRect: self.dirty_rects.append(drawRect)
                if hasattr(obj, 'hurtbox'):
                    if (self.settings['showHurtboxes']): 
                        offset = current_stage.stageToScreen(obj.hurtbox.rect)
                        drawRect = obj.hurtbox.draw(screen,offset,scale)
                        if drawRect: self.dirty_rects.append(drawRect)
                    
                    hitbox_collisions = pygame.sprite.spritecollide(obj.hurtbox, active_hitboxes, False)
                    for hbox in hitbox_collisions:
                        if hbox.owner != obj:
                            hbox.onCollision(obj)
                if hasattr(obj, 'articles'):
                    for art in obj.articles:
                        offset = current_stage.stageToScreen(art.rect)
                        scale =  current_stage.getScale()
                        drawRect = art.draw(screen,offset,scale)
                        if drawRect: self.dirty_rects.append(drawRect)
        
                if (self.settings['showHitboxes']):
                    for hbox in active_hitboxes:
                        drawRect = hbox.draw(screen,current_stage.stageToScreen(hbox.rect),scale)
                        if drawRect: self.dirty_rects.append(drawRect)
            #hitbox collision with hurtboxes is covered above, this will check for collision with stages
            for hitbox in active_hitboxes:
                hitbox_collisions = pygame.sprite.spritecollide(hitbox, self.stage.platform_list, False)
                for wall in hitbox_collisions:
                    hitbox.onCollision(wall)
            for fight in currentFighters:
                if fight.rect.right < current_stage.blast_line.left or fight.rect.left > current_stage.blast_line.right or fight.rect.top > current_stage.blast_line.bottom or fight.rect.bottom < current_stage.blast_line.top:
                    if not trackStocks:
                        # Get score
                        fight.die()
                    else:
                        fight.stocks -= 1
                        print(fight.stocks)
                        if fight.stocks == 0:
                            fight.die(False)
                            currentFighters.remove(fight)
                            current_stage.follows.remove(fight.rect)
                            #If someon's eliminated and there's 1 or fewer people left
                            if len(currentFighters) < 2:
                                exitStatus = 2 #Game set
                        else: fight.die()
            # End object updates
            drawRects = current_stage.drawFG(screen)    
            self.dirty_rects.extend(drawRects)
            
            for obj in guiObjects:
                drawRect = obj.draw(screen, obj.rect.topleft,1)
                if drawRect: self.dirty_rects.append(drawRect)
            if trackTime and clockTime <= 5:
                countAlpha = max(0,countAlpha - 5)
                countdownSprite.alpha(countAlpha)
                
            
            clock.tick(clock_speed) #change back
            #pygame.display.update(self.dirty_rects)
            self.dirty_rects = []
            pygame.display.update()
            if debug_mode:
                while not debug_pass:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            sys.exit()
                            return -1
                        
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_RCTRL:
                                debug_pass = True
                        
                        for cont in self.controllers:
                            cont.getInputs(event)
                
            debug_pass = False
                
        # End while loop
        
        if exitStatus == 1:
            musicManager.getMusicManager().stopMusic(1000)
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
                resultSprite.image.set_alpha(255)
                nameSprite = spriteManager.TextSprite(fighter.name,size=24)
                nameSprite.rect.midtop = (resultSprite.rect.width / 2,0)
                resultSprite.image.blit(nameSprite.image,nameSprite.rect.topleft)
                
                score = fighter.dataLog.getData('KOs') - fighter.dataLog.getData('Falls')
                text = spriteManager.TextSprite('Score: ' + str(score))
                resultSprite.image.blit(text.image,(0,32))
                    
                dist = 48
                
                print(fighter.dataLog.data)
                for item,val in fighter.dataLog.data.items():
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
                    for i in range(0,len(self.players)):
                        controls = settingsManager.getControls(i)
                        k = controls.getInputs(event)
                        if k == 'attack':
                            resultSprites[i].image.set_alpha(0)
                            confirmedList[i] = True
                        elif k == 'special':
                            resultSprites[i].image.set_alpha(255)
                            confirmedList[i] = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            print("saving screenshot")
                            pygame.image.save(screen,settingsManager.createPath('screenshot.jpg'))
                        if event.key == pygame.K_ESCAPE:
                            return
                                
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
The HealthTracker object contains the sprites needed to display the percentages and stocks.

It is itself a SpriteObject, with an overloaded draw method.
"""
class HealthTracker(spriteManager.Sprite):
    def __init__(self,fighter):
        spriteManager.Sprite.__init__(self)
        self.fighter = fighter
        self.percent = fighter.damage
        
        self.bgSprite = fighter.franchise_icon
        self.bgSprite.recolor(self.bgSprite.image,pygame.Color('#cccccc'),pygame.Color(settingsManager.getSetting('playerColor'+str(fighter.playerNum))))
        self.bgSprite.alpha(128)
        
        self.image = self.bgSprite.image
        self.rect = self.bgSprite.image.get_rect()
        
        #Until I can figure out the percentage sprites
        self.percentSprites = spriteManager.SheetSprite(settingsManager.createPath('sprites/guisheet.png'), 64)
        self.kerningValues = [49,33,44,47,48,43,43,44,49,43,48] #This is the width of each sprite, for kerning purposes
        
        self.percentSprite = spriteManager.Sprite()
        self.percentSprite.image = pygame.Surface((196,64), pygame.SRCALPHA, 32).convert_alpha()
        self.redness = 0
        
        self.updateDamage()
        self.percentSprite.rect = self.percentSprite.image.get_rect()
        self.percentSprite.rect.center = self.rect.center
        
        
    
    def updateDamage(self):
        #recolor the percentage
        oldredness = self.redness
        self.redness = min(1.0,float(self.percent) / 300)
        #the lighter color first
        rgbFrom = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(0,oldredness,1.0))
        rgbTo = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(0,self.redness,1.0))
        self.percentSprites.recolor(self.percentSprites.sheet, rgbFrom, rgbTo)
        #the darker color next
        rgbFrom = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(0,oldredness,0.785))
        rgbTo = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(0,self.redness,0.785))
        self.percentSprites.recolor(self.percentSprites.sheet, rgbFrom, rgbTo)
        
        
        self.percentSprite.image = pygame.Surface((196,64), pygame.SRCALPHA, 32).convert_alpha()
        
        percentString = str(self.percent) #converting it to a string so we can iterate over it.
        length = 0
        for ch in percentString:
            i = int(ch)
            self.percentSprite.image.blit(self.percentSprites.getImageAtIndex(i), (length,0))
            length += self.kerningValues[i]
        
        #add the % sign at the end
        self.percentSprite.image.blit(self.percentSprites.getImageAtIndex(10), (length,0))
        
        self.percentSprite.image = pygame.transform.smoothscale(self.percentSprite.image, (96,32))
        length += self.kerningValues[10]
        
    def draw(self,screen,offset,scale):
        if not self.percent == self.fighter.damage:
            self.percent = self.fighter.damage
            self.updateDamage()
        
        h = int(round(self.rect.height * scale))
        w = int(round(self.rect.width * scale))
        newOff = (int(offset[0] * scale), int(offset[1] * scale))
        
        screen.blit(self.image,pygame.Rect(newOff,(w,h)))
        
        rect = self.percentSprite.rect
        self.percentSprite.draw(screen, (newOff[0] + rect.left,newOff[1] + rect.top), scale)

"""
The Data Log object keeps track of information that happens in-game, such as score, deaths, total damage dealt/received, etc.

A log will be made for each character, and it will be given to them on load. They will keep track of updating their logs,
and characters are free to give it new information as they see fit. For example, you could make a character like Game & Watch log
how many of each number he scored.
"""
class DataLog(object):
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
