import pygame
import os
 
from OpenGL.GL import *
from OpenGL.GLU import *
 
def initializeDisplay(w, h):
    pygame.display.set_mode((w,h), pygame.OPENGL|pygame.DOUBLEBUF)
 
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
 
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity();
    # this puts us in quadrant 1, rather than quadrant 4
    gluOrtho2D(0, w, h, 0)
    glMatrixMode(GL_MODELVIEW)
 
    # set up texturing
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
 
 
def render_init(w,h):
    """Finds the smallest available resolution that fits the desired
    viewfield."""
    pygame.init()
    modelist = pygame.display.list_modes()
    nextmode = [l for l in modelist if l[0]>=w and l[1]>=h]
    bestx, besty = -1,-1
    for l in nextmode:
        if (bestx==-1 or bestx>=l[0]) and (besty==-1 or besty>=l[1]):
            bestx, besty = l[0],l[1]
 
    print "resolution: ",bestx, besty
 
    initializeDisplay(bestx, besty)
 
def loadImage(image):
    textureSurface = pygame.image.load(image)
 
    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
 
    width = textureSurface.get_width()
    height = textureSurface.get_height()
 
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
        GL_UNSIGNED_BYTE, textureData)
 
    return texture, width, height
 
def SurfaceClip(surface, rect):
    textureSurface = surface.subsurface(rect)
 
    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
 
    width = textureSurface.get_width()
    height = textureSurface.get_height()
 
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA,
        GL_UNSIGNED_BYTE, textureData)
 
    return texture, width, height
 
 
def delTexture(texture):
    glDeleteTextures(texture)
 
 
def createTexDL(texture, width, height):
    newList = glGenLists(1)
    glNewList(newList,GL_COMPILE);
    glBindTexture(GL_TEXTURE_2D, texture)
    glBegin(GL_QUADS)
 
    # Bottom Left Of The Texture and Quad
    glTexCoord2f(0, 0); glVertex2f(0, 0)
 
    # Top Left Of The Texture and Quad
    glTexCoord2f(0, 1); glVertex2f(0, height)
 
    # Top Right Of The Texture and Quad
    glTexCoord2f(1, 1); glVertex2f( width,  height)
 
    # Bottom Right Of The Texture and Quad
    glTexCoord2f(1, 0); glVertex2f(width, 0)
    glEnd()
    glEndList()
 
    return newList
 
 
def delDL(list):
    glDeleteLists(list, 1)
 
def render(layers):
    for l in layers:
        l.render()
 
class GL_Texture:
    def __init__(self, texname=None, texappend=".png"):
        filename = os.path.join('data', texname)
        filename += texappend
       
        self.texture, self.width, self.height = loadImage(filename)
        self.displaylist = createTexDL(self.texture, self.width, self.height)       
 
    def __del__(self):
        if self.texture != None:
            delTexture(self.texture)
            self.texture = None
        if self.displaylist != None:
            delDL(self.displaylist)
            self.displaylist = None
 
    def __repr__(self):
        return self.texture.__repr__()
 
class Textureset:
    """Texturesets contain and name textures."""
 
    def __init__(self):
        self.textures = {}
    def load(self, texname=None, texappend=".png"):
        self.textures[texname] = GL_Texture(texname, texappend)
    def set(self, texname, data):
        self.textures[texname] = data
    def delete(self, texname):
        del self.textures[texname]
    def __del__(self):
        self.textures.clear()
        del self.textures
    def get(self, name):
        return self.textures[name]
 
