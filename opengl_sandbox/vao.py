import OpenGL.GL as GL
import OpenGL.GL.shaders
import ctypes
import pygame
import numpy
from OpenGL.raw.GL.VERSION.GL_1_0 import glTexParameteri, glPixelStorei
from OpenGL.GL.VERSION.GL_1_0 import glTexParameterfv
from OpenGL.GL.VERSION.GL_1_1 import glGenTextures
from OpenGL.raw.GL.VERSION.GL_1_1 import glBindTexture
from OpenGL.GL.images import glTexImage2D
from OpenGL.arrays._arrayconstants import GL_UNSIGNED_BYTE

vertex_shader = """
#version 330

in vec4 position;
void main()
{
   gl_Position = position;
}
"""

fragment_shader = """
#version 330

void main()
{
   gl_FragColor = vec4(1.0f, 1.0f, 1.0f, 1.0f);
}
"""

vertices = [ 0.6,  0.6, 0.0, 1.0,
            -0.6,  0.6, 0.0, 1.0,
             0.0, -0.6, 0.0, 1.0]

#cast the array as floats
vertices = numpy.array(vertices, dtype=numpy.float32)

texCoords = [ 1.0, 1.0,
              0.0, 1.0,
              0.5, 0.0]

def create_object(shader):
    # Create a new VAO (Vertex Array Object) and bind it
    vertex_array_object = GL.glGenVertexArrays(1)
    GL.glBindVertexArray( vertex_array_object )
    
    # Generate buffers to hold our vertices
    vertex_buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vertex_buffer)
    
    # Get the position of the 'position' in parameter of our shader and bind it.
    position = GL.glGetAttribLocation(shader, 'position')
    GL.glEnableVertexAttribArray(position)
    
    # Describe the position data layout in the buffer
    GL.glVertexAttribPointer(position, 4, GL.GL_FLOAT, False, 0, ctypes.c_void_p(0))
    
    tex = GL.glGetAttribLocation(shader, 'texCoord')
    GL.glEnableVertexAttribArray(tex)
    
    GL.glVertexAttribPointer(tex, 4, GL.GL_FLOAT, False, 0, ctypes.c_void_p(0))
    
    # Send the data over to the buffer
    GL.glBufferData(GL.GL_ARRAY_BUFFER, 48, vertices, GL.GL_STATIC_DRAW)
    
    # Unbind the VAO first (Important)
    GL.glBindVertexArray( 0 )
    
    # Unbind other stuff
    GL.glDisableVertexAttribArray(position)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)
    
    """Texture Info"""
    #S and T are X and Y for textures. Set the repeat mode
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_MIRRORED_REPEAT) #i - integer
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_MIRRORED_REPEAT)
    
    #Set the border color as an array of floats
    borderColor = [1.0, 1.0, 0.0, 1.0]
    borderColor = numpy.array(borderColor, dtype=numpy.float32)
    GL.glTexParameterfv(GL.GL_TEXTURE_2D,GL.GL_TEXTURE_BORDER_COLOR,borderColor) #fv - float vector
    
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_NEAREST)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_NEAREST)
    
    texSurface = pygame.image.load('wall.jpg')
    texData = pygame.image.tostring(texSurface,"RGBA",1)
    width, height = (texSurface.get_width(), texSurface.get_height())
    
    texID = glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D,texID)
    #glPixelStorei(GL.GL_UNPACK_ALIGNMENT,1) #not asked for in learnopengl, but might be python-specific
    
    GL.glTexImage2D(GL.GL_TEXTURE_2D,0,GL.GL_RGBA,
                 width,height, 0, GL.GL_RGBA,GL_UNSIGNED_BYTE,texData)
    
    #unbind the texture
    GL.glBindTexture(GL.GL_TEXTURE_2D,0)
    
    
    return vertex_array_object
    
def display(shader, vertex_array_object):
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    GL.glUseProgram(shader)
    
    GL.glBindVertexArray( vertex_array_object )
    GL.glDrawArrays(GL.GL_TRIANGLES, 0, 3)
    GL.glBindVertexArray( 0 )
    
    GL.glUseProgram(0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((512, 512), pygame.OPENGL|pygame.DOUBLEBUF)
    GL.glClearColor(0.5, 0.5, 0.5, 1.0)
    GL.glEnable(GL.GL_DEPTH_TEST)

    shader = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(vertex_shader, GL.GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(fragment_shader, GL.GL_FRAGMENT_SHADER)
    )
    
    vertex_array_object = create_object(shader)
    
    clock = pygame.time.Clock()
    
    while True:     
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE:
                return
        
        display(shader, vertex_array_object)
        pygame.display.flip()

if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()