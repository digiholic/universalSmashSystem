import random
import pygame
import settingsManager
import spriteManager
import sys
import musicManager
import fighters.sandbag.fighter
import engine.hitbox as hitbox
import engine.optimize_dirty_rects
import colorsys
import pdb
import io
import string
from cgi import log

"""
The battle object actually creates the fight and plays it out on screen.
It calls the update function of all of the fighters and the stage, and draws them.
It takes a Rules object (see below), a list of players, and a stage.


"""
class Battle():
    def __init__(self,_rules,_players,_stage):
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
        
        #TODO bring over InputBuffer from fighter.
        random.seed
        self.random_state = random.getstate
        
    def startBattle(self,_screen): 
        # Try block to catch any and every error
        try:
            # Fill background
            background = pygame.Surface(_screen.get_size())
            background = background.convert()
            background.fill((128, 128, 128))
            
            _screen.fill(self.stage.background_color)
            current_stage = self.stage
            active_hitboxes = pygame.sprite.Group()
            active_hurtboxes = pygame.sprite.Group()
            
            #game_objects
            current_fighters = self.players[:] #We have to slice this list so it passes by value instead of reference
            game_objects = []
            game_objects.extend(current_fighters)
            
            track_stocks = True
            track_time = True
            if self.rules.stocks == 0:
                track_stocks = False
            if self.rules.time == 0:
                track_time = False
                
            clock_time = self.rules.time * 60
            
            gui_objects = []
            
            if track_time:
                pygame.time.set_timer(pygame.USEREVENT+2, 1000)
                countdown_sprite = spriteManager.TextSprite('5','full Pack 2025',128,[0,0,0])
                countdown_sprite.rect.center = _screen.get_rect().center
                count_alpha = 0
                countdown_sprite.alpha(count_alpha)
                gui_objects.append(countdown_sprite)
                
                clock_sprite = spriteManager.TextSprite('8:00','rexlia rg',32,[0,0,0])
                clock_sprite.rect.topright = _screen.get_rect().topright
                clock_sprite.changeText(str(clock_time / 60)+':'+str(clock_time % 60).zfill(2))
                gui_objects.append(clock_sprite)
            
            gui_offset = _screen.get_rect().width / (len(self.players) + 1)
            for fighter in current_fighters:
                fighter.rect.midbottom = current_stage.spawn_locations[fighter.player_num]
                fighter.sprite.updatePosition(fighter.rect)
                fighter.ecb.normalize()
                fighter.ecb.store()
                fighter.game_state = current_stage
                fighter.players = self.players
                current_stage.follows.append(fighter.rect)
                log = DataLog()
                self.data_logs.append(log)
                fighter.data_log = log
                if track_stocks: fighter.stocks = self.rules.stocks
                
                percent_sprite = HealthTracker(fighter)
                
                percent_sprite.rect.bottom = _screen.get_rect().bottom
                percent_sprite.rect.centerx = gui_offset
    
                gui_offset += _screen.get_rect().width / (len(self.players) + 1)
                
                gui_objects.append(percent_sprite)
            
            center_stage_rect = pygame.rect.Rect((0,0),(16,16))
            center_stage_rect.center = current_stage.size.center
            current_stage.follows.append(center_stage_rect)
            current_stage.initializeCamera()
            
            
            clock = pygame.time.Clock()
            clock_speed = 60
            debug_mode = False
            debug_pass = False
            """
            ExitStatus breaks us out of the loop. The battle loop can end in many ways, which is reflected here.
            In general, ExitStatus positive means that the game was supposed to end, while a negative value indicates an error.
            
            ExitStatus == 1: Battle ended early by submission. Declare the other players winners, show victory screen.
            ExitStatus == 2: Battle ended by time or stock. Declare winner from stocks and percentage, show victory screen. 
            ExitStatus == 3: Battle ended early by mutual agreement. Declare draw by agreement, return to menu. 
            ExitStatus == -1: Battle ended in error. Print stack trace, return to menu. 
            """
            exit_status = 0
            
            data_log = DataLog()
            data_log.addSection('test', 1)
            data_log.setData('test', 3, (lambda x,y: x + y))
            self.dirty_rects = [pygame.Rect(0,0,self.settings['windowWidth'],self.settings['windowHeight'])]
            while exit_status == 0:
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
                            pygame.image.save(_screen,settingsManager.createPath('screenshot.jpg'))
                        elif event.key == pygame.K_RSHIFT:
                            debug_mode = not debug_mode
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_ESCAPE:
                            exit_status = 1
                                
                    if event.type == pygame.USEREVENT+2:
                        pygame.time.set_timer(pygame.USEREVENT+2, 1000)
                        clock_sprite.changeText(str(clock_time / 60)+':'+str(clock_time % 60).zfill(2))
                        clock_time -= 1
                        if clock_time <= 5 and clock_time > 0:
                            countdown_sprite.changeText(str(clock_time))
                            count_alpha = 255
                        if clock_time == 0:
                            exit_status = 2
                # End pygame event loop
                                       
                _screen.fill(self.stage.background_color)
                
                current_stage.update()
                current_stage.cameraUpdate()
                active_hitboxes.add(current_stage.active_hitboxes)
                active_hurtboxes.add(current_stage.active_hurtboxes)
                
                draw_rects = current_stage.drawBG(_screen)
                self.dirty_rects.extend(draw_rects)
            
                for obj in game_objects:
                    obj.update()
                
                    foreground_articles = []
                    if hasattr(obj, 'articles'):
                        for art in obj.articles:
                            if art.draw_depth == -1:
                                offset = current_stage.stageToScreen(art.rect)
                                scale =  current_stage.getScale()
                                draw_rect = art.draw(_screen,offset,scale)
                                if draw_rect: self.dirty_rects.append(draw_rect)
                            else: foreground_articles.append(art)
                    
                    if hasattr(obj,'active_hitboxes'):
                        active_hitboxes.add(obj.active_hitboxes)
                    if hasattr(obj, 'hurtbox'):
                        active_hurtboxes.add(obj.hurtbox)
                    
                    offset = current_stage.stageToScreen(obj.rect)
                    scale =  current_stage.getScale()
                    draw_rect = obj.draw(_screen,offset,scale)
                    if draw_rect: self.dirty_rects.append(draw_rect)
                    
                    for art in foreground_articles:
                        offset = current_stage.stageToScreen(art.rect)
                        scale =  current_stage.getScale()
                        draw_rect = art.draw(_screen,offset,scale)
                        if draw_rect: self.dirty_rects.append(draw_rect)
                    
                    if hasattr(obj, 'hurtbox'):
                        if (self.settings['showHurtboxes']): 
                            offset = current_stage.stageToScreen(obj.hurtbox.rect)
                            draw_rect = obj.hurtbox.draw(_screen,offset,scale)
                            if draw_rect: self.dirty_rects.append(draw_rect)
                    if (self.settings['showHitboxes']):
                        for hbox in active_hitboxes:
                            draw_rect = hbox.draw(_screen,current_stage.stageToScreen(hbox.rect),scale)
                            if draw_rect: self.dirty_rects.append(draw_rect)
    
                hitbox_hits = pygame.sprite.groupcollide(active_hitboxes, active_hitboxes, False, False)
                for hbox in hitbox_hits:
                    #first, check for clanks
                    hitbox_clank = hitbox_hits[hbox]
                    hitbox_clank = [x for x in hitbox_clank if (x is not hbox) and (x.owner is not hbox.owner)]
                    if hitbox_clank: print(hitbox_clank)
                    for other in hitbox_clank:
                        print('Other hitbox: '+str(other))
                        hbox_clank = False
                        other_clank = False
                        hbox_prevail = False
                        other_prevail = False
                        if not hbox.compareTo(other):
                            if other.owner.lockHitbox(hbox) and hasattr(hbox.owner,'current_action'):
                                hbox_clank = True
                            print("CLANK!")
                        else:
                            if other.owner.lockHitbox(hbox) and hasattr(hbox.owner,'current_action'):
                                hbox_prevail = True
                        if not other.compareTo(hbox):
                            if hbox.owner.lockHitbox(other) and hasattr(other.owner,'current_action'):
                                other_clank = True
                            print("CLANK!")
                        else:
                            if hbox.owner.lockHitbox(other) and hasattr(other.owner,'current_action'):
                                other_prevail = True
                        if not isinstance(hbox, hitbox.InertHitbox) and not isinstance(other, hitbox.InertHitbox):
                            if hbox_clank:
                                if isinstance(hbox, hitbox.DamageHitbox) and hbox.article == None:
                                    hbox.owner.applyPushback(hbox.base_knockback/5.0, hbox.getTrajectory()+180, (hbox.damage/4.0+2.0)*hbox.hitlag_multiplier + 6.0)
                                elif hbox.article == None:
                                    hbox.owner.hitstop = 8
                                if hbox.article == None:
                                    hbox.owner.current_action.onClank(hbox.owner, hbox, other)
                                else:
                                    hbox.article.onClank(hbox.owner, hbox, other)
                            if hbox_prevail:
                                if hbox.article == None:
                                    hbox.owner.current_action.onPrevail(hbox.owner, hbox, other)
                                else:
                                    hbox.article.onPrevail(hbox.owner, hbox, other)
                            if other_clank:
                                if isinstance(other, hitbox.DamageHitbox) and other.article == None:
                                    other.owner.applyPushback(other.base_knockback/5.0, other.getTrajectory()+180, (other.damage/4.0+2.0)*other.hitlag_multiplier + 6.0)
                                elif other.article == None:
                                    other.owner.hitstop = 8
                                if other.article == None:
                                    other.owner.current_action.onClank(other.owner, other, hbox)
                                else:
                                    other.article.onClank(other.owner, other, hbox)
                            if other_prevail:
                                if other.article == None:
                                    other.owner.current_action.onPrevail(other.owner, other, hbox)
                                else:
                                    other.article.onPrevail(other.owner, other, hbox)
                        elif hbox_clank and other_clank:
                            if isinstance(hbox, hitbox.DamageHitbox) and hbox.article == None:
                                hbox.owner.applyPushback(hbox.base_knockback/5.0, hbox.getTrajectory()+180, (hbox.damage/4.0+2.0)*hbox.hitlag_multiplier + 6.0)
                            elif hbox.article == None:
                                hbox.owner.hitstop = 8
                            if isinstance(other, hitbox.DamageHitbox) and other.article == None:
                                other.owner.applyPushback(other.base_knockback/5.0, other.getTrajectory()+180, (other.damage/4.0+2.0)*other.hitlag_multiplier + 6.0)
                            elif other.article == None:
                                other.owner.hitstop = 8
                                
                hurtbox_hits = pygame.sprite.groupcollide(active_hitboxes, active_hurtboxes, False, False)
                for hbox in hurtbox_hits:
                    #then, hurtbox collisions
                    hitbox_collisions = hurtbox_hits[hbox]
                    for hurtbox in hitbox_collisions:
                        if hbox.owner != hurtbox.owner:
                            hbox.onCollision(hurtbox.owner)
                            hurtbox.onHit(hbox)
                            
                platform_hits = pygame.sprite.groupcollide(active_hitboxes, self.stage.platform_list, False, False)
                for hbox in platform_hits:
                    #then platform collisions
                    platform_collisions = platform_hits[hbox]
                    for wall in platform_collisions:
                        hbox.onCollision(wall)            
                
                for fight in current_fighters:
                    if fight.rect.right < current_stage.blast_line.left or fight.rect.left > current_stage.blast_line.right or fight.rect.top > current_stage.blast_line.bottom or fight.rect.bottom < current_stage.blast_line.top:
                        if not track_stocks:
                            # Get score
                            fight.die()
                        else:
                            fight.stocks -= 1
                            print(fight.stocks)
                            if fight.stocks == 0:
                                fight.die(False)
                                current_fighters.remove(fight)
                                current_stage.follows.remove(fight.rect)
                                #If someone's eliminated and there's 1 or fewer people left
                                if len(current_fighters) < 2:
                                    exit_status = 2 #Game set
                            else: fight.die()
                # End object updates
                draw_rects = current_stage.drawFG(_screen)    
                self.dirty_rects.extend(draw_rects)
                
                for obj in gui_objects:
                    draw_rect = obj.draw(_screen, obj.rect.topleft,1)
                    if draw_rect: self.dirty_rects.append(draw_rect)
                if track_time and clock_time <= 5:
                    count_alpha = max(0,count_alpha - 5)
                    countdown_sprite.alpha(count_alpha)
                 
                clock.tick(clock_speed)
                optimized_rects = engine.optimize_dirty_rects.optimize_dirty_rects(self.dirty_rects)
                #pygame.display.update(optimized_rects)
                self.dirty_rects = []
                pygame.display.update()
                if debug_mode:
                    print("Paused, press left shift key again to continue, debugger coming soon (I promise)")
                    while debug_mode:
                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                exit_status = 1
                            
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_LSHIFT:
                                    debug_mode = False
                                    debug_pass = False
                                elif event.key == pygame.K_RETURN:
                                    debug_mode = True
                                    if not debug_pass:
                                        debug_pass = True
                                        pygame.set_repeat(500, 100)
                                    else:
                                        debug_pass = False
                                elif debug_pass:
                                    print("Hold on, debugger functionality coming soon")
                                    debug_pass = False
                                        
                                        
                            
                            if not debug_pass:
                                pygame.set_repeat() #Disable
                                for cont in self.controllers:
                                    cont.getInputs(event)
        except:
            try:
                import traceback
                traceback.print_exc()
            finally:
                exit_status = -1
            
            
        if exit_status == 1:
            musicManager.getMusicManager().stopMusic(1000)
            print("SUBMISSION")
        elif exit_status == 2:
            musicManager.getMusicManager().stopMusic()
            frame_hold = 0
            game_sprite = spriteManager.TextSprite('GAME!','full Pack 2025',128,[0,0,0])
            game_sprite.rect.center = _screen.get_rect().center
            while frame_hold < 150:
                game_sprite.draw(_screen, game_sprite.rect.topleft, 1)
                clock.tick(60)
                pygame.display.flip()
                frame_hold += 1
            print("GAME SET")
        elif exit_status == -1:
            musicManager.getMusicManager().stopMusic()
            frame_hold = 0
            game_sprite = spriteManager.TextSprite('NO CONTEST','full Pack 2025',64,[0,0,0])
            game_sprite.rect.center = _screen.get_rect().center
            while frame_hold < 150:
                game_sprite.draw(_screen, game_sprite.rect.topleft, 1)
                clock.tick(60)
                pygame.display.flip()
                frame_hold += 1
            print("NO CONTEST")
            
        
        self.endBattle(exit_status,_screen)    
        return exit_status # This'll pop us back to the character select screen.
        
         
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
    def endBattle(self,_exitStatus,_screen):
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
                    sys.exit()
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
                        pygame.image.save(_screen,settingsManager.createPath('screenshot.jpg'))
                    if event.key == pygame.K_ESCAPE:
                        return
                            
            _screen.fill((0,0,0))
            for sprite in result_sprites:
                sprite.draw(_screen, sprite.rect.topleft, 1.0)
            
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
