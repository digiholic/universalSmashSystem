#! /usr/bin/env python

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import shaders

import logging
logging.basicConfig()

class TestContext( BaseContext ):
    def OnInit( self ):
        #Just load the GLSL shaders in here
        VERTEX_SHADER = shaders.compileShader(
            """
            varying vec4 vertex_color;
            void main() {
                gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                vertex_color = gl_Color;
            }""",GL_VERTEX_SHADER)
        #Fragment Shader
        FRAGMENT_SHADER = shaders.compileShader("""
            varying vec4 vertex_color;
            void main() {
                gl_FragColor = vertex_color;
            }""",GL_FRAGMENT_SHADER)
        
        
        self.shader = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)
        
        """
        The VBO contains:
        glBindBuffer
        glBufferData
        glVertexAttribPointer
        glEnableVertexAttribArray
        """
        
        self.vbo = vbo.VBO(
            array( [
                [-1.0,-1.0, 0.0,  0,1,1], #bottom left
                [ 1.0,-1.0, 0.0,  0,1,0], #bottom right
                [-1.0, 1.0, 0.0,  1,0,0], #top left
                
                [-1.0, 1.0, 0.0,  1,0,0], #top left
                [ 1.0,-1.0, 0.0,  0,1,0], #bottom right
                [ 1.0, 1.0, 0.0,  0,0,1]  #top right
            ],'f')
        )
        
    def Render( self, mode):
        colorLocation = glGetUniformLocation(self.shader,"ourColor")
        shaders.glUseProgram(self.shader)
        glUniform4f(colorLocation,0.0,1.0,0.0,1.0)
        
        try:
            #This sends the VBO to the graphics card
            self.vbo.bind()
            try:
                glEnableClientState(GL_VERTEX_ARRAY)
                glEnableClientState(GL_COLOR_ARRAY)
                glVertexPointer(3, GL_FLOAT, 24, self.vbo )
                glColorPointer(3, GL_FLOAT, 24, self.vbo+12)
                glDrawArrays(GL_TRIANGLES, 0, 6)
                
            finally:
                self.vbo.unbind()
                glDisableClientState(GL_VERTEX_ARRAY)
                glDisableClientState(GL_COLOR_ARRAY)
        finally:
            shaders.glUseProgram(0)
            
if __name__ == "__main__":
    TestContext.ContextMainLoop()