import pygame
import math
import settingsManager
import spriteManager
import numpy

def checkGround(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.grounded = False
    _object.ecb.current_ecb.rect.y += 4
    ground_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(_object.ecb.current_ecb, _objectList, False)
    _object.ecb.current_ecb.rect.y -= 4
    for block in block_hit_list:
        if block.solid or (_object.platform_phase <= 0):
            if _object.ecb.current_ecb.rect.bottom <= block.rect.top+4 and (not _checkVelocity or (hasattr(_object, 'change_y') and hasattr(block, 'change_y') and _object.change_y > block.change_y-1)):
                _object.grounded = True
                ground_block.add(block)
    return ground_block

def checkLeftWall(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    if _object.facing == 1:
        _object.back_walled = False
    else:
        _object.front_walled = False
    _object.ecb.current_ecb.rect.x -= 4
    wall_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(_object.ecb.current_ecb, _objectList, False)
    _object.ecb.current_ecb.rect.x += 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.left >= block.rect.right-4 and (not _checkVelocity or (hasattr(_object, 'change_x') and hasattr(block, 'change_x') and _object.change_x < block.change_x+1)):
                if _object.facing == 1:
                    _object.back_walled = True
                else:
                    _object.front_walled = True
                wall_block.add(block)
    return wall_block

def checkRightWall(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    if _object.facing == 1:
        _object.front_walled = False
    else:
        _object.back_walled = False
    _object.ecb.current_ecb.rect.x += 4
    wall_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(_object.ecb.current_ecb, _objectList, False)
    _object.ecb.current_ecb.rect.x -= 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.right <= block.rect.left+4 and (not _checkVelocity or (hasattr(_object, 'change_x') and hasattr(block, 'change_x') and _object.change_x > block.change_x-1)):
                if _object.facing == 1:
                    _object.front_walled = True
                else:
                    _object.back_walled = True
                wall_block.add(block)
    return wall_block

def checkBackWall(_object, _objectList, _checkVelocity=True):
    if _object.facing == 1:
        _object.checkLeftWall(_object, _objectList, _checkVelocity)
    else:
        _object.checkRightWall(_object, _objectList, _checkVelocity)

def checkFrontWall(_object, _objectList, _checkVelocity=True):
    if _object.facing == 1:
        _object.checkRightWall(_object, _objectList, _checkVelocity)
    else:
        _object.checkLeftWall(_object, _objectList, _checkVelocity)

def checkCeiling(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.ceilinged = False
    _object.ecb.current_ecb.rect.y -= 4
    ceiling_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(_object.ecb.current_ecb, _objectList, False)
    _object.ecb.current_ecb.rect.y += 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.top >= block.rect.bottom-4 and (not _checkVelocity or (hasattr(_object, 'change_y') and hasattr(block, 'change_y') and _object.change_y < block.change_y+1)):
                _object.ceilinged = True
                ceiling_block.add(block)
    return ceiling_block

########################################################

def getMovementCollisionsWith(_object,_spriteGroup):
    future_rect = _object.ecb.current_ecb.rect.copy()
    future_rect.x += _object.change_x
    future_rect.y += _object.change_y
    collide_sprite = spriteManager.RectSprite(_object.ecb.current_ecb.rect.union(future_rect))
    return filter(lambda r: pathRectIntersects(_object.ecb.current_ecb.rect, future_rect, r.rect) <= 1, sorted(pygame.sprite.spritecollide(collide_sprite, _spriteGroup, False), key = lambda q: pathRectIntersects(_object.ecb.current_ecb.rect, future_rect, q.rect)))

def getSizeCollisionsWith(_object,_spriteGroup):
    return sorted(filter(lambda r: intersectPoint(_object.ecb.current_ecb.rect, r.rect) != None, pygame.sprite.spritecollide(_object.ecb.current_ecb, _spriteGroup, False)), key = lambda q: -numpy.linalg.norm(intersectPoint(_object.ecb.current_ecb.rect, q.rect)[0]))

def catchMovement(_object, _other, _platformPhase=False):
    _object.sprite.updatePosition(_object.rect)
    _object.ecb.normalize()
    check_rect = _other.rect.copy()

    future_rect = _object.ecb.current_ecb.rect.copy()
    future_rect.x += _object.change_x
    future_rect.y += _object.change_y
    t = pathRectIntersects(_object.ecb.current_ecb.rect, future_rect, check_rect)

    my_rect = _object.ecb.current_ecb.rect.copy()
    my_rect.x += t*(future_rect.x-_object.ecb.current_ecb.rect.x)
    my_rect.y += t*(future_rect.y-_object.ecb.current_ecb.rect.y)

    if _other.solid:
        contact = intersectPoint(my_rect, check_rect)
        if contact is None:
            return False
        v_vel = [_object.change_x-_other.change_x, _object.change_y-_other.change_y]
        return numpy.dot(contact[1], v_vel) < 0
    elif not _platformPhase:
        return checkPlatform(my_rect, _object.ecb.current_ecb.rect, check_rect, _object.change_y)
    else:
        return False
        
#Prepare for article usage
def eject(_object, _other, _platformPhase=False):
    _object.sprite.updatePosition(_object.rect)
    _object.ecb.normalize()
    check_rect = _other.rect.copy()
    contact = intersectPoint(_object.ecb.current_ecb.rect, check_rect)
    
    if _other.solid:
        if contact is not None:
            _object.rect.x += contact[0][0]
            _object.rect.y += contact[0][1]
            return reflect(_object, _other)
    else:
        new_prev = _object.ecb.current_ecb.rect.copy()
        new_prev.center = _object.ecb.previous_ecb.rect.center
        if not _platformPhase and checkPlatform(_object.ecb.current_ecb.rect, _object.ecb.previous_ecb.rect, check_rect, _object.change_y):
            if contact is not None:
                _object.rect.x += contact[0][0]
                _object.rect.y += contact[0][1]
                return reflect(_object, _other)
    return False

#Prepare for article usage
def reflect(_object, _other):
    if not hasattr(_object, 'elasticity'):
        _object.elasticity = 0
    if not hasattr(_object, 'ground_elasticity'):
        _object.ground_elasticity = 0
    _object.sprite.updatePosition(_object.rect)
    _object.ecb.normalize()
    check_rect = _other.rect.copy()
    contact = intersectPoint(_object.ecb.current_ecb.rect, check_rect)

    if contact is not None:
        #The contact vector is perpendicular to the axis over which the reflection should happen
        v_vel = [_object.change_x-_other.change_x, _object.change_y-_other.change_y]
        if numpy.dot(v_vel, contact[1]) < 0:
            v_norm = [contact[1][1], -contact[1][0]]
            dot = numpy.dot(v_norm, v_vel)
            norm = numpy.linalg.norm(v_norm)
            ratio = 1 if norm == 0 else dot/(norm*norm)
            projection = [v_norm[0]*ratio, v_norm[1]*ratio] #Projection of v_vel onto v_norm
            elasticity = _object.ground_elasticity if contact[1][1] < 0 else _object.elasticity
            _object.change_x = projection[0]+elasticity*(projection[0]-v_vel[0])+_other.change_x
            _object.change_y = projection[1]+elasticity*(projection[1]-v_vel[1])+_other.change_y
            return True
    return False

########################################################

#Prepare for article usage
def intersectPoint(_firstRect, _secondRect): 
    first_points = [_firstRect.midtop, _firstRect.midbottom, _firstRect.midleft, _firstRect.midright]
    second_points = [_secondRect.topleft, _secondRect.topright, _secondRect.bottomleft, _secondRect.bottomright]

    norm = numpy.linalg.norm([_firstRect.height, _firstRect.width])
    if norm == 0:
        norm = 1

    left_dist = [directionalDisplacement(first_points, second_points, [float(-1), float(0)]), [float(-1), float(0)]]
    right_dist = [directionalDisplacement(first_points, second_points, [float(1), float(0)]), [float(1), float(0)]]
    up_dist = [directionalDisplacement(first_points, second_points, [float(0), float(-1)]), [float(0), float(-1)]]
    down_dist = [directionalDisplacement(first_points, second_points, [float(0), float(1)]), [float(0), float(1)]]
    up_left_dist = [directionalDisplacement(first_points, second_points, [float(-_firstRect.height), float(-_firstRect.width)]), [float(-_firstRect.height)/norm, float(-_firstRect.width)/norm]]
    up_right_dist = [directionalDisplacement(first_points, second_points, [float(_firstRect.height), float(-_firstRect.width)]), [float(_firstRect.height)/norm, float(-_firstRect.width)/norm]]
    down_left_dist = [directionalDisplacement(first_points, second_points, [float(-_firstRect.height), float(_firstRect.width)]), [float(-_firstRect.height)/norm, float(_firstRect.width)/norm]]
    down_right_dist = [directionalDisplacement(first_points, second_points, [float(_firstRect.height), float(_firstRect.width)]), [float(_firstRect.height)/norm, float(_firstRect.width)/norm]]

    min_direction = min(left_dist, right_dist, up_dist, down_dist, up_left_dist, up_right_dist, down_left_dist, down_right_dist, key=lambda x: x[0][0]*x[1][0]+x[0][1]*x[1][1])
    if directionalDisplacement(first_points, second_points, min_direction[1]) < 0:
        return None
    else:
        return min_direction

#Prepare for article usage
def checkPlatform(_current, _previous, _platform, _yvel):
    intersect = intersectPoint(_current, _platform)
    if _platform.top >= _previous.bottom-4-_yvel and intersect is not None and intersect[1][1] < 0 and _current.bottom >= _platform.top:
        return True
    return False
    
#Prepare for article usage
def directionalDisplacement(_firstPoints, _secondPoints, _direction):
    #Given a direction to displace in, determine the displacement needed to get it out
    first_dots = map(lambda x: numpy.dot(x, _direction), _firstPoints)
    second_dots = map(lambda x: numpy.dot(x, _direction), _secondPoints)
    projected_displacement = max(second_dots)-min(first_dots)
    norm_sqr = 1.0 if _direction == [0, 0] else _direction[0]*_direction[0]+_direction[1]*_direction[1]
    return [projected_displacement/norm_sqr*_direction[0], projected_displacement/norm_sqr*_direction[1]]

# Returns a 2-entry array representing a range of time when the points and the rect intersect
# If the range's min is greater than its max, it represents an empty interval
#Prepare for article usage
def projectionIntersects(_startPoints, _endPoints, _rectPoints, _vector):
    start_dots = map(lambda x: numpy.dot(x, _vector), _startPoints)
    end_dots = map(lambda x: numpy.dot(x, _vector), _endPoints)
    rect_dots = map(lambda x: numpy.dot(x, _vector), _rectPoints)

    if min(start_dots) == min(end_dots):
        if min(start_dots) <= max(rect_dots): #.O.|...
            t_mins = [float("-inf"), float("inf")]
        else:                               #...|.O.
            t_mins = [float("inf"), float("-inf")]
    elif min(start_dots) > min(end_dots):
        t_mins = [float(max(rect_dots)-min(start_dots))/(min(end_dots)-min(start_dots)), float("inf")]
    else:
        t_mins = [float("-inf"), float(max(rect_dots)-min(start_dots))/(min(end_dots)-min(start_dots))]

    if max(start_dots) == max(end_dots):
        if max(start_dots) >= min(rect_dots): #...|.O.
            t_maxs = [float("-inf"), float("inf")]
        else:                               #.O.|...
            t_maxs = [float("inf"), float("-inf")]
    elif max(start_dots) < max(end_dots):
        t_maxs = [float(min(rect_dots)-max(start_dots))/(max(end_dots)-max(start_dots)), float("inf")]
    else:
        t_maxs = [float("-inf"), float(min(rect_dots)-max(start_dots))/(max(end_dots)-max(start_dots))]

    if max(end_dots)-max(start_dots) == min(end_dots)-min(start_dots):
        if max(start_dots) > min(start_dots):
            t_open = [float("-inf"), float("inf")]
        else:
            t_open = [float("inf"), float("-inf")]
    elif max(end_dots)-max(start_dots) > min(end_dots)-min(start_dots):
        t_open = [float("-inf"), float(max(end_dots)-max(start_dots)-min(end_dots)+min(start_dots))/(max(start_dots)-min(start_dots))]
    else:
        t_open = [float(max(end_dots)-max(start_dots)-min(end_dots)+min(start_dots))/(max(start_dots)-min(start_dots)), float("inf")]

    return [max(t_mins[0], t_maxs[0], t_open[0]), min(t_mins[1], t_maxs[1], t_open[1])]

#Prepare for article usage
def pathRectIntersects(_startRect, _endRect, _rect):
    if _startRect.colliderect(_rect):
        return 0
    start_corners = [_startRect.midtop, _startRect.midbottom, _startRect.midleft, _startRect.midright]
    end_corners = [_endRect.midtop, _endRect.midbottom, _endRect.midleft, _endRect.midright]
    rect_corners = [_rect.topleft, _rect.topright, _rect.bottomleft, _rect.bottomright]

    horizontal_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [1, 0])
    vertical_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [0, 1])
    downward_diagonal_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [_startRect.height, _startRect.width])
    upward_diagonal_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [-_startRect.height, _startRect.width])

    total_intersects = [max(horizontal_intersects[0], vertical_intersects[0], downward_diagonal_intersects[0], upward_diagonal_intersects[0], 0), min(horizontal_intersects[1], vertical_intersects[1], downward_diagonal_intersects[1], upward_diagonal_intersects[1], 1)]
    if total_intersects[0] > total_intersects[1]:
        return 999
    else:
        return total_intersects[0]

