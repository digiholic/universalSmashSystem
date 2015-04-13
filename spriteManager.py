import pygame
import os
from _ctypes import Array

class Sprite(pygame.sprite.Sprite):
    
    def draw(self,screen,offset,scale):
        #TODO: Check for bit depth first, inform user about alpha
        h = int(round(self.rect.height * scale))
        w = int(round(self.rect.width * scale))
        newOff = (int(offset[0] * scale), int(offset[1] * scale))
        blitSprite = pygame.transform.smoothscale(self.image, (w,h))
        screen.blit(blitSprite,pygame.Rect(newOff,(w,h)))
        
class ImageSprite(Sprite):
    def __init__(self,directory,prefix,startingImage,offset,colorMap = {}):
        self.colorMap = colorMap
        self.imageLibrary = self.buildImageLibrary(ImageLibrary(directory,prefix), offset)
        self.currentSprite = self.imageLibrary[startingImage]
        
        self.startingImage = startingImage
        self.rect = self.currentSprite.image.get_rect().center
        self.flip = False
        self.angle = 0
        
    def buildImageLibrary(self,lib,offset):
        library = {}
        for key,value in lib.imageDict.iteritems():
            library[key] = SheetSprite(value,offset,self.colorMap)
        return library
    
    def getImageAtIndex(self,index):
        self.index = index
        self.changeImage(self.imageText + str(self.index))
        
    def flipX(self):
        self.flip = not self.flip
        
    def changeImage(self,newImage):
        try:
            self.currentSprite = self.imageLibrary[newImage]
            if self.flip: self.image = pygame.transform.flip(self.currentSprite.image,True,False)
            self.rect = self.currentSprite.image.get_rect(center=self.rect.center)
        except:
            print "Error loading sprite ", newImage, " Loading default"
            self.currentSprite = self.imageLibrary[self.startingImage]
    
    def changeSubImage(self,index):
        self.currentSprite.getImageAtIndex(index)
        
    def draw(self,screen,offset,scale):
        self.currentSprite.draw(screen,offset,scale)

class SheetSprite(ImageSprite):
    def __init__(self,sheet,offset=0,colorMap = {}):
        Sprite.__init__(self)
        
        self.colorMap = colorMap
        self.index = 0
        self.maxIndex = sheet.get_width() / offset
        self.offset = offset
        
        self.sheet = sheet
        
        if self.offset > 0:
            self.imageList = self.buildSubimageList(sheet,offset)
        else:
            self.imageList = [sheet]
            
        self.flip = False
        self.angle = 0
        
        self.image = self.imageList[0]
        self.rect = self.image.get_rect()
    
    def buildSubimageList(self,sheet,offset):
        index = 0
        
        imageList = []
        while index < self.maxIndex:
            self.sheet.set_clip(pygame.Rect(index * offset, 0, offset,sheet.get_height()))
            image = sheet.subsurface(sheet.get_clip())
            #image = image.convert_alpha()
            for fromColor,toColor in self.colorMap.iteritems():
                self.recolor(image, list(fromColor), list(toColor))
            imageList.append(image)
            index += 1
        return imageList
    
    def recolor(self,image,fromColor,toColor):
        
        arr = pygame.PixelArray(image)
        arr.replace(fromColor,toColor)
        del arr  
        
    def getImageAtIndex(self,index):
        self.index = index % self.maxIndex
        self.image = self.imageList[self.index]
        
    def draw(self,screen,offset,scale):
        Sprite.draw(self, screen, offset, scale)
        
class MaskSprite(ImageSprite):
    def __init__(self, parentSprite,color,duration,pulse = False,pulseSize = 16):
        self.parentSprite = parentSprite
        self.duration = duration
        self.pulse = pulse
        self.pulseSize = pulseSize
        self.color = color
        if self.pulse: self.alpha = 200
        else: self.alpha = 128
        self.visible = True
        
        self.image = self.parentSprite.image.copy()
        self.color_surface(self.color)
        
        
    def color_surface(self,color):
        arr = pygame.surfarray.pixels3d(self.image)
        arr[:,:,0] = color[0]
        arr[:,:,1] = color[1]
        arr[:,:,2] = color[2]
        del arr
        
        arr = pygame.surfarray.pixels_alpha(self.image)
        arr[arr>self.alpha] = self.alpha
        del arr
        
    
    def update(self):
        if self.duration > 0:
            if self.pulse:
                self.alpha -= self.pulseSize
                if self.alpha > 200:
                    self.alpha = 200
                    self.pulseSize = -self.pulseSize
                elif self.alpha < 0:
                    self.alpha = 0
                    self.pulseSize = -self.pulseSize 
            self.duration -= 1
            self.image = self.parentSprite.image.copy()
            self.color_surface(self.color)
            
            self.rect = self.parentSprite.rect
            
            return self
        else:
            return None

class ImageLibrary():
    def __init__(self,directory,prefix=""):
        self.directory = os.path.join(os.path.dirname(__file__),directory)
        self.imageDict = {}
        supportedFileTypes = [".jpg",".png",".gif",".bmp",".pcx",".tga",".tif",".lbm",".pbm",".xpm"]
             
        for f in os.listdir(self.directory):
            fname, ext = os.path.splitext(f)
            if fname.startswith(prefix) and supportedFileTypes.count(ext):
                spriteName = fname[len(prefix):]
                sprite = pygame.image.load(os.path.join(self.directory,f))
                sprite = sprite.convert_alpha()
                self.imageDict[spriteName] = sprite
                print sprite.get_alpha(), spriteName, self.imageDict[spriteName]

def test():
    pygame.init()
    screen = pygame.display.set_mode([640,480])
    pygame.display.set_caption("USS Sprite Viewer")
    sprites = ImageSprite("fighters/hitboxie/sprites", "hitboxie_", "dsmash", 92, {(0,0,0)       : (0,0,255),
                                                                                   (128,128,128) : (0,0,128),
                                                                                   (166,166,166) : (0,0,200)})
    clock = pygame.time.Clock()
    index = 0
    
    while 1:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1
        
        screen.fill([100, 100, 100])
        
        
        sprites.draw(screen, [0,0], 1.0)
        sprites.changeSubImage(index)
        index += 1
        
        clock.tick(20)    
        pygame.display.flip()
    
if __name__  == '__main__': test()      