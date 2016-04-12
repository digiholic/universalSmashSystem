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
        
        self.preferred_zoomLevel = 1.0
        self.zoomLevel = 1.0
    
        self.active_hitboxes = pygame.sprite.Group()
        self.follows = []
        self.spawnLocations = []
        
        """
        Background sprites are drawn before the fighters are,
        foreground sprites are drawn after the fighters.
        The sprites are drawn in order, with the first elements
        of the list drawn first, and later elements drawn over them.
        """
        self.backgroundSprites = []
        self.foregroundSprites = []
        self.backgroundColor = [100, 100, 100]
        
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
        
        self.deadZone = [64,32]
    
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
        
        if self.preferred_zoomLevel != self.zoomLevel:
            diff = self.zoomLevel - self.preferred_zoomLevel
            #If the camera is too narrow
            if diff > 0: self.zoomLevel -= min([0.1,diff])
            #If the camera is too wide
            else: self.zoomLevel += min([0.1,-diff])
            self.camera_position.width  = round(float(settingsManager.getSetting('windowWidth'))  * self.zoomLevel)
            self.camera_position.height = round(float(settingsManager.getSetting('windowHeight')) * self.zoomLevel)
        
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
    def centerCamera(self,center):
        # First, build the rect, then center it
        self.camera_preferred_position.width  = round(settingsManager.getSetting('windowWidth')  * self.preferred_zoomLevel)
        self.camera_preferred_position.height = round(settingsManager.getSetting('windowHeight') * self.preferred_zoomLevel)
        self.camera_preferred_position.center = center
        
        # If it's too far to one side, fix it.
        if self.camera_preferred_position.left < self.camera_maximum.left: self.camera_preferred_position.left = self.camera_maximum.left
        if self.camera_preferred_position.right > self.camera_maximum.right: self.camera_preferred_position.right = self.camera_maximum.right
        if self.camera_preferred_position.top < self.camera_maximum.top: self.camera_preferred_position.top = self.camera_maximum.top
        if self.camera_preferred_position.bottom > self.camera_maximum.bottom: self.camera_preferred_position.bottom = self.camera_maximum.bottom
        
        
    """
    If Center is not given, will shift the camera by the given x and y
    If Center is True, will center the camera on the given x and y
    """
    def moveCamera(self,x,y,center=False):
        if center:
            newRect = self.camera_preferred_position.copy()
            newRect.center = [x,y]
        else:
            newRect = self.camera_preferred_position.copy()
            newRect.x += x
            newRect.y += y
        self.camera_preferred_position = newRect
        
    
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
        xdist = (rightmost.right - leftmost.left) + (2*self.deadZone[0])
        ydist = (bottommost.bottom - topmost.top) + (2*self.deadZone[1])
        
        # Compare that distance with the window size to get the scale
        xZoom = xdist / float(settingsManager.getSetting('windowWidth'))
        yZoom = ydist / float(settingsManager.getSetting('windowHeight'))
        
        # Minimum Zoom level
        if xZoom < 1.0: xZoom = 1.0
        if yZoom < 1.0: yZoom = 1.0
        
        # If our new zoomed value is too big, we need to cut it down to size
        if xZoom * settingsManager.getSetting('windowWidth') > self.camera_maximum.width:
            xZoom = self.camera_maximum.width / float(settingsManager.getSetting('windowWidth'))
        if yZoom * settingsManager.getSetting('windowHeight') > self.camera_maximum.height:
            yZoom = self.camera_maximum.height / float(settingsManager.getSetting('windowHeight'))
        
        # Set the preferred zoom level and camera position to be centered on later
        self.preferred_zoomLevel = max([xZoom,yZoom])
        if self.preferred_zoomLevel > (self.camera_maximum.width/float(settingsManager.getSetting('windowWidth'))):
            self.preferred_zoomLevel = self.camera_maximum.width/float(settingsManager.getSetting('windowWidth'))
        if self.preferred_zoomLevel > (self.camera_maximum.height/float(settingsManager.getSetting('windowHeight'))):
            self.preferred_zoomLevel = self.camera_maximum.height/float(settingsManager.getSetting('windowHeight'))
    
        # Now that everything is set, we create the boundingBox around the cornermost objects, then get the center of it
        boundingBox = pygame.Rect(leftmost.left-self.deadZone[0],topmost.top-self.deadZone[1],xdist,ydist)
        center = boundingBox.center
        
        # And finally, move the camera.
        self.centerCamera(center)
    
    """
    Calculates the port on screen of a given rect on the stage.
    These are the coordinates that will be passed to draw.
    """    
    def stageToScreen(self,rect):
        x = rect.x - self.camera_position.x
        y = rect.y - self.camera_position.y
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
    def drawBG(self,screen):
        rects = []
        for sprite,paralax in self.backgroundSprites:
            x = sprite.rect.x - (self.camera_position.x * paralax)
            y = sprite.rect.y - (self.camera_position.y)
            rect = sprite.draw(screen,(x,y),self.getScale())
            if rect: rects.append(rect)
        return rects
            
    def drawFG(self,screen):
        rects = []
        if settingsManager.getSetting('showPlatformLines'):
            for plat in self.platform_list: 
                platSprite = spriteManager.RectSprite(pygame.Rect(plat.rect.topleft,plat.rect.size))
                rect = platSprite.draw(screen,self.stageToScreen(platSprite.rect),self.getScale())
                if rect: rects.append(rect)
        #for ledge in self.platform_ledges:
            #ledgeSprite = spriteObject.RectSprite(ledge.rect.topleft,ledge.rect.size,[0,0,255])
            #ledgeSprite.draw(screen,self.stageToScreen(ledge.rect),self.getScale())
        for sprite in self.foregroundSprites:
            rect = sprite.draw(screen,self.stageToScreen(sprite.rect),self.getScale())
            if rect: rects.append(rect)
        return rects
    
    """
    Adds an object to the background. Optionally pass a paralax factor which determines how much
    it is affected by paralax. 1.0 is full scrolling with screen, 0.0 is no scrolling.
    """
    def addToBackground(self,sprite,paralaxFactor = 1.0):
        self.backgroundSprites.append((sprite,paralaxFactor))
