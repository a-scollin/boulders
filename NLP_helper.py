import re
from os import name
import flair
from flair.data import Sentence
from flair.models import MultiTagger
from flair.models import SequenceTagger
from flair.tokenization import SegtokSentenceSplitter

# load the NER tagger
tagger = MultiTagger.load(['pos','ner'])


# This function will extract information about singular boulder paragraphs (ie. a numbered paragraph that refers to a single boulder), returns the attributes found within the paragraph
def find_boulder_from_numbered_regex(match):

    number = match[0] 
        
    paragraph = match[1]  

    # initialize sentence splitter
    splitter = SegtokSentenceSplitter()

    # use splitter to split text into list of sentences
    sentences = splitter.split(paragraph)

    size = None

    location = None

    rocktype = None

    for flair_sentence in sentences:
        
        # predict NER and POS tags
        tagger.predict(flair_sentence)

        if location is None:
            location = find_location(flair_sentence,flair_sentence.to_original_text())

        if size is None:
            size = find_size(flair_sentence,flair_sentence.to_original_text())
        
        if rocktype is None:
            rocktype = find_rocktype(flair_sentence,flair_sentence.to_original_text())
    
        if size and location and rocktype:
            break

    return number, location, size, rocktype


# This function analyses a sentence to extract size information relating to height and width 

def find_size(flair_sentence,sentence):
    
    size = re.search("[0-9]+ (X|x) [0-9]+ (X|x) [0-9]+",sentence)
    
    if size:
    
        return size.group(0)

    else: 
        
        return size

# This function analyses a sentence to extract the rock type mentioned 

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
        for word in sentence.split(" "):
            if word.casefold() in rocktypes:
                return word


# This function analyses a sentence to extract the main location mentioned 

def find_location(flair_sentence,sentence):    
    location = None
    for entity in flair_sentence.to_dict(tag_type='ner')['entities']:
        for label in entity["labels"]:
            if "LOC" in label.value:
                return entity["text"]

    
 
