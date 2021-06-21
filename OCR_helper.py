# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import numpy as np


# Very simple set of functions for running the OCR from PIL image,
# will include methods for training the OCR model once verification data is made 

def read_image_to_df(image):
    text = pytesseract.image_to_data(OCR_pre_process_image(image), output_type='data.frame')
    
    return text[text.conf != -1]

def print_from_image(image):

    # Running basic tesseract on the test.png in TestingSnips folder

    text = pytesseract.image_to_data(OCR_pre_process_image(image), output_type='data.frame')

    # Removing false word predictions (ie. no confidence) 

    teswords = text[text.conf != -1]

    print(teswords)

# This is the preprocessing done before OCRing any image, makes the data alot more uniform and with less artifacts. 

def OCR_pre_process_image(image):
    
    open_cv_image = np.array(image.convert('RGB')) 
    grayscaled = cv2.cvtColor(open_cv_image,cv2.COLOR_BGR2GRAY)


    clean = cv2.fastNlMeansDenoising(grayscaled, h=50)
    kernel = np.ones((1,1),np.uint8)
    erosion = cv2.erode(clean,kernel,iterations = 1)
    
  

    return Image.fromarray(erosion)
   