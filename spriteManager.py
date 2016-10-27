import pygame
import os
import sys
import math
import settingsManager

class Sprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.angle = 0
        self.scale = 1
        self.visible = True
        self.changed = False
        self.lastDrawnPosition = pygame.Rect(0,0,0,0)
        self.spriteOffset = (0,0)
        
    def draw(self,_screen,_offset,_scale):
        if not self.visible:
            return
        #TODO: Check for bit depth first, inform user about alpha
        h = int(self.scale*self.rect.height * _scale)
        w = int(self.scale*self.rect.width * _scale)
        unit_vector = [math.cos(math.radians(self.angle)), math.sin(math.radians(self.angle))]
        rotated_w = abs(w*unit_vector[0])+abs(h*unit_vector[1])
        rotated_h = abs(w*unit_vector[1])+abs(h*unit_vector[0])
        dx = (rotated_w-w)/2.0
        dy = (rotated_h-h)/2.0
        new_off = (int((_offset[0]+self.spriteOffset[0]*self.scale) * _scale - dx - (self.scale-1)*_scale*self.rect.width*.5), int((_offset[1]+self.spriteOffset[1]*self.scale) * _scale - dy - (self.scale-1)*_scale*self.rect.height*.5))
        try:
            blit_sprite = pygame.transform.smoothscale(self.image, (int(w), int(h)))
        except Exception as e:
            print(e)
            raise ValueError("Please use 32-bit PNG files")
        if self.angle != 0:
            blit_sprite = pygame.transform.rotate(blit_sprite,self.angle)
        new_rect = pygame.Rect(new_off,(int(rotated_w), int(rotated_h)))
        ret_rect = new_rect
        if not new_rect == self.lastDrawnPosition:
            self.changed = True
            ret_rect = new_rect.union(self.lastDrawnPosition)
            self.lastDrawnPosition = new_rect
        if self.changed:
            _screen.blit(blit_sprite,new_rect)
            self.changed = False
            return ret_rect
        _screen.blit(blit_sprite,new_rect) #Until this starts working
        return None
    
    def rotate(self,_angle = 0):
        self.angle = _angle
        self.changed = True
    
    
    def getColorIndexes(self,_color):
        import numpy as np
        arr = np.array(self.image)
        arr[arr < 10] = 0

    def getBoundingBox(self):
        bounding_rect = self.image.get_bounding_rect()
        bounding_rect.top += self.rect.top
        bounding_rect.left += self.rect.left
        return bounding_rect

    def updatePosition(self,_posx, _posy):
        self.rect.centerx = _posx
        self.rect.centery = _posy
        self.bounding_rect = self.getBoundingBox()
        self.changed = True
        
        
class SpriteHandler(Sprite):
    def __init__(self,_directory,_prefix,_startingImage,_offset,_colorMap = {},_scale=1.0):
        Sprite.__init__(self)
        self.color_map = _colorMap
        self.scale_factor = _scale
        self.image_library = self.buildImageLibrary(ImageLibrary(_directory,_prefix), _offset)
        
        self.starting_image = _startingImage
        
        self.flip = "right"
        if not self.starting_image in self.image_library[self.flip]:
            key_list = self.image_library[self.flip].keys()
            self.starting_image = key_list[0] 
            print("Default Sprite not found. New default sprite: " + str(self.starting_image))
            
        self.current_sheet = self.starting_image
        self.index = 0
        self.angle = 0
        
        print(self.image_library)
        self.image = self.image_library[self.flip][self.starting_image][self.index]
        
        self.rect = self.image.get_rect()
        self.bounding_rect = self.getBoundingBox()
        
    def flipX(self):
        if self.flip == "right": self.flip = "left"
        else: self.flip = "right"
        self.changed = True
                
    def changeImage(self,_newImage,_subImage = 0):
        self.current_sheet = _newImage
        self.index = _subImage
        self.get_image()
        self.changed = True
        
    def changeSubImage(self,_index,_loop=False):
        if _index < 0:
            _index = self.currentAnimLength() + _index
        if _loop:
            self.index = _index % self.currentAnimLength()
        else:
            self.index = min(_index, self.currentAnimLength()-1)
            
        self.get_image()
        self.changed = True
    
    def currentAnimLength(self):
        return len(self.image_library[self.flip][self.current_sheet])
    
    def get_image(self):
        try:
            self.image = self.image_library[self.flip][self.current_sheet][int(self.index)]
        except:
            print("Error loading sprite " + str(self.current_sheet) + " Loading default")
            self.image = self.image_library[self.flip][self.starting_image][0]
            self.current_sheet = self.starting_image
            
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)
        self.bounding_rect = self.getBoundingBox()
        return self.image
    
    def draw(self,_screen,_offset,_scale):
        self.get_image()
        return Sprite.draw(self,_screen,_offset,_scale)
    
    def buildImageLibrary(self,_lib,_offset):
        library = {}
        flipped_library = {}
        for key,value in _lib.image_dict.items():
            image_list = self.buildSubimage_list(value,_offset)
            library[key] = image_list
            flip_list = []
            for image in image_list:
                img = image.copy()
                img = pygame.transform.flip(img,True,False)
                flip_list.append(img)
            flipped_library[key] = flip_list

        return {"right": library, "left": flipped_library}
        
    def buildSubimage_list(self,_sheet,_offset):
        index = 0
        image_list = []
        while index < _sheet.get_width() // _offset:
            _sheet.set_clip(pygame.Rect(index * _offset, 0, _offset,_sheet.get_height()))
            image = _sheet.subsurface(_sheet.get_clip())
            for from_color,to_color in self.color_map.items():
                self.recolor(image, tuple(list(from_color)), tuple(list(to_color)))
            if not self.scale_factor == 1.0:
                w = int(image.get_width() * self.scale_factor)
                h = int(image.get_height() * self.scale_factor)
                image = pygame.transform.scale(image, (w,h))
            image_list.append(image)
            index += 1
        return image_list
    
    def recolor(self,_image,_fromColor,_toColor):
        arr = pygame.PixelArray(_image)
        arr.replace(_fromColor,_toColor)
        del arr
        self.changed = True
        
            
