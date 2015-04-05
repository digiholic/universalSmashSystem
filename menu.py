import settingsManager
import pygame
import main

def main():
    settings = settingsManager.getSetting().setting
    
    pygame.init()
    screen = pygame.display.set_mode((settings['windowSize'][0], settings['windowSize'][1]))
    pygame.display.set_caption(settings['windowName'])
    
    

if __name__  == '__main__': main()