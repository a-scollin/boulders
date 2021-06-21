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

    # hopefully will just be a simple l x b x h
    if size:
    
        return size.group(0)

    else: 
    # If not, then check for length and breadth keywords.. not checking specifically for height because height is mentioned alot when desribing boulder locality
        if "breadth".casefold() in sentence.casefold() or "length".casefold() in sentence.casefold() or "width".casefold() in sentence.casefold():
            spans = flair_sentence.get_spans('pos')
            breadth, length, height = None, None, None
            breadth_index, length_index, height_index = None, None, None

            for i in range(0,len(spans)):
        
                if (spans[i].text.casefold() == "breadth".casefold() or spans[i].text.casefold() == "width".casefold()) and not breadth:
                    span_counter = 0    
                    j = i
                    k = i 
                    while not breadth and (j > 0 or k < len(spans) - 1):           
                        
                        if span_counter:
                            span_counter += 1 
                            if span_counter > 8:
                                breadth = spans[span_index].text
                                breadth_index = span_index
                                break
                        
                        if j > 0:
                            j -= 1
                        if k < len(spans) - 1:
                            k += 1 
                        for label in spans[j].labels:    
                            if "CD" in label.value:
                                
                                if (j != length_index and j != height_index and spans[j].text.isnumeric()):
                                    breadth = spans[j].text
                                    breadth_index = j
                                
                                
                                if span_counter == 0:
                                    if (j == length_index or j == height_index) and breadth is None:
                                        span_index = j
                                        span_counter = 1 

                                    
                        if not breadth:
                            for label in spans[k].labels:
                                if "CD" in label.value:
                                    if k != length_index and k != height_index and spans[k].text.isnumeric():
                                     
                                        
                                        breadth = spans[k].text 
                                        breadth_index = k  

                                    if span_counter == 0:
                                        if (j == length_index or j == height_index) and breadth is None:
                                            span_index = j
                                            span_counter = 1 
    
                
                
                if spans[i].text.casefold() == "length".casefold() and not length:
                    
                    span_counter = 0    
                    j = i
                    k = i 
                    while not length and (j > 0 or k < len(spans) - 1):           
                        
                        if span_counter:
                            span_counter += 1 
                            if span_counter > 6:
                                length = spans[span_index].text
                                breadth_index = span_index
                                break
                        
                        if j > 0:
                            j -= 1
                        if k < len(spans) - 1:
                            k += 1 
                        for label in spans[j].labels:    
                            if "CD" in label.value:
                             
                                if (j != breadth_index and j != height_index and spans[j].text.isnumeric()):
                                    length = spans[j].text
                                    breadth_index = j
                            
                                if span_counter == 0:
                                    if (j == breadth_index or j == height_index) and length is None:
                                        
                                        span_index = j
                                        span_counter = 1 

                                    
                        if not length:
                            for label in spans[k].labels:
                                if "CD" in label.value:
                                    if k != breadth_index and k != height_index and spans[k].text.isnumeric():
                               
                                        
                                        length = spans[k].text 
                                        breadth_index = k  

                                    if span_counter == 0:
                                        if (j == breadth_index or j == height_index) and length is None:
                                            
                                            span_index = j
                                            span_counter = 1 

                if spans[i].text.casefold() == "height".casefold() and not height:
                    
                    span_counter = 0    
                    j = i
                    k = i 
                    while not height and (j > 0 or k < len(spans) - 1):           
                        
                        if span_counter:
                            span_counter += 1 
             
                            if span_counter > 6:
                                height = spans[span_index].text
                                breadth_index = span_index
                                break
                        
                        if j > 0:
                            j -= 1
                        if k < len(spans) - 1:
                            k += 1 
                        for label in spans[j].labels:    
                            if "CD" in label.value:
                                # print("CD!")
                                # print(spans[j].text)
                                if (j != breadth_index and j != length_index and spans[j].text.isnumeric()):
                                    height = spans[j].text
                                    breadth_index = j
                                
                                # print(breadth_index)
                                # print(j)
                                # print(height)
                                if span_counter == 0:
                                    if (j == breadth_index or j == length_index) and height is None:
                                        # print("span on")
                                        span_index = j
                                        span_counter = 1 

                                    
                        if not height:
                            for label in spans[k].labels:
                                if "CD" in label.value:
                                    if k != breadth_index and k != length_index and spans[k].text.isnumeric():
                                        # print("K")
                                        # print(span_counter)
                                        # print(spans[k].text)

                                        # print(i)
                                        # print(j)
                                        # print(k)
                                        
                                        height = spans[k].text 
                                        breadth_index = k  

                                    if span_counter == 0:
                                        if (j == breadth_index or j == length_index) and height is None:
                                            # print("span on")
                                            span_index = j
                                            span_counter = 1 
                                    
            return "Length :" + str(length) + " Breadth : " + str(breadth) + " Height : " + str(height)
        
        return None
                

                    

        

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
    location = ""
    for entity in flair_sentence.to_dict(tag_type='ner')['entities']:
        for label in entity["labels"]:
            if "LOC" in label.value:
                location += entity["text"] + " "

    return location
    
 
