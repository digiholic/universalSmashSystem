import pygame
import spriteObject
import fighter
import fighters.hitboxie.hitboxie
import fighters.sandbag.sandbag
import stage
from pygame.locals import *

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Universal Smash System')
    
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((128, 128, 128))
    current_stage = stage.Stage()
    
    #gameObjects
    testBoxie = fighters.hitboxie.hitboxie.Hitboxie(spriteObject.RectSprite([64,64],[64,64]),defaultKeybindingsDict())
    testBoxie.rect.x = 128
    testBoxie.gameState = current_stage
    sandbag = fighters.sandbag.sandbag.Sandbag(spriteObject.RectSprite([128,128],[128,128]))
    sandbag.rect.midtop = current_stage.size.midtop
    sandbag.gameState = current_stage
    gravityText = spriteObject.TextSprite([0,0], str(testBoxie.var['gravity']))
    
    gameObjects = []
    gameObjects.append(testBoxie)
    gameObjects.append(gravityText)
    gameObjects.append(sandbag)
    
    current_stage.follows.append(testBoxie.rect)
    current_stage.follows.append(sandbag.rect)
        
    clock = pygame.time.Clock()
    
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return -1
            if event.type == KEYDOWN:
                testBoxie.keyPressed(event.key)
            if event.type == KEYUP:
                if event.key == pygame.K_EQUALS:
                    testBoxie.gravity += 0.01
                    gravityText.text = str(testBoxie.gravity)
                elif event.key == pygame.K_MINUS:
                    testBoxie.gravity -= 0.01
                    gravityText.text = str(testBoxie.gravity)
                elif event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_k:
                    sandbag.applyKnockback(10, 0.5, 35)
                    sandbag.dealDamage(10)
                elif event.key == pygame.K_d:
                    gravityText.rect.x += 10
                elif event.key == pygame.K_a:
                    gravityText.rect.x -= 10
                elif event.key == pygame.K_s:
                    gravityText.rect.y += 10
                elif event.key == pygame.K_w:
                    gravityText.rect.y -= 10
                testBoxie.keyReleased(event.key)
                               
        screen.fill([100, 100, 100])
        
        current_stage.update()
        current_stage.cameraUpdate()
        current_stage.draw(screen)
        for obj in gameObjects:
            obj.update()
            offset = current_stage.stageToScreen(obj.rect)
            scale =  current_stage.getScale()
            obj.draw(screen,offset,scale)
            hitbox_collisions = pygame.sprite.spritecollide(obj, current_stage.active_hitboxes, False)
            for hbox in hitbox_collisions:
                if hbox.owner != obj:
                    hbox.onCollision(obj)
        
              
        clock.tick(60)    
        pygame.display.flip()

def defaultKeybindingsDict():
    bindings = {
                'left': pygame.K_LEFT,
                'right': pygame.K_RIGHT,
                'up': pygame.K_UP,
                'down': pygame.K_DOWN,
                'jump': pygame.K_UP,
                'attack': pygame.K_z,
                'shield': pygame.K_a
                }
    return bindings
    
if __name__  == '__main__': main()

