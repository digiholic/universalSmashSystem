import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

vertices = (
            # x  y  z
            ( 1,-1,-1),
            ( 1, 1,-1),
            (-1, 1,-1),
            (-1,-1,-1),
            ( 1,-1, 1),
            ( 1, 1, 1),
            (-1,-1, 1),
            (-1, 1, 1)
            )

edges = (
         (0,1),
         (0,3),
         (0,4),
         (2,1),
         (2,3),
         (2,7),
         (6,3),
         (6,4),
         (6,7),
         (5,1),
         (5,4),
         (5,7)
         )

surfaces = (
            (0,1,2,3),
            (3,2,7,6),
            (6,7,5,4),
            (4,5,1,0),
            (1,5,7,2),
            (4,0,3,6)
            )

def Cube(offset):
    # Get the surfaces
    glBegin(GL_QUADS)
    for surface in surfaces:
        glColor3fv((0,0,1))
        for vertex in surface:
            x,y,z = vertices[vertex]
            glVertex3fv((x+offset,y+offset,z+offset))        
    glEnd()
    
    # Get the lines that make up the cube
    glColor3fv((1,1,1))
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            x,y,z = vertices[vertex]
            glVertex3fv((x+offset,y+offset,z+offset))
    glEnd() 

def Plane(left,top):
    # Draw a flat plane
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(left, top,  1.0)
    glTexCoord2f(1, 0.0)
    glVertex3f(left+1, top,  1.0)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(left+1,  top+1,  1.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(left, top+1, 1.0)
    glEnd()

class Texture():
    def __init__(self,filepath):
        textureSurface = pygame.image.load(filepath)
        self.textureData = pygame.image.tostring(textureSurface,"RGBA",1)
        self.width = textureSurface.get_width()
        self.height = textureSurface.get_height()
        
        glEnable(GL_TEXTURE_2D)
        
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.textureData)
        
        glEnable(GL_BLEND);
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    
    def bind(self,unit):
        glActiveTexture(unit)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.textureData)
    
def main():
    pygame.init()
    display = (800,600)
    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL | OPENGLBLIT)
    
    gluPerspective(45, display[0]/display[1],0.1,50.0)
    glTranslatef(0.0,0.0,-5)
    glRotatef(0, 0, 0, 0)
    
    horMov = 0
    vertMov = 0
    zoom = 0
    
    while True:
        # Pygame camera movement code
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    vertMov = .1
                elif event.key == pygame.K_DOWN:
                    vertMov = -.1
                elif event.key == pygame.K_LEFT:
                    horMov = -.1
                elif event.key == pygame.K_RIGHT:
                    horMov = .1
            if event.type == pygame.KEYUP:
                if event.key in [pygame.K_DOWN, pygame.K_UP]:
                    vertMov = 0
                elif event.key in [pygame.K_LEFT, pygame.K_RIGHT]:
                    horMov = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    glTranslatef(0,0,1)
                elif event.button == 5:
                    glTranslatef(0,0,-1)
                    
        glTranslatef(horMov,vertMov,zoom)
        
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #glActiveTexture(GL_TEXTURE0)
        
        Cube(0)
        zeroTex = Texture('zero_shield.png')
        zeroTex.bind(GL_TEXTURE0)
        Plane(0,0)
        
        #otherTex = Texture('editor-logo.png')
        #otherTex.bind(GL_TEXTURE1)
        #Plane(-2,0)
        
        
        pygame.display.flip()
        pygame.time.wait(10)
        
main()
    