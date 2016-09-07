import pygame
import engine.baseActions as baseActions
import engine.collisionBox as collisionBox
import math
import settingsManager
import spriteManager
import engine.article as article
import engine.hitbox as hitbox
import weakref
import xml.etree.ElementTree as ElementTree
import os
import actionLoader
import numpy
import engine.articleLoader

class AbstractFighter():
    def __init__(self,_baseDir,_playerNum):
        self.base_dir = _baseDir
        self.player_num = _playerNum
        
        """
        Load the fighter variables from fighter.xml
        """
        directory = os.path.join(_baseDir,'sprites')
        prefix = ''
        default_sprite = 'idle'
        img_width = '64'
        try:
            self.xml_data = ElementTree.parse(os.path.join(_baseDir,'fighter.xml')).getroot()
        except:
            self.xml_data = ElementTree.ElementTree()
            
        try:
            self.name = self.xml_data.find('name').text
        except:
            self.name = 'Unknown'
        
        try:
            franchise_icon_path = os.path.join(_baseDir,self.xml_data.find('icon').text)
            self.franchise_icon_path = self.xml_data.find('icon').text
        except:
            franchise_icon_path = settingsManager.createPath('sprites/default_franchise_icon.png')
            self.franchise_icon_path = settingsManager.createPath('sprites/default_franchise_icon.png')
        
        self.franchise_icon = spriteManager.ImageSprite(franchise_icon_path)
        
        try:
            css_icon_path = os.path.join(_baseDir,self.xml_data.find('css_icon').text)
            self.css_icon_path = self.xml_data.find('css_icon').text
        except:
            css_icon_path = settingsManager.createPath('sprites/icon_unknown.png')
            self.css_icon_path = settingsManager.createPath('sprites/icon_unknown.png')
        self.css_icon = spriteManager.ImageSprite(css_icon_path)
        
        try:
            scale = float(self.xml_data.find('scale').text)
        except:
            scale = 1.0
        
        self.var = {
                'weight': 100,
                'gravity': .5,
                'max_fall_speed': 20.0,
                'max_ground_speed': 7.0,
                'run_speed': 11.0,
                'max_air_speed': 5.5,
                'aerial_transition_speed': 9.0,
                'crawl_speed': 2.5,
                'dodge_speed': 10.0,
                'friction': 0.3,
                'static_grip': 0.3,
                'pivot_grip': 0.6,
                'air_resistance': 0.2,
                'air_control': 0.2,
                'jumps': 1,
                'jump_height': 12.5,
                'short_hop_height': 8.5,
                'air_jump_height': 15.0,
                'heavy_land_lag': 4,
                'fastfall_multiplier': 2.0,
                'hitstun_elasticity': .8,
                'shield_size': 1.0
                }
        
        try:
            for stat in self.xml_data.find('stats'):
                vartype = type(self.var[stat.tag]).__name__
                if vartype == 'int': self.var[stat.tag] = int(stat.text)
                if vartype == 'float': self.var[stat.tag] = float(stat.text)
                
        except: pass
        
        try:
            for var in self.xml_data.find('variables'):
                vartype = 'string'
                if var.attrib.has_key('type'): vartype = var.attrib['type']
                val = var.text
                if vartype == 'int': val = int(val)
                elif vartype == 'float': val = float(val)
                elif vartype == 'bool': val = bool(val)
                setattr(self, var.tag, val)
        except: pass
        
        try:
            self.article_path = os.path.join(_baseDir,self.xml_data.find('article_path').text)
            self.article_path_short = self.xml_data.find('article_path').text
        except:
            self.article_path = _baseDir
            self.article_path_short = ''
        
        try:
            self.article_loader_path = self.xml_data.find('articles').text
            self.article_loader = engine.articleLoader.ArticleLoader(self)
        except:
            self.article_loader_path = ''
            try:
                self.article_loader = settingsManager.importFromURI(os.path.join(_baseDir,self.article_path+'/articles.py'),'articles.py',_suffix=str(self.player_num))
            except:
                self.article_loader = None
            
        try:
            self.sound_path = os.path.join(_baseDir,self.xml_data.find('sound_path').text)
            self.sound_path_short = self.xml_data.find('sound_path').text
        except:
            self.sound_path = None
            self.sound_path_short = ''
        #self.actions = settingsManager.importFromURI(os.path.join(_baseDir,'fighter.xml'),'articles.py',_suffix=str(player_num))
        try:
            directory = os.path.join(_baseDir,self.xml_data.find('sprite_directory').text)
            prefix = self.xml_data.find('sprite_prefix').text
            default_sprite = self.xml_data.find('default_sprite').text
            img_width = int(self.xml_data.find('sprite_width').text)
            self.sprite_directory = self.xml_data.find('sprite_directory').text
        except:
            print('Could not load sprites')
            directory = settingsManager.createPath('sprites')
            prefix = ''
            default_sprite = 'sandbag_idle'
            img_width = 64
            self.sprite_directory = settingsManager.createPath('sprites')
            
        self.sprite_prefix = prefix
        self.default_sprite = default_sprite
        self.sprite_width = img_width
        
        self.color_palettes = []
        try:
            for color_palette in self.xml_data.findall('color_palette'):
                color_dict = {}
                for color_map in color_palette.findall('color_map'):
                    from_color = pygame.Color(color_map.attrib['from_color'])
                    to_color = pygame.Color(color_map.attrib['to_color'])
                    color_dict[(from_color.r, from_color.g, from_color.b)] = (to_color.r, to_color.g, to_color.b)
                
                self.color_palettes.append(color_dict)
        except: pass
        
        while len(self.color_palettes) < 4:
            self.color_palettes.append({})
        
        color = self.color_palettes[self.player_num] #TODO: Pick colors
        
        self.sprite = spriteManager.SpriteHandler(directory,prefix,default_sprite,img_width,color,scale)
        
        #try:
        try:
            actions = self.xml_data.find('actions').text
            self.action_file = actions
            if actions.endswith('.py'):
                self.actions = settingsManager.importFromURI(os.path.join(_baseDir,'fighter.xml'),actions,_suffix=str(self.player_num))
            else:
                self.actions = actionLoader.ActionLoader(_baseDir,actions)
        except:
            self.actions = baseActions
            self.action_file = baseActions.__file__
        
        self.rect = self.sprite.rect
        
        self.game_state = None
        self.players = None
        
        # data_log holds information for the post-game results screen
        self.data_log = None
        
    def saveFighter(self,_path=None):
        if not _path: _path = os.path.join(self.base_dir,'fighter.xml')
        tree = ElementTree.Element('fighter')
        
        tree.append(self.createElement('name', self.name))
        tree.append(self.createElement('icon', self.franchise_icon_path))
        tree.append(self.createElement('css_icon', self.css_icon_path))
        tree.append(self.createElement('scale', self.sprite.scale))
        
        tree.append(self.createElement('sprite_directory', self.sprite_directory))
        tree.append(self.createElement('sprite_prefix', self.sprite_prefix))
        tree.append(self.createElement('sprite_width', self.sprite_width))
        tree.append(self.createElement('default_sprite', self.default_sprite))
        tree.append(self.createElement('article_path', self.article_path_short))
        tree.append(self.createElement('sound_path', self.sound_path_short))
        tree.append(self.createElement('actions', self.action_file))
        
        for i,color_dict in enumerate(self.color_palettes):
            color_elem = ElementTree.Element('color_palette')
            color_elem.attrib['id'] = str(i)
            color_elem.attrib['displayColor'] = '#000000'
            for from_color,to_color in color_dict.iteritems():
                map_elem = ElementTree.Element('color_map')
                map_elem.attrib['from_color'] = '#%02x%02x%02x' % from_color
                map_elem.attrib['to_color'] = '#%02x%02x%02x' % to_color
                color_elem.append(map_elem)
            tree.append(color_elem)
        stats_elem = ElementTree.Element('stats')
        for tag,val in self.var.iteritems():
            stats_elem.append(self.createElement(tag, val))
        tree.append(stats_elem)
        
        ElementTree.ElementTree(tree).write(_path)
    
    def createElement(self,_tag,_val):
        elem = ElementTree.Element(_tag)
        elem.text = str(_val)
        return elem
    
    def initialize(self):     

        self.last_input_frame = 0

        # Super armor variables
        # Set with attacks to make them super armored
        # Remember to set them back at some point
        self.no_flinch_hits = 0
        self.flinch_damage_threshold = 0
        self.flinch_knockback_threshold = 0
        self.armor_damage_multiplier = 1
        
        # Invulnerable flag
        # While this is above zero, hitboxes can't connect with the fighter
        # There are ways of bypassing invulnerability, but please avoid doing so
        self.invulnerable = 0
        self.respawn_invulnerable = 0

        self.elasticity = 0
        self.ground_elasticity = 0
        
        # Whenever a fighter is hit, they are 'tagged' by that player, if they die while tagged, that player gets a point
        self.hit_tagged = None
        
        #Initialize engine variables
        
        # Connect the key_bindings object to the fighter and flush any residual inputs
        self.key_bindings = settingsManager.getControls(self.player_num)
        self.key_bindings.loadFighter(self)
        self.key_bindings.flushInputs()
        
        self.input_buffer = InputBuffer()
        self.keys_held = dict()
        
        self.mask = None
        self.ecb = collisionBox.ECB(self)
        
        self.active_hitboxes = pygame.sprite.Group()
        self.articles = pygame.sprite.Group()
        if self.sound_path:
            settingsManager.getSfx().addSoundsFromDirectory(self.sound_path, self.name)
        
        self.shield = False
        self.shield_integrity = 100
        
        # Grabbing variables
        self.grabbing = None
        self.grabbed_by = None
        self.grab_point = (32,0)
        
        # Hitstop freezes the character for a few frames when hitting or being hit.
        self.hitstop = 0
        self.hitstop_vibration = (0,0)
        self.hitstop_pos = (0,0)
        
        # HitboxLock is a list of hitboxes that will not hit the fighter again for a given amount of time.
        # Each entry in the list is a hitboxLock object
        self.hitbox_lock = weakref.WeakSet()
        self.hitbox_contact = set()
        
        # When a fighter lets go of a ledge, he can't grab another one until he gets out of the area.
        self.ledge_lock = False
        
        #initialize the action
        if hasattr(self.actions,'loadAction'):
            self.current_action = self.actions.loadAction('NeutralAction')
        elif hasattr(self.actions, 'NeutralAction'):
            class_ = getattr(self.actions,'NeutralAction')
            self.current_action = class_()
            
        self.hurtbox = hitbox.Hurtbox(self,self.sprite.bounding_rect,[255,255,0])
        
        #state variables and flags
        self.angle = 0
        self.grounded = False
        self.back_walled = False
        self.front_walled = False
        self.ceilinged = False
        self.jumps = self.var['jumps']
        self.damage = 0
        self.landing_lag = 6
        self.platform_phase = 0
        self.tech_window = 0
        
        self.change_x = 0
        self.change_y = 0
        self.preferred_xspeed = 0
        self.preferred_yspeed = 0
        
        #facing right = 1, left = -1
        self.facing = 1
        if self.sprite.flip == 'left': self.sprite.flipX()
        self.unRotate()
    
    def update(self):
        self.ecb.normalize()
        self.ecb.store()
        #Step one, push the input buffer
        self.input_buffer.push()
        self.last_input_frame += 1
        
        if self.hitstop > 0:

            self.hitstop -= 1 #Don't do anything this frame except reduce the hitstop time

            loop_count = 0
            while loop_count < 2:
                self.sprite.updatePosition(self.rect)
                self.ecb.normalize()
                bumped = False
                block_hit_list = collisionBox.getSizeCollisionsWith(self, self.game_state.platform_list)
                if not block_hit_list:
                    break
                for block in block_hit_list:
                    if block.solid or (self.platform_phase <= 0):
                        self.platform_phase = 0
                        if collisionBox.eject(self, block, self.platform_phase > 0):
                            bumped = True
                            break
                if not bumped:
                    break
                loop_count += 1

            self.sprite.updatePosition(self.rect)
            self.ecb.normalize()

            if not self.hitstop_vibration == (0,0):
                (x,y) = self.hitstop_vibration
                self.rect.x += x
                if not self.grounded: 
                    self.rect.y += y
                self.hitstop_vibration = (-x,-y)

            #Smash directional influence AKA hitstun shuffling
            di_vec = self.getSmoothedInput(int(self.key_bindings.timing_window['smoothing_window']))
            self.rect.x += di_vec[0]*5
            if not self.grounded or self.keysContain('jump', _threshold=1):
                self.rect.y += di_vec[1]*5

            self.sprite.updatePosition(self.rect)
            self.ecb.normalize()
        
            ground_blocks = self.checkGround()
            self.checkLeftWall()
            self.checkRightWall()
            self.checkCeiling()

            # Move with the platform
            block = reduce(lambda x, y: y if x is None or y.rect.top <= x.rect.top else x, ground_blocks, None)
            if not block is None:
                self.rect.x += block.change_x

            self.sprite.updatePosition(self.rect)

            self.hitbox_contact.clear()
            if self.invulnerable > -1000:
                self.invulnerable -= 1

            if self.platform_phase > 0:
                self.platform_phase -= 1
            self.ecb.normalize()
            return
        elif self.hitstop == 0 and not self.hitstop_vibration == (0,0):
            #self.hitstop_vibration = False #Lolwut?
            self.rect.center = self.hitstop_pos
            self.hitstop_vibration = (0,0)
            self.sprite.updatePosition(self.rect)
            self.ecb.normalize()
        #Step two, accelerate/decelerate
        if self.grounded: self.accel(self.var['friction'])
        else: self.accel(self.var['air_resistance'])
        
        if self.ledge_lock:
            ledges = pygame.sprite.spritecollide(self, self.game_state.platform_ledges, False)
            if len(ledges) == 0: # If we've cleared out of all of the ledges
                self.ledge_lock = False
        
        # Count down the tech window
        if self.tech_window > 0:
            if self.grounded:
                (direct,_) = self.getDirectionMagnitude()
                print('Ground tech!')
                self.unRotate()
                self.doAction('Prone')
                self.current_action.frame = self.current_action.last_frame
            self.tech_window -= 1

        # We set the hurbox to be the Bounding Rect of the sprite.
        # It is done here, so that the hurtbox can be changed by the action.
        self.hurtbox.rect = self.sprite.bounding_rect.copy()
        
        #Step three, change state and update
        self.current_action.stateTransitions(self)
        self.current_action.update(self) #update our action
        
        if self.mask:self.mask = self.mask.update()
        self.shield_integrity += 0.2
        if self.shield_integrity > 100: self.shield_integrity = 100
        #reset the flash if you're still invulnerable
        if not self.mask and (self.respawn_invulnerable > 0 or self.invulnerable > 0):
            self.createMask([255,255,255], max(self.respawn_invulnerable,self.invulnerable), True, 12)
        
        for art in self.articles:
            art.update()
            
            
        self.sprite.updatePosition(self.rect)
        self.ecb.normalize()

        # Gravity
        self.calcGrav()

        loop_count = 0
        while loop_count < 2:
            self.sprite.updatePosition(self.rect)
            self.ecb.normalize()
            bumped = False
            block_hit_list = collisionBox.getSizeCollisionsWith(self, self.game_state.platform_list)
            if not block_hit_list:
                break
            for block in block_hit_list:
                if block.solid or (self.platform_phase <= 0):
                    self.platform_phase = 0
                    if collisionBox.eject(self, block, self.platform_phase > 0):
                        bumped = True
                        break
            if not bumped:
                break
            loop_count += 1
        # TODO: Crush death if loopcount reaches the 10 resolution attempt ceiling

        self.sprite.updatePosition(self.rect)
        self.ecb.normalize()

        future_rect = self.ecb.current_ecb.rect.copy()
        future_rect.x += self.change_x
        future_rect.y += self.change_y

        t = 1

        to_bounce_block = None

        self.sprite.updatePosition(self.rect)
        self.ecb.normalize()
        block_hit_list = collisionBox.getMovementCollisionsWith(self, self.game_state.platform_list)
        for block in block_hit_list:
            if collisionBox.pathRectIntersects(self.ecb.current_ecb.rect, future_rect, block.rect) > 0 and collisionBox.pathRectIntersects(self.ecb.current_ecb.rect, future_rect, block.rect) < t and collisionBox.catchMovement(self, block, self.platform_phase > 0): 
                t = collisionBox.pathRectIntersects(self.ecb.current_ecb.rect, future_rect, block.rect)
                to_bounce_block = block
                
        self.rect.y += self.change_y*t
        self.rect.x += self.change_x*t

        self.sprite.updatePosition(self.rect)
        self.ecb.normalize()
        
        ground_blocks = self.checkGround()
        self.checkLeftWall()
        self.checkRightWall()
        self.checkCeiling()

        # Move with the platform
        block = reduce(lambda x, y: y if x is None or y.rect.top <= x.rect.top else x, ground_blocks, None)
        if not block is None:
            self.rect.x += block.change_x
            self.change_y -= self.var['gravity']

        if to_bounce_block is not None:
            collisionBox.reflect(self, to_bounce_block)

        self.sprite.updatePosition(self.rect)

        self.hitbox_contact.clear()
        if self.invulnerable > -1000:
            self.invulnerable -= 1
        if self.respawn_invulnerable > -1000:
            self.respawn_invulnerable -= 1

        if self.platform_phase > 0:
            self.platform_phase -= 1

        self.ecb.normalize()
        
    """
    Change speed to get closer to the preferred speed without going over.
    xFactor - The factor by which to change xSpeed. Usually self.var['friction'] or self.var['air_resistance']
    """
    def accel(self,_xFactor):
        if self.change_x > self.preferred_xspeed: #if we're going too fast
            diff = self.change_x - self.preferred_xspeed
            self.change_x -= min(diff,_xFactor)
        elif self.change_x < self.preferred_xspeed: #if we're going too slow
            diff = self.preferred_xspeed - self.change_x
            self.change_x += min(diff,_xFactor)
    
    # Change ySpeed according to gravity.        
    def calcGrav(self, _multiplier=1):
        if self.change_y > self.preferred_yspeed:
            diff = self.change_y - self.preferred_yspeed
            self.change_y -= min(diff, _multiplier*self.var['gravity'])
        elif self.change_y < self.preferred_yspeed:
            diff = self.preferred_yspeed - self.change_y
            self.change_y += min(diff, _multiplier*self.var['gravity'])
        if self.grounded: self.jumps = self.var['jumps']

    def checkGround(self):
        self.sprite.updatePosition(self.rect)
        return collisionBox.checkGround(self, self.game_state.platform_list, self.tech_window <= 0)

    def checkLeftWall(self):
        self.sprite.updatePosition(self.rect)
        return collisionBox.checkLeftWall(self, self.game_state.platform_list, True)

    def checkRightWall(self):
        self.sprite.updatePosition(self.rect)
        return collisionBox.checkRightWall(self, self.game_state.platform_list, True)

    def checkBackWall(self):
        return collisionBox.checkBackWall(self, self.game_state.platform_list, True)

    def checkFrontWall(self):
        return collisionBox.checkFrontWall(self, self.game_state.platform_list, True)

    def checkCeiling(self):
        self.sprite.updatePosition(self.rect)
        return collisionBox.checkCeiling(self, self.game_state.platform_list, True)
    
    """
    A simple function that converts the facing variable into a direction in degrees.
    """
    def getFacingDirection(self):
        if self.facing == 1: return 0
        else: return 180

    def setGrabbing(self, _other):
        self.grabbing = _other
        _other.grabbed_by = self

    def isGrabbing(self):
        if self.grabbing is None:
            return False
        if self.grabbing and self.grabbing.grabbed_by == self:
            return True
        return False
        
