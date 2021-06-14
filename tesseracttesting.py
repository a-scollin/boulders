# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os


# Running basic tesseract on the test.png in TestingSnips folder

text = pytesseract.image_to_data(Image.open(input("Please enter the path to the image : ")), output_type='data.frame')

# Removing false word predictions (ie. no confidence) 

teswords = text[text.conf != -1]

print(teswords)

