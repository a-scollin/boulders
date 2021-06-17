from os import name
import OCR_helper as OCR
from PIL import Image
from spellchecker import SpellChecker
import pandas as pd
import re
import NLP_helper
import json
# Convert from path reutrns a list of PIL images making it very easy to use
from pdf2image import convert_from_path

def review_vol(number):

    images = convert_from_path("./bouldercopies/"+str(number)+"_Report.pdf", 500)
    
    words = ""  
    
    for image in images:
        
        data = OCR.read_image_to_df(image)

        for index in data.index:
            word = data[data.index == index]["text"]
            words += word.array[0] + " "

       
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

def attempt_spellcheck_on_volume(number):
    
    images = convert_from_path("./bouldercopies/" + str(number) + "_Report.pdf", 500)
    words = []    
    for image in images:
         for word in OCR.read_image_to_df(image)["text"]:
             words.append(word)
             
    spell = SpellChecker()

    with open('./dictionaries/lochs.json', 'r') as json_file:
        safewords = json.load(json_file)

    safewords = list(safewords.keys())

    with open('./dictionaries/rocktypes.txt', 'r') as f:
        for line in f:
            safeword = ""
            for char in line:
                if char.isalpha():
                    safeword += char
            if len(safeword):
                safewords.append(safeword)            

    print("SafeWords : " + str(safewords))

    spell.word_frequency.load_words(safewords)


    # find those words that may be misspelled
    misspelled = spell.unknown(words)

    for word in misspelled:
        # For misspellings based on puncutation and numerics 
        for char in word :
            if not (char.isalpha() or char.isnumeric()):
                break
        # Might not work
        if (char.isalpha() or char.isnumeric()):
            print(word)
            print(spell.correction(word))
        
# review_vol(input("please input the number of the volume you wish to analyse : "))

attempt_spellcheck_on_volume(3)