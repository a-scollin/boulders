from os import name
import OCR_helper as OCR
from PIL import Image
import SPL_helper as SPL
import pandas as pd
import sys
import re
import NLP_helper
import json
import numpy as np
import flag
import pickle
# Convert from path reutrns a list of PIL images making it very easy to use
from pdf2image import convert_from_path

# This is the main entry point function for the project, it takes a number as an argument and will run a complete boulder data extraction over whatever volume is specified
def review_vol(number):

    patch = False

    if number == "3" or number == "4":
        return print_vol(number)
        
    print("Reviewing volume : " + str(number))
    print("Running OCR and Spellchecker...")

    word_data, word_string = SPL.get_spellchecked_volume(number)
       
    with open('word_data.pickle', 'wb') as f:
        pickle.dump(word_data, f)

    with open('word_string.pickle', 'wb') as f:
        pickle.dump(word_string, f)

    df = get_boulders(word_data, word_string)

    print("All done!")

    print(df)



    if input("Would you like to save this data to a csv file?  ( enter y or n ) : " ) == 'y':
        df.to_csv(input("Please enter filename"))

def get_boulders(word_data, word_string):
    # This regex splits paragraphs over "X. ..." meaning any paragraph mentioning a numbered boulder will be assessed, this will need extra 
    # consideration for the later volumes where they change the labeling standarads 

    matches = re.findall("([\d]+\. )(.*?)(?=([\d]+\.)|($))",word_string)

    numbers = []

    locations = []

    sizes = []
 
    rocktypes = []

    print("Running NLP...")

    # Ie for boulder paragraph in report..

    for match in matches:
        if len(match[1]) > 5:

            number, location, size, rocktype = NLP_helper.find_boulder_from_numbered_regex(match)
            
            numbers.append(number)
            locations.append(location)
            sizes.append(size)
            rocktypes.append(rocktype)

    d = {'Boulder Number': numbers, 'Boulder Location': locations, 'Boulder Size' : sizes, 'Boulder Rocktype' : rocktypes}
    
    return pd.DataFrame(data=d)



def print_vol(number):

    print("Reviewing volume : " + str(number))
    print("Running OCR and Spellchecker...")

    word_data, word_string = SPL.get_spellchecked_volume_for_printing(number)
       
    # This regex splits paragraphs over "X. ..." meaning any paragraph mentioning a numbered boulder will be assessed, this will need extra 
    # consideration for the later volumes where they change the labeling standarads 

    matches = re.findall("([\d]+\. )(.*?)(?=([\d]+\.)|($))",word_string)

    numbers = []

    locations = []

    sizes = []
 
    rocktypes = []

    print("Running NLP...")

    # Ie for boulder paragraph in report..

    for match in matches:
        
        if len(match[1]) > 5:

            number, location, size, rocktype = NLP_helper.find_boulder_from_numbered_regex(match)
            numbers.append(number)
            locations.append(location)
            sizes.append(size)
            rocktypes.append(rocktype)

    d = {'Boulder Number': numbers, 'Boulder Location': locations, 'Boulder Size' : sizes, 'Boulder Rocktype' : rocktypes}
    
    df = pd.DataFrame(data=d)

    print(df)

    return df
    

def get_index_range_of_words(df, words):
    print("Breaktime")

# Basic functions I wrote for testing the OCR .. 

def print_all_volumes():
    for i in range(3,8):
        images = convert_from_path("./bouldercopies/" + str(i) + "_Report.pdf", 500)    
        for image in images:
            OCR.print_from_image(image)

def print_one_volume(number):
    images = convert_from_path("./bouldercopies/" + str(number) + "_Report.pdf", 500)    
    for image in images:
        OCR.print_from_image(image)


if len(sys.argv) == 1:

    review_vol(sys.argv[1])

elif len(sys.argv) == 2:
    
    with open(sys.argv[1], 'rb') as f:
        word_data = pickle.load(f)
    
    with open(sys.argv[2], 'rb') as f:
        word_string = pickle.load(f)
    
    get_boulders(word_data,word_string)

else:

    review_vol(input("Please input number of report to review : "))