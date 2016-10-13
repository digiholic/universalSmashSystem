import settingsManager
import pygame
import xml.etree.ElementTree as ElementTree
import xml.dom.minidom
import os
import baseActions
import engine.collisionBox as collisionBox
import weakref
import engine.hitbox as hitbox
import math
import numpy

class AbstractFighter():
    """ The Abstract Fighter is an individual fighter in the battle. It holds all of the data
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
    css_icon_path = 'sprites/icon_unknown.png'
    css_portrait_path =''
    
    sprite_directory = 'sprites/'
    sprite_prefix = ''
    sprite_width = '64'
    default_sprite = 'sandbag_idle'
    
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
    
    input_buffer = InputBuffer()
    keys_held = dict()
    
    hitbox_lock = weakref.WeakSet()
    hitbox_contact = set()
    
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
                    return self.xml_data.find(_tag)
                else: return _default
        
        
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
        
        #TODO color palettes
        #TODO costumes
        
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
            
        for tag,val in self.var.iteritems():
            stats_elem.append(self.createElement(tag, val))
        tree.append(stats_elem)
        
        xmlfile = xml.dom.minidom.parseString(ElementTree.tostring(tree))
        outputFile = open(_path,'w')
        outputFile.write(xmlfile.toprettyxml())
    
    
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
    #            INITIALIZED FIGHTER METHODS               #
    ########################################################
    
    def update(self):
        """
        This method will step the fighter forward one frame. It will resolve movement,
        collisions, animations, and all sorts of things. It should be called every frame.
        """ 
        pass
    
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
        
     
    ########################################################
    #              COLLISIONS AND MOVEMENT                 #
    ########################################################
    def accel(self,_xFactor):
        """ Change speed to get closer to the preferred speed without going over.
        
        Parameters
        -----------
        _xFactor : float
            The factor by which to change xSpeed. Usually self.var['friction'] or self.var['air_resistance']
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
            self.change_y -= min(diff, _multiplier*self.var['gravity'] * settingsManager.getSetting('gravity')) 
        elif self.change_y < self.preferred_yspeed:
            diff = self.preferred_yspeed - self.change_y
            self.change_y += min(diff, _multiplier*self.var['gravity'] * settingsManager.getSetting('gravity'))
        
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
    #                  INPUT FUNCTIONS                     #
    ########################################################
    
    
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
    
def test():
    fight = AbstractFighter('',0)

if __name__ == '__main__': test()