########################################################
#                  ACTION SETTERS                      #
########################################################
    """
    These functions are meant to be overridden. They are
    provided so the baseActions can change the AbstractFighter's
    actions. If you've changed any of the base actions
    for the fighter (including adding a sprite change)
    override the corresponding method and have it set
    an instance of your overridden action.
    """

    def changeAction(self,_newAction):
        #print(self.player_num,self.current_action.name,_newAction.name)
        self.current_action.tearDown(self,_newAction)
        _newAction.setUp(self)
        self.current_action = _newAction
        
    
    def doAction(self,_actionName):
        if hasattr(self.actions,'loadAction'):
            action = self.actions.loadAction(_actionName)
            if action.last_frame > 0: self.changeAction(action)
            else: action.setUp(self)
        elif hasattr(self.actions, _actionName):
            class_ = getattr(self.actions,_actionName)
            action = class_()
            if action.last_frame > 0: self.changeAction(action)
            else: action.setUp(self)
            
    def getAction(self,_actionName):
        action = None
        if hasattr(self.actions,'loadAction'):
            action = self.actions.loadAction(_actionName)
        elif hasattr(self.actions, _actionName):
            class_ = getattr(self.actions,_actionName)
            action = class_()
        return action
            
    def hasAction(self,_actionName):
        if hasattr(self.actions,'hasAction'):
            return self.actions.hasAction(_actionName)
        else: return hasattr(self.actions, _actionName)
            
    def loadArticle(self,_articleName):
        print(self.article_loader,_articleName)
        
        if hasattr(self.article_loader, 'loadArticle'):
            return self.article_loader.loadArticle(_articleName)
        elif hasattr(self.article_loader, _articleName):
            class_ = getattr(self.article_loader, _articleName)
            return(class_(self)) 
                            
    def doGroundMove(self,_direction):
        if (self.facing == 1 and _direction == 180) or (self.facing == -1 and _direction == 0):
            self.flip()
        self.doAction('Move')
        
    def doDash(self,_direction):
        if (self.facing == 1 and _direction == 180) or (self.facing == -1 and _direction == 0):
            self.flip()
        self.doAction('Dash')
        
    def doGroundAttack(self):
        (key, invkey) = self.getForwardBackwardKeys()
        if self.keysContain(key):
            self.doAction('ForwardSmash') if self.checkSmash(key) else self.doAction('ForwardAttack') 
        elif self.keysContain(invkey):
            self.flip()
            self.doAction('ForwardSmash') if self.checkSmash(invkey) else self.doAction('ForwardAttack')
        elif self.keysContain('down'):
            self.doAction('DownSmash') if self.checkSmash('down') else self.doAction('DownAttack')
        elif self.keysContain('up'):
            self.doAction('UpSmash') if self.checkSmash('up') else self.doAction('UpAttack')
        else:
            self.doAction('NeutralAttack')
    
    def doAirAttack(self):
        (forward, backward) = self.getForwardBackwardKeys()
        if (self.keysContain(forward)):
            self.doAction('ForwardAir')
        elif (self.keysContain(backward)):
            self.doAction('BackAir')
        elif (self.keysContain('down')):
            self.doAction('DownAir')
        elif(self.keysContain('up')):
            self.doAction('UpAir')
        else: self.doAction('NeutralAir')
    
    def doGroundSpecial(self):
        (forward, backward) = self.getForwardBackwardKeys()
        if self.keysContain(forward):
            if self.hasAction('ForwardSpecial'): #If there's a ground/air version, do it
                self.doAction('ForwardSpecial')
            else: #If there is not a universal one, do a ground one
                self.doAction('ForwardGroundSpecial')
        elif self.keysContain(backward):
            self.flip()
            if self.hasAction('ForwardSpecial'):
                self.doAction('ForwardSpecial')
            else:
                self.doAction('ForwardGroundSpecial')
        elif (self.keysContain('down')):
            if self.hasAction('DownSpecial'):
                self.doAction('DownSpecial')
            else:
                self.doAction('DownGroundSpecial')
        elif (self.keysContain('up')):
            if self.hasAction('UpSpecial'):
                self.doAction('UpSpecial')
            else:
                self.doAction('UpGroundSpecial')
        else: 
            if self.hasAction('NeutralSpecial'):
                self.doAction('NeutralSpecial')
            else:
                self.doAction('NeutralGroundSpecial')
                
    def doAirSpecial(self):
        (forward, backward) = self.getForwardBackwardKeys()
        if self.keysContain(forward):
            if self.hasAction('ForwardSpecial'): #If there's a ground/air version, do it
                self.doAction('ForwardSpecial')
            else: #If there is not a universal one, do an air one
                self.doAction('ForwardAirSpecial')
        elif self.keysContain(backward):
            self.flip()
            if self.hasAction('ForwardSpecial'):
                self.doAction('ForwardSpecial')
            else:
                self.doAction('ForwardAirSpecial')
        elif (self.keysContain('down')):
            if self.hasAction('DownSpecial'):
                self.doAction('DownSpecial')
            else:
                self.doAction('DownAirSpecial')
        elif (self.keysContain('up')):
            if self.hasAction('UpSpecial'):
                self.doAction('UpSpecial')
            else:
                self.doAction('UpAirSpecial')
        else: 
            if self.hasAction('NeutralSpecial'):
                self.doAction('NeutralSpecial')
            else:
                self.doAction('NeutralAirSpecial')
    
    def doHitStun(self,_hitstun,_trajectory):
        self.doAction('HitStun')
        self.current_action.direction = _trajectory
        self.current_action.last_frame = _hitstun
        
    def doProne(self, _length):
        self.doAction('Prone')
        self.current_action.last_frame = _length

    def doShield(self, _newShield=True):
        self.doAction('Shield')
        self.current_action.new_shield = _newShield

    def doShieldStun(self, _length):
        self.doAction('ShieldStun')
        self.current_action.last_frame = _length
             
    def doLedgeGrab(self,_ledge):
        self.doAction('LedgeGrab')
        self.current_action.ledge = _ledge

    def doTrapped(self, _length):
        self.doAction('Trapped')
        self.current_action.last_frame = _length

    def doStunned(self, _length):
        self.doAction('Stunned')
        self.current_action.last_frame = _length

    def doGrabbed(self, _height):
        self.doAction('Grabbed')
        self.current_action.height = _height
    
