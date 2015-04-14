import pygame
import stages.stage as stage
import settingsManager
import imp
import os
from pygame.locals import *

def main(debug = False):
    settings = settingsManager.getSetting().setting
    
    if debug:
        pygame.init()
        screen = pygame.display.set_mode((settings['windowWidth'], settings['windowHeight']))
        pygame.display.set_caption(settings['windowName'])
    
    # Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((128, 128, 128))
    current_stage = stage.Stage()
    active_hitboxes = pygame.sprite.Group()
    
    #gameObjects
    currentFighters = []
    
    fight = importFromURI(__file__,'fighters/hitboxie/fighter.py')
    testBoxie = fight.getFighter(0,0)
    testBoxie.rect.midtop = current_stage.size.midtop
    testBoxie.gameState = current_stage
    
    fight = importFromURI(__file__,'fighters/sandbag/fighter.py')
    sandbag = fight.Fighter(1)
    sandbag.rect.midtop = current_stage.size.midtop
    sandbag.gameState = current_stage
    
    currentFighters.append(testBoxie)
    currentFighters.append(sandbag)
    
    gameObjects = []
    gameObjects.extend(currentFighters)
    
    current_stage.follows.append(testBoxie.rect)
    current_stage.follows.append(sandbag.rect)
        
    clock = pygame.time.Clock()
    
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                return -1
            if event.type == KEYDOWN:
                for fight in currentFighters:
                    fight.keyPressed(event.key)
            if event.type == KEYUP:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_k:
                    sandbag.dealDamage(999)
                for fight in currentFighters:
                    fight.keyReleased(event.key)
                               
        screen.fill([100, 100, 100])
        
        current_stage.update()
        current_stage.cameraUpdate()
        current_stage.draw(screen)
        for obj in gameObjects:
            obj.update()
            if hasattr(obj,'active_hitboxes'):
                active_hitboxes.add(obj.active_hitboxes)
            
            
            offset = current_stage.stageToScreen(obj.rect)
            scale =  current_stage.getScale()
            obj.draw(screen,offset,scale)
            hitbox_collisions = pygame.sprite.spritecollide(obj, active_hitboxes, False)
            for hbox in hitbox_collisions:
                if hbox.owner != obj:
                    hbox.onCollision(obj)
            for hbox in active_hitboxes:
                hbox.draw(screen,current_stage.stageToScreen(hbox.rect),scale)
              
        clock.tick(60)    
        pygame.display.flip()

def importFromURI(file, uri, absl=False):
    if not absl:
        uri = os.path.normpath(os.path.join(os.path.dirname(file), uri))
    path, fname = os.path.split(uri)
    mname, ext = os.path.splitext(fname)
        
    no_ext = os.path.join(path, mname)
         
    #if os.path.exists(no_ext + '.pyc'):
        #try:
            #return imp.load_compiled(mname, no_ext + '.pyc')
        #except:
            #pass
    if os.path.exists(no_ext + '.py'):
        try:
            return imp.load_source(mname, no_ext + '.py')
        except Exception as e:
            print mname, e
        
    
if __name__  == '__main__': main(True)

