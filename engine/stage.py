from __future__ import print_function
import pygame
import spriteManager
import settingsManager
import math

class Stage():
    def __init__(self):
        #Platforms are static, non-moving interactables.
        #They are never updated after creation, to save on memory.
        self.platform_list = []
        self.platform_ledges = []
        
        #Entities are updated whenever the frame is drawn.
        #If it changes at all on the stage, it is an entity
        self.entity_list = []
        
        self.size = None
        self.camera_maximum = None
        self.blast_line = None
        
        self.preferred_zoom_level = 1.0
        self.zoom_level = 1.0
    
        self.active_hitboxes = pygame.sprite.Group()
        self.follows = []
        self.spawn_locations = []
        
        """
        Background sprites are drawn before the fighters are,
        foreground sprites are drawn after the fighters.
        The sprites are drawn in order, with the first elements
        of the list drawn first, and later elements drawn over them.
        """
        self.background_sprites = []
        self.foreground_sprites = []
        self.background_color = [100, 100, 100]
        
    """
    Puts the camera in the proper position.
    This MUST be called after creation.
    It is its own separate function in case anything needs to be changed (for example, on a scrolling stage)
    and so it can be done after initializing both the base stage and the module.
    """
    def initializeCamera(self):
        self.camera_position = pygame.Rect(24,16,settingsManager.getSetting('windowWidth'),settingsManager.getSetting('windowHeight'))
        self.camera_position.midtop = self.size.midtop
        
        self.camera_preferred_position = pygame.Rect(24,16,settingsManager.getSetting('windowWidth'),settingsManager.getSetting('windowHeight'))
        self.camera_preferred_position.midtop = self.size.midtop
        
        self.dead_zone = [64,32]
    
        self.cameraUpdate()
        self.camera_position = self.camera_preferred_position
        
    def getLedges(self):
        self.platform_ledges = []
        for plat in self.platform_list:
            for ledge in plat.ledges:
                if ledge != None:
                    self.platform_ledges.append(ledge)
        return self.platform_ledges
    """
    The frame-by-frame changes to the stage.
    Updates all entities, then moves the camera closer to its preferred size
    """    
    def update(self):

        for entity in self.entity_list:
            entity.update()
        
        if self.preferred_zoom_level != self.zoom_level:
            diff = self.zoom_level - self.preferred_zoom_level
            #If the camera is too narrow
            if diff > 0: self.zoom_level -= min([0.1,diff])
            #If the camera is too wide
            else: self.zoom_level += min([0.1,-diff])
            self.camera_position.width  = round(float(settingsManager.getSetting('windowWidth'))  * self.zoom_level)
            self.camera_position.height = round(float(settingsManager.getSetting('windowHeight')) * self.zoom_level)
        
        if self.camera_position.x != self.camera_preferred_position.x:
            diff = self.camera_position.x - self.camera_preferred_position.x
            #If the camera is too far to the right
            if diff > 0: self.camera_position.x -= min([10,diff]) #otherwise, move 10 pixels closer
            #If the camera is too far to the left
            else: self.camera_position.x += min([10,-diff])
        
        if self.camera_position.y != self.camera_preferred_position.y:
            diff = self.camera_position.y - self.camera_preferred_position.y
            #If the camera is too far to the bottom
            if diff > 0: self.camera_position.y -= min([20,diff])
            #If the camera is too far to the top
            else: self.camera_position.y += min([20,-diff])
    
    """
    Centers the camera on the given point
    """    
    def centerCamera(self,_center):
        # First, build the rect, then center it
        self.camera_preferred_position.width  = round(settingsManager.getSetting('windowWidth')  * self.preferred_zoom_level)
        self.camera_preferred_position.height = round(settingsManager.getSetting('windowHeight') * self.preferred_zoom_level)
        self.camera_preferred_position.center = _center
        
        # If it's too far to one side, fix it.
        if self.camera_preferred_position.left < self.camera_maximum.left: self.camera_preferred_position.left = self.camera_maximum.left
        if self.camera_preferred_position.right > self.camera_maximum.right: self.camera_preferred_position.right = self.camera_maximum.right
        if self.camera_preferred_position.top < self.camera_maximum.top: self.camera_preferred_position.top = self.camera_maximum.top
        if self.camera_preferred_position.bottom > self.camera_maximum.bottom: self.camera_preferred_position.bottom = self.camera_maximum.bottom
        
        
    """
    If Center is not given, will shift the camera by the given x and y
    If Center is True, will center the camera on the given x and y
    """
    def moveCamera(self,_x,_y,_center=False):
        if _center:
            new_rect = self.camera_preferred_position.copy()
            new_rect.center = [_x,_y]
        else:
            new_rect = self.camera_preferred_position.copy()
            new_rect.x += _x
            new_rect.y += _y
        self.camera_preferred_position = new_rect
        
    
    """
    Okay, this method's a doozy. It'll reposition and rescale the camera as necessary.
    Each chunk is commented as it goes if you need to follow along.
    """
    def cameraUpdate(self):
        # Initialize our corner objects
        leftmost = self.follows[0]
        rightmost = self.follows[0]
        topmost = self.follows[0]
        bottommost = self.follows[0]
        
        # Iterate through all of the objects to get the cornermost objects
        for obj in self.follows:
            if obj.left < leftmost.left:
                leftmost = obj
            if obj.right > rightmost.right:
                rightmost = obj
            if obj.top < topmost.top:
                topmost = obj
            if obj.bottom > bottommost.bottom:
                bottommost = obj
        
        # Calculate the width and height between the two farthest sidewas objects (plus deadzone)
        x_dist = (rightmost.right - leftmost.left) + (2*self.dead_zone[0])
        y_dist = (bottommost.bottom - topmost.top) + (2*self.dead_zone[1])
        
        # Compare that distance with the window size to get the scale
        x_zoom = x_dist / float(settingsManager.getSetting('windowWidth'))
        y_zoom = y_dist / float(settingsManager.getSetting('windowHeight'))
        
        # Minimum Zoom level
        if x_zoom < 1.0: x_zoom = 1.0
        if y_zoom < 1.0: y_zoom = 1.0
        
        # If our new zoomed value is too big, we need to cut it down to size
        if x_zoom * settingsManager.getSetting('windowWidth') > self.camera_maximum.width:
            x_zoom = self.camera_maximum.width / float(settingsManager.getSetting('windowWidth'))
        if y_zoom * settingsManager.getSetting('windowHeight') > self.camera_maximum.height:
            y_zoom = self.camera_maximum.height / float(settingsManager.getSetting('windowHeight'))
        
        # Set the preferred zoom level and camera position to be centered on later
        self.preferred_zoom_level = max([x_zoom,y_zoom])
        if self.preferred_zoom_level > (self.camera_maximum.width/float(settingsManager.getSetting('windowWidth'))):
            self.preferred_zoom_level = self.camera_maximum.width/float(settingsManager.getSetting('windowWidth'))
        if self.preferred_zoom_level > (self.camera_maximum.height/float(settingsManager.getSetting('windowHeight'))):
            self.preferred_zoom_level = self.camera_maximum.height/float(settingsManager.getSetting('windowHeight'))
    
        # Now that everything is set, we create the bounding_box around the cornermost objects, then get the center of it
        bounding_box = pygame.Rect(leftmost.left-self.dead_zone[0],topmost.top-self.dead_zone[1],x_dist,y_dist)
        center = bounding_box.center
        
        # And finally, move the camera.
        self.centerCamera(center)
    
    """
    Calculates the port on screen of a given rect on the stage.
    These are the coordinates that will be passed to draw.
    """    
    def stageToScreen(self,_rect):
        x = _rect.x - self.camera_position.x
        y = _rect.y - self.camera_position.y
        return (x,y)
    
    """
    Gets the current scale of the screen. 1.0 means the camera is showing the window size. Any lower means
    the camera is zoomed out, any higher means the camera is zoomed in.
    """
    def getScale(self):
        h = round(float(settingsManager.getSetting('windowHeight')) / self.camera_position.height,5)
        w = round(float(settingsManager.getSetting('windowWidth')) / self.camera_position.width,5)
        
        # If they match, the math is good and we can just pick one
        if h == w:
            return h
        # If they don't match, something might have gone wrong.
        else:
            if abs(h - w) <= 0.02:
                # Fuck it, close enough.
                return h
            print("Scaling Error", h, w, abs(h-w))
            return w
        
    """
    Draws the background elements in order.
    """
    def drawBG(self,_screen):
        rects = []
        for sprite,paralax in self.background_sprites:
            x = sprite.rect.x - (self.camera_position.x * paralax)
            y = sprite.rect.y - (self.camera_position.y)
            rect = sprite.draw(_screen,(x,y),self.getScale())
            if rect: rects.append(rect)
        return rects
            
    def drawFG(self,_screen):
        rects = []
        if settingsManager.getSetting('showPlatformLines'):
            for plat in self.platform_list: 
                platSprite = spriteManager.RectSprite(pygame.Rect(plat.rect.topleft,plat.rect.size))
                rect = platSprite.draw(_screen,self.stageToScreen(platSprite.rect),self.getScale())
                if rect: rects.append(rect)
        #for ledge in self.platform_ledges:
            #ledgeSprite = spriteObject.RectSprite(ledge.rect.topleft,ledge.rect.size,[0,0,255])
            #ledgeSprite.draw(_screen,self.stageToScreen(ledge.rect),self.getScale())
        for sprite in self.foreground_sprites:
            rect = sprite.draw(_screen,self.stageToScreen(sprite.rect),self.getScale())
            if rect: rects.append(rect)
        return rects
    
    """
    Adds an object to the background. Optionally pass a paralax factor which determines how much
    it is affected by paralax. 1.0 is full scrolling with screen, 0.0 is no scrolling.
    """
    def addToBackground(self,_sprite,_paralaxFactor = 1.0):
        self.background_sprites.append((_sprite,_paralaxFactor))
