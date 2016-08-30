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

#Prepare for article usage
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

#Prepare for article usage
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

#Prepare for article usage
def checkBackWall(_object, _objectList, _checkVelocity=True):
    if _object.facing == 1:
        _object.checkLeftWall(_object, _objectList, _checkVelocity)
    else:
        _object.checkRightWall(_object, _objectList, _checkVelocity)

#Prepare for article usage
def checkFrontWall(_object, _objectList, _checkVelocity=True):
    if _object.facing == 1:
        _object.checkRightWall(_object, _objectList, _checkVelocity)
    else:
        _object.checkLeftWall(_object, _objectList, _checkVelocity)

#Prepare for article usage
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
#                       ECB                            #
########################################################        
class ECB():
    def __init__(self,_actor):
        self.actor = _actor

        self.current_ecb = spriteManager.RectSprite(self.actor.sprite.bounding_rect.copy(), pygame.Color('#ECB134'))
        self.original_size = self.current_ecb.rect.size
        self.current_ecb.rect.center = self.actor.sprite.bounding_rect.center

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
