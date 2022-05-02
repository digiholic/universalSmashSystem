import pygame
import math
import settingsManager
import spriteManager
import numpy
import copy

def checkGround(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.ecb.current_ecb.rect.y += 4
    collide_sprite = spriteManager.RectSprite(_object.ecb.current_ecb.rect.union(_object.ecb.previous_ecb.rect))
    ground_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(collide_sprite, _objectList, False)
    _object.ecb.current_ecb.rect.y -= 4
    for block in block_hit_list:
        if block.solid or (_object.platform_phase <= 0):
            if _object.ecb.current_ecb.rect.bottom <= block.rect.top+4 and (not _checkVelocity or (hasattr(_object, 'change_y') and hasattr(block, 'change_y') and _object.change_y > block.change_y-1)):
                ground_block.add(block)
            else:
                print(_object.ecb.current_ecb.rect.bottom, block.rect.top+4)
    return ground_block

def checkLeftWall(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.ecb.current_ecb.rect.x -= 4
    collide_sprite = spriteManager.RectSprite(_object.ecb.current_ecb.rect.union(_object.ecb.previous_ecb.rect))
    wall_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(collide_sprite, _objectList, False)
    _object.ecb.current_ecb.rect.x += 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.left >= block.rect.right-4 and (not _checkVelocity or (hasattr(_object, 'change_x') and hasattr(block, 'change_x') and _object.change_x < block.change_x+1)):
                wall_block.add(block)
    return wall_block

def checkRightWall(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.ecb.current_ecb.rect.x += 4
    collide_sprite = spriteManager.RectSprite(_object.ecb.current_ecb.rect.union(_object.ecb.previous_ecb.rect))
    wall_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(collide_sprite, _objectList, False)
    _object.ecb.current_ecb.rect.x -= 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.right <= block.rect.left+4 and (not _checkVelocity or (hasattr(_object, 'change_x') and hasattr(block, 'change_x') and _object.change_x > block.change_x-1)):
                wall_block.add(block)
    return wall_block

def checkBackWall(_object, _objectList, _checkVelocity=True):
    if _object.facing == 1:
        return checkLeftWall(_object, _objectList, _checkVelocity)
    else:
        return checkRightWall(_object, _objectList, _checkVelocity)

def checkFrontWall(_object, _objectList, _checkVelocity=True):
    if _object.facing == 1:
        return checkRightWall(_object, _objectList, _checkVelocity)
    else:
        return checkLeftWall(_object, _objectList, _checkVelocity)

def checkCeiling(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.ecb.current_ecb.rect.y -= 4
    collide_sprite = spriteManager.RectSprite(_object.ecb.current_ecb.rect.union(_object.ecb.previous_ecb.rect))
    ceiling_block = pygame.sprite.Group()
    block_hit_list = pygame.sprite.spritecollide(collide_sprite, _objectList, False)
    _object.ecb.current_ecb.rect.y += 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.top >= block.rect.bottom-4 and (not _checkVelocity or (hasattr(_object, 'change_y') and hasattr(block, 'change_y') and _object.change_y < block.change_y+1)):
                ceiling_block.add(block)
    return ceiling_block


def isGrounded(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.ecb.current_ecb.rect.y += 4
    collide_sprite = spriteManager.RectSprite(_object.ecb.current_ecb.rect.union(_object.ecb.previous_ecb.rect))
    block_hit_list = pygame.sprite.spritecollide(collide_sprite, _objectList, False)
    _object.ecb.current_ecb.rect.y -= 4
    for block in block_hit_list:
        if block.solid or (_object.platform_phase <= 0):
            if (_object.ecb.current_ecb.rect.bottom <= block.rect.top+4) and (not _checkVelocity or (hasattr(_object, 'change_y') and hasattr(block, 'change_y') and _object.change_y > block.change_y-1)):
                return True
    return False

def isLeftWalled(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.ecb.current_ecb.rect.x -= 4
    collide_sprite = spriteManager.RectSprite(_object.ecb.current_ecb.rect.union(_object.ecb.previous_ecb.rect))
    block_hit_list = pygame.sprite.spritecollide(collide_sprite, _objectList, False)
    _object.ecb.current_ecb.rect.x += 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.left >= block.rect.right-4 and (not _checkVelocity or (hasattr(_object, 'change_x') and hasattr(block, 'change_x') and _object.change_x < block.change_x+1)):
                return True
    return False

def isRightWalled(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.ecb.current_ecb.rect.x += 4
    collide_sprite = spriteManager.RectSprite(_object.ecb.current_ecb.rect.union(_object.ecb.previous_ecb.rect))
    block_hit_list = pygame.sprite.spritecollide(collide_sprite, _objectList, False)
    _object.ecb.current_ecb.rect.x -= 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.right <= block.rect.left+4 and (not _checkVelocity or (hasattr(_object, 'change_x') and hasattr(block, 'change_x') and _object.change_x > block.change_x-1)):
                return True
    return False

def isBackWalled(_object, _objectList, _checkVelocity=True):
    if _object.facing == 1:
        return isLeftWalled(_object, _objectList, _checkVelocity)
    else:
        return isRightWalled(_object, _objectList, _checkVelocity)

def isFrontWalled(_object, _objectList, _checkVelocity=True):
    if _object.facing == 1:
        return isRightWalled(_object, _objectList, _checkVelocity)
    else:
        return isLeftWalled(_object, _objectList, _checkVelocity)

def isCeilinged(_object, _objectList, _checkVelocity=True):
    _object.ecb.normalize()
    _object.ecb.current_ecb.rect.y -= 4
    collide_sprite = spriteManager.RectSprite(_object.ecb.current_ecb.rect.union(_object.ecb.previous_ecb.rect))
    block_hit_list = pygame.sprite.spritecollide(collide_sprite, _objectList, False)
    _object.ecb.current_ecb.rect.y += 4
    for block in block_hit_list:
        if block.solid:
            if _object.ecb.current_ecb.rect.top >= block.rect.bottom-4 and (not _checkVelocity or (hasattr(_object, 'change_y') and hasattr(block, 'change_y') and _object.change_y < block.change_y+1)):
                return True
    return False

########################################################

def getMovementCollisionsWith(_object,_spriteGroup):
    future_rect = _object.ecb.current_ecb.rect.copy()
    future_rect.x += _object.change_x
    future_rect.y += _object.change_y
    collide_sprite = spriteManager.RectSprite(_object.ecb.current_ecb.rect.union(future_rect))
    check_dict = {k: _object.ecb.pathRectIntersects(k.rect, _object.change_x, _object.change_y) for k in pygame.sprite.spritecollide(collide_sprite, _spriteGroup, False)}
    return sorted(filter(lambda k: check_dict[k] <= 1, check_dict), key=lambda q: check_dict[q])

def getSizeCollisionsWith(_object,_spriteGroup):
    check_dict = filter(lambda r: _object.ecb.doesIntersect(r.rect), pygame.sprite.spritecollide(_object.ecb.current_ecb, _spriteGroup, False))
    return sorted(check_dict, key = lambda q: numpy.linalg.norm(_object.ecb.primaryEjection(q.rect)[0]))

def catchMovement(_object, _other, _platformPhase=False):
    check_rect = _other.rect.copy()
    t = _object.ecb.pathRectIntersects(check_rect, _object.change_x, _object.change_y)

    if _other.solid:
        if not _object.ecb.doesIntersect(check_rect, _dx=t*(_object.change_x), _dy=t*(_object.change_y)):
            return False
        contact = _object.ecb.primaryEjection(check_rect, _dx=t*(_object.change_x), _dy=t*(_object.change_y))
        v_vel = [_object.change_x-_other.change_x, _object.change_y-_other.change_y]
        return numpy.dot(contact[1], v_vel) < 0
    elif not _platformPhase:
        return _object.ecb.interceptPlatform(check_rect, _dx=t*(_object.change_x), _dy=t*(_object.change_y), _yvel=_object.change_y-_other.change_y)
    else:
        return False
        
#Prepare for article usage
def eject(_object, _other, _platformPhase=False):
    _object.updatePosition()
    _object.ecb.normalize()
    check_rect = _other.rect.copy()
    
    if _other.solid:
        if _object.ecb.doesIntersect(check_rect):
            contact = _object.ecb.primaryEjection(check_rect)
            _object.posx += contact[0][0]
            _object.posy += contact[0][1]
            return reflect(_object, _other)
    else:
        if not _platformPhase and _object.ecb.checkPlatform(check_rect, _object.change_y-_other.change_y):
            if _object.ecb.doesIntersect(check_rect):
                contact = _object.ecb.primaryEjection(check_rect)
                _object.posx += contact[0][0]
                _object.posy += contact[0][1]
                return reflect(_object, _other)
    return False

#Prepare for article usage
def reflect(_object, _other):
    if not hasattr(_object, 'elasticity'):
        _object.elasticity = 0.0
    if not hasattr(_object, 'ground_elasticity'):
        _object.ground_elasticity = 0.0
    _object.updatePosition()
    _object.ecb.normalize()
    check_rect = _other.rect.copy()

    if _object.ecb.doesIntersect(check_rect):
        contact = _object.ecb.primaryEjection(check_rect)
        #The contact vector is perpendicular to the axis over which the reflection should happen
        v_vel = [_object.change_x-_other.change_x, _object.change_y-_other.change_y]
        if (numpy.dot(v_vel, contact[1]) < 0 or True):
            v_norm = [contact[1][1], -contact[1][0]]
            dot = numpy.dot(v_norm, v_vel)
            projection = [v_norm[0]*dot, v_norm[1]*dot] #Projection of v_vel onto v_norm
            elasticity = _object.ground_elasticity if contact[1][1] < 0 else _object.elasticity
            _object.change_x = projection[0]+elasticity*(projection[0]-v_vel[0])+_other.change_x
            _object.change_y = projection[1]+elasticity*(projection[1]-v_vel[1])+_other.change_y
            return True
    return False

########################################################

#Not used anymore, but kept around
def directionalDisplacement(_firstPoints, _secondPoints, _direction):
    #Given a direction to displace in, determine the displacement needed to get it out
    first_dots = numpy.inner(_firstPoints, _direction)
    second_dots = numpy.inner(_secondPoints, _direction)
    projected_displacement = max(second_dots)-min(first_dots)
    norm_sqr = 1.0 if _direction == [0, 0] else _direction[0]*_direction[0]+_direction[1]*_direction[1]
    return [projected_displacement/norm_sqr*_direction[0], projected_displacement/norm_sqr*_direction[1]]

def directionalDisplacements(_firstRect, _secondRect):
    norm = numpy.linalg.norm([_firstRect.width, _firstRect.height])
    directions = numpy.array([[float(-1), float(0)], [float(1), float(0)], [float(0), float(-1)], [float(0), float(1)], [-_firstRect.height/norm, -_firstRect.width/norm], [_firstRect.height/norm, -_firstRect.width/norm], [-_firstRect.height/norm, _firstRect.width/norm], [_firstRect.height/norm, _firstRect.width/norm]])
    first_points = numpy.array([_firstRect.midtop, _firstRect.midbottom, _firstRect.midleft, _firstRect.midright])
    second_points = numpy.array([_secondRect.topleft, _secondRect.topright, _secondRect.bottomleft, _secondRect.bottomright])
    first_dots = numpy.inner(first_points, directions)
    second_dots = numpy.inner(second_points, directions)
    projected_displacements = numpy.amax(second_dots, 0) - numpy.amin(first_dots, 0)
    return numpy.stack((directions*projected_displacements.reshape((8, 1)), directions.reshape((8, 2))), axis=1)

# Returns a 2-entry array representing a range of time when the points and the rect intersect
# If the range's min is greater than its max, it represents an empty interval
#Prepare for article usage
def projectionIntersects(_startPoints, _endPoints, _rectPoints, _vector):
    start_dots = numpy.inner(_startPoints, _vector)
    end_dots = numpy.inner(_endPoints, _vector)
    rect_dots = numpy.inner(_rectPoints, _vector)

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

########################################################
#                       ECB                            #
########################################################        
class ECB():
    def __init__(self,_actor):
        self.actor = _actor

        self.current_ecb = spriteManager.RectSprite(self.actor.sprite.bounding_rect.copy(), pygame.Color('#ECB134'))
        self.current_ecb.rect.center = self.actor.sprite.bounding_rect.center

        self.original_size = self.current_ecb.rect.size
        self.tracking_rect = self.current_ecb.rect.copy()
        self.game_state = self.actor.game_state

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
        self.tracking_rect.center = self.actor.posx, self.actor.posy
    
    """
    Set the ECB's height and width to the sprite's, and centers it
    """
    def normalize(self):
        if hasattr(self.actor, 'current_action'):
            sizes = self.actor.current_action.ecb_size
            offsets = self.actor.current_action.ecb_offset
        else:
            sizes = self.actor.ecb_size
            offsets = self.actor.ecb_offset
        
        sizes = list(sizes)
        offsets = list(offsets)
        
        if sizes and offsets:
            if sizes[0] == 0: 
                self.current_ecb.rect.width = self.actor.sprite.bounding_rect.width
            else:
                self.current_ecb.rect.width = sizes[0]
            if sizes[1] == 0: 
                self.current_ecb.rect.height = self.actor.sprite.bounding_rect.height
            else:
                self.current_ecb.rect.height = sizes[1]
            
            self.current_ecb.rect.center = self.actor.sprite.bounding_rect.center

            self.current_ecb.rect.x += offsets[0]
            self.current_ecb.rect.y += offsets[1]
        
    def draw(self,_screen,_offset,_scale):
        self.current_ecb.draw(_screen,self.actor.game_state.stageToScreen(self.current_ecb.rect),_scale)
        self.previous_ecb.draw(_screen,self.actor.game_state.stageToScreen(self.previous_ecb.rect),_scale)

    def doesIntersect(self, _other, _dx=0, _dy=0):
        test_rect = self.current_ecb.rect.copy()
        test_rect.x += _dx
        test_rect.y += _dy

        displacements = directionalDisplacements(test_rect, _other)
        return all(map(lambda k: numpy.dot(k[0], k[1]) >= 0, displacements))

    def intersectPoint(self, _other, _dx=0, _dy=0):
        test_rect = self.current_ecb.rect.copy()
        test_rect.x += _dx
        test_rect.y += _dy

        distances = directionalDisplacements(test_rect, _other)
        return min(distances, key=lambda x: x[0][0]*x[1][0]+x[0][1]*x[1][1])

    def ejectionDirections(self, _other, _dx=0, _dy=0):
        test_rect = self.current_ecb.rect.copy()
        test_rect.x += _dx
        test_rect.y += _dy

        distances = directionalDisplacements(test_rect, _other)

        working_list = filter(lambda e: numpy.dot(e[0], e[1]) >= 0, distances)
        reference_list = copy.deepcopy(working_list)
        for element in reference_list:
            working_list = filter(lambda k: abs(numpy.dot(k[0], element[1]) - numpy.dot(element[0], element[1])) > 0.01 or numpy.allclose(k[0], element[0]), working_list)
        return working_list

    def primaryEjection(self, _other, _dx=0, _dy=0):
        good_directions = self.ejectionDirections(_other, _dx, _dy)
        distances = directionalDisplacements(self.previous_ecb.rect, _other)
        previous_dir = min(distances, key=lambda x: x[0][0]*x[1][0]+x[0][1]*x[1][1])
        return min(good_directions, key=lambda y: -numpy.dot(previous_dir[1], y[0])+numpy.linalg.norm(y[0]))
        #return min(good_directions, key=lambda y: numpy.linalg.norm(y[0]))

    def checkPlatform(self, _platform, _yvel):
        distances = directionalDisplacements(self.previous_ecb.rect, _platform)

        intersect = min(distances, key=lambda x: x[0][0]*x[1][0]+x[0][1]*x[1][1])

        if _platform.top >= self.previous_ecb.rect.bottom-4-_yvel and numpy.dot(intersect[0], intersect[1]) >= 0 and intersect[1][1] < 0 and self.current_ecb.rect.bottom >= _platform.top:
            return True
        return False

    def interceptPlatform(self, _platform, _dx, _dy, _yvel):
        intersect = self.intersectPoint(_platform, _dx, _dy)
        if _platform.top >= self.current_ecb.rect.bottom+_dy-4-_yvel and numpy.dot(intersect[0], intersect[1]) >= 0 and intersect[1][1] < 0 and self.current_ecb.rect.bottom+_dy >= _platform.top:
            return True
        return False

    def pathRectIntersects(self, _platform, _dx, _dy):
        if self.current_ecb.rect.colliderect(_platform):
            return 0
        start_corners = [self.current_ecb.rect.midtop, self.current_ecb.rect.midbottom, self.current_ecb.rect.midleft, self.current_ecb.rect.midright]
        end_corners = [[self.current_ecb.rect.centerx+_dx, self.current_ecb.rect.top+_dy], 
                       [self.current_ecb.rect.centerx+_dx, self.current_ecb.rect.bottom+_dy],
                       [self.current_ecb.rect.left+_dx, self.current_ecb.rect.centery+_dy], 
                       [self.current_ecb.rect.right+_dx, self.current_ecb.rect.centery+_dy]]
        rect_corners = [_platform.topleft, _platform.topright, _platform.bottomleft, _platform.bottomright]
    
        horizontal_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [1, 0])
        vertical_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [0, 1])
        downward_diagonal_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [self.current_ecb.rect.height, self.current_ecb.rect.width])
        upward_diagonal_intersects = projectionIntersects(start_corners, end_corners, rect_corners, [-self.current_ecb.rect.height, self.current_ecb.rect.width])

        total_intersects = [max(horizontal_intersects[0], vertical_intersects[0], downward_diagonal_intersects[0], upward_diagonal_intersects[0], 0), min(horizontal_intersects[1], vertical_intersects[1], downward_diagonal_intersects[1], upward_diagonal_intersects[1], 1)]
        if total_intersects[0] > total_intersects[1]:
            return 999
        else:
            return total_intersects[0]
