import pygame
import spriteManager
import settingsManager

def main():
    pygame.init()
    pygame.joystick.init()
    
    screen = pygame.display.set_mode((640,480))
    pygame.display.set_caption('Joystick Test')
        
    joystickCount = pygame.joystick.get_count()
    
    joysticks = []
    
    for i in range(joystickCount):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        offset = 0
        for i in range(joystick.get_numaxes() / 2):
            joysticks.append(JoystickMonitor(offset))
            offset += 200
    
    clock = pygame.time.Clock()
    status = True
    while status:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.JOYAXISMOTION:
                joystick = pygame.joystick.Joystick(event.joy)
                if event.axis == 0 or event.axis == 1:
                    xaxis = 0
                    yaxis = 1
                    stick = 0
                    x, y = (joystick.get_axis(xaxis) * 100,joystick.get_axis(yaxis) * 100)
                    joysticks[stick].relocateJoystick(x,y)    
                elif event.axis == 3 or event.axis == 4:
                    xaxis = 4
                    yaxis = 3
                    stick = 1
                    x, y = (joystick.get_axis(xaxis) * 100,joystick.get_axis(yaxis) * 100)
                    joysticks[stick].relocateJoystick(x,y)    
                    
        screen.fill([100,100,100])
        for monitor in joysticks:
            monitor.draw(screen,monitor.rect.topleft,1.0)
            
        pygame.display.flip()
        clock.tick(60)

class JoystickMonitor(spriteManager.Sprite):
    def __init__(self,position):
        spriteManager.Sprite.__init__(self)
        self.joystickSprite = spriteManager.ImageSprite(settingsManager.createPath('sprites/joyTest.png'))
        self.jLocSprite = spriteManager.RectSprite(pygame.Rect(0,0,10,10),[255,255,255])
        self.jStatus = spriteManager.TextSprite('No Input','rexlia rg')
        
        self.jStatus.rect.midtop = self.joystickSprite.rect.midbottom
        
        self.rect = pygame.Rect(position,0,self.jLocSprite.rect.height + self.jStatus.rect.height, self.jLocSprite.rect.width)
        
    def relocateJoystick(self,x,y):
        self.jLocSprite.rect.centerx = x + 100
        self.jLocSprite.rect.centery = y + 100
        
        if abs(x) <= 10 and abs(y) <= 10:
            #dead zone
            self.jStatus.changeText('No Input')
            
        if y > 10 and y >= abs(x):
            self.jStatus.changeText('Down')
        if y < -10 and -y >= abs(x):
            self.jStatus.changeText('Up')
        if x < -10 and -x >= abs(y):
            self.jStatus.changeText('Left')
        if x > 10 and x >= abs(y):
            self.jStatus.changeText('Right')
        
        if y > 70 and y >= abs(x):
            self.jStatus.changeText('Smash Down')
        if y < -70 and -y >= abs(x):
            self.jStatus.changeText('Smash Up')
        if x < -70 and -x >= abs(y):
            self.jStatus.changeText('Smash Left')
        if x > 70 and x >= abs(y):
            self.jStatus.changeText('Smash Right')
            
    def draw(self,screen,offset,scale):
        ox, oy = offset
        self.joystickSprite.draw(screen, (self.joystickSprite.rect.left + ox,self.joystickSprite.rect.top + oy), scale)
        self.jLocSprite.draw(screen, (self.jLocSprite.rect.left + ox,self.jLocSprite.rect.top + oy), scale)
        self.jStatus.draw(screen, (self.jStatus.rect.left + ox,self.jStatus.rect.top + oy), scale)
        
if __name__ == '__main__': main()