class ImageSprite(Sprite):
    def __init__(self,_path):
        Sprite.__init__(self)
        self.path = _path
        self.image = pygame.image.load(_path)
        self.rect = self.image.get_rect()
        self.bounding_rect = self.getBoundingBox()
    
    def color_surface(self,_color,_alpha):
        arr = pygame.surfarray.pixels3d(self.image)
        arr[:,:,0] = _color[0]
        arr[:,:,1] = _color[1]
        arr[:,:,2] = _color[2]
        del arr
        self.changed = True
    
    def alpha(self,_newAlpha):
        arr = pygame.surfarray.pixels_alpha(self.image)
        arr[arr!=0] = _newAlpha
        del arr
        self.changed = True
    
    def recolor(self,_image,_fromColor,_toColor,_ignoreAlpha=False):
        arr = pygame.PixelArray(_image)
        arr.replace(_fromColor,_toColor)
        del arr
        self.changed = True
        
class SheetSprite(ImageSprite):
    def __init__(self,_sheet,_offset=0,_colorMap = {}):
        Sprite.__init__(self)
        
        self.sheet = _sheet
        if isinstance(_sheet,str) or isinstance(_sheet, unicode):
            self.sheet = pygame.image.load(_sheet)
        
        self.color_map = _colorMap
        self.index = 0
        self.max_index = self.sheet.get_width() // _offset
        self.offset = _offset
        
        
        if self.offset > 0:
            self.image_list = self.buildSubimage_list(self.sheet,_offset)
        else:
            self.image_list = [self.sheet]
            
        self.flip = False
        self.angle = 0
        
        self.image = self.image_list[0]
        self.rect = self.image.get_rect()
        self.bounding_rect = self.getBoundingBox()
    
    def buildSubimage_list(self,_sheet,_offset):
        index = 0
        
        image_list = []
        while index < self.max_index:
            self.sheet.set_clip(pygame.Rect(index * _offset, 0, _offset,_sheet.get_height()))
            image = _sheet.subsurface(_sheet.get_clip())
            #image = image.convert_alpha()
            for from_color,to_color in self.color_map.items():
                self.recolor(image, tuple(list(from_color)), tuple(list(to_color)))
            image_list.append(image)
            index += 1
        return image_list
    
    def flipX(self):
        self.flip = not self.flip
        self.image = pygame.transform.flip(self.image,True,False)
        self.changed = True
        
    def recolor(self,_image,_fromColor,_toColor):
        arr = pygame.PixelArray(_image)
        arr.replace(_fromColor,_toColor)
        del arr
        self.changed = True
        
    def getImageAtIndex(self,_index):
        self.index = _index % self.max_index
        self.image = self.image_list[self.index]
        if self.flip:
            self.image = pygame.transform.flip(self.image,True,False)
        self.changed = True
        return self.image
        
    def draw(self,_screen,_offset,_scale):
        return Sprite.draw(self, _screen, _offset, _scale)
    
    def changeImage(self,_newImage,_subImage = 0):
        pass
                    
