#! /usr/bin/env python
'''=First steps (Basic Geometry)=

[shader_1.py-screen-0001.png Screenshot]

In this tutorial we'll learn:

    * What a vertex shader *must* do in GLSL.
    * What a fragment shader *must* do.
    * What a VBO object looks like.
    * How to activate and deactivate shaders and VBOs.
    * How to render simple geometry.

First we do our imports, the [http://pyopengl.sourceforge.net/context OpenGLContext] testingcontext allows
for the use of Pygame, wxPython, or GLUT GUI systems with the same 
code.  These imports retrieve an appropriate context for this 
machine.  If you have not installed any "extra" packages, such as 
Pygame or wxPython, this will likely be a GLUT context on your 
machine.
'''
from OpenGLContext import testingcontext
BaseContext = testingcontext.getInteractive()
'''Now we import the PyOpenGL functionality we'll be using.

OpenGL.GL contains the standard OpenGL functions that you can 
read about in the PyOpenGL man pages.
'''
from OpenGL.GL import *
'''The OpenGL.arrays.vbo.VBO class is a convenience wrapper 
which makes it easier to use Vertex Buffer Objects from within 
PyOpenGL.  It takes care of determining which implementation 
to use, the creation of offset objects, and even basic slice-based 
updating of the content in the VBO.'''
from OpenGL.arrays import vbo
'''OpenGLContext.arrays is just an abstraction point which imports 
either Numpy (preferred) or the older Numeric library 
with a number of compatability functions to make Numeric look like 
the newer Numpy module.'''
from OpenGLContext.arrays import *
'''OpenGL.GL.shaders is a convenience library for accessing the 
shader functionality.'''
from OpenGL.GL import shaders

class TestContext( BaseContext ):
    def OnInit( self ):
        VERTEX_SHADER = shaders.compileShader("""#version 120
        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }""", GL_VERTEX_SHADER)
        
        FRAGMENT_SHADER = shaders.compileShader("""#version 120
        void main() {
            gl_FragColor = vec4( 0, 1, 0, 1 );
        }""", GL_FRAGMENT_SHADER)

        self.shader = shaders.compileProgram(VERTEX_SHADER,FRAGMENT_SHADER)
        self.vbo = vbo.VBO(
            array( [
                [  0, 1, 0 ],
                [ -1,-1, 0 ],
                [  1,-1, 0 ],
                
                [  2,-1, 0 ],
                [  4,-1, 0 ],
                [  4, 1, 0 ],
                [  2,-1, 0 ],
                [  4, 1, 0 ],
                [  2, 1, 0 ],
            ],'f')
        )
    def Render( self, mode):
        shaders.glUseProgram(self.shader)
        try:
            self.vbo.bind()
            try:
                glEnableClientState(GL_VERTEX_ARRAY);
                glVertexPointerf( self.vbo )
                glDrawArrays(GL_TRIANGLES, 0, 9)
            finally:
                self.vbo.unbind()
                glDisableClientState(GL_VERTEX_ARRAY);
        finally:
            shaders.glUseProgram( 0 )

if __name__ == "__main__":
    TestContext.ContextMainLoop()