"""
Platforms for the stage.
Given two points (as a tuple of XY coordinates), it will
draw a line between the points.
grabbable is a tuple of booleans, determining if the corresponding ledge
is grabble, so a (True,False) would mean the left edge is grabbable,
but the right edge is not.
"""
class Platform(pygame.sprite.Sprite):
    def __init__(self,_leftPoint, _rightPoint,_grabbable = (False,False)):
        pygame.sprite.Sprite.__init__(self)
        self.left_point = _leftPoint
        self.right_point = _rightPoint
        self.x_dist = max(1,_rightPoint[0] - _leftPoint[0])
        self.y_dist = max(1,_rightPoint[1] - _leftPoint[1])
        self.angle = self.getDirectionBetweenPoints(_leftPoint, _rightPoint)
        self.solid = True
        self.change_x = 0
        self.change_y = 0
        
        self.players_on = []
        self.rect = pygame.Rect([_leftPoint[0],min(_leftPoint[1],_rightPoint[1])], [self.x_dist,self.y_dist])
        
        left_ledge = None
        right_ledge = None
        if _grabbable[0]: left_ledge = Ledge(self,'left')
        if _grabbable[1]: right_ledge = Ledge(self,'right')
        self.ledges = [left_ledge,right_ledge]
        
    def playerCollide(self,_player):
        self.players_on.append(_player)
    
    def playerLeaves(self,_player):
        self.players_on.remove(_player)
    
    def ledgeGrabbed(self,_fighter):
        pass
        
    def getDirectionBetweenPoints(self, _p1, _p2):
        (x1, y1) = _p1
        (x2, y2) = _p2
        dx = x2 - x1
        dy = y1 - y2
        return (180 * math.atan2(dy, dx)) / math.pi
    
    def getXYfromDM(self, _direction,_magnitude):
        rad = math.radians(_direction)
        x = round(math.cos(rad) * _magnitude,5)
        y = -round(math.sin(rad) * _magnitude,5)
        return (x,y)
    