########################################################
#                       ECB                            #
########################################################        
class ECB():
    def __init__(self,_actor):
        self.actor = _actor

        if hasattr(self.actor, 'sprite'):
            self.current_ecb = spriteManager.RectSprite(self.actor.sprite.bounding_rect.copy(), pygame.Color('#ECB134'))
            self.current_ecb.rect.center = self.actor.sprite.bounding_rect.center
        else:
            self.current_ecb = spriteManager.RectSprite(self.actor.bounding_rect.copy(), pygame.Color('#ECB134'))
            self.current_ecb.rect.center = self.actor.bounding_rect.center
        self.original_size = self.current_ecb.rect.size

        self.previous_ecb = spriteManager.RectSprite(self.current_ecb.rect.copy(), pygame.Color('#EA6F1C'))
        
    """
    Resize the ECB. Give it a height, width, and center point.
    xoff is the offset from the center of the x-bar, where 0 is dead center, negative is left and positive is right
    yoff is the offset from the center of the y-bar, where 0 is dead center, negative is up and positive is down
    """
    def resize(self,_height,_width,_center,_xoff,_yoff):
        pass
    
    """
    Returns the dimensions of the ECB of the previous frame
    """
    def getPreviousECB(self):
        pass
    
    """
    This one moves the ECB without resizing it.
    """
    def move(self,_newCenter):
        self.current_ecb.rect.center = _newCenter
    
    """
    This stores the previous location of the ECB
    """
    def store(self):
        self.previous_ecb = spriteManager.RectSprite(self.current_ecb.rect,pygame.Color('#EA6F1C'))
    
    """
    Set the ECB's height and width to the sprite's, and centers it
    """
    def normalize(self):
        #center = (self.actor.sprite.bounding_rect.centerx + self.actor.current_action.ecb_center[0],self.actor.sprite.bounding_rect.centery + self.actor.current_action.ecb_center[1])
        sizes = self.actor.current_action.ecb_size
        offsets = self.actor.current_action.ecb_offset
        
        
        if sizes[0] == 0: 
            if hasattr(self.actor, 'sprite'):
                self.current_ecb.rect.width = self.actor.sprite.bounding_rect.width
            else:
                self.current_ecb.rect.width = self.actor.bounding_rect.width
        else:
            self.current_ecb.rect.width = sizes[0]
        if sizes[1] == 0: 
            if hasattr(self.actor, 'sprite'):
                self.current_ecb.rect.height = self.actor.sprite.bounding_rect.height
            else:
                self.current_ecb.rect.height = self.actor.bounding_rect.height
        else:
            self.current_ecb.rect.height = sizes[1]
        
        if hasattr(self.actor, 'sprite'):
            self.current_ecb.rect.center = self.actor.sprite.bounding_rect.center
        else:
            self.current_ecb.rect.center = self.actor.bounding_rect.center
        self.current_ecb.rect.x += offsets[0]
        self.current_ecb.rect.y += offsets[1]
        
    def draw(self,_screen,_offset,_scale):
        self.current_ecb.draw(_screen,self.actor.game_state.stageToScreen(self.current_ecb.rect),_scale)
        self.previous_ecb.draw(_screen,self.actor.game_state.stageToScreen(self.previous_ecb.rect),_scale)
