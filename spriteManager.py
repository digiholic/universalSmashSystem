import pygame
import os
import sys
import settingsManager

class Sprite(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.angle = 0
    
    def draw(self,screen,offset,scale):
        #TODO: Check for bit depth first, inform user about alpha
        h = int(round(self.rect.height * scale))
        w = int(round(self.rect.width * scale))
        newOff = (int(offset[0] * scale), int(offset[1] * scale))
        try:
            blitSprite = pygame.transform.smoothscale(self.image, (w,h))
        except Exception as e:
            print e
            print "Please use 32-bit PNG files"
            sys.exit()
        if self.angle != 0:
            blitSprite = pygame.transform.rotate(blitSprite,self.angle)
        screen.blit(blitSprite,pygame.Rect(newOff,(w,h)))
  
class SpriteHandler(Sprite):
    def __init__(self,directory,prefix,startingImage,offset,colorMap = {}):
        Sprite.__init__(self)
        self.colorMap = colorMap
        self.imageLibrary = self.buildImageLibrary(ImageLibrary(directory,prefix), offset)
        
        self.startingImage = startingImage
         
        self.flip = "right"
        self.currentSheet = startingImage
        self.index = 0
        self.angle = 0
        
        self.image = self.imageLibrary[self.flip][self.startingImage][self.index]
        
        self.rect = self.image.get_rect()
        self.boundingRect = self.getBoundingBox()
        
    def flipX(self):
        if self.flip == "right": self.flip = "left"
        else: self.flip = "right"
    
    def getBoundingBox(self):
        boundingRect = self.image.get_bounding_rect()
        boundingRect.top += self.rect.top
        boundingRect.left += self.rect.left
        return boundingRect
    
    def updatePosition(self,rect):
        self.rect = rect
        self.boundingRect = self.getBoundingBox()
                
    def changeImage(self,newImage,subImage = 0):
        self.currentSheet = newImage
        self.index = subImage
        self.get_image()
        
    def changeSubImage(self,index):
        self.index = index % len(self.imageLibrary[self.flip][self.currentSheet])
        self.get_image()
    
    def rotate(self,angle = 0):
        self.angle = angle
    
    def get_image(self):
        try:
            self.image = self.imageLibrary[self.flip][self.currentSheet][self.index]
        except:
            print "Error loading sprite ", self.currentSheet, " Loading default"
            self.image = self.imageLibrary[self.flip][self.startingImage][0]
        
        self.rect = self.image.get_rect(center=self.rect.center)
        self.boundingRect = self.getBoundingBox()
        return self.image
    
    def draw(self,screen,offset,scale):
        self.get_image()
        Sprite.draw(self,screen,offset,scale)
    
    def buildImageLibrary(self,lib,offset):
        library = {}
        flippedLibrary = {}
        for key,value in lib.imageDict.iteritems():
            imageList = self.buildSubimageList(value,offset)
            library[key] = imageList
            flipList = []
            for image in imageList:
                img = image.copy()
                img = pygame.transform.flip(img,True,False)
                flipList.append(img)
            flippedLibrary[key] = flipList

        return {"right": library, "left": flippedLibrary}
        
    def buildSubimageList(self,sheet,offset):
        index = 0
        imageList = []
        while index < sheet.get_width() / offset:
            sheet.set_clip(pygame.Rect(index * offset, 0, offset,sheet.get_height()))
            image = sheet.subsurface(sheet.get_clip())
            for fromColor,toColor in self.colorMap.iteritems():
                self.recolor(image, list(fromColor), list(toColor))
            imageList.append(image)
            index += 1
        return imageList
    
    def recolor(self,image,fromColor,toColor):
        arr = pygame.PixelArray(image)
        arr.replace(fromColor,toColor)
        del arr  
        
            
class ImageSprite(Sprite):
    def __init__(self,path):
        Sprite.__init__(self)
        self.image = pygame.image.load(path)
        self.rect = self.image.get_rect()
    
    def color_surface(self,color,alpha):
        arr = pygame.surfarray.pixels3d(self.image)
        arr[:,:,0] = color[0]
        arr[:,:,1] = color[1]
        arr[:,:,2] = color[2]
        del arr
    
    def alpha(self,newAlpha):
        arr = pygame.surfarray.pixels_alpha(self.image)
        arr[arr!=0] = newAlpha
        del arr
    
    def recolor(self,image,fromColor,toColor):
        arr = pygame.PixelArray(image)
        arr.replace(fromColor,toColor)
        del arr  
        
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
    
    def flipX(self):
        self.flip = not self.flip
        self.image = pygame.transform.flip(self.image,True,False)
        
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
        Sprite.__init__(self)
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
        arr[arr!=0] = self.alpha
        del arr
        
    
    def update(self):
        if self.duration > 0:
            if self.pulse:
                self.alpha -= self.pulseSize
                if self.alpha > 200:
                    self.alpha = 200
                    self.pulseSize = -self.pulseSize
                elif self.alpha < 16:
                    self.alpha = 16
                    self.pulseSize = -self.pulseSize 
            self.duration -= 1
            self.image = self.parentSprite.image.copy()
            self.color_surface(self.color)
            
            self.rect = self.parentSprite.rect
            
            return self
        else:
            return None

class TextSprite(ImageSprite):
    def __init__(self,text,font="monospace",size=12,color=[0,0,0]):
        Sprite.__init__(self)
        try:
            self.font = pygame.font.Font(settingsManager.createPath(font+".ttf"),size)
        except Exception as e:
            self.font = pygame.font.SysFont(font, size)
            
        self.image = self.font.render(text,False,color).convert_alpha()
        self.rect = self.image.get_rect()
        
        self.text = text
        self.color = color
        
    def changeColor(self,color):
        self.image = self.font.render(self.text,False,color).convert_alpha()
        self.color = color
        
    def changeText(self,text):
        self.image = self.font.render(text,False,self.color).convert_alpha()
        self.text = text
        self.rect = self.image.get_rect(center=self.rect.center)
        
        
class ImageLibrary():
    def __init__(self,directory,prefix=""):
        self.directory = os.path.join(os.path.dirname(__file__).replace('main.exe',''),directory)
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

class RectSprite(Sprite):
    def __init__(self,rect,color=[0,0,0]):
        Sprite.__init__(self)
        
        self.color = color  
        
        self.image = pygame.Surface(rect.size)
        self.image.fill(self.color)
        
        self.rect = self.image.get_rect()
        self.rect.topleft = rect.topleft    
        
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