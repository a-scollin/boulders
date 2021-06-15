import re
from os import name
import flair
from flair.data import Sentence
from flair.models import SequenceTagger

# load the NER tagger
tagger = SequenceTagger.load('ner')

def find_boulder(match):
   
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
                for i in range(0,len(flair_sentence)):
                    if str(flair_sentence[i].get_tag('ner').value) == "S-LOC":
                        location = sentence

            size = re.search("[0-9]+ (X|x) [0-9]+ (X|x) [0-9]+",sentence)
        
            if size and location:
                size = size.group(0)
                break

        print("Boulder " + number + " located @ " + str(location) + " sized " + str(size) + " feet" )
            