class PassthroughPlatform(Platform):
    def __init__(self,_leftPoint,_rightPoint,_grabbable = (False,False)):
        Platform.__init__(self,_leftPoint,_rightPoint,_grabbable)
        self.solid = False 
        
class MovingPlatform(Platform):
    def __init__(self,_leftPoint,_rightPoint,_endPoint,_moveSpeed = 1, _grabbable = (False,False), _solid = False):
        Platform.__init__(self, _leftPoint, _rightPoint, _grabbable)
        self.solid = _solid
        
        self.start_point = self.rect.center
        self.end_point = _endPoint
        
        self.direction = self.getDirectionBetweenPoints(self.start_point, self.end_point)
        self.speed = _moveSpeed
        self.delta_x, self.delta_y = self.getXYfromDM(self.direction,self.speed)
        self.change_x = 0
        self.change_y = 0
        
        self.real_x = 0
        self.real_y = 0
        print(self.delta_x, self.delta_y)
    
    def update(self):
        if self.rect.center == self.end_point:
            #swap our destination, direction, and change_xy parameters
            tmp = self.end_point
            self.end_point = self.start_point
            self.start_point = tmp
            self.direction = self.getDirectionBetweenPoints(self.start_point, self.end_point)
            self.delta_x, self.delta_y = self.getXYfromDM(self.direction,self.speed)
            self.change_x = 0
            self.change_y = 0
        
        #add another delta change, strip off the whole numbers, and keep the decimal parts
        #the whole part passes to the rect update later
        self.real_x += self.delta_x
        self.change_x = math.floor(self.real_x)
        partial_x = self.real_x % 1
        self.real_x = partial_x
        
        self.real_y += self.delta_y
        self.change_y = math.floor(self.real_y)
        partial_y = self.real_y % 1
        self.real_y = partial_y
        
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        
        self.left_point = self.rect.topleft
        self.right_point = self.rect.topright
        
        self.x_dist = max(1,self.right_point[0] - self.left_point[0])
        self.y_dist = max(1,self.right_point[1] - self.left_point[1])
  
