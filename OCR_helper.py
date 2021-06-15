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

def OCR_pre_process_image(image):
    
    open_cv_image = np.array(image.convert('RGB')) 
    grayscaled = cv2.cvtColor(open_cv_image,cv2.COLOR_BGR2GRAY)

    # No threshold preprocessing should be needed for the first report as it's all evenly scanned and is already black and white.

    # th = cv2.adaptiveThreshold(grayscaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 115, 1)
    # cv2.imwrite('./preprocessing/grayscaled.jpg', grayscaled)
    # cv2.imwrite('./preprocessing/adaptive_threshold_processed.jpg',th)
   

    clean = cv2.fastNlMeansDenoising(grayscaled, h=50)
    kernel = np.ones((2,2),np.uint8)
    erosion = cv2.erode(clean,kernel,iterations = 1)
    
    # change values for thinning and denoising above for different volumes
    
    # cv2.imshow("original",grayscaled)
    # cv2.imshow("denoised",clean)
    # cv2.imshow("denoised + thinned",erosion)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return Image.fromarray(erosion)
   