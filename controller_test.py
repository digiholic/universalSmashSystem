#!/usr/bin/env python
import pygame
import spriteManager
import settingsManager

def main():
    pygame.init()
    pygame.joystick.init()
    
    screen = pygame.display.set_mode((640,480))
    pygame.display.set_caption('Joystick Test')
        
    joystick_count = pygame.joystick.get_count()
    
    joysticks = []
    
    for i in range(joystick_count):
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
    def __init__(self,_position):
        spriteManager.Sprite.__init__(self)
        self.joystick_sprite = spriteManager.ImageSprite(settingsManager.createPath('sprites/joyTest.png'))
        self.j_loc_sprite = spriteManager.RectSprite(pygame.Rect(0,0,10,10),[255,255,255])
        self.j_status = spriteManager.TextSprite('No Input','Orbitron Medium')
        
        self.j_status.rect.midtop = self.joystick_sprite.rect.midbottom
        
        self.rect = pygame.Rect(_position,0,self.j_loc_sprite.rect.height + self.j_status.rect.height, self.j_loc_sprite.rect.width)
        
    def relocateJoystick(self,_x,_y):
        self.j_loc_sprite.rect.centerx = _x + 100
        self.j_loc_sprite.rect.centery = _y + 100
        
        if abs(_x) <= 10 and abs(_y) <= 10:
            #dead zone
            self.j_status.changeText('No Input')
            
        if _y > 10 and _y >= abs(_x):
            self.j_status.changeText('Down')
        if _y < -10 and -_y >= abs(_x):
            self.j_status.changeText('Up')
        if _x < -10 and -_x >= abs(_y):
            self.j_status.changeText('Left')
        if _x > 10 and _x >= abs(_y):
            self.j_status.changeText('Right')
        
        if _y > 70 and _y >= abs(_x):
            self.j_status.changeText('Smash Down')
        if _y < -70 and -_y >= abs(_x):
            self.j_status.changeText('Smash Up')
        if _x < -70 and -_x >= abs(_y):
            self.j_status.changeText('Smash Left')
        if _x > 70 and _x >= abs(_y):
            self.j_status.changeText('Smash Right')
            
    def draw(self,_screen,_offset,_scale):
        ox, oy = _offset
        self.joystick_sprite.draw(_screen, (self.joystick_sprite.rect.left + ox,self.joystick_sprite.rect.top + oy), _scale)
        self.j_loc_sprite.draw(_screen, (self.j_loc_sprite.rect.left + ox,self.j_loc_sprite.rect.top + oy), _scale)
        self.j_status.draw(_screen, (self.j_status.rect.left + ox,self.j_status.rect.top + oy), _scale)
        
if __name__ == '__main__': main()
