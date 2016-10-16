import settingsManager
import pygame
import xml.etree.ElementTree as ElementTree
import xml.dom.minidom
import os
import engine.baseActions as baseActions
import engine.collisionBox as collisionBox
import weakref
import engine.hitbox as hitbox
import math
import numpy
import spriteManager
import engine.article as article
import engine.controller as controller
import engine.actionLoader as actionLoader
import engine.articleLoader
from global_functions import *

class AbstractFighter():
    """The Abstract Fighter is an individual fighter in the battle. It holds all of the data
    needed to create, control, and clear a fighter. It is created initially by the Character Select Screen,
    as a container for things like icons and costume selections. It becomes a 'real' fighter when Initialize()
    is called, creating an object that can interact with the world.
    """
    
    # Top Level fighter variables #
    base_dir = ''
    player_num = 0
    xml_data = None
    
    # Data loaded from XML #
    name = 'Null'
    franchise_icon_path = 'sprites/default_franchise_icon.png'
    css_icon_path = './sprites/icon_unknown.png'
    css_portrait_path =''
    
    sprite_directory = 'sprites/'
    sprite_prefix = ''
    sprite_width = 64
    default_sprite = 'sandbag_idle'
    sprite = None
    
    article_sprite_path = ''
    article_file = ''
    
    sound_path = ''
    
    actions_file = baseActions.__file__
    
    default_stats = {
                'weight': 100,
                'gravity': .5,
                'max_fall_speed': 20.0,
                'max_ground_speed': 7.0,
                'run_speed': 11.0,
                'max_air_speed': 5.5,
                'aerial_transition_speed': 9.0,
                'crawl_speed': 0.0,
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
                'wavedash_lag': 12,
                'fastfall_multiplier': 2.0,
                'hitstun_elasticity': .8,
                'shield_size': 1.0
                }
    
    default_vars = dict()
    
    # Data gotten from the XML data, like loading files and folders #
    actions = baseActions
    stats = dict()
    vars = dict()
    
    # Initialized fighter variables #
    key_bindings = None
    
    active_hitboxes = pygame.sprite.Group()
    articles = pygame.sprite.Group()
    active_hurtboxes = pygame.sprite.Group()
    auto_hurtbox = None
    
    shield = False
    shield_integrity = 100    
        
    input_buffer = controller.InputBuffer()
    last_input_frame = 0
    keys_held = dict()
    
    hitbox_lock = weakref.WeakSet()
    hitbox_contact = set()
    
    ledge_lock = False
        
    mask = None
    
    hit_tagged = None
     
    angle = 0
    grounded = False
    back_walled = False
    front_walled = False
    ceilinged = False
    jumps = 0
    damage = 0
    landing_lag = 6
    platform_phase = 0
    tech_window = 0
    airdodges = 1
    
    change_x = 0
    change_y = 0
    preferred_xspeed = 0
    preferred_yspeed = 0
    trail_color = "#000000"
    
    #facing right = 1, left = -1
    facing = 1
    
    #Adding a move to the disabled moves list prevents it from activating.
    #If told to switch to it, the fighter will ignore the request.
    disabled_moves = []
    
    invulnerable = 0
    respawn_invulnerable = 0
    
    hitstop = 0
    hitstop_vibration = (0,0)
    hitstop_pos = (0,0)
        
    custom_timers = list()
    
    current_color = 0
    current_costume = 0
    
    css_icon = spriteManager.ImageSprite(settingsManager.createPath('sprites/icon_unknown.png'))
    
    color_palettes = []
    palette_display = []
    
    def __init__(self,_baseDir,_playerNum):
        """ Create a fighter. To start, all that's needed is the directory it is in, and the player number.
        It uses the directory to find its fighter.xml file and begin storing data.
        
        Parameters
        -----------
        _baseDir : string
            The filepath of the folder being loaded. Used to determine the location of fighter.xml, icons, and sprites
        _playerNum: int
            The number of the controlling player. 0-indexed, so Player 1 is number 0
        """
        def loadNodeWithDefault(_tag,_default):
            """ An anonymous inner function to quickly pull from XML, giving a default value if the node
            is not present or otherwise can't be loaded.
            
            Parameters
            -----------
            _node : Element
                The XML tree to be searching from. The node directly above the one you're looking for.
            _tag : string
                The name of the XML tag to search for
            _default : any type
                the default value of the node, in case it cannot find the proper value
            
            Return
            -----------
            The string value of the Node, or the given default if it is not valid
            """
            
            if self.xml_data:
                if self.xml_data.find(_tag) is not None:
                    if self.xml_data.find(_tag).text is None:
                        return _default
                    else: return self.xml_data.find(_tag).text
            return _default
        
        self.base_dir = _baseDir
        self.player_num = _playerNum
        
        #Load the xml data if fighter.xml exists
        if os.path.exists(os.path.join(self.base_dir,'fighter.xml')):
            self.xml_data = ElementTree.parse(os.path.join(_baseDir,'fighter.xml')).getroot()
        else: self.xml_data = ElementTree.ElementTree().getroot()
        
        #Load the CSS info
        self.name = loadNodeWithDefault('name', self.name)
        self.franchise_icon_path = loadNodeWithDefault('icon', self.franchise_icon_path)
        self.css_icon_path = loadNodeWithDefault('css_icon', self.css_icon_path)
        self.css_portrait_path = loadNodeWithDefault('css_portrait', self.css_portrait_path)
        
        #Load the sprite info
        self.sprite_directory = loadNodeWithDefault('sprite_directory', os.path.join(self.base_dir,'sprites/'))
        self.sprite_prefix = loadNodeWithDefault('sprite_prefix', self.sprite_prefix)
        self.sprite_width = int(loadNodeWithDefault('sprite_width', self.sprite_width))
        self.default_sprite = loadNodeWithDefault('default_sprite', self.default_sprite)
        
        #Load the article info
        self.article_sprite_path = loadNodeWithDefault('article_path', self.article_sprite_path)
        self.article_file = loadNodeWithDefault('articles', self.article_file)
        
        #Load sounds
        self.sound_path = loadNodeWithDefault('sound_path', self.sound_path)
        
        #Load actions
        self.actions_file = loadNodeWithDefault('actions', self.actions_file)
        
        #Load the article loader
        self.article_path_short = loadNodeWithDefault('article_path', '')
        self.article_path = os.path.join(self.base_dir,self.article_path_short)
        self.article_loader_path = loadNodeWithDefault('articles', None)
        
        if self.article_loader_path == '':
            self.article_loader = None
        else:
            self.article_loader = engine.articleLoader.ArticleLoader(self)
        
        
        #TODO color palettes
        for color_palette in self.xml_data.findall('color_palette'):
            color_dict = {}
            for color_map in color_palette.findall('color_map'):
                from_color = pygame.Color(color_map.attrib['from_color'])
                to_color = pygame.Color(color_map.attrib['to_color'])
                color_dict[(from_color.r, from_color.g, from_color.b)] = (to_color.r, to_color.g, to_color.b)
            
            self.color_palettes.append(color_dict)
            self.palette_display.append(pygame.Color(color_palette.attrib['displayColor']))
        
        while len(self.color_palettes) < 4:
            self.color_palettes.append({})
        
        self.costumes = [self.sprite_prefix]
        for costume in self.xml_data.findall('costume'):
            self.costumes.append(costume.text)
         
        if self.xml_data:
            if self.xml_data.find('stats') is not None:
                for stat in self.xml_data.find('stats'):
                    vartype = type(self.default_stats[stat.tag]).__name__
                    if vartype == 'int': self.default_stats[stat.tag] = int(stat.text)
                    if vartype == 'float': self.default_stats[stat.tag] = float(stat.text)
            
            if self.xml_data.find('variables') is not None:
                for variable in self.xml_data.find('variables'):
                    vartype = 'string'
                    if variable.attrib.has_key('type'): vartype = variable.attrib['type']
                    val = variable.text
                    if vartype == 'int': val = int(val)
                    elif vartype == 'float': val = float(val)
                    elif vartype == 'bool': val = bool(val)
                    self.default_vars[variable.tag] = val
        
        self.current_color = self.player_num
          
        # Now that we've got all the paths, need to actually load the files
        if self.css_icon_path[0] == '.': #If the path starts with a period, start from the top of the game directory instead
            self.css_icon = spriteManager.ImageSprite(settingsManager.createPath(self.css_icon_path))
        else:
            self.css_icon = spriteManager.ImageSprite(os.path.join(self.base_dir,self.css_icon_path))
        
        if self.franchise_icon_path[0] == '.': #If the path starts with a period, start from the top of the game directory instead
            self.franchise_icon = spriteManager.ImageSprite(settingsManager.createPath(self.franchise_icon_path))
        else:
            self.franchise_icon = spriteManager.ImageSprite(os.path.join(self.base_dir,self.franchise_icon_path))
        
        #TODO: The ECB crashes unless there is a sprite to pull from, so we load this one even though it'll never actually be drawn
        spriteName = self.sprite_prefix + self.default_sprite + '.png'
        self.sprite = spriteManager.SheetSprite(os.path.join(self.base_dir,self.sprite_directory,spriteName), self.sprite_width)
        self.rect = self.sprite.rect
        
        try:
            if self.actions_file.endswith('.py'):
                self.actions = settingsManager.importFromURI(os.path.join(_baseDir,'fighter.xml'),self.actions_file,_suffix=str(self.player_num))
            else:
                self.actions = actionLoader.ActionLoader(_baseDir,self.actions_file)
        except:
            self.actions = baseActions
            self.action_file = baseActions.__file__
        
        if self.sound_path:
            settingsManager.getSfx().addSoundsFromDirectory(os.path.join(self.base_dir,self.sound_path), self.name)
        
    def saveFighter(self,_path=None):
        """ Save the fighter's data to XML. Basically the inverse of __init__.
        
        Parameters
        -----------
        _path : string
            The path to store the fighter.xml file in. If left blank, it will use base_dir.
        """
        def createElement(_tag,_val):
            """ An anonymouse inner function for quickly creating an XML element with a value.
            
            Parameters
            -----------
            _tag : The XML tag of the element
            _val : The data to go into the element
            """
            elem = ElementTree.Element(_tag)
            if _val is not None:
                elem.text = str(_val)
            else: elem.text = ''
            return elem
        
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
        
        for costume in self.costumes:
            if not costume == self.sprite_prefix:
                tree.append(self.createElement('costume', costume))
            
        for tag,val in self.stats.iteritems():
            stats_elem.append(self.createElement(tag, val))
        tree.append(stats_elem)
        
        xmlfile = xml.dom.minidom.parseString(ElementTree.tostring(tree))
        outputFile = open(_path,'w')
        outputFile.write(xmlfile.toprettyxml())
    
    def loadSpriteLibrary(self,_color=None):
        """ Loads the sprite library for the fighter, with the current
        costume and color.
        
        Parameters
        -----------
        _color : int
            The index of the color to use. By default, will use the stored current_color variable,
            which is set while selecting. This optional argument should be used when you're overriding
            the game's color choice to load up a different palette.
        """
        directory = os.path.join(self.base_dir,self.sprite_directory)
        try:
            scale = float(self.xml_data.find('scale').text)
        except:
            scale = 1.0
        
        if _color == None: _color = self.current_color
        
        self.sprite = spriteManager.SpriteHandler(str(directory),
                                                  self.costumes[self.current_costume % len(self.costumes)],
                                                  self.default_sprite,
                                                  self.sprite_width,
                                                  self.color_palettes[_color % len(self.color_palettes)],
                                                  scale)
        self.rect = self.sprite.rect
    
    def initialize(self):
        """ This method is called when shit gets real. It creates the collision box, sprite library,
        etc. and is ready to start getting updates and doing actions. No parameters, no return value.
        Converts this object into an Initialized Fighter Object.
        """
        
        """ Initialize components """
        # Initialize key bindings object
        self.key_bindings = settingsManager.getControls(self.player_num)
        self.key_bindings.linkObject(self)
        self.key_bindings.flushInputs()
        
        # Evironmental Collision Box
        self.ecb = collisionBox.ECB(self)
        
        # Hitboxes and Hurtboxes
        self.auto_hurtbox = hitbox.Hurtbox(self)
        
        if self.sound_path:
            settingsManager.getSfx().addSoundsFromDirectory(self.sound_path, self.name)
        
        #initialize the action
        if hasattr(self.actions,'loadAction'):
            self.current_action = self.actions.loadAction('NeutralAction')
        elif hasattr(self.actions, 'NeutralAction'):
            class_ = getattr(self.actions,'NeutralAction')
            self.current_action = class_()

        self.stats = self.default_stats.copy()
        self.vars = self.default_vars.copy()
        
        self.jumps = self.stats['jumps']
        
        self.trail_color = settingsManager.getSetting('playerColor' + str(self.player_num))
        
        if self.sprite.flip == 'left': self.sprite.flipX()
        self.unRotate()   
    
        
    ########################################################
    #                   UPDATE METHODS                     #
    ########################################################
    
    def update(self):
        """ This method will step the fighter forward one frame. It will resolve movement,
        collisions, animations, and all sorts of things. It should be called every frame.
        """ 
        self.ecb.normalize()
        self.ecb.store()
        
        self.input_buffer.push()
        self.last_input_frame += 1
        
        if self.hitstop > 0:
            #We're in hitstop, let's take care of that and ignore a normal update
            self.hitstopUpdate()
            return
        elif self.hitstop == 0 and not self.hitstop_vibration == (0,0):
            #self.hitstop_vibration = False #Lolwut?
            self.rect.center = self.hitstop_pos
            self.hitstop_vibration = (0,0)
            self.sprite.updatePosition(self.rect)
            self.ecb.normalize()
        
        # Allow ledge re-grabs if we've vacated a ledge
        if self.ledge_lock:
            ledges = pygame.sprite.spritecollide(self, self.game_state.platform_ledges, False)
            if len(ledges) == 0: # If we've cleared out of all of the ledges
                self.ledge_lock = False
        
        # Prepare for movement by setting change_x and change_y from acceleration
        if self.grounded: self.accel(self.stats['friction'])
        else: self.accel(self.stats['air_resistance'])
        self.calcGrav()
        
        # Check for transitions, then execute actions
        self.current_action.stateTransitions(self)
        self.current_action.update(self) #update our action
        
        self.sprite.updatePosition(self.rect)
        self.ecb.normalize()
        self.ecb.normalize()
        
        self.collisionUpdate()            
        self.childUpdate()
        self.timerUpdate()
        
    def collisionUpdate(self):
        """ Execute movement and resolve collisions.
        This function is due for a huge overhaul.
        """
        
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
            self.change_y -= self.stats['gravity'] * settingsManager.getSetting('gravity')

        if to_bounce_block is not None:
            collisionBox.reflect(self, to_bounce_block)

    def childUpdate(self):
        """ The fighter contains many child objects, that all need to be updated.
        This function calls those updates.
        """
        if self.mask:self.mask = self.mask.update()
        
        #reset the flash if you're still invulnerable
        if not self.mask and (self.respawn_invulnerable > 0 or self.invulnerable > 0):
            self.createMask([255,255,255], max(self.respawn_invulnerable,self.invulnerable), True, 12)
        
        for art in self.articles:
            art.update()
        
        
    def timerUpdate(self):
        """ There are several frame counters that determine things like teching, invulnerability,
        platform phasing, etc. as well as possible custom timers.
        """
        #These max calls will decrement the window, but not below 0
        self.tech_window = max(0,self.tech_window-1)
        self.shield_integrity = min(100,self.shield_integrity+0.15)
        self.platform_phase = max(0,self.platform_phase-1)
        
        #QUESTION: Why -1000?
        self.invulnerable = max(-1000,self.invulnerable-1)
        self.respawn_invulnerable = max(-1000,self.invulnerable-1)
        
        finished_timers = []
        for timer in self.custom_timers:
            time,event = timer
            time -= 1
            if time <= 0:
                for subact in event:
                    subact.execute(self,self.current_action)
                #In order to avoid mucking up the iterative loop, we store finished timers to remove later
                finished_timers.append(timer)
                
        for timer in finished_timers:
            self.custom_timers.remove(timer)
        
    def hitstopUpdate(self):
        """ Handles what to do if the fighter is in hitstop (that freeze frame state when you
        get hit). Vibrates the fighter's sprite, and handles SDI
        """
        self.hitstop -= 1

        loop_count = 0
        
        #QUESTION: Why is this a loop?
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

        # Vibrate the sprite
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

    def draw(self,_screen,_offset,_scale):
        if (settingsManager.getSetting('showSpriteArea')): spriteManager.RectSprite(self.rect).draw(_screen, _offset, _scale)
        rect = self.sprite.draw(_screen,_offset,_scale)
        
        if self.mask: self.mask.draw(_screen,_offset,_scale)
        if settingsManager.getSetting('showECB'): 
            for ecb in self.active_hurtboxes:
                ecb.draw(_screen,_offset,_scale)
        return rect
    ########################################################
    #                 ACTION MANAGEMENT                    #
    ########################################################
    
    def doAction(self,_actionName):
        """ Load up the given action. If it's executable, change to it.
        If it's not, still execute the setUp (this allows for certain code
        to happen, even if the action is not executed.)
        
        If the move is disabled, it won't even bother to
        load it, since we shouldn't be doing anything with it.
        
        Parameters
        -----------
        _actionName : String
            The Action to load and switch to
        """
        if not _actionName in self.disabled_moves:
            # If our action is an ActionLoader, we need to pull it from XML
            if hasattr(self.actions,'loadAction'):
                action = self.actions.loadAction(_actionName)
                if action.last_frame > 0: self.changeAction(action)
                else: action.setUp(self)
            # If it has an object of the given name, get that object
            elif hasattr(self.actions, _actionName):
                class_ = getattr(self.actions,_actionName)
                action = class_()
                if action.last_frame > 0: self.changeAction(action)
                else: action.setUp(self)
    
    def changeAction(self,_newAction):
        """ Switches from the current action to the given action. Calls tearDown on the
        current action, before setting up the new one. If we get this far, the new action
        is valid and ready to be executed
        
        Parameters
        -----------
        _newAction : Action
            The Action to switch to
        """
        self.current_action.tearDown(self,_newAction)
        _newAction.setUp(self)
        self.current_action = _newAction
    
    def getAction(self,_actionName):
        """ Loads an action, without changing to it or executing it.
        Since this is just to read, it will load an action that is
        disabled, or unexecutable. If you need to change to it, please
        use doAction instead, which will make sure the action is valid
        before executing.
        
        Parameters
        -----------
        _actionName : String
            The name of the action to load
        
        Return
        -----------
        Action : The loaded action with the given name. Returns None
                 if there is no action with that name.
        """
        action = None
        if hasattr(self.actions,'loadAction'):
            action = self.actions.loadAction(_actionName)
        elif hasattr(self.actions, _actionName):
            class_ = getattr(self.actions,_actionName)
            action = class_()
        return action
            
    def hasAction(self,_actionName):
        """ Returns True if the fighter has an action of the given name.
        Does not load the action, change to it, or do anything other than
        check if it exists. You do not need to run this before getAction or
        doAction, as they check for the action themselves.
        
        Parameters
        -----------
        _actionName : String
            The name of the action to check for
        """
        if hasattr(self.actions,'hasAction'):
            return self.actions.hasAction(_actionName)
        else: return hasattr(self.actions, _actionName)
            
    def loadArticle(self,_articleName):
        """ Loads and returns an article. Checks if the articles are loading
        from XML or Python, and loads the appropriate one.
        
        Parameters
        -----------
        _articleName : String
            The name of the article to load
            
        Return
        -----------
        Article : The article of the given name. Returns None if no Article with that name exists.
        """        
        if hasattr(self.article_loader, 'loadArticle'):
            return self.article_loader.loadArticle(_articleName)
        elif hasattr(self.article_loader, _articleName):
            class_ = getattr(self.article_loader, _articleName)
            return(class_(self))
    
    
    """ All of this stuff below should probably be rewritten or find a way to be removed """
    
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
        direct = self.netDirection([key, invkey, 'down', 'up'])
        if direct == key:
            self.doAction('ForwardSmash') if self.checkSmash(key) else self.doAction('ForwardAttack') 
        elif direct == invkey:
            self.flip()
            self.doAction('ForwardSmash') if self.checkSmash(invkey) else self.doAction('ForwardAttack')
        elif direct == 'down':
            self.doAction('DownSmash') if self.checkSmash('down') else self.doAction('DownAttack')
        elif direct == 'up':
            self.doAction('UpSmash') if self.checkSmash('up') else self.doAction('UpAttack')
        else:
            self.doAction('NeutralAttack')
    
    def doAirAttack(self):
        (forward, backward) = self.getForwardBackwardKeys()
        direct = self.netDirection([forward, backward, 'down', 'up'])
        if direct == forward:
            self.doAction('ForwardAir')
        elif direct == backward:
            self.doAction('BackAir')
        elif direct == 'down':
            self.doAction('DownAir')
        elif direct == 'up':
            self.doAction('UpAir')
        else: self.doAction('NeutralAir')
    
    def doGroundSpecial(self):
        (forward, backward) = self.getForwardBackwardKeys()
        direct = self.netDirection(['up', forward, backward, 'down'])
        if direct == 'up':
            if self.hasAction('UpSpecial'):
                self.doAction('UpSpecial')
            else:
                self.doAction('UpGroundSpecial')
        elif direct == forward:
            if self.hasAction('ForwardSpecial'): #If there's a ground/air version, do it
                self.doAction('ForwardSpecial')
            else: #If there is not a universal one, do a ground one
                self.doAction('ForwardGroundSpecial')
        elif direct == backward:
            self.flip()
            if self.hasAction('ForwardSpecial'):
                self.doAction('ForwardSpecial')
            else:
                self.doAction('ForwardGroundSpecial')
        elif direct == 'down':
            if self.hasAction('DownSpecial'):
                self.doAction('DownSpecial')
            else:
                self.doAction('DownGroundSpecial')
        else: 
            if self.hasAction('NeutralSpecial'):
                self.doAction('NeutralSpecial')
            else:
                self.doAction('NeutralGroundSpecial')
                
    def doAirSpecial(self):
        (forward, backward) = self.getForwardBackwardKeys()
        direct = self.netDirection(['up', forward, backward, 'down'])
        if direct == 'up':
            if self.hasAction('UpSpecial'):
                self.doAction('UpSpecial')
            else:
                self.doAction('UpAirSpecial')
        elif direct == forward:
            if self.hasAction('ForwardSpecial'): #If there's a ground/air version, do it
                self.doAction('ForwardSpecial')
            else: #If there is not a universal one, do an air one
                self.doAction('ForwardAirSpecial')
        elif direct == backward:
            self.flip()
            if self.hasAction('ForwardSpecial'):
                self.doAction('ForwardSpecial')
            else:
                self.doAction('ForwardAirSpecial')
        elif direct == 'down':
            if self.hasAction('DownSpecial'):
                self.doAction('DownSpecial')
            else:
                self.doAction('DownAirSpecial')
        else: 
            if self.hasAction('NeutralSpecial'):
                self.doAction('NeutralSpecial')
            else:
                self.doAction('NeutralAirSpecial')

    def doTech(self):
        (forward, backward) = self.getForwardBackwardKeys()
        direct = self.netDirection([forward, backward, 'down', 'up'])
        if direct == forward:
            self.doAction('ForwardTech')
        elif direct == backward:
            self.doAction('BackwardTech')
        elif direct == 'down':
            self.doAction('DodgeTech')
        else:
            if self.hasAction('NormalTech'):
                self.doAction('NormalTech')
            else:
                self.doAction('Getup')
    
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
    #              COLLISIONS AND MOVEMENT                 #
    ########################################################
    def accel(self,_xFactor):
        """ Change speed to get closer to the preferred speed without going over.
        
        Parameters
        -----------
        _xFactor : float
            The factor by which to change xSpeed. Usually self.stats['friction'] or self.stats['air_resistance']
        """
        #TODO: I feel like there's a better way to do this but I can't think of one
        if self.change_x > self.preferred_xspeed: #if we're going too fast
            diff = self.change_x - self.preferred_xspeed
            self.change_x -= min(diff,_xFactor*(settingsManager.getSetting('friction') if self.grounded else settingsManager.getSetting('airControl')))
        elif self.change_x < self.preferred_xspeed: #if we're going too slow
            diff = self.preferred_xspeed - self.change_x
            self.change_x += min(diff,_xFactor*(settingsManager.getSetting('friction') if self.grounded else settingsManager.getSetting('airControl')))
           
    # Change ySpeed according to gravity.        
    def calcGrav(self, _multiplier=1):
        """ Changes the ySpeed according to gravity
        
        Parameters
        -----------
        _multiplier : float
            A multiple of gravity to adjust by, in case gravity is changed temporarily
        """
        if self.change_y > self.preferred_yspeed:
            diff = self.change_y - self.preferred_yspeed
            self.change_y -= min(diff, _multiplier*self.stats['gravity'] * settingsManager.getSetting('gravity')) 
        elif self.change_y < self.preferred_yspeed:
            diff = self.preferred_yspeed - self.change_y
            self.change_y += min(diff, _multiplier*self.stats['gravity'] * settingsManager.getSetting('gravity'))
        
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
    
    def setSpeed(self,_speed,_direction):
        """ Set the actor's speed. Instead of modifying the change_x and change_y values manually,
        this will calculate what they should be set at if you want to give a direction and
        magnitude instead.
        
        Parameters
        -----------
        _speed : float
            The total speed you want the fighter to move
        _direction : int
            The angle of the speed vector in degrees, 0 being right, 90 being up, 180 being left.
        """
        (x,y) = getXYFromDM(_direction,_speed)
        self.change_x = x
        self.change_y = y
    
    ########################################################
    #              ANIMATION FUNCTIONS                     #
    ########################################################
    
    def rotateSprite(self,_direction):
        """ Rotate's the fighter's sprite a given number of degrees
        
        Parameters
        -----------
        _direction : int
            The degrees to rotate towards. 0 being forward, 90 being up
        """
        self.sprite.rotate(-1 * (90 - _direction)) 
        
    def unRotate(self):
        """ Resets rotation to it's proper, straight upwards value """
        self.sprite.rotate()
        
    def changeSprite(self,_newSprite,_frame=0):
        """ Changes the fighter's sprite to the one with the given name.
        Optionally can change into a frame other than zero.
        
        Parameters
        -----------
        _newSprite : string
            The name of the sprite in the SpriteLibrary to change to
        _frame : int : default 0
            The frame to switch to in the new sprite. Leave off to start the new animation at zero
        """
        self.sprite.changeImage(_newSprite)
        self.current_action.sprite_name = _newSprite
        if _frame != 0: self.sprite.changeSubImage(_frame)
        
    def changeSpriteImage(self,_frame,_loop=False):
        """ Change the subimage of the current sprite.
        
        Parameters
        -----------
        _frame : int
            The frame number to change to.
        _loop : bool
            If True, any subimage value larger than maximum will loop back into a new value.
            For example, if _loop is set, accessing the 6th subimage of an animation 4 frames long will get you the second.
        """
        self.sprite.changeSubImage(_frame,_loop)

    def updatePosition(self, _updateRect):
        """ Passes the updatePosition call to the sprite.
        See documentation in SpriteLibrary.updatePosition
        """
        return self.sprite.updatePosition(_updateRect)
    
    ########################################################
    #                  INPUT FUNCTIONS                     #
    ########################################################
    
    
    def keyPressed(self,_key):
        """ Add a key to the buffer. This function should be adding
        to the buffer, and ONLY adding to the buffer. Any sort
        of calculations and state changes should probably be done
        in the stateTransitions function of the current action.
        
        Parameters
        -----------
        _key : String
            The key to append to the buffer
        """
        self.input_buffer.append((_key,1.0))
        self.keys_held[_key] = 1.0
        
    def keyReleased(self,_key):
        """ Removes a key from the buffer. That is to day, it appends
        a release to the buffer. It is safe to call this function if the key
        is not in the buffer, and it will return False if the key was not in there
        to begin with.
        
        Parameters
        -----------
        _key : String
            The key to remove
            
        Return
        -----------
        If the key was successfully removed, True. False if the key was not present to be removed.
        """
        if _key in self.keys_held:
            self.input_buffer.append((_key,0))    
            del self.keys_held[_key]
            return True
        else: return False
    

    def keyBuffered(self, _key, _from = 1, _state = 0.1, _to = 0):
        """ Checks if a key was pressed within a certain amount of frames.
        
        Parameters
        -----------
        _key : String
            The key to search fore
        _from : int : 1
            The furthest back frame to look to.
        _state : float : 0.1
            A value from 0 to 1 for a threshold on value before a button registers as a press.
            Usually only applies to sticks, since buttons are always 0.0 or 1.0
        _to : int : 0
            The furthest forward frame to look to.
        """
        if any(map(lambda k: _key in k and k[_key] >= _state,self.input_buffer.getLastNFrames(_from, _to))):
            self.last_input_frame = 0
            return True
        return False

    def keyTapped(self, _key, _from = None, _state = 0.1, _to = 0):
        """ Checks if a key was pressed and released within a certain amount of frames.
        
        Parameters
        -----------
        _key : String
            The key to search fore
        _from : int : None
            The furthest back frame to look to. If set to None, it will look at the default Buffer
            Window in the player's control settings
        _state : float : 0.1
            A value from 0 to 1 for a threshold on value before a button registers as a press.
            Usually only applies to sticks, since buttons are always 0.0 or 1.0
        _to : int : 0
            The furthest forward frame to look to.
        """
        if _from is None:
            _from = max(min(int(self.key_bindings.timing_window['buffer_window']), self.last_input_frame), 1)
        down_frames = map(lambda k: _key in k and k[_key] >= _state, self.input_buffer.getLastNFrames(_from, _to))
        up_frames = map(lambda k: _key in k and k[_key] < _state, self.input_buffer.getLastNFrames(_from, _to))
        if not any(down_frames) or not any(up_frames):
            return False
        first_down_frame = reduce(lambda j, k: j if j != None else (k if down_frames[k] else None), range(len(down_frames)), None)
        last_up_frame = reduce(lambda j, k: k if up_frames[k] else j, range(len(up_frames)), None)
        if first_down_frame >= last_up_frame:
            self.last_input_frame = 0
            return True
        return False

    #A key press which hasn't been released yet
    def keyHeld(self, _key, _from = None, _state = 0.1, _to = 0):
        """ Checks if a key was pressed within a certain amount of frames and is still being held.
        
        Parameters
        -----------
        _key : String
            The key to search fore
        _from : int : None
            The furthest back frame to look to. If set to None, it will look at the default Buffer
            Window in the player's control settings
        _state : float : 0.1
            A value from 0 to 1 for a threshold on value before a button registers as a press.
            Usually only applies to sticks, since buttons are always 0.0 or 1.0
        _to : int : 0
            The furthest forward frame to look to.
        """
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
        if first_down_frame < last_up_frame:
            self.last_input_frame = 0
            return True
        return False
    
    def keyUp(self, _key, _from = 1, _state = 0.1, _to = 0):
        """ Checks if a key was released within a certain amount of frames.
        
        Parameters
        -----------
        _key : String
            The key to search fore
        _from : int : 1
            The furthest back frame to look to.
        _state : float : 0.1
            A value from 0 to 1 for a threshold on value before a button registers as a press.
            Usually only applies to sticks, since buttons are always 0.0 or 1.0
        _to : int : 0
            The furthest forward frame to look to.
        """
        if any(map(lambda k: _key in k and k[_key] < _state, self.input_buffer.getLastNFrames(_from, _to))):
            self.last_input_frame = 0
            return True
        return False

    def keyReinput(self, _key, _from = None, _state = 0.1, _to = 0):
        """ Checks if a key was pressed twice within a certain amount of time
        
        Parameters
        -----------
        _key : String
            The key to search fore
        _from : int : 1
            The furthest back frame to look to. If set to None, it will look at the default Buffer
            Window in the player's control settings
        _state : float : 0.1
            A value from 0 to 1 for a threshold on value before a button registers as a press.
            Usually only applies to sticks, since buttons are always 0.0 or 1.0
        _to : int : 0
            The furthest forward frame to look to.
        """
        if _from is None:
            _from = max(min(int(self.key_bindings.timing_window['buffer_window']), self.last_input_frame), 1)
        up_frames = map(lambda k: _key in k and k[_key] < _state, self.input_buffer.getLastNFrames(_from, _to))
        down_frames = map(lambda k: _key in k and k[_key] >= _state, self.input_buffer.getLastNFrames(_from, _to))
        if not any(down_frames) or not any(down_frames):
            return False
        first_up_frame = reduce(lambda j, k: j if j != None else (k if up_frames[k] else None), range(len(up_frames)), None)
        last_down_frame = reduce(lambda j, k: k if down_frames[k] else j, range(len(down_frames)), None)
        if first_up_frame < last_down_frame:
            self.last_input_frame = 0
            return True
        return False

    def keyIdle(self, _key, _from = None, _state = 0.1, _to = 0):
        """ Checks if a key was released and not pressed again within a certain amount of time.
        
        Parameters
        -----------
        _key : String
            The key to search fore
        _from : int : 1
            The furthest back frame to look to. If set to None, it will look at the default Buffer
            Window in the player's control settings
        _state : float : 0.1
            A value from 0 to 1 for a threshold on value before a button registers as a press.
            Usually only applies to sticks, since buttons are always 0.0 or 1.0
        _to : int : 0
            The furthest forward frame to look to.
        """
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
        if first_up_frame >= last_down_frame:
            self.last_input_frame = 0
            return True
        return False

    def getSmoothedInput(self, _distanceBack = None, _maxMagnitude = 1.0):
        """ Converts buttons into an analog direction. It checks back for a set amount of frames
        and averages the inputs into a direction.
        
        Parameters
        -----------
        _distanceBack : int : None
            How many frames to look back to get direction inputs from
        _maxMagnitude:
        
        """
        #QUESTION - explain this algorithm a little better
        #TODO If this is a gamepad, simply return its analog input
        if _distanceBack is None:
            smooth_distance = int(self.key_bindings.timing_window['smoothing_window'])
            _distanceBack = smooth_distance
        else:
            smooth_distance = _distanceBack
        
        hold_buffer = reversed(self.input_buffer.getLastNFrames(_distanceBack))
        smoothed_x = 0.0
        smoothed_y = 0.0
        if self.key_bindings.type == "Keyboard":
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
        else:
            smoothed_x = -self.keys_held['left']+self.keys_held['right']
            smoothed_y = -self.keys_held['up']+self.keys_held['down']
        final_magnitude = numpy.linalg.norm([smoothed_x, smoothed_y])
        if final_magnitude > _maxMagnitude:
            smoothed_x /= final_magnitude/_maxMagnitude
            smoothed_y /= final_magnitude/_maxMagnitude
        return [smoothed_x, smoothed_y]
    

    def getSmoothedAngle(self,_default=90):
        """ Returns the angle that the smoothedInput currently points to. 0 being forward, 90 being up
        
        Parameters
        -----------
        _default : int : 90
            What to return if input is [0,0]
        """    
        inputValue = self.getSmoothedInput()
        print(inputValue)
        if (inputValue == [0, 0]):
            angle =  _default
        else:
            angle = math.atan2(-inputValue[1], inputValue[0])*180.0/math.pi
        print('ANGLE:',angle)
        return angle
    
    def checkSmash(self,_direction):
        """ This function checks if the player has Smashed in a direction. It does this by noting if the direction was
        pressed recently and is now above a threshold
        
        Parameters
        -----------
        _direction : String
            The joystick direction to check for a smash in
        """
        #TODO different for buttons than joysticks
        return self.keyBuffered(_direction, int(self.key_bindings.timing_window['smash_window']), 0.85)

    def checkTap(self, _direction, _firstThreshold=0.6):
        """ Checks if the player has tapped a button, but not smashed it. If a joystick is used, the checkSmash function should
        cover this.
        
        Parameters
        -----------
        _direction : String
            The joystick direction to check for a smash in
        _firstThreshold : float : 0.6
            
        """
        if self.key_bindings.type == "Keyboard":
            return self.keyBuffered(_direction, _state=1) and self.keyBuffered(_direction, int(self.key_bindings.timing_window['repeat_window'])+1, _firstThreshold, 1)
        else:
            return self.checkSmash(_direction)

    def netDirection(self, _checkDirectionList):
        """ Gets the net total direction of all of the directions currently being held.
        
        Parameters
        -----------
        _checkDirectionList : 
        
        """
        coords = self.getSmoothedInput()
        if not filter(lambda a: a in ['left', 'right', 'up', 'down'], _checkDirectionList):
            return 'neutral'
        left_check = -coords[0] if 'left' in _checkDirectionList and 'left' in self.keys_held else -2
        right_check = coords[0] if 'right' in _checkDirectionList and 'right' in self.keys_held else -2
        up_check = -coords[1] if 'up' in _checkDirectionList and 'up' in self.keys_held else -2
        down_check = coords[1] if 'down' in _checkDirectionList and 'down' in self.keys_held else -2
        if left_check == -2 and right_check == -2 and up_check == -2 and down_check == -2:
            if 'left' in self.keys_held: left_check = self.keys_held['left']
            if 'right' in self.keys_held: right_check = self.keys_held['right']
            if 'up' in self.keys_held: up_check = self.keys_held['up']
            if 'down' in self.keys_held: down_check = self.keys_held['down']
            if left_check == -2 and right_check == -2 and up_check == -2 and down_check == -2:
                return 'neutral'
        check_dict = {'left': left_check, 'right': right_check, 'up': up_check, 'down': down_check}
        return max(_checkDirectionList, key=lambda k: check_dict[k])
    
    def keysContain(self,_key,_threshold=0.1):
        """ Checks for keys that are currently being held, regardless of when they were pressed.
        
        Parameters
        -----------
        _key : String
            The key to check for.
        _threshold : float : 0.1
            The value that represents a "press", will check for values lower than the threshold
        """
        if _key in self.keys_held:
            return self.keys_held[_key] >= _threshold
        return False
    
    def getForwardBackwardKeys(self):
        """ This returns a tuple of the key for forward, then backward
        Useful for checking if the fighter is pivoting, or doing a back air, or getting the
        proper key to dash-dance, etc.
        
        The best way to use this is something like
        (key,invkey) = actor.getForwardBackwardKeys()
        which will assign the variable "key" to the forward key, and "invkey" to the backward key.
        """
        if self.facing == 1: return ('right','left')
        else: return ('left','right')
    
    ########################################################
    #                 COMBAT FUNCTIONS                     #
    ########################################################
    
    def dealDamage(self, _damage):
        """ Deal damage to the fighter.
        Checks to make sure the damage caps at 999.
        If you want to have higher damage, override this function and remove it.
        This function is called in the applyKnockback function, so you shouldn't
        need to call this function directly for normal attacks, although you can
        for things like poison, non-knockback attacks, etc.
        
        Parameters
        -----------
        _damage : float
            The amount of damage to deal
        """ 
        self.damage += float(math.floor(_damage))
        self.damage = min(999,max(self.damage,0))
            
        if self.data_log:
            self.data_log.addToData('Damage Taken',float(math.floor(_damage)))
            
    def applyKnockback(self, _damage, _kb, _kbg, _trajectory, _weightInfluence=1, _hitstunMultiplier=1, _baseHitstun=1, _hitlagMultiplier=1, _ignoreArmor = False):
        """Do Knockback to the fighter. The knockback calculation is derived from the SSBWiki, and a bit of information from
        ColinJF and Amazing Ampharos on Smashboards, it is based off of Super Smash Bros. Brawl's knockback calculation, which
        is the one with the most information available
        
        Parameters
        -----------
        _damage : float
            The damage dealt by the attack. This is used in some calculations, so it is applied here.
        _kb : float
            The base knockback of the attack.
        _kbg : float
            The knockback growth ratio of the attack.
        _trajectory : int
            The direction the attack sends the fighter, in degrees, with 0 being right, 90 being upward, 180 being left.
            This is an absolute direction, irrelevant of either character's facing direction. Those tend to be taken
            into consideration in the hitbox collision event itself, to allow the hitbox to also take in the attacker's
            current state as well as the fighter receiving knockback.
        _weightInfluence : float
            The degree to which weight influences knockback. Default value is 1, set to 0 to make knockback 
            weight-independent, or to whatever other value you want to change the effect of weight on knockback. 
        _hitstunMultiplier : float
            The ratio of the knockback to the additional hitstun that the hit should inflict. Default value is 
            2 for normal levels of hitstun. To disable flinching, set to 0. 
        _baseHitstun : int
            The minimum hitstun that the hit should inflict regardless of knockback. This also influences how much gravity and 
            air resistance affect base knockback. 
        _hitlagMultiplier : float
            The ratio of normal calculated hitlag to the amount of hitlag the hit should inflict. This affects both 
            attacker and target. 
        
        """
        self.hitstop = math.floor((_damage / 4.0 + 2)*_hitlagMultiplier)
        if self.grounded:
            self.hitstop_vibration = (3,0)
        else:
            self.hitstop_vibration = (0,3)
        self.hitstop_pos = self.rect.center

        #Crouch cancelling
        if self.current_action.name in ('Crouch', 'CrouchCancel'):
            _kb *= 0.5
            _kbg *= 0.9
            _baseHitstun *= 0.5
            _hitstunMultiplier *= 0.8
        
        p = float(self.damage)
        d = float(_damage)
        w = float(self.stats['weight']) * settingsManager.getSetting('weight')
        s = float(_kbg)
        b = float(_kb)
        print('weight influence',_weightInfluence)
        # Thank you, ssbwiki!
        total_kb = (((((p/10.0) + (p*d)/20.0) * (200.0/(w*_weightInfluence+100))*1.4) + 5) * s) + b

        if not _ignoreArmor and (_damage < self.flinch_damage_threshold or total_kb < self.flinch_knockback_threshold):
            self.dealDamage(_damage*self.armor_damage_multiplier)
            return 0

        di_vec = self.getSmoothedInput(int(self.key_bindings.timing_window['smoothing_window']))

        trajectory_vec = [math.cos(_trajectory/180*math.pi), math.sin(_trajectory/180*math.pi)]

        additional_kb = .5*_baseHitstun*math.sqrt(abs(trajectory_vec[0])*(self.stats['air_resistance']*settingsManager.getSetting('airControl'))**2+abs(trajectory_vec[1])*(self.stats['gravity']*settingsManager.getSetting('gravity'))**2)

        di_multiplier = 1+numpy.dot(di_vec, trajectory_vec)*.05
        _trajectory += numpy.cross(di_vec, trajectory_vec)*13.5

        hitstun_frames = math.floor((total_kb+additional_kb)*_hitstunMultiplier+_baseHitstun)
        
        if not _ignoreArmor and self.no_flinch_hits > 0:
            if hitstun_frames > 0.5:
                self.no_flinch_hits -= 1
            self.dealDamage(_damage*self.armor_damage_multiplier)
            return 0
        
        if hitstun_frames > 0.5:
            #If the current action is not hitstun or you're in hitstun, but there's not much of it left
            if not isinstance(self.current_action, baseActions.HitStun) or (self.current_action.last_frame-self.current_action.frame)/float(settingsManager.getSetting('hitstun')) <= hitstun_frames+15:
                self.setSpeed((total_kb+additional_kb)*di_multiplier, _trajectory)
                self.doHitStun(hitstun_frames*settingsManager.getSetting('hitstun'), _trajectory)
        
        self.dealDamage(_damage)
        return math.floor((total_kb+additional_kb)*di_multiplier)

    def applyPushback(self, _kb, _trajectory, _hitlag):
        """ Pushes back the fighter when they hit a foe. This is the corollary to applyKnockback,
        except this one is called on the fighter who lands the hit. It applies the hitlag to the fighter,
        and pushes them back slightly from the opponent.
        
        Parameters
        -----------
        _kb : 
        _trajectory : int
            The direction to push the attacker back. In degrees, zero being forward, 90 being up
        _hitlag : int
            The hitlag from the attack        
        """
        self.hitstop = math.floor(_hitlag*settingsManager.getSetting('hitlag'))
        print(self.hitstop)
        (x, y) = getXYFromDM(_trajectory, _kb)
        self.change_x += x
        if not self.grounded:
            self.change_y += y
    
    def die(self,_respawn = True):
        """ This function is called when a fighter dies. It spawns the
        death particles and resets some variables.
        
        Parameters
        -----------
        _respawn : Boolean
            Whether or not to respawn the fighter after death
        """
        sfxlib = settingsManager.getSfx()
        if sfxlib.hasSound('death', self.name):
            self.playSound('death')
        
        self.damage = 0
        self.change_x = 0
        self.change_y = 0
        self.jumps = self.stats['jumps']
        self.data_log.addToData('Falls',1)
        if self.hit_tagged != None:
            if hasattr(self.hit_tagged, 'data_log'):
                self.hit_tagged.data_log.addToData('KOs',1)
        if _respawn:
            if self.hit_tagged is not None:
                color = settingsManager.getSetting('playerColor' + str(self.hit_tagged.player_num))
            else:
                color = settingsManager.getSetting('playerColor' + str(self.player_num))
                
            self.initialize()
            for i in range(0, 11):
                next_hit_article = article.HitArticle(self, self.rect.center, 1, i*30, 30, 1.5, color)
                self.articles.add(next_hit_article)
                next_hit_article = article.HitArticle(self, self.rect.center, 1, i*30+10, 60, 1.5, color)
                self.articles.add(next_hit_article)
                next_hit_article = article.HitArticle(self, self.rect.center, 1, i*30+20, 90, 1.5, color)
                self.articles.add(next_hit_article)
            self.rect.midbottom = self.game_state.spawn_locations[self.player_num]
            self.rect.bottom -= 200
            self.sprite.updatePosition(self.rect)
            self.ecb.normalize()
            self.ecb.store()
            self.createMask([255,255,255], 480, True, 12)
            self.respawn_invulnerable = 480
            self.doAction('Respawn')
    
    ########################################################
    #                 HELPER FUNCTIONS                     #
    ########################################################
    """ These are ways of getting properly formatted data, accessing specific things,
    converting data, etc. """
    
    def getForwardWithOffset(self,_offSet = 0):
        """ Get a direction that is angled from the direction the fighter is facing, 
        rather than angled from right. For example, sending the opponent 30 degrees is
        fine when facing right, but if you're facing left, you'd still be sending them to the right!
        
        Hitboxes use this calculation a lot. It'll return the proper angle that is the given offset
        from "forward". Defaults to 0, which will give either 0 or 180, depending on the direction
        of the fighter.
        
        Parameters
        -----------
        _offSet : int
            The angle to convert
        
        Return
        -----------
        The adjusted angle for the proper facing angle
        """
        if self.facing == 1:
            return _offSet
        else:
            return 180 - _offSet

    
    def getDirectionMagnitude(self):
        """ Converts the fighter's current speed from XY components into
        a Direction and Magnitude. Angles are in degrees, with 0 being forward
        
        Return
        -----------
        (direction,magnitude) : Tuple (int,float)
            The direction in degrees, and the magnitude in map uints
        """
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
    
    
    def getFacingDirection(self):
        """ A simple function that converts the facing variable into a direction in degrees.
        
        Return
        -----------
        The direction the fighter is facing in degrees, zero being right, 90 being up
        """
        if self.facing == 1: return 0
        else: return 180
        
    def setGrabbing(self, _other):
        """ Sets a grabbing state. Tells this fighter that it's grabbing something else,
        and tells that thing what's grabbing it.
        
        Parameters
        -----------
        _other : GameObject
            The object to be grabbing
        """
        self.grabbing = _other
        _other.grabbed_by = self

    def isGrabbing(self):
        """ Check whether the fighter is current holding something. If this object says that it's
        holding something, but the other object doesn't agree, assume that there is no grab.
        
        Return
        -----------
        bool : Whether the fighter is currently holding something
        """
        if self.grabbing is None:
            return False
        if self.grabbing and self.grabbing.grabbed_by == self:
            return True
        return False
    
    def flip(self):
        """ Flip the fighter so he is now facing the other way.
        Also flips the sprite for you.
        """
        self.facing = -self.facing
        self.sprite.flipX()
          
    def updateLandingLag(self,_lag,_reset=False):
        """ Updates landing lag, but doesn't overwrite a longer lag with a short one.
        Useful for things like fast aerials that have short endlag, but you don't want to be
        able to override something like an airdodge lag with it.
        
        Parameters
        -----------
        _lag : int
            The number of frames of endlag to set
        _reset : bool : False
            When True, will always set the landing lag to the given value, regardless of current lag.
        """
        if _reset: self.landing_lag = _lag
        else:
            if _lag > self.landing_lag: self.landing_lag = _lag
    
    def createMask(self,_color,_duration,_pulse = False,_pulse_size = 16):
        """ Creates a color mask sprite over the fighter
        
        Parameters
        -----------
        _color : String
            The color of the mask in RGB of the format #RRGGBB
        _duration : int
            How many frames should the mask stay active
        _pulse : bool
            Should the mask "flash" in transparency, or just stay solid?
        _pulse_size : int
            If pulse is true, this is how long it takes for one full rotation of transparency
        """
        self.mask = spriteManager.MaskSprite(self.sprite,_color,_duration,_pulse, _pulse_size)
        
    def playSound(self,_sound):
        """ Play a sound effect. If the sound is not in the fighter's SFX library, it will play the base sound.
        
        Parameters
        -----------
        _sound : String
            The name of the sound to be played 
        """
        sfxlib = settingsManager.getSfx()
        if sfxlib.hasSound(_sound, self.name):
            sfxlib.playSound(_sound, self.name)
        else:
            sfxlib.playSound(_sound,'base')
    
    def activateHitbox(self,_hitbox):
        """ Activates a hitbox, adding it to your active_hitboxes list.
        Parameters
        -----------
        _hitbox : Hitbox
            The hitbox to activate
        """
        self.active_hitboxes.add(_hitbox)
        _hitbox.activate()

    def activateHurtbox(self,_hurtbox):
        """ Activates a hurtbox, adding it to your active_hurtboxes list.
        _hurtbox : Hurtbox
            The hitbox to activate
        """
        self.active_hurtboxes.add(_hurtbox)
        
    def lockHitbox(self,_hbox):
        """ This will "lock" the hitbox so that another hitbox with the same ID from the same fighter won't hit again.
        Returns true if it was successful, false if it already exists in the lock.
        
        Parameters
        -----------
        _hbox : Hitbox
            The hitbox we are checking for
        """
        
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
        """ Creates a shield particle and adds it to your active articles list """
        self.articles.add(article.ShieldArticle(settingsManager.createPath("sprites/melee_shield.png"),self))
                    
def test():
    fight = AbstractFighter('',0)
    print(fight.__init__.__doc__)
if __name__ == '__main__': test()