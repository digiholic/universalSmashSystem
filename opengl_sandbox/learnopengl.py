#! /usr/bin/env python

from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.arrays import vbo
from OpenGLContext.arrays import *
from OpenGL.GL import shaders

class TestContext( BaseContext ):
    def OnInit( self ):
        #Just load the GLSL shaders in here
        VERTEX_SHADER = shaders.compileShader("""#version 330 core
        layout (location = 0) in vec3 position;
        void main() {
            gl_Position = vec4(position.x, position.y, position.z, 1.0);
        }""", GL_VERTEX_SHADER)
        
        #Fragment Shader
        FRAGMENT_SHADER = shaders.compileShader("""#version 330 core
        out vec4 color;
        void main() {
            color = vec4(1.0f, 0.5f, 0.2f, 1.0f);
        } """, GL_FRAGMENT_SHADER)
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
                [-0.5,-0.5, 0.0], #bottom left
                [ 0.5,-0.5, 0.0], #bottom right
                [-0.5, 0.5, 0.0], #top left
                
                [-0.5, 0.5, 0.0], #top left
                [ 0.5,-0.5, 0.0], #bottom right
                [ 0.5, 0.5, 0.0]  #top right
            ],'f')
        )
        
    def Render( self, mode):
        shaders.glUseProgram(self.shader)
        try:
            self.vbo.bind()
            try:
                glEnableClientState(GL_VERTEX_ARRAY);
                glVertexPointerf( self.vbo )
                glDrawArrays(GL_TRIANGLES, 0, 6)
                
            finally:
                self.vbo.unbind()
                glDisableClientState(GL_VERTEX_ARRAY);
        finally:
            shaders.glUseProgram(0)
            
if __name__ == "__main__":
    TestContext.ContextMainLoop()