"""
Ledge object. This is what the fighter interacts with.
It has a parent platform, and a side of that platform.
Most of the attributes of the ledge are altered by the settings.
"""
class Ledge(pygame.sprite.Sprite):
    def __init__(self,_plat,_side):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect([0,0],settingsManager.getSetting('ledgeSweetspotSize'))
        self.side = _side
        if _side == 'left': self.rect.midtop = _plat.left_point
        else: self.rect.midtop = [_plat.right_point[0], _plat.left_point[1]]
        self.fighters_grabbed = [] # this is a list in case "Ledge Conflict" is set to "share"
        
    """
    When a fighter wants to grab the ledge, this function is called.
    This function determines if a fighter is successful in his grab
    (which will call doLedgeGrab on the fighter). It will also
    pop opponents off if conflict is set to trump.
    """
    def fighterGrabs(self,_fighter):
        if len(self.fighters_grabbed) == 0: # if no one's on the ledge, we don't care about conflict resolution
            self.fighters_grabbed.append(_fighter)
            _fighter.doLedgeGrab(self)
        else: # someone's already here
            conflict = settingsManager.getSetting('ledgeConflict')
            if conflict == 'share':
                self.fighters_grabbed.append(_fighter)
                _fighter.doLedgeGrab(self)
            elif conflict == 'hog':
                return
            elif conflict == 'trump':
                for other in self.fighters_grabbed:
                    self.fighterLeaves(other)
                    other.doGetTrumped()
                self.fighters_grabbed.append(_fighter)
                _fighter.doLedgeGrab(self)
    
    """
    A simple wrapper function to take someone off of the
    ledge grab list.
    """
    def fighterLeaves(self,_fighter):
        self.fighters_grabbed.remove(_fighter)
