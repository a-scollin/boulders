import pygame
from PIL import Image

# WIP pygame window for verifying tesseract OCR guesses, will be used in near future
# to build a set of training data specific to the boulder reports. 


def flag(box):
    window()

def window():

    pygame.init()
  
    white = (255, 255, 255)

    X = 400
    Y = 400
    
    
    display_surface = pygame.display.set_mode((X, Y ))
    
    pygame.display.set_caption('Image')
    
    image = pygame.image.load('test.png')

    while True :
    
        display_surface.fill(white)
    
        display_surface.blit(image, (0, 0))
    
        for event in pygame.event.get() :

            if event.type == pygame.QUIT :
    
                pygame.quit()
    
                quit()
    
            pygame.display.update() 
