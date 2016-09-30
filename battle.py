import random
import pygame
import settingsManager
import spriteManager
import sys
import os
import musicManager
import fighters.sandbag.fighter
import engine.hitbox as hitbox
import menu.debugConsole as debugConsole
import engine.optimize_dirty_rects
import colorsys
import pdb
import io
import string
import menu
import inspect
from cgi import log

"""
The battle object actually creates the fight and plays it out on screen.
It calls the update function of all of the fighters and the stage, and draws them.
It takes a Rules object (see below), a list of players, and a stage.


"""
class Battle():
    def __init__(self,_rules,_players,_stage,_randomSeed=None):
        self.settings = settingsManager.getSetting().setting
        
        if _rules is None: _rules = Rules()
        
        self.rules = _rules
        self.players = _players
        self.controllers = []
        for player in _players:
            player.initialize()
            player.key_bindings.loadFighter(player)
            self.controllers.append(player.key_bindings)
            
        self.stage = _stage
        self.input_buffer = None
        self.data_logs = []

        random.seed(_randomSeed)
        
        self.active_hitboxes = pygame.sprite.Group()
        self.active_hurtboxes = pygame.sprite.Group()
        
        self.track_stocks = True
        self.track_time = True
        if self.rules.stocks == 0:
            self.track_stocks = False
        if self.rules.time == 0:
            self.track_time = False
            
            
    def startBattle(self,_screen): 
        self.screen = _screen
        self.debug_console = debugConsole.debugConsole(self.screen, self)
        
        # Try block to catch any and every error
        try:
            self.screen.fill(self.stage.background_color)
            
            #game_objects
            self.current_fighters = self.players[:] #We have to slice this list so it passes by value instead of reference
            self.game_objects = []
            self.game_objects.extend(self.current_fighters)
               
            self.clock_time = self.rules.time * 60
            
            self.gui_objects = []
            
            if self.track_time:
                pygame.time.set_timer(pygame.USEREVENT+2, 1000)
                countdown_sprite = spriteManager.TextSprite('5','full Pack 2025',128,[0,0,0])
                countdown_sprite.rect.center = self.screen.get_rect().center
                count_alpha = 0
                countdown_sprite.alpha(count_alpha)
                self.gui_objects.append(countdown_sprite)
                
                self.clock_sprite = spriteManager.TextSprite('8:00','rexlia rg',32,[0,0,0])
                self.clock_sprite.rect.topright = self.screen.get_rect().topright
                self.clock_sprite.changeText(str(self.clock_time / 60)+':'+str(self.clock_time % 60).zfill(2))
                self.gui_objects.append(self.clock_sprite)
            
            gui_offset = self.screen.get_rect().width / (len(self.players) + 1)
            for fighter in self.current_fighters:
                fighter.rect.midbottom = self.stage.spawn_locations[fighter.player_num]
                fighter.sprite.updatePosition(fighter.rect)
                fighter.ecb.normalize()
                fighter.ecb.store()
                fighter.game_state = self.stage
                fighter.players = self.players
                self.stage.follows.append(fighter.rect)
                log = DataLog()
                self.data_logs.append(log)
                fighter.data_log = log
                if self.track_stocks: fighter.stocks = self.rules.stocks
                
                percent_sprite = HealthTracker(fighter)
                
                percent_sprite.rect.bottom = self.screen.get_rect().bottom
                percent_sprite.rect.centerx = gui_offset
    
                gui_offset += self.screen.get_rect().width / (len(self.players) + 1)
                
                self.gui_objects.append(percent_sprite)
            
            center_stage_rect = pygame.rect.Rect((0,0),(16,16))
            center_stage_rect.center = self.stage.size.center
            self.stage.follows.append(center_stage_rect)
            self.stage.initializeCamera()
            
            
            self.clock = pygame.time.Clock()
            self.clock_speed = 60
            self.debug_mode = False
            """
            ExitStatus breaks us out of the loop. The battle loop can end in many ways, which is reflected here.
            In general, ExitStatus positive means that the game was supposed to end, while a negative value indicates an error.
            
            ExitStatus == 1: Battle ended early by submission. Declare the other players winners, show victory screen.
            ExitStatus == 2: Battle ended by time or stock. Declare winner from stocks and percentage, show victory screen. 
            ExitStatus == 3: Battle ended early by mutual agreement. Declare draw by agreement, return to menu. 
            ExitStatus == -1: Battle ended in error. Print stack trace, return to menu. 
            """
            self.exit_status = 0
            
            data_log = DataLog()
            data_log.addSection('test', 1)
            data_log.setData('test', 3, (lambda x,y: x + y))
            self.dirty_rects = [pygame.Rect(0,0,self.settings['windowWidth'],self.settings['windowHeight'])]
            while self.exit_status == 0:
                self.gameEventLoop()
                
        except:
            try:
                import traceback
                traceback.print_exc()
            finally:
                self.exit_status = -1
            
        if self.exit_status == 1:
            musicManager.getMusicManager().stopMusic(1000)
            print("SUBMISSION")
        elif self.exit_status == 2:
            musicManager.getMusicManager().stopMusic()
            frame_hold = 0
            game_sprite = spriteManager.TextSprite('GAME!','full Pack 2025',128,[0,0,0])
            game_sprite.rect.center = self.screen.get_rect().center
            while frame_hold < 150:
                game_sprite.draw(self.screen, game_sprite.rect.topleft, 1)
                self.clock.tick(60)
                pygame.display.flip()
                frame_hold += 1
            print("GAME SET")
        elif self.exit_status == -1:
            musicManager.getMusicManager().stopMusic()
            frame_hold = 0
            game_sprite = spriteManager.TextSprite('NO CONTEST','full Pack 2025',64,[0,0,0])
            game_sprite.rect.center = self.screen.get_rect().center
            while frame_hold < 150:
                game_sprite.draw(self.screen, game_sprite.rect.topleft, 1)
                self.clock.tick(60)
                pygame.display.flip()
                frame_hold += 1
            print("NO CONTEST")
            
        
        self.endBattle(self.exit_status)    
        return self.exit_status # This'll pop us back to the character select screen.
        
    def gameEventLoop(self):
        for cont in self.controllers:
            cont.passInputs()
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                os._exit(1)
                return -1
            
            for cont in self.controllers:
                cont.getInputs(event)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F2:
                    print("saving screenshot")
                    pygame.image.save(self.screen,settingsManager.createPath('screenshot.jpg'))
                elif event.key == pygame.K_RSHIFT:
                    self.debug_mode = not self.debug_mode
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE:
                    self.exit_status = 1
                        
            if event.type == pygame.USEREVENT+2:
                pygame.time.set_timer(pygame.USEREVENT+2, 1000)
                self.clock_sprite.changeText(str(self.clock_time / 60)+':'+str(self.clock_time % 60).zfill(2))
                self.clock_time -= 1
                if self.clock_time <= 5 and self.clock_time > 0:
                    self.countdown_sprite.changeText(str(self.clock_time))
                    count_alpha = 255
                if self.clock_time == 0:
                    self.exit_status = 2
        # End pygame event loop
        
        self.stage.update()
        self.stage.cameraUpdate()
        self.active_hitboxes.add(self.stage.active_hitboxes)
        self.active_hurtboxes.add(self.stage.active_hurtboxes)
    
        for obj in self.game_objects:
            obj.update()
            if hasattr(obj,'active_hitboxes'):
                self.active_hitboxes.add(obj.active_hitboxes)
            if hasattr(obj, 'hurtbox'):
                self.active_hurtboxes.add(obj.hurtbox)

        hitbox_hits = pygame.sprite.groupcollide(self.active_hitboxes, self.active_hitboxes, False, False)
        for hbox in hitbox_hits:
            #first, check for clanks
            hitbox_clank = hitbox_hits[hbox]
            hitbox_clank = [x for x in hitbox_clank if (x is not hbox) and (x.owner is not hbox.owner)]
            if hitbox_clank: print(hitbox_clank)
            for other in hitbox_clank:
                hbox_clank = False
                other_clank = False
                if not hbox.compareTo(other):
                    hbox_clank = True
                    print("CLANK!")
                if not other.compareTo(hbox):
                    other_clank = True
                    print("clank!")
                if hbox_clank: other.owner.lockHitbox(hbox)
                if other_clank: hbox.owner.lockHitbox(other)
                        
        hurtbox_hits = pygame.sprite.groupcollide(self.active_hitboxes, self.active_hurtboxes, False, False)
        for hbox in hurtbox_hits:
            #then, hurtbox collisions
            hitbox_collisions = hurtbox_hits[hbox]
            for hurtbox in hitbox_collisions:
                if hbox.owner != hurtbox.owner:
                    hbox.onCollision(hurtbox.owner)
                    hurtbox.onHit(hbox)
                    
        platform_hits = pygame.sprite.groupcollide(self.active_hitboxes, self.stage.platform_list, False, False)
        for hbox in platform_hits:
            #then platform collisions
            platform_collisions = platform_hits[hbox]
            for wall in platform_collisions:
                hbox.onCollision(wall)            
        
        for fight in self.current_fighters:
            if fight.rect.right < self.stage.blast_line.left or fight.rect.left > self.stage.blast_line.right or fight.rect.top > self.stage.blast_line.bottom or fight.rect.bottom < self.stage.blast_line.top:
                if not self.track_stocks:
                    # Get score
                    fight.die()
                else:
                    fight.stocks -= 1
                    print(fight.stocks)
                    if fight.stocks == 0:
                        fight.die(False)
                        self.current_fighters.remove(fight)
                        self.stage.follows.remove(fight.rect)
                        #If someone's eliminated and there's 1 or fewer people left
                        if len(self.current_fighters) < 2:
                            self.exit_status = 2 #Game set
                    else: fight.die()
        # End object updates
        self.draw()
        pygame.display.update()
        if self.debug_mode:
            print("Paused, press left shift key again to continue, press tab to drop into the debugger console")
            while self.debug_mode:
                self.debugLoop()

    def draw(self):
        self.screen.fill(self.stage.background_color)
        
        draw_rects = self.stage.drawBG(self.screen)
        self.dirty_rects.extend(draw_rects)

        for obj in self.game_objects:
            foreground_articles = []
            if hasattr(obj, 'articles'):
                for art in obj.articles:
                    if art.draw_depth == -1:
                        offset = self.stage.stageToScreen(art.rect)
                        scale =  self.stage.getScale()
                        draw_rect = art.draw(self.screen,offset,scale)
                        if draw_rect: self.dirty_rects.append(draw_rect)
                    else: foreground_articles.append(art)

            offset = self.stage.stageToScreen(obj.rect)
            scale =  self.stage.getScale()
            draw_rect = obj.draw(self.screen,offset,scale)
            if draw_rect: self.dirty_rects.append(draw_rect)
            
            for art in foreground_articles:
                offset = self.stage.stageToScreen(art.rect)
                scale =  self.stage.getScale()
                draw_rect = art.draw(self.screen,offset,scale)
                if draw_rect: self.dirty_rects.append(draw_rect)
            if hasattr(obj, 'hurtbox'):
                if (self.settings['showHurtboxes']): 
                    offset = self.stage.stageToScreen(obj.hurtbox.rect)
                    draw_rect = obj.hurtbox.draw(self.screen,offset,scale)
                    if draw_rect: self.dirty_rects.append(draw_rect)
            if (self.settings['showHitboxes']):
                for hbox in self.active_hitboxes:
                    draw_rect = hbox.draw(self.screen,self.stage.stageToScreen(hbox.rect),scale)
                    if draw_rect: self.dirty_rects.append(draw_rect)


        draw_rects = self.stage.drawFG(self.screen)    
        self.dirty_rects.extend(draw_rects)
        
        for obj in self.gui_objects:
            draw_rect = obj.draw(self.screen, obj.rect.topleft,1)
            if draw_rect: self.dirty_rects.append(draw_rect)
        if self.track_time and self.clock_time <= 5:
            count_alpha = max(0,count_alpha - 5)
            self.countdown_sprite.alpha(count_alpha)
         
        self.clock.tick(self.clock_speed)
        optimized_rects = engine.optimize_dirty_rects.optimize_dirty_rects(self.dirty_rects)
        #pygame.display.update(optimized_rects)
        self.dirty_rects = []
        
            
    def debugLoop(self):
        self.draw()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.exit_status = 1
                self.debug_mode = False
            
            if event.type == pygame.KEYDOWN or event.type == pygame.KEYUP:
                if event.key == pygame.K_LSHIFT and event.type == pygame.KEYDOWN:
                    self.debug_mode = False
                elif event.key == pygame.K_TAB and event.type == pygame.KEYDOWN:
                    self.debug_console.set_trace() #Drop into the console
                        
            for cont in self.controllers:
                cont.getInputs(event)
        
    """
    In a normal game, the frame input won't matter.
    It will matter in replays and (eventually) online.
    """
    def getInputsforFrame(self,_frame):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                pass
            if event.type == pygame.KEYUP:
                pass
             
    def saveReplay(self,_path):
        pass
    
    """
    Ends the battle and goes to a relevant menu or error page depending on how the
    battle ended.
    """    
    def endBattle(self,_exitStatus):
        if not (_exitStatus == 1 or _exitStatus == 2 or _exitStatus == 3):
            print("An error occured that caused TUSSLE to stop working. If you can replicate this error, please file a bug report so the relevant developers can fix it. Post-mortem debugging coming soon. ")
        result_sprites = []
        width = settingsManager.getSetting('windowWidth')
        height = settingsManager.getSetting('windowHeight')
        for i in range(0,len(self.players)):
            print(self.players)
            print("player"+str(i))
            fighter = self.players[i]
            result_sprite = spriteManager.RectSprite(pygame.Rect((width / 4) * i,0,(width / 4),height), pygame.Color(settingsManager.getSetting('playerColor'+str(i))))
            result_sprite.image.set_alpha(255)
            name_sprite = spriteManager.TextSprite(fighter.name,_size=24)
            name_sprite.rect.midtop = (result_sprite.rect.width / 2,0)
            result_sprite.image.blit(name_sprite.image,name_sprite.rect.topleft)
            
            score = fighter.data_log.getData('KOs') - fighter.data_log.getData('Falls')
            text = spriteManager.TextSprite('Score: ' + str(score))
            result_sprite.image.blit(text.image,(0,32))
                
            dist = 48
            
            print(fighter.data_log.data)
            for item,val in fighter.data_log.data.items():
                text = spriteManager.TextSprite(str(item) + ': ' + str(val))
                result_sprite.image.blit(text.image,(0,dist))
                dist += 16
            result_sprites.append(result_sprite)
            confirmed_list = [False] * len(result_sprites) #This pythonic hacking will make a list of falses equal to the result panels
       
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    os._exit(1)
                    return -1
                for i in range(0,len(self.players)):
                    controls = settingsManager.getControls(i)
                    k = controls.getInputs(event)
                    if k == 'attack':
                        result_sprites[i].image.set_alpha(0)
                        confirmed_list[i] = True
                    elif k == 'special':
                        result_sprites[i].image.set_alpha(255)
                        confirmed_list[i] = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        print("Saving screenshot")
                        pygame.image.save(self.screen,settingsManager.createPath('screenshot.jpg'))
                    if event.key == pygame.K_ESCAPE:
                        return
                            
            self.screen.fill((0,0,0))
            for sprite in result_sprites:
                sprite.draw(self.screen, sprite.rect.topleft, 1.0)
            
            if all(confirmed_list):
                return
            pygame.display.flip()
        return
        