########################################################
#                  STATE CHANGERS                      #
########################################################
    """
    These involve the game engine. They will likely be
    sufficient for your character implementation, although
    in a heavily modified game engine, these might no
    longer be relevant. Override only if you're changing
    the core functionality of the fighter system. Extend
    as you see fit, if you need to tweak sprites or
    set flags.
    """
    
    """
    Flip the fighter so he is now facint the other way.
    Also flips the sprite for you.
    """
    def flip(self):
        self.facing = -self.facing
        self.sprite.flipX()
    
    """
    Deal damage to the fighter.
    Checks to make sure the damage caps at 999.
    If you want to have higher damage, override this function and remove it.
    This function is called in the applyKnockback function, so you shouldn't
    need to call this function directly for normal attacks, although you can
    for things like poison, non-knockback attacks, etc.
    """ 
    def dealDamage(self, _damage):
        self.damage += float(math.floor(_damage))
        if self.damage >= 999:
            self.damage = 999
        if self.damage <= 0:
            self.damage = 0
    
    """
    Do Knockback to the fighter.
    
    damage - the damage dealt by the attack. This is used in some calculations, so it is applied here.
    kb - the base knockback of the attack.
    kbg - the knockback growth ratio of the attack.
    trajectory - the direction the attack sends the fighter, in degrees, with 0 being right, 90 being upward, 180 being left.
                 This is an absolute direction, irrelevant of either character's facing direction. Those tend to be taken
                 into consideration in the hitbox collision event itself, to allow the hitbox to also take in the attacker's
                 current state as well as the fighter receiving knockback.
    weight_influence - The degree to which weight influences knockback. Default value is 1, set to 0 to make knockback 
                 weight-independent, or to whatever other value you want to change the effect of weight on knockback. 
    hitstun_multiplier - The ratio of the knockback to the additional hitstun that the hit should inflict. Default value is 
                 2 for normal levels of hitstun. To disable flinching, set to 0. 
    base_hitstun - The minimum hitstun that the hit should inflict regardless of knockback. This also influences how much gravity and 
                 air resistance affect base knockback. 
    hitlag_multiplier - The ratio of normal calculated hitlag to the amount of hitlag the hit should inflict. This affects both 
                 attacker and target. 
    
    The knockback calculation is derived from the SSBWiki, and a bit of information from ColinJF and Amazing Ampharos on Smashboards,
    it is based off of Super Smash Bros. Brawl's knockback calculation, which is the one with the most information available (due to
    all the modding)
    """
    def applyKnockback(self, _damage, _kb, _kbg, _trajectory, _weightInfluence=1, _hitstunMultiplier=1, _baseHitstun=1, _hitlagMultiplier=1):
        self.hitstop = math.floor((_damage / 4.0 + 2)*_hitlagMultiplier)
        if self.grounded:
            self.hitstop_vibration = (3,0)
        else:
            self.hitstop_vibration = (0,3)
        self.hitstop_pos = self.rect.center
        
        p = float(self.damage)
        d = float(_damage)
        w = float(self.var['weight'])
        s = float(_kbg)
        b = float(_kb)

        # Thank you, ssbwiki!
        total_kb = (((((p/10.0) + (p*d)/20.0) * (200.0/(w*_weightInfluence+100))*1.4) + 5) * s) + b

        if _damage < self.flinch_damage_threshold or total_kb < self.flinch_knockback_threshold:
            self.dealDamage(_damage*self.armor_damage_multiplier)
            return 0

        di_vec = self.getSmoothedInput(int(self.key_bindings.timing_window['smoothing_window']))

        trajectory_vec = [math.cos(_trajectory/180*math.pi), math.sin(_trajectory/180*math.pi)]

        additional_kb = .5*_baseHitstun*math.sqrt(abs(trajectory_vec[0])*self.var['air_resistance']**2+abs(trajectory_vec[1])*self.var['gravity']**2)

        di_multiplier = 1+numpy.dot(di_vec, trajectory_vec)*.05
        _trajectory += numpy.cross(di_vec, trajectory_vec)*13.5

        hitstun_frames = math.floor((total_kb+additional_kb)*_hitstunMultiplier+_baseHitstun)
        
        if self.no_flinch_hits > 0:
            if hitstun_frames > 0.5:
                self.no_flinch_hits -= 1
            self.dealDamage(_damage*self.armor_damage_multiplier)
            return 0
        
        if hitstun_frames > 0.5:
            #If the current action is not hitstun or you're in hitstun, but there's not much of it left
            if not isinstance(self.current_action, baseActions.HitStun) or self.current_action.last_frame-self.current_action.frame <= hitstun_frames+15:
                self.setSpeed((total_kb+additional_kb)*di_multiplier, _trajectory)
                self.doHitStun(hitstun_frames, _trajectory)
        
        self.dealDamage(_damage)
        return math.floor((total_kb+additional_kb)*di_multiplier)

    def applyPushback(self, _kb, _trajectory, _hitlag):
        self.hitstop = math.floor(_hitlag)
        (x, y) = getXYFromDM(_trajectory, _kb)
        self.change_x += x
        if not self.grounded:
            self.change_y += y
    
    """
    Set the actor's speed. Instead of modifying the change_x and change_y values manually,
    this will calculate what they should be set at if you want to give a direction and
    magnitude instead.
    
    speed - the total speed you want the fighter to move
    direction - the angle of the speed vector, 0 being right, 90 being up, 180 being left.
    """
    def setSpeed(self,_speed,_direction):
        (x,y) = getXYFromDM(_direction,_speed)
        self.change_x = x
        self.change_y = y
        
    def rotateSprite(self,_direction):
        self.sprite.rotate(-1 * (90 - _direction)) 
            
    def unRotate(self):
        self.sprite.rotate()
        
    def die(self,_respawn = True):
        sfxlib = settingsManager.getSfx()
        if sfxlib.hasSound('death', self.name):
            self.playSound('death')
        
        self.damage = 0
        self.change_x = 0
        self.change_y = 0
        self.jumps = self.var['jumps']
        self.data_log.setData('Falls',1,lambda x,y: x+y)
        if self.hit_tagged != None:
            if hasattr(self.hit_tagged, 'data_log'):
                self.hit_tagged.data_log.setData('KOs',1,lambda x,y: x+y)
        
        if _respawn:
            if self.hit_tagged is not None:
                color = settingsManager.getSetting('playerColor' + str(self.hit_tagged.player_num))
            else:
                color = settingsManager.getSetting('playerColor' + str(self.player_num))
                
            self.initialize()
            for i in range(0, 19):
                next_hit_article = article.HitArticle(self, self.rect.center, 1, i*18, 30, 1.5, pygame.Color(color))
                self.articles.add(next_hit_article)
                next_hit_article = article.HitArticle(self, self.rect.center, 1, i*18+6, 60, 1.5, pygame.Color(color))
                self.articles.add(next_hit_article)
                next_hit_article = article.HitArticle(self, self.rect.center, 1, i*18+12, 90, 1.5, pygame.Color(color))
                self.articles.add(next_hit_article)
            self.rect.midbottom = self.game_state.spawn_locations[self.player_num]
            self.rect.bottom -= 200
            self.sprite.updatePosition(self.rect)
            self.ecb.normalize()
            self.ecb.store()
            self.createMask([255,255,255], 480, True, 12)
            self.respawn_invulnerable = 480
            self.doAction('Respawn')
        
    def changeSprite(self,_newSprite,_frame=0):
        self.sprite.changeImage(_newSprite)
        self.current_action.sprite_name = _newSprite
        if _frame != 0: self.sprite.changeSubImage(_frame)
        
    def changeSpriteImage(self,_frame,_loop=False):
        self.sprite.changeSubImage(_frame,_loop)
    
    """
    Play a sound effect. If the sound is not in the fighter's SFX library, it will play the base sound.
    @_sound - the name of the sound to be played 
    """
    def playSound(self,_sound):
        sfxlib = settingsManager.getSfx()
        if sfxlib.hasSound(_sound, self.name):
            sfxlib.playSound(_sound, self.name)
        else:
            sfxlib.playSound(_sound,'base')
    
    """
    Activates a hitbbox, adding it to your active_hitboxes list.
    @_hitbox - the hitbox to activate
    """
    def activateHitbox(self,_hitbox):
        self.active_hitboxes.add(_hitbox)
        _hitbox.activate()
        
    """
    This will "lock" the hitbox so that another hitbox with the same ID from the same fighter won't hit again.
    Returns true if it was successful, false if it already exists in the lock.
    
    hbox - the hitbox we are checking for
    """
    def lockHitbox(self,_hbox):
        #Check for invulnerability first
        if self.invulnerable > 0 or self.respawn_invulnerable > 0:
            return False

        #If the hitbox belongs to something, get tagged by it
        if not _hbox.owner is None:
            self.hit_tagged = _hbox.owner

        if _hbox.hitbox_lock is None:
            return False

        if _hbox.hitbox_lock in self.hitbox_lock:
            return False

        self.hitbox_lock.add(_hbox.hitbox_lock)
        return True
    
    def startShield(self):
        self.articles.add(article.ShieldArticle(settingsManager.createPath("sprites/melee_shield.png"),self))
        
    def shieldDamage(self,_damage,_knockback,_hitlagMultiplier):
        if self.shield_integrity > 0:
            self.shield_integrity -= _damage
            if _damage > 1:
                self.doAction('shieldStun')
                self.hitstop = math.floor((self.damage / 4.0 + 2.0)*_hitlagMultiplier)
                self.change_x = _knockback
                self.current_action.last_frame = math.floor(_damage*3/4.0)
        else:
            self.change_y = -15
            self.invincible = 20
            self.shield_integrity = 100
            self.doStunned(400)
    
    def updateLandingLag(self,_lag,_reset=False):
        if _reset: self.landing_lag = _lag
        else:
            if _lag > self.landing_lag: self.landing_lag = _lag
            
