import pygame
from PIL import Image
from pdf2image import convert_from_path







# WIP pygame window for verifying tesseract OCR guesses, will be used in near future
# to build a set of training data specific to the boulder reports. 


# 17/06 - Pygame doens't work apparently, Spent a fair amount of time trying to make this 
# work and it doens't easily work on my operating system, should've googled that before.. 
 

def flag(image):

    mode = image.mode
    size = image.size
    data = image.tobytes()

    # activate the pygame library .
    # initiate pygame and give permission
    # to use pygame's functionality.
    pygame.init()
    
    # define the RGB value
    # for white colour
    white = (255, 255, 255)
    
    # assigning values to X and Y variable
    X = 400
    Y = 400
    
    # create the display surface object
    # of specific dimension..e(X, Y).
    display_surface = pygame.display.set_mode((X, Y ))
    
    # set the pygame window name
    pygame.display.set_caption('Image')

    py_image = pygame.image.fromstring(data, size, mode)
    
    # infinite loop
    while True :
    
        # copying the image surface object
        # to the display surface object at
        # (0, 0) coordinate.
        display_surface.blit(py_image, (0, 0))
    
        # iterate over the list of Event objects
        # that was returned by pygame.event.get() method.
        for event in pygame.event.get() :
    
            # if event object type is QUIT
            # then quitting the pygame
            # and program both.
            if event.type == pygame.QUIT :
    
                # deactivates the pygame library
                pygame.quit()
    
                # quit the program.
                quit()
    
            # Draws the surface object to the screen.  
            pygame.display.update() 
images = convert_from_path("./bouldercopies/3_Report.pdf", 500)
    
flag(images[2])
             