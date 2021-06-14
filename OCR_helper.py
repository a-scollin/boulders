# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os

# Very simple set of functions for running the OCR from PIL image,
# will include methods for training the OCR model once verification data is made 

def read_image_to_df(image):
    text = pytesseract.image_to_data(image, output_type='data.frame')


def print_from_image(image):

    # Running basic tesseract on the test.png in TestingSnips folder

    text = pytesseract.image_to_data(image, output_type='data.frame')

    # Removing false word predictions (ie. no confidence) 

    teswords = text[text.conf != -1]

    print(teswords)