class MaskSprite(ImageSprite):
    def __init__(self, _parentSprite,_color,_duration,_pulse = False,_pulseSize = 16):
        Sprite.__init__(self)
        self.parent_sprite = _parentSprite
        self.duration = _duration
        self.pulse = _pulse
        self.pulse_size = _pulseSize
        self.color = _color
        if self.pulse: self.alpha = 200
        else: self.alpha = 128
        self.visible = True
        
        self.image = self.parent_sprite.image.copy()
        self.rect = self.parent_sprite.rect
        
        self.color_surface(self.color)
        
        
    def color_surface(self,_color):
        arr = pygame.surfarray.pixels3d(self.image)
        arr[:,:,0] = _color[0]
        arr[:,:,1] = _color[1]
        arr[:,:,2] = _color[2]
        del arr
        
        arr = pygame.surfarray.pixels_alpha(self.image)
        arr[arr!=0] = self.alpha
        del arr
        self.changed = True
        
    
    def update(self):
        if not self.duration == 0:
            if self.pulse:
                self.alpha -= self.pulse_size
                if self.alpha > 200:
                    self.alpha = 200
                    self.pulse_size = -self.pulse_size
                elif self.alpha < 16:
                    self.alpha = 16
                    self.pulse_size = -self.pulse_size
            self.duration -= 1
            self.image = self.parent_sprite.image.copy()
            self.color_surface(self.color)
            
            self.rect = self.parent_sprite.rect
            
            return self
        else:
            if not hasattr(self, 'rect'):
                self.rect = self.parent_sprite.rect
            return None

class TextSprite(ImageSprite):
    def __init__(self,_text,_font="Orbitron Medium",_size=12,_color=[0,0,0]):
        Sprite.__init__(self)
        self.font = pygame.font.Font(settingsManager.createPath(_font+".ttf"),_size)
            
        self.image = self.font.render(_text,False,_color).convert_alpha()
        self.rect = self.image.get_rect()
        
        self.text = _text
        self.color = _color
        
    def changeColor(self,_color):
        self.image = self.font.render(self.text,False,_color).convert_alpha()
        self.color = _color
        self.changed = True
        
    def changeText(self,_text):
        self.image = self.font.render(_text,False,self.color).convert_alpha()
        self.text = _text
        self.rect = self.image.get_rect(center=self.rect.center)
        self.changed = True
        
class ImageLibrary():
    def __init__(self,_directory,_prefix=""):
        self.directory = os.path.join(os.path.dirname(__file__).replace('main.exe',''),_directory)
        if _prefix is None: _prefix=''
        self.image_dict = {}
        supported_file_types = [".jpg",".png",".gif",".bmp",".pcx",".tga",".tif",".lbm",".pbm",".xpm"]
        
        for f in os.listdir(self.directory):
            fname, ext = os.path.splitext(f)
            if fname.startswith(_prefix) and supported_file_types.count(ext):
                sprite_name = fname[len(_prefix):]
                sprite = pygame.image.load(os.path.join(self.directory,f))
                sprite = sprite.convert_alpha()
                self.image_dict[sprite_name] = sprite
                #print(sprite.get_alpha(), sprite_name, self.image_dict[sprite_name])

class RectSprite(Sprite):
    def __init__(self,_rect,_color=[0,0,0]):
        Sprite.__init__(self)
        
        self.color = _color  
        
        self.image = pygame.Surface(_rect.size)
        self.image.fill(self.color)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = _rect.topleft    
        self.bounding_rect = self.getBoundingBox()
        
        self.image.set_alpha(128)
        
def test():
    pygame.init()
    screen = pygame.display.set_mode([640,480])
    pygame.display.set_caption("USS Sprite Viewer")
    sprites = SpriteHandler("fighters/hitboxie/sprites", "hitboxie_", "run", 92, {(0,0,0)       : (0,0,255),
                                                                                   (128,128,128) : (0,0,128),
                                                                                   (166,166,166) : (0,0,200)})
    clock = pygame.time.Clock()
    index = 0
    
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1
            if event.type == pygame.KEYDOWN:
                sprites.flipX()
        
        screen.fill([100, 100, 100])
        
        
        sprites.draw(screen, [0,0], 1.0)
        sprites.changeSubImage(index)
        index += 1
        
        clock.tick(20)    
        pygame.display.flip()
    
if __name__  == '__main__': test()      