"""
The rules object determines the battle's rules.
By default it's 3 stock, 8 minute, free for all.
If stocks is set to 0, infinite stocks are used.
If time is set to 0, infinite time is used.
Self.teams is a list of tuples. Each tuple is in the form of (teamNumber, [player_numbers]).
For example, if players 1 and 4 were on a team against players 2 and 3, the variable would look like this:

self.teams = [(0, [0,3]), (1, [1,2])]

Remember that PlayerNum is zero-indexed, so player 1 is PlayerNum 0, and so on.
"""
class Rules():
    def __init__(self,_stocks=3,_time=480,_teams=[]):
        self.stocks = _stocks #default to 3 stock
        self.time = _time #default to 8 minutes
        self.teams = _teams #teams off
    
class Replay(Battle):
    def __init__(self):
        pass
    

"""
The HealthTracker object contains the sprites needed to display the percentages and stocks.

It is itself a SpriteObject, with an overloaded draw method.
"""
class HealthTracker(spriteManager.Sprite):
    def __init__(self,_fighter):
        spriteManager.Sprite.__init__(self)
        self.fighter = _fighter
        self.percent = int(_fighter.damage)
        
        self.bg_sprite = _fighter.franchise_icon
        self.bg_sprite.recolor(self.bg_sprite.image,pygame.Color('#cccccc'),pygame.Color(settingsManager.getSetting('playerColor'+str(_fighter.player_num))))
        self.bg_sprite.alpha(128)
        
        self.image = self.bg_sprite.image
        self.rect = self.bg_sprite.image.get_rect()
        
        #Until I can figure out the percentage sprites
        self.percent_sprites = spriteManager.SheetSprite(settingsManager.createPath('sprites/guisheet.png'), 64)
        self.kerning_values = [49,33,44,47,48,43,43,44,49,43,48] #This is the width of each sprite, for kerning purposes
        
        self.percent_sprite = spriteManager.Sprite()
        self.percent_sprite.image = pygame.Surface((196,64), pygame.SRCALPHA, 32).convert_alpha()
        self.redness = 0
        
        self.updateDamage()
        self.percent_sprite.rect = self.percent_sprite.image.get_rect()
        self.percent_sprite.rect.center = self.rect.center
        
    def updateDamage(self):
        #recolor the percentage
        old_redness = self.redness
        self.redness = min(1.0,float(self.percent) / 300)
        #the lighter color first
        rgb_from = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(0,old_redness,1.0))
        rgb_to = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(0,self.redness,1.0))
        self.percent_sprites.recolor(self.percent_sprites.sheet, rgb_from, rgb_to)
        #the darker color next
        rgb_from = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(0,old_redness,0.785))
        rgb_to = tuple(int(i * 255) for i in colorsys.hsv_to_rgb(0,self.redness,0.785))
        self.percent_sprites.recolor(self.percent_sprites.sheet, rgb_from, rgb_to)
        
        
        self.percent_sprite.image = pygame.Surface((196,64), pygame.SRCALPHA, 32).convert_alpha()
        
        percent_string = str(int(self.percent)) #converting it to a string so we can iterate over it.
        length = 0
        for ch in percent_string:
            i = int(ch)
            self.percent_sprite.image.blit(self.percent_sprites.getImageAtIndex(i), (length,0))
            length += self.kerning_values[i]
        
        #add the % sign at the end
        self.percent_sprite.image.blit(self.percent_sprites.getImageAtIndex(10), (length,0))
        
        self.percent_sprite.image = pygame.transform.smoothscale(self.percent_sprite.image, (96,32))
        length += self.kerning_values[10]
        
    def draw(self,_screen,_offset,_scale):
        if not self.percent == int(self.fighter.damage):
            self.percent = int(self.fighter.damage)
            self.updateDamage()
        
        h = int(round(self.rect.height * _scale))
        w = int(round(self.rect.width * _scale))
        new_off = (int(_offset[0] * _scale), int(_offset[1] * _scale))
        
        _screen.blit(self.image,pygame.Rect(new_off,(w,h)))
        
        rect = self.percent_sprite.rect
        self.percent_sprite.draw(_screen, (new_off[0] + rect.left,new_off[1] + rect.top), _scale)

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
        
    def addSection(self,_section,_initial):
        self.data[_section] = _initial
            
    def getData(self,_section):
        return self.data[_section]
    
    # If this last function looks scary to you, don't worry. Leave it out, and it changes the value at section to value.
    # You can pass a function to it to apply to section and value and it'll do a cool thing!
    def setData(self,_section,_value,_function = (lambda x,y: y)):
        self.data[_section] = _function(self.getData(_section),_value)
        print(str(_section) + ": " + str(self.data[_section]))
