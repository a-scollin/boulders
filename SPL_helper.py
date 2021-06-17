import json
from pdf2image import convert_from_path
import OCR_helper as OCR
from spellchecker import SpellChecker
import pandas as pd

def get_spellchecked_volume(number):

    images = convert_from_path("./bouldercopies/" + str(number) + "_Report.pdf", 500)
    unchecked_words = []    
    word_data = []

    for image in images:
        df = OCR.read_image_to_df(image)
        for word in df["text"]:
            unchecked_words.append(word)
             
        word_data.append(df)

    corrections = attempt_spellcheck_on_volume(unchecked_words)

    for word_correction in corrections:

        for df in word_data:
            
            if not df.loc[df['text'] == word_correction[0]].empty:
                print(len(df.loc[df['text'] == word_correction[0]]))
                    
        
    
    return word_data
    


def attempt_spellcheck_on_volume(words):
             
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


    spell.word_frequency.load_words(safewords)


    # find those words that may be misspelled
    misspelled = spell.unknown(words)

    corrections = []

    for word in misspelled:
        # For misspellings based on puncutation and numerics 
        for char in word :
            if not (char.isalpha() or char.isnumeric()):
                break
        # Might not work
        if (char.isalpha() or char.isnumeric()):
            corrections.append((word,spell.correction(word)))

    return corrections

# review_vol(input("please input the number of the volume you wish to analyse : "))

