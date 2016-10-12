import pygame
import sys
import ctypes
import numpy

from OpenGL import GL, GLU
from OpenGL.GL import shaders
from OpenGL.arrays import vbo

import pygame
from numpy import array

class OpenGLSprite():
    def __init__(self,_sprite='',_rect = None,_vertexShader = None, _fragmentShader = None):
        if not isinstance(_sprite, pygame.Surface):
            self.sprite = pygame.image.load(_sprite)
        else: self.sprite = _sprite
        
        if _rect is None: _rect = pygame.rect.Rect(-1,0,1,1)
        vertexData = numpy.array([
             # X,             Y,       Z   U,   V
            _rect.left,  _rect.top,    0, 0.0, 0.0,
            _rect.left,  _rect.bottom, 0, 0.0, 1.0,
            _rect.right, _rect.bottom, 0, 1.0, 1.0,
            
            _rect.right, _rect.bottom, 0, 1.0, 1.0,
            _rect.right, _rect.top,    0, 1.0, 0.0,
            _rect.left,  _rect.top,    0, 0.0, 0.0,
            
            ], dtype=numpy.float32)
        
        self.loadTexture()
        self.buildShaders(_vertexShader, _fragmentShader)
        
        self.VAO = GL.glGenVertexArrays(1)
        GL.glBindVertexArray(self.VAO)
        
        self.VBO = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.VBO)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertexData.nbytes, vertexData,
            GL.GL_STATIC_DRAW)
        
        positionAttrib = GL.glGetAttribLocation(self.shaderProgram, 'position')
        coordsAttrib = GL.glGetAttribLocation(self.shaderProgram, 'texCoords')
    
        GL.glEnableVertexAttribArray(0)
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(positionAttrib, 3, GL.GL_FLOAT, GL.GL_FALSE, 20,
            None)
        # the last parameter is a pointer
        GL.glVertexAttribPointer(coordsAttrib, 2, GL.GL_FLOAT, GL.GL_TRUE, 20,
            ctypes.c_void_p(12))
    
        # load texture and assign texture unit for shaders
        self.texUnitUniform = GL.glGetUniformLocation(self.shaderProgram, 'texUnit')
    
        # Finished
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
        GL.glBindVertexArray(0)

    def loadTexture(self):
        img_data = pygame.image.tostring(self.sprite,"RGBA",1)
        width, height = (self.sprite.get_width(), self.sprite.get_height())
        
        texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
        
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameterf(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)
        
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0,
            GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, img_data)
        self.texture = texture
    
    def buildShaders(self,_vertexShader = None, _fragmentShader = None):
        if _vertexShader is None:
            _vertexShader = """
                #version 330
                
                layout (location=0) in vec3 position;
                layout (location=1) in vec2 texCoords;
                
                out vec2 theCoords;
                
                void main()
                {
                    gl_Position = vec4(position, 1);
                    theCoords = texCoords;
                }
                """
        if _fragmentShader is None:
            _fragmentShader = """
                #version 330
                
                uniform sampler2D texUnit;
                
                in vec2 theCoords;
                
                out vec4 outputColour;
                
                void main()
                {
                    outputColour = texture(texUnit, theCoords);
                }
                """
        vertexShader = shaders.compileShader(_vertexShader, GL.GL_VERTEX_SHADER)
        fragmentShader = shaders.compileShader(_fragmentShader, GL.GL_FRAGMENT_SHADER)
        self.shaderProgram = shaders.compileProgram(vertexShader, fragmentShader)
        
    def render(self):
        GL.glClearColor(0, 0, 0, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    
        # active shader program
        GL.glUseProgram(self.shaderProgram)
    
        try:
            # Activate texture
            GL.glActiveTexture(GL.GL_TEXTURE0)
            GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
            GL.glUniform1i(self.texUnitUniform, 0)
    
            # Activate array
            GL.glBindVertexArray(self.VAO)
            
            # draw triangle
            GL.glDrawArrays(GL.GL_TRIANGLES, 0, 6)
        finally:
            GL.glBindVertexArray(0)
            GL.glUseProgram(0)
            

def main():
    pygame.init()
    screen = pygame.display.set_mode((640,480),pygame.OPENGL|pygame.DOUBLEBUF)
    GL.glClearColor(0.5, 0.5, 0.5, 1.0)
    GL.glEnable(GL.GL_DEPTH_TEST)

    camX = 0.0
    camZ = 3.0
    
    sprite = OpenGLSprite(pygame.image.load('logo-bluebg-square.png'))
    
    status = 0
    
    while status == 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                status = 1
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    status = 1
                elif event.key == pygame.K_LEFT:
                    camX -= 0.1
                elif event.key == pygame.K_RIGHT:
                    camX += 0.1
                    
        GLU.gluLookAt(camX,0.0,camZ,
                      0.0,0.0,0.0,
                      0.0,1.0,0.0)
    
        sprite.render()
        
        pygame.display.flip()
        
    return 0

if __name__ == '__main__': 
    main()