########################################################
#                 ENGINE FUNCTIONS                     #
########################################################
    """
    These functions are not meant to be overridden, and
    likely won't need to be extended. Most of these are
    input/output related, and shouldn't be trifled with.
    Many of them reference outside variables, so 
    functionality can be changed by tweaking those values.
    Edit at your own risk.
    """

    """
    Add a key to the buffer. This function should be adding
    to the buffer, and ONLY adding to the buffer. Any sort
    of calculations and state changes should probably be done
    in the stateTransitions function of the current action.
    """
    def keyPressed(self,_key):
        self.input_buffer.append((_key,1.0))
        self.keys_held[_key] = 1.0
        
    """
    As above, but opposite.
    """
    def keyReleased(self,_key):
        if _key in self.keys_held:
            self.input_buffer.append((_key,0))	
            del self.keys_held[_key]
            return True
        else: return False
    
    def joyButtonPressed(self,_pad,_button):
        # TODO: Check gamepad first
        self.keyPressed(_button)
                
    def joyButtonReleased(self,_pad,_button):
        # TODO: Check gamepad first
        self.keyReleased(_button)
        
    def joyAxisMotion(self,_pad,_axis):
        #TODO - Actually check if this the right gamePad
        value = round(_pad.get_axis(_axis),3) # We really only need three decimals of precision
        if abs(value) < 0.05: value = 0
        if value < 0: sign = '-'
        else: sign = '+'
        
        k = self.key_bindings.get('axis ' + str(_axis) + sign)
        self.input_buffer.append((k,value)) # This should hopefully append something along the line of ('left',0.8)
        self.keys_held[k] = value

    """
    Various wrappers for the InputBuffer function, each one corresponding to a kind of input. 
    """

    #A key press
    def keyBuffered(self, _key, _from = 1, _state = 0.1, _to = 0):
        if any(map(lambda k: _key in k and k[_key] >= _state,self.input_buffer.getLastNFrames(_from, _to))):
            self.last_input_frame = 0
            return True
        return False

    #A key tap (press, then release)
    def keyTapped(self, _key, _from = None, _state = 0.1, _to = 0):
        if _from is None:
            _from = max(min(int(self.key_bindings.timing_window['buffer_window']), self.last_input_frame), 1)
        down_frames = map(lambda k: _key in k and k[_key] >= _state, self.input_buffer.getLastNFrames(_from, _to))
        up_frames = map(lambda k: _key in k and k[_key] < _state, self.input_buffer.getLastNFrames(_from, _to))
        if not any(down_frames) or not any(up_frames):
            return False
        first_down_frame = reduce(lambda j, k: j if j != None else (k if down_frames[k] else None), range(len(down_frames)), None)
        last_up_frame = reduce(lambda j, k: k if up_frames[k] else j, range(len(up_frames)), None)
        if first_down_frame <= last_up_frame:
            self.last_input_frame = 0
            return True
        return False

    #A key press which hasn't been released yet
    def keyHeld(self, _key, _from = None, _state = 0.1, _to = 0):
        if _from is None:
            _from = max(min(int(self.key_bindings.timing_window['buffer_window']), self.last_input_frame), 1)
        down_frames = map(lambda k: _key in k and k[_key] >= _state, self.input_buffer.getLastNFrames(_from, _to))
        up_frames = map(lambda k: _key in k and k[_key] < _state, self.input_buffer.getLastNFrames(_from, _to))
        if not any(down_frames):
            return False
        if any(down_frames) and not any(up_frames):
            self.last_input_frame = 0
            return True
        first_down_frame = reduce(lambda j, k: j if j != None else (k if down_frames[k] else None), range(len(down_frames)), None)
        last_up_frame = reduce(lambda j, k: k if up_frames[k] else j, range(len(up_frames)), None)
        if first_down_frame > last_up_frame:
            self.last_input_frame = 0
            return True
        return False

    #If the button is still being held
    def keyUnreleased(self,_key):
        return _key in self.keys_held
    
    #A key release
    def keyUp(self, _key, _from = 1, _state = 0.1, _to = 0):
        if any(map(lambda k: _key in k and k[_key] < _state, self.input_buffer.getLastNFrames(_from, _to))):
            self.last_input_frame = 0
            return True
        return False

    #A key reinput (release, then press)
    def keyReinput(self, _key, _from = None, _state = 0.1, _to = 0):
        if _from is None:
            _from = max(min(int(self.key_bindings.timing_window['buffer_window']), self.last_input_frame), 1)
        up_frames = map(lambda k: _key in k and k[_key] < _state, self.input_buffer.getLastNFrames(_from, _to))
        down_frames = map(lambda k: _key in k and k[_key] >= _state, self.input_buffer.getLastNFrames(_from, _to))
        if not any(down_frames) or not any(down_frames):
            return False
        first_up_frame = reduce(lambda j, k: j if j != None else (k if up_frames[k] else None), range(len(up_frames)), None)
        last_down_frame = reduce(lambda j, k: k if down_frames[k] else j, range(len(down_frames)), None)
        if first_up_frame <= last_down_frame:
            self.last_input_frame = 0
            return True
        return False

    #A key release which hasn't been pressed yet
    def keyIdle(self, _key, _from = None, _state = 0.1, _to = 0):
        if _from is None:
            _from = max(min(int(self.key_bindings.timing_window['buffer_window']), self.last_input_frame), 1)
        up_frames = map(lambda k: _key in k and k[_key] < _state, self.input_buffer.getLastNFrames(_from, _to))
        down_frames = map(lambda k: _key in k and k[_key] >= _state, self.input_buffer.getLastNFrames(_from, _to))
        if not any(up_frames):
            return False
        if any(up_frames) and not any(down_frames):
            self.last_input_frame = 0
            return True
        first_up_frame = reduce(lambda j, k: j if j != None else (k if up_frames[k] else None), range(len(up_frames)), None)
        last_down_frame = reduce(lambda j, k: k if down_frames[k] else j, range(len(down_frames)), None)
        if first_up_frame > last_down_frame:
            self.last_input_frame = 0
            return True
        return False

    #Analog directional input
    def getSmoothedInput(self, _distanceBack = None, _maxMagnitude = 1.0):
        #TODO If this is a gamepad, simply return its analog input
        if _distanceBack is None:
            smooth_distance = int(self.key_bindings.timing_window['smoothing_window'])
            _distanceBack = max(min(int(self.key_bindings.timing_window['smoothing_window']), self.last_input_frame), 1)
        else:
            smooth_distance = _distanceBack
        
        hold_buffer = reversed(self.input_buffer.getLastNFrames(_distanceBack))
        smoothed_x = 0.0
        smoothed_y = 0.0
        for frame_input in hold_buffer:
            working_x = 0.0
            working_y = 0.0
            x_decay = float(1.5)/smooth_distance
            y_decay = float(1.5)/smooth_distance
            if 'left' in frame_input: working_x -= frame_input['left']
            if 'right' in frame_input: working_x += frame_input['right']
            if 'up' in frame_input: working_y -= frame_input['up']
            if 'down' in frame_input: working_y += frame_input['down']
            if (working_x > 0 and smoothed_x > 0) or (working_x < 0 and smoothed_x < 0):
                x_decay = float(1)/smooth_distance
            elif (working_x < 0 and smoothed_x > 0) or (working_x > 0 and smoothed_x < 0):
                x_decay = float(4)/smooth_distance
            if (working_y < 0 and smoothed_y < 0) or (working_y > 0 and smoothed_y > 0):
                y_decay = float(1)/smooth_distance
            elif (working_y < 0 and smoothed_y > 0) or (working_y > 0 and smoothed_y < 0):
                ySmooth = float(4)/smooth_distance
            magnitude = numpy.linalg.norm([working_x, working_y])
            if magnitude > _maxMagnitude:
                working_x /= magnitude/_maxMagnitude
                working_y /= magnitude/_maxMagnitude
            if smoothed_x > 0:
                smoothed_x -= x_decay
                if smoothed_x < 0:
                    smoothed_x = 0
            elif smoothed_x < 0:
                smoothed_x += x_decay
                if smoothed_x > 0:
                    smoothed_x = 0
            if smoothed_y > 0:
                smoothed_y -= y_decay
                if smoothed_y < 0:
                    smoothed_y = 0
            elif smoothed_y < 0:
                smoothed_y += y_decay
                if smoothed_y > 0:
                    smoothed_y = 0
            smoothed_x += working_x
            smoothed_y += working_y

        final_magnitude = numpy.linalg.norm([smoothed_x, smoothed_y])
        if final_magnitude > 0: self.last_input_frame = 0
        if final_magnitude > _maxMagnitude:
            smoothed_x /= final_magnitude/_maxMagnitude
            smoothed_y /= final_magnitude/_maxMagnitude
        return [smoothed_x, smoothed_y]
        
    
    """
    This function checks if the player has Smashed in a direction. It does this by noting if the direction was
    pressed recently and is now above a threshold
    """
    def checkSmash(self,_direction):
        #TODO different for buttons than joysticks
        return self.keyBuffered(_direction, int(self.key_bindings.timing_window['smash_window']), 1.0)
    
    """
    This checks for keys that are currently being held, whether or not they've actually been pressed recently.
    This is used, for example, to transition from a landing state into a running one. Using the InputBuffer
    would mean that you'd either need to iterate over the WHOLE buffer and look for one less release than press,
    or limit yourself to having to press the button before landing, whether you were moving in the air or not.
    If you are looking for a button PRESS, use one of the input methods provided. If you are looking for IF A KEY 
    IS STILL BEING HELD, this is your function.
    """
    def keysContain(self,_key,_threshold=0.1):
        if _key in self.keys_held:
            return self.keys_held[_key] >= _threshold
        return False
    
    """
    This returns a tuple of the key for forward, then backward
    Useful for checking if the fighter is pivoting, or doing a back air, or getting the
    proper key to dash-dance, etc.
    
    The best way to use this is something like
    (key,invkey) = actor.getForwardBackwardKeys()
    which will assign the variable "key" to the forward key, and "invkey" to the backward key.
    """
    def getForwardBackwardKeys(self):
        if self.facing == 1: return ('right','left')
        else: return ('left','right')
        
    def draw(self,_screen,_offset,_scale):
        if (settingsManager.getSetting('showSpriteArea')): spriteManager.RectSprite(self.rect).draw(_screen, _offset, _scale)
        rect = self.sprite.draw(_screen,_offset,_scale)
        
        if self.mask: self.mask.draw(_screen,_offset,_scale)
        if settingsManager.getSetting('showECB'): self.ecb.draw(_screen,_offset,_scale)
        return rect
        
    """
    Use this function to get a direction that is angled from the direction the fighter
    is facing, rather than angled from right. For example, sending the opponent 30 degrees
    is fine when facing right, but if you're facing left, you'd still be sending them to the right!
    
    Hitboxes use this calculation a lot. It'll return the proper angle that is the given offset
    from "forward". Defaults to 0, which will give either 0 or 180, depending on the direction
    of the fighter.
    """
    def getForwardWithOffset(self,_offSet = 0):
        if self.facing == 1:
            return _offSet
        else:
            return 180 - _offSet

    def createMask(self,_color,_duration,_pulse = False,_pulse_size = 16):
        self.mask = spriteManager.MaskSprite(self.sprite,_color,_duration,_pulse, _pulse_size)
        
    def getDirectionMagnitude(self):
        if self.change_x == 0:
            magnitude = self.change_y
            direction = 90 if self.change_y < 0 else 270
            return (direction,magnitude)
        if self.change_y == 0:
            magnitude = self.change_x
            direction = 0 if self.change_x > 0 else 180
            return(direction,magnitude)
        
        direction = math.degrees(math.atan2(-self.change_y, self.change_x))
        direction = round(direction)
        magnitude = numpy.linalg.norm([self.change_x, self.change_y])
        
        return (direction,magnitude)
        
