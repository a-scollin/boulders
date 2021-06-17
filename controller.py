from os import name
import OCR_helper as OCR
from PIL import Image
import SPL_helper as SPL
import pandas as pd
import re
import NLP_helper
import json
# Convert from path reutrns a list of PIL images making it very easy to use
from pdf2image import convert_from_path

def review_vol(number):

    words = SPL.get_spellchecked_volume(number)
       
    matches = re.findall("([\d]+\. )(.*?)(?=([\d]+\.)|($))",words)

    numbers = []

    locations = []

    sizes = []
 
    for match in matches:
        if len(match[1]) > 5:
            number, location, size = NLP_helper.find_boulder_from_numbered_regex(match)
            
            numbers.append(number)
            locations.append(location)
            sizes.append(size)

    d = {'Boulder Number': numbers, 'Boulder Location': locations, 'Boulder Size' : sizes}
    
    df = pd.DataFrame(data=d)

    print(df)
    
def print_all_volumes():
    for i in range(3,8):
        images = convert_from_path("./bouldercopies/" + str(i) + "_Report.pdf", 500)    
        for image in images:
            OCR.print_from_image(image)

def print_one_volume(number):
    images = convert_from_path("./bouldercopies/" + str(number) + "_Report.pdf", 500)    
    for image in images:
        OCR.print_from_image(image)

# The function below is a primitive spellchecker, it currently overextends to correct 
# punctuation which should be an easy fix but also isn't the main goal right now

review_vol(input("Please input number of report to review."))