class GL_Image:
    def __init__(self, texset, texname):
        self.texture = texset.get(texname)
        self.width = self.texture.width
        self.height = self.texture.height
        self.abspos=None
        self.relpos=None
        self.color=(1,1,1,1)
        self.rotation=0
        self.rotationCenter=None
 
    def draw(self, abspos=None, relpos=None, width=None, height=None,
            color=None, rotation=None, rotationCenter=None):
        if color==None:
            color = self.color
 
        glColor4fv(color)
 
        if abspos:
            glLoadIdentity()
            glTranslate(abspos[0],abspos[1],0)
        elif relpos:
            glTranslate(relpos[0],relpos[1],0)
 
        if rotation==None:
            rotation=self.rotation
 
        if rotation != 0:
                if rotationCenter == None:
                    rotationCenter = (self.width / 2, self.height / 2)
                # (w,h) = rotationCenter
                glTranslate(rotationCenter[0],rotationCenter[1],0)
                glRotate(rotation,0,0,-1)
                glTranslate(-rotationCenter[0],-rotationCenter[1],0)
 
        if width or height:
            if not width:
                width = self.width
            elif not height:
                height = self.height
 
            glScalef(width/(self.width*1.0), height/(self.height*1.0), 1.0)
                
 
        glCallList(self.texture.displaylist)
 
        if rotation != 0: # reverse
            glTranslate(rotationCenter[0],rotationCenter[1],0)
            glRotate(-rotation,0,0,-1)
            glTranslate(-rotationCenter[0],-rotationCenter[1],0)
 
class CImage:
    """CImage is a "composed image" that refs multiple GLImages.
    format is [(GLImage,argstoimage)...()..()]
    Cimage is fast but immutable - it has to recreate
    the display list to be changed."""
    
    def __init__(self, ilist):
        newlist = glGenLists(1)
        glNewList(newlist,GL_COMPILE)
 
        # see GL_Image.draw
        for i in ilist:
            if i[1][0] == None:
                i[0].draw(i[1][0], i[1][1], i[1][2], i[1][3], i[1][4],
                    i[1][5], i[1][6])
            else: # absolute positioning normally resets the identity
                i[0].draw(None,i[1][0], i[1][2], i[1][3], i[1][4], i[1][5],
                    i[1][6])
                glTranslate(-i[1][0][0], -i[1][0][1],0)               
 
        glEndList()
        self.displaylist = newlist
 
    def __del__(self):
        if self.displaylist != None:
            delDL(self.displaylist)
            self.displaylist = None
 
    def draw(self, abspos=None,relpos=None):
        if abspos:
            glLoadIdentity()
            glTranslate(abspos[0],abspos[1],0)
        elif relpos:
            glTranslate(relpos[0],relpos[1],0)
 
        glCallList(self.displaylist)
 
class DCImage:
    """Dynamic Composite Image - elements are mutable, at the caveat of
    runtime performance."""
    def __init__(self, ilist):      
        self.ilist = ilist
    def draw(self, abspos):
        glLoadIdentity()
        glTranslate(abspos[0],abspos[1],0)
 
        for i in self.ilist:
            i[0].draw(i[1])
 
class LDCImage:
    """Limited Dynamic Composite Image. LDCImage uses only the
    texture display lists for drawing, which makes it useful for simpler
    applications like text and tiles that don't need the features of DCImage.
    
    Remember not to mistake this for *LCD* Image!"""
    def __init__(self, cache):
        """cache format is: (texture ref, (absx, absy))"""
        self.cache = cache
    def draw(self, abspos):
 
        glLoadIdentity()
        glTranslate(abspos[0],abspos[1],0)
 
        for c in self.cache:
            glTranslate(c[1][0], c[1][1],0)
            glCallList(c[0].displaylist)
            glTranslate(-c[1][0], -c[1][1],0)
 
def main():
    render_init(640,480)
    tset = Textureset()
    tset.load('editor-logo','.png')
    fooimage = GL_Image(tset, 'editor-logo')
    rawfootex = tset.get('editor-logo')
 
    compositelist = []
    examplegrid = []
 
    for x in xrange(4):
        for y in xrange(4):
            examplegrid.append((rawfootex,(x*32,y*32)))
            compositelist.append((fooimage, ((x*32,y*32), None, None,
                None, (1,1,1,1), 1, None)))
   
    ldcimg = LDCImage(examplegrid)
    foocomposite = CImage(compositelist)
    
    clock = pygame.time.Clock()
    t = 0
    glLoadIdentity()
    for count in range(100):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        if t==0:
            ldcimg.draw((10,10))
            fooimage.draw((0,0))
            t=1
        else:
            t=0
            foocomposite.draw((320,200))   
        clock.tick()
        pygame.display.flip()
        pygame.event.pump()
    print "result: "+str(clock.get_fps())+" FPS"
    
 
if __name__=="__main__":
    main()