########################################################
#             STATIC HELPER FUNCTIONS                  #
########################################################
# Functions that don't require a fighter instance to use
        
"""
A helper function to get the X and Y magnitudes from the Direction and Magnitude of a trajectory
"""
def getXYFromDM(_direction,_magnitude):
    rad = math.radians(_direction)
    x = round(math.cos(rad) * _magnitude,5)
    y = -round(math.sin(rad) * _magnitude,5)
    return (x,y)

"""
Get the direction between two points. 0 means the second point is to the right of the first,
90 is straight above, 180 is straight left. Used in some knockback calculations.
"""

def getDirectionBetweenPoints(_p1, _p2):
    (x1, y1) = _p1
    (x2, y2) = _p2
    dx = x2 - x1
    dy = y1 - y2
    return (180 * math.atan2(dy, dx)) / math.pi 
        
########################################################
#                  INPUT BUFFER                        #
########################################################        
"""
The input buffer is a list of all of the buttons pressed and released,
and the frames they're put in on. It's used to check for buttons that
were pressed in the past, such as for a wall tech, or a buffered jump,
but can also be used to re-create the entire battle (once a replay manager
is set up)
"""
class InputBuffer():
    
    def __init__(self):
        self.buffer = [[]]
        self.working_buff = []
        self.last_index = 0
      
    """
    Pushes the buttons for the frame into the buffer, then extends the index by one.
    """
    def push(self):
        self.buffer.append(dict(self.working_buff))
        self.working_buff = []
        self.last_index += 1
                
    """
    Get a sub-buffer of N frames
    """
    def getLastNFrames(self,_from,_to=0):
        ret_buffer = []
        if _from > self.last_index: _from = self.last_index
        if _to > self.last_index: _to = self.last_index
        for i in range(self.last_index - _to,self.last_index - _from,-1):
            ret_buffer.append(self.buffer[i - _to])
        return ret_buffer
    
    """
    put a key into the current working buffer. The working buffer is all of the inputs for
    one frame, before the frame is actually executed.
    """
    def append(self,_key):
        self.working_buff.append(_key)

