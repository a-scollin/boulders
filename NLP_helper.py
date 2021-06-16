import re
from os import name
import flair
from flair.data import Sentence
from flair.models import MultiTagger
from flair.models import SequenceTagger


# load the NER tagger
tagger = SequenceTagger.load('ner')

def find_boulder_from_numbered_regex(match):

    number = match[0] 
        
    paragraph = match[1]

    sentences = paragraph.split('.')

    sentences = [sentence for sentence in sentences if len(sentence) > 5]

    size = None

    location = None

    for sentence in sentences:

        flair_sentence = Sentence(sentence)
        
        # predict NER tags
        tagger.predict(flair_sentence)

        if location is None:
            location = find_location(flair_sentence,sentence)

        if size is None:
            size = find_size(flair_sentence,sentence)
    
        if size and location:
            break

    return number, location, size


def find_size(flair_sentence,sentence):
    
    size = re.search("[0-9]+ (X|x) [0-9]+ (X|x) [0-9]+",sentence)
    
    if size:
    
        return size.group(0)

    else: 
        
        return size
    



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
