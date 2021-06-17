import re
from os import name
import flair
from flair.data import Sentence
from flair.models import MultiTagger
from flair.models import SequenceTagger


# load the NER tagger
tagger = MultiTagger.load(['pos','ner'])

def find_boulder_from_numbered_regex(match):

    number = match[0] 
        
    paragraph = match[1]

    sentences = paragraph.split('.')

    sentences = [sentence for sentence in sentences if len(sentence) > 5]

    size = None

    location = None

    rocktype = None

    for sentence in sentences:

        flair_sentence = Sentence(sentence)
        
        # predict NER tags
        tagger.predict(flair_sentence)

        if location is None:
            location = find_location(flair_sentence,sentence)

        if size is None:
            size = find_size(flair_sentence,sentence)
        
        if rocktype is None:
            rocktype = find_rocktype(flair_sentence,sentence)
    
        if size and location and rocktype:
            break

    return number, location, size, rocktype


def find_size(flair_sentence,sentence):
    
    size = re.search("[0-9]+ (X|x) [0-9]+ (X|x) [0-9]+",sentence)
    
    if size:
    
        return size.group(0)

    else: 
        
        return size

def find_rocktype(flair_sentence, sentence):

    rocktypes = []    

    with open('./dictionaries/rocktypes.txt', 'r') as f:
        for line in f:
            word = ""
            for char in line:
                if char.isalpha():
                    word += char
            if len(word):
                rocktypes.append(word)           

    if any(rocktype.casefold() in sentence.casefold() for rocktype in rocktypes):
        for rocktype in rocktypes:
            if rocktype.casefold() in sentence.casefold():
                return rocktype
        


def find_location(flair_sentence,sentence):    
    location = None
    
    for i in range(0,len(flair_sentence)):
        if str(flair_sentence[i].get_tag('ner').value) == "S-LOC":
            location = sentence
    
    if location is None:
        for i in range(0,len(flair_sentence)):
            if str(flair_sentence[i].get_tag('ner').value[2:]) == "LOC":
                location = sentence
    
    return location
