import re
from os import name
import flair
from flair.data import Sentence
from flair.models import MultiTagger
from flair.models import SequenceTagger
from flair.tokenization import SegtokSentenceSplitter
import string

# load the NER tagger
tagger = MultiTagger.load(['pos','ner'])


# This function will extract information about singular boulder paragraphs (ie. a numbered paragraph that refers to a single boulder), returns the attributes found within the paragraph
def find_boulder_from_paragraph(match):
  
    paragraph = ""
    for word in match.text:
        paragraph += word + " " 

    # initialize sentence splitter
    splitter = SegtokSentenceSplitter()

    # use splitter to split text into list of sentences
    sentences = splitter.split(paragraph)

    size = None

    location = None

    rocktype = None

    sentence_length = 0



    for flair_sentence in sentences:
        
        # predict NER and POS tags
        tagger.predict(flair_sentence)

        # Run find location to search the sentence for the location of the boulder. 
        if location is None:
            # TODO find_Location has all locations not dealt with properly... also redo all of the find from paragraph function for rating .. 
            loc_dict, location = find_location(flair_sentence,match)
            # Get accurate position of the location in whole paragraph
            
            

            if loc_dict:
                for loc in loc_dict:
                    tup = loc_dict[loc] 
                    tup = (tup[0]+sentence_length, tup[1]+sentence_length)
                    loc_dict[loc] = tup
        
         
        # Run find size to search the sentence for the size of the boulder
        if size is None:
            siz_pos, size = find_size(flair_sentence,flair_sentence.to_original_text()) 
            
            # Get position of the size related features in the whole paragraph, size is variable therefore we use a dictionary instead of tuple
            if size:
                if "l" in siz_pos:
                    siz_pos["l"] = (siz_pos["l"][0]+sentence_length,siz_pos["l"][1]+sentence_length)

                if "b" in siz_pos:
                    siz_pos["b"] = (siz_pos["b"][0]+sentence_length,siz_pos["b"][1]+sentence_length)

                if "h" in siz_pos:
                    siz_pos["h"] = (siz_pos["h"][0]+sentence_length,siz_pos["h"][1]+sentence_length)

                if "x" in siz_pos:
                    siz_pos["x"] = (siz_pos["x"][0]+sentence_length,siz_pos["x"][1]+sentence_length)

        # Run find rocktype to search the sentence for the rocktype of the boulder. 
        if rocktype is None:
            rt_dict, rocktype = find_rocktype(flair_sentence,flair_sentence.to_original_text())
            if rt_dict:
                for rt in rt_dict:
                    tup = rt_dict[rt]
                    tup = (tup[0]+sentence_length, tup[1]+sentence_length)
                    rt_dict[rt] = tup

        
        # # If we have all features stop searching 
        # if size and location and rocktype:
        #     break

        sentence_length += len(flair_sentence.to_original_text())

    return loc_dict, siz_pos, rt_dict, location, size, rocktype

# This function analyses a sentence to extract size information relating to height and width 

def find_size(flair_sentence,sentence):

    size = re.search("([0-9]+ (X|x) [0-9]+ (X|x) [0-9]+|[0-9]+ (X|x) [0-9]+)",sentence)

    # hopefully will just be a simple l x b x h
    if size:
    
        index = sentence.find(size.group(0))

        return {"x" : (index,index+len(size.group(0)))},size.group(0)

    else: 
    # If not, then check for length and breadth keywords.. not checking specifically for height because height is mentioned alot when desribing boulder locality
        if "breadth".casefold() in sentence.casefold() or "length".casefold() in sentence.casefold() or "width".casefold() in sentence.casefold():
            spans = flair_sentence.get_spans('pos')
            breadth, length, height = None, None, None
            breadth_index, length_index, height_index = None, None, None

            # Each word is searched in a span outwords and the first cardinal number found near the breadth or length or width.. that number is assigned to the breadth, length ..
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
                               
                                if (j != breadth_index and j != length_index and spans[j].text.isnumeric()):
                                    height = spans[j].text
                                    breadth_index = j
                                
                               
                                if span_counter == 0:
                                    if (j == breadth_index or j == length_index) and height is None:
                                    
                                        span_index = j
                                        span_counter = 1 

                                    
                        if not height:
                            for label in spans[k].labels:
                                if "CD" in label.value:
                                    if k != breadth_index and k != length_index and spans[k].text.isnumeric():
                               
                                        
                                        height = spans[k].text 
                                        breadth_index = k  

                                    if span_counter == 0:
                                        if (j == breadth_index or j == length_index) and height is None:
                                            
                                            span_index = j
                                            span_counter = 1 
                


            # TODO: Only uses the key words location right now needs to be more accurate showing the number it associates with the dimension aswell.. 
                 
            l1, l2 = sentence.casefold().find("length"),sentence.casefold().find("length") + 6
            b1, b2 = sentence.casefold().find("breadth"),sentence.casefold().find("breadth") + 7
            if b1 == -1:
                b1, b2 = sentence.casefold().find("width"),sentence.casefold().find("width") + 7
            h1, h2 = sentence.casefold().find("height"),sentence.casefold().find("height") + 6

            siz_pos = {}

            if l1 != -1:
                siz_pos["l"] = (l1,l2)

            if b1 != -1:
                siz_pos["b"] = (b1,b2)
    
            if h1 != -1:
                siz_pos["h"] = (h1,h2)

            return siz_pos,"Length :" + str(length) + " Breadth : " + str(breadth) + " Height : " + str(height)
        
        return None, None

# This function analyses a sentence to extract the rock type mentioned 

# TODO Needs secondary rocktype list to query over.. 

rocktypes = []
with open('./dictionaries/rocktypes.txt', 'r') as f:
    for line in f:
        word = ""
        for char in line:
            if char.isalpha():
                word += char
        if len(word):
            rocktypes.append(word)          


def find_rocktype(flair_sentence, sentence):

    rt_dict = {}
    rt = ""
    first = True
    if any(rocktype.casefold() in sentence.casefold() for rocktype in rocktypes):
        for word in re.sub(r"[,.—;@#?!&$]+\ *", " ", sentence).split(" "):
            if word.casefold() in rocktypes:
                print(word)
                index = sentence.casefold().find(word.casefold())
                print(index)
                if first:
                    rt = word
                    first = False
                if not(word in rt_dict):
                    rt_dict[word] = (index,index + len(word))
    if rt_dict:
        return rt_dict, rt
    else:
        return None, None

# This function analyses a sentence to extract the main location mentioned 

# TODO needs more accurate location ! 

def find_location(flair_sentence,match):    
    location = ''    
    loc_dict = {}

    # Manual override for first report as the text orientation is consistent
    if True:
        senlen = 0
        for word in match.iterrows():
            if word[1]['left'] < 900:
                if not word[1]['text'].isupper():                    
                    location = word[1]['text']
                    loc_dict[word[1]["text"]] = (senlen,senlen+len(word[1]))
            senlen += len(word[1]['text'])
    
    location = location.split(".—")[0]

    first = True
    for entity in flair_sentence.to_dict(tag_type='ner')['entities']:
        for label in entity["labels"]:
            if "LOC" in label.value:

                if first:
                    location += " - " + entity["text"]
                    first = False

                if not (entity["text"] in loc_dict):
                    loc_dict[entity["text"]] = (entity["start_pos"],entity["end_pos"])

    if loc_dict:
        return loc_dict, location  
    else:
        return None, None


        
 
