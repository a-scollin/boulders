import json
from pdf2image import convert_from_path
import OCR_helper as OCR
from spellchecker import SpellChecker
import pandas as pd
import string

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

    # Corrections ^^ works very well but actually making the swaps \/ doens't idk why  

    check = []

    for word_correction in corrections:
        for df in word_data:
            df = df.replace([word_correction[0]],word_correction[1])
          
            for word in df["text"]:
                check.append(word)

    if check == unchecked_words:
        print("They're the same") 
    

    word_string = ""

    for df in word_data:
        for index in df.index:
            word = df[df.index == index]["text"]
            word_string += word.array[0] + " "
            
    with open('report_text.txt', 'w') as f:
        f.write(word_string + "\nCorrections made :\n" + str(corrections))


    return word_data, word_string
    


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

    # Problematic word :P
    spell.word_frequency.remove_words(['geiss'])


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
        else:
            if any(char.isalpha() for char in word):
                word_with_punc = word
                word.translate(str.maketrans('', '', string.punctuation))
                miss = spell.unknown(word)
                if miss:
                    corrections.append((word_with_punc,spell.correction(word)))


    return corrections

# review_vol(input("please input the number of the volume you wish to analyse : "))