"""
Platforms for the stage.
Given two points (as a tuple of XY coordinates), it will
draw a line between the points.
grabbable is a tuple of booleans, determining if the corresponding ledge
is grabble, so a (True,False) would mean the left edge is grabbable,
but the right edge is not.
"""
class Platform(pygame.sprite.Sprite):
    def __init__(self,leftPoint, rightPoint,grabbable = (False,False)):
        pygame.sprite.Sprite.__init__(self)
        self.leftPoint = leftPoint
        self.rightPoint = rightPoint
        self.xdist = max(1,rightPoint[0] - leftPoint[0])
        self.ydist = max(1,rightPoint[1] - leftPoint[1])
        self.angle = self.getDirectionBetweenPoints(leftPoint, rightPoint)
        self.solid = True
        self.change_x = 0
        self.change_y = 0
        
        self.playersOn = []
        self.rect = pygame.Rect([leftPoint[0],min(leftPoint[1],rightPoint[1])], [self.xdist,self.ydist])
        
        leftLedge = None
        rightLedge = None
        if grabbable[0]: leftLedge = Ledge(self,'left')
        if grabbable[1]: rightLedge = Ledge(self,'right')
        self.ledges = [leftLedge,rightLedge]
        
    def playerCollide(self,player):
        self.playersOn.append(player)
    
    def playerLeaves(self,player):
        self.playersOn.remove(player)
    
    def ledgeGrabbed(self,fighter):
        pass
        
    def getDirectionBetweenPoints(self, p1, p2):
        (x1, y1) = p1
        (x2, y2) = p2
        dx = x2 - x1
        dy = y1 - y2
        return (180 * math.atan2(dy, dx)) / math.pi
    
    def getXYfromDM(self, direction,magnitude):
        rad = math.radians(direction)
        x = round(math.cos(rad) * magnitude,5)
        y = -round(math.sin(rad) * magnitude,5)
        return (x,y)
    
class PassthroughPlatform(Platform):
    def __init__(self,leftPoint,rightPoint,grabbable = (False,False)):
        Platform.__init__(self,leftPoint,rightPoint,grabbable)
        self.solid = False 
        
class MovingPlatform(Platform):
    def __init__(self,leftPoint,rightPoint,endPoint,moveSpeed = 1, grabbable = (False,False), solid = False):
        Platform.__init__(self, leftPoint, rightPoint, grabbable)
        self.solid = solid
        
        self.startPoint = self.rect.center
        self.endPoint = endPoint
        
        self.direction = self.getDirectionBetweenPoints(self.startPoint, self.endPoint)
        self.speed = moveSpeed
        self.delta_x, self.delta_y = self.getXYfromDM(self.direction,self.speed)
        self.change_x = 0
        self.change_y = 0
        
        self.real_x = 0
        self.real_y = 0
        print(self.delta_x, self.delta_y)
    
    def update(self):
        if self.rect.center == self.endPoint:
            #swap our destination, direction, and change_xy parameters
            tmp = self.endPoint
            self.endPoint = self.startPoint
            self.startPoint = tmp
            self.direction = self.getDirectionBetweenPoints(self.startPoint, self.endPoint)
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
        
        self.leftPoint = self.rect.topleft
        self.rightPoint = self.rect.topright
        
        self.xdist = max(1,self.rightPoint[0] - self.leftPoint[0])
        self.ydist = max(1,self.rightPoint[1] - self.leftPoint[1])
  
"""
Ledge object. This is what the fighter interacts with.
It has a parent platform, and a side of that platform.
Most of the attributes of the ledge are altered by the settings.
"""
class Ledge(pygame.sprite.Sprite):
    def __init__(self,plat,side):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect([0,0],settingsManager.getSetting('ledgeSweetspotSize'))
        self.side = side
        if side == 'left': self.rect.midtop = plat.leftPoint
        else: self.rect.midtop = [plat.rightPoint[0], plat.leftPoint[1]]
        self.fightersGrabbed = [] # this is a list in case "Ledge Conflict" is set to "share"
        
    """
    When a fighter wants to grab the ledge, this function is called.
    This function determines if a fighter is successful in his grab
    (which will call doLedgeGrab on the fighter). It will also
    pop opponents off if conflict is set to trump.
    """
    def fighterGrabs(self,fighter):
        if len(self.fightersGrabbed) == 0: # if no one's on the ledge, we don't care about conflict resolution
            self.fightersGrabbed.append(fighter)
            fighter.doLedgeGrab(self)
        else: # someone's already here
            conflict = settingsManager.getSetting('ledgeConflict')
            if conflict == 'share':
                self.fightersGrabbed.append(fighter)
                fighter.doLedgeGrab(self)
            elif conflict == 'hog':
                return
            elif conflict == 'trump':
                for other in self.fightersGrabbed:
                    self.fighterLeaves(other)
                    other.doGetTrumped()
                self.fightersGrabbed.append(fighter)
                fighter.doLedgeGrab(self)
    
    """
    A simple wrapper function to take someone off of the
    ledge grab list.
    """
    def fighterLeaves(self,fighter):
        self.fightersGrabbed.remove(fighter)
