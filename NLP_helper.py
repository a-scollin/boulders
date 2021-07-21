import re
from os import name
import flair
from flair.data import Sentence
from flair.models import MultiTagger
from flair.models import SequenceTagger
from flair.tokenization import SegtokSentenceSplitter
import string
from word2number import w2n

# load the NER tagger
tagger = MultiTagger.load(['pos','ner'])

compass = []
with open('./dictionaries/compass.txt', 'r') as f:
    for line in f:
        word = ""
        for char in line:
            if char.isalpha() or char == '.' or char == ',':
                word += char
        if len(word):
            compass.append(word)      


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

    author = None

    dims = None

    numberofboulders = None

    sentence_length = 0


    extra = None

    rt_dict = {}
    siz_pos = {}
    aut_dict = {}   
    loc_dict = {}
    dim_dict = {}
    extra_dict = {}
    comp_dict = {}
    numbox = None

    for flair_sentence in sentences:
        
        # predict NER and POS tags
        tagger.predict(flair_sentence)


        if "boulders" in flair_sentence.to_original_text() and numberofboulders is None:

            numberstring, numberofboulders = find_number(flair_sentence)

            if numberstring:
                for j, word in match.iterrows():
                    if numberstring in word['text']:
                        numbox = (word['left'], word['top'], word['width'], word['height'])

        can_extra_dict, can_extra = find_extra(flair_sentence,flair_sentence.to_original_text())

        if extra is None and can_extra:
            extra = can_extra

        if can_extra_dict:
            for ext in can_extra_dict:
                ext_hl_array = []
                for j, word in match.iterrows():
                    if ext.casefold() in word['text'].casefold():
                        box = (word['left'], word['top'], word['width'], word['height'])
                        ext_hl_array.append(box)
        
                if ext in extra_dict:
                    extra_dict[ext].extend(ext_hl_array)
                else:
                    extra_dict[ext] = ext_hl_array

        can_dim_dict, can_dims = find_dims(flair_sentence,flair_sentence.to_original_text())

        if dims is None and can_dims:
            dims = can_dims

        if can_dim_dict:
            for dim in can_dim_dict:
                dim_hl_array = []
                for j, word in match.iterrows():
                    if dim.casefold() in word['text'].casefold():
                        box = (word['left'], word['top'], word['width'], word['height'])
                        dim_hl_array.append(box)
        
                if dim in dim_dict:
                    dim_dict[dim].extend(dim_hl_array)
                else:
                    dim_dict[dim] = dim_hl_array


        # Run find location to search the sentence for the location of the boulder. 
       
        # TODO find_Location has all locations not dealt with properly... also redo all of the find from paragraph function for rating .. 
        can_loc_dict, can_location = find_location(flair_sentence,match)
        # Get accurate position of the location in whole paragraph

        if location is None and can_location:
            location = can_location
        
        if can_loc_dict:
            
            for loc in can_loc_dict:
                loc_hl_array = []
                for j, word in match.iterrows():
                    if loc in word['text']:
                        if not loc[0].isupper() and len(loc) < 4:
                            continue
                        box = (word['left'], word['top'], word['width'], word['height'])
                        loc_hl_array.append(box)
                                
                if loc in loc_dict:
                    loc_dict[loc].extend(loc_hl_array)
                else:
                    loc_dict[loc] = loc_hl_array
        


        for j, word in match.iterrows():
            last_character = None
            stripped_word = ""
            for character in word['text'].replace(",", "."):
                if character != last_character:
                    stripped_word += character
                last_character = character
            if stripped_word in compass:
                if word['text'] in comp_dict:
                    comp_dict[word['text']].append((word['left'], word['top'], word['width'], word['height']))
                else:
                    comp_dict[word['text']] = [(word['left'], word['top'], word['width'], word['height'])]

        openquote = False
        can_loc_box = []
        can_location = ""
        for j, word in match.iterrows():

            if len(can_location) > 30 and openquote:
                openquote = False
            elif ('“' in word['text'] or '¢' in word['text'] or '*' in word['text']) and not openquote:
                can_location = word['text']
                can_loc_box.append((word['left'], word['top'], word['width'], word['height']))
                openquote = True
            elif ('”' in word['text'] and openquote):
                can_location += " " + word['text']
                can_loc_box.append((word['left'], word['top'], word['width'], word['height']))
                openquote = False
                
                if location:
                    location += ' - ' + can_location 
                else:
                    location = can_location
                    
                if can_location in loc_dict:
                    loc_dict[can_location].extend(can_loc_box)
                else:
                    loc_dict[can_location] = can_loc_box
                
                can_loc_box = []
            elif openquote:
                if len(can_location) < 3:
                    can_location += word['text']    
                else:
                    can_location += " " + word['text']
                can_loc_box.append((word['left'], word['top'], word['width'], word['height']))
            



                        
        can_aut_dict, can_author = find_author(flair_sentence)

        if author is None and can_author:
            author = can_author

        if can_aut_dict:
            
            for aut in can_aut_dict:
                if len(aut) < 4:
                    continue
                aut_hl_array = []
                for j, word in match.iterrows():
                    if aut.casefold() in word['text'].casefold():
                        box = (word['left'], word['top'], word['width'], word['height'])
                        aut_hl_array.append(box)
                
                if aut in aut_dict:
                    aut_dict[aut].extend(aut_hl_array)
                else:
                    aut_dict[aut] = aut_hl_array


        # Run find size to search the sentence for the size of the boulder
        
        can_siz_pos, can_size = find_size(flair_sentence,flair_sentence.to_original_text()) 

        if size is None:    
            size = can_size

        # Get position of the size related features in the whole paragraph, size is variable therefore we use a dictionary instead of tuple
        if can_siz_pos:
            for siz in can_siz_pos:
                siz_pos[siz] = (can_siz_pos[siz][0]+sentence_length,can_siz_pos[siz][1]+sentence_length)

        # Run find rocktype to search the sentence for the rocktype of the boulder. 
        
        can_rts, can_rocktype = find_rocktype(flair_sentence,flair_sentence.to_original_text())

        if rocktype is None and can_rocktype:
            rocktype = can_rocktype

        if can_rts:
            for rt in can_rts:
                rt_hl_array = []
            
                for j, word in match.iterrows():
                    if rt.casefold() in word['text'].casefold():
                        box = (word['left'], word['top'], word['width'], word['height'])
                        rt_hl_array.append(box)
                
                if rt in rt_dict:
                    rt_dict[rt].extend(rt_hl_array)
                else:
                    rt_dict[rt] = rt_hl_array
      

        # # If we have all features stop searching 
        # if size and location and rocktype:
        #     break

        sentence_length += len(flair_sentence.to_original_text())
    
    if numberofboulders is None:
        numberofboulders = 1 

    return loc_dict, siz_pos, rt_dict, aut_dict, location, size, rocktype, author, numberofboulders, numbox, extra_dict, extra, dim_dict, dims, comp_dict


ext_features = []
with open('./dictionaries/extra.txt', 'r') as f:
    for line in f:
        word = ""
        for char in line:
            if char.isalpha():
                word += char
        if len(word):
            ext_features.append(word)          
    
colours = []
with open('./dictionaries/colours.txt', 'r') as f:
    for line in f:
        word = ""
        for char in line:
            if char.isalpha():
                word += char
        if len(word):
            colours.append(word)          
    

def find_extra(flair_sentence, sentence):
    exts = []
    extra = ""
    first = True

    lastword = None
    
    if any(ext.casefold() in sentence.casefold() for ext in ext_features):
        for word in re.sub(r"[,.—;@#?!&$]+\ *", " ", sentence).split(" "):
            if word.casefold() in ext_features:
               
                if lastword:
                    ex_word = lastword + " " + word if lastword in colours else word
                else:
                    ex_word = word                
                
                if len(extra):
                    extra += ' - ' + ex_word
                else:
                    extra = ex_word

                exts.extend(ex_word.split(' '))         
            
            lastword = word       
    
    if exts:   
        return list(dict.fromkeys(exts)), extra
    else:
        return None, None



def find_number(flair_sentence):
    for entity in flair_sentence.to_dict(tag_type='pos')['entities']:    
        for label in entity['labels']:
            if "boulders" in entity['text']:
                return None, None
            if "CD" in label.value:
                if not entity['text'].strip().isnumeric() and entity['text'].strip().isalpha():
                    try:
                        ret = int(w2n.word_to_num(entity['text']))
                        return entity['text'], ret
                    except:
                        return None, None
    return None, None

# Currently Hard coded for report 1 
def find_author(flair_sentence):

    if True:

        author = None 

        auts = []

        brackets = re.findall('\(.*?\)|\(.*?-', flair_sentence.to_original_text())
        for bracket in brackets:
            if "Report".casefold() in bracket.casefold():
                
                if len(bracket) > 100:
                    continue

                author = bracket

                index = flair_sentence.to_original_text().casefold().find(bracket.casefold())

                auts.extend(bracket.split(' '))

                return auts, author

    author = None 

    auts = []

    for entity in flair_sentence.to_dict(tag_type='ner')['entities']:
        for label in entity['labels']:
            if "PER" in label.value:
                if author:
                    author += ", " + entity['text']
                else:
                    author = entity["text"]

                auts.extend(entity['text'].split(' '))
                
                


    #     else:

    #         index = flair_sentence.to_original_text().casefold().find(bracket.casefold())
    #         fsentence = Sentence(bracket)
    #         tagger.predict(fsentence)
    #         for entity in fsentence.to_dict(tag_type='ner')['entities']:
    #             for label in entity['labels']:
    #                 if "PER" in label.value:

    #                     if author:
    #                         author += ", " + entity['text']
    #                     else:
    #                         author = entity["text"]
                        
    #                     if not (entity["text"] in aut_dict):
    #                         aut_dict[entity["text"]] = (index+entity["start_pos"],index+entity["end_pos"])

    if auts:
        return auts, author  
    else:
        return None, None


dimensions = []
with open('./dictionaries/dimensions.txt', 'r') as f:
    for line in f:
        word = ""
        for char in line:
            if char.isalpha():
                word += char
        if len(word):
            dimensions.append(word)          

metrics = []
with open('./dictionaries/metrics.txt', 'r') as f:
    for line in f:
        word = ""
        for char in line:
            if char.isalpha():
                word += char
        if len(word):
            metrics.append(word)      

# This function analyses a sentence to extract size information relating to height and width 

def find_dims(flair_sentence,sentence):
    
        # Needs a bit more work! none type error so far... :/ TODO 16/07
    dims = []
    size = None
#  if dimension != 'above' could be the play
    if any(dimension in sentence for dimension in dimensions):
        number = None
        dim = None
        met = None
        for entity in flair_sentence.to_dict(tag_type='pos')['entities']:

            if entity['text'].casefold() in dimensions:
                
                if dim and entity['text'] == 'above':
                    continue

                dim = entity['text']
                
            
            for label in entity["labels"]:
                if "CD" in label.value:
                    if any(metric in sentence[entity['start_pos']-5:entity['end_pos']+12] for metric in metrics if metric != "miles" and metric != "yards"):
                        number = entity['text']
                        met = None
                        if any(sub.isnumeric() for sub in sentence[entity['start_pos']+len(entity['text']):entity['end_pos']+12].split(" ")):
                            continue
                        for metric in metrics:
                            if metric in sentence[entity['start_pos']+len(entity['text']):entity['end_pos']+12]:
                                if met: 
                                    met += " " + metric 
                                else:
                                    met = metric
            
            if (dim and number and met) or (number and met):
        
                if dim is None:
                    if "cubic" in met:
                        dim = "volume"
                    elif "tons" in met:
                        dim = "weight"
                    else:
                        continue

                if "high" in dim or "height" in dim or "above" in dim:
                    try:
                        if "sea" in sentence[entity['start_pos']-5:entity['end_pos']+20] or w2n.word_to_num(number) > 100:
                            if dim not in dims:
                                dims.append(dim)
                            dim = 'height above sea level'
                    except:
                        
                        print("Nan : " + number)
                    
                        number = None

                        continue

                if dim == "above":
                    dim = None
                    continue

                if size:
                    size += ", " + dim + " : " + number + " " + met
                else:
                    size = dim + " : " + number + " " + met

                if dim not in dims:
                    dims.extend(dim.split(' '))
                
                if number not in dims:
                    dims.append(number)

                if met not in dims:
                    dims.extend(met.split(' '))

                number = None
                dim = None
                met = None
       

    if dims:
        print(sentence)
        print("DIMS : " + str(list(dict.fromkeys(dims))))
        print("SIZE : " + str(size))
        return list(dict.fromkeys(dims)), size
    else:
        return None, None

def find_size(flair_sentence,sentence):

    size = re.findall("([0-9]+ (X|x) [0-9]+ (X|x) [0-9]+|[0-9]+ (X|x) [0-9]+)",sentence)

    # hopefully will just be a simple l x b x h
    if size:
    
        siz_dict = {}

        sizes = None

        for match in size:

            for submatch in list(match):

                if len(submatch) > 3:

                    index = sentence.find(submatch)

                    siz_dict[match] = (index,index+len(submatch))

                    if sizes:
                        sizes += ", " + submatch 
                    else:
                        sizes = submatch

        return siz_dict, sizes            

    

    return None, None 
        
        
        
        
        
            # # If not, then check for length and breadth keywords.. not checking specifically for height because height is mentioned alot when desribing boulder locality
    #     if "breadth".casefold() in sentence.casefold() or "length".casefold() in sentence.casefold() or "width".casefold() in sentence.casefold():
    #         spans = flair_sentence.get_spans('pos')
    #         breadth, length, height = None, None, None
    #         breadth_index, length_index, height_index = None, None, None

    #         # Each word is searched in a span outwords and the first cardinal number found near the breadth or length or width.. that number is assigned to the breadth, length ..
    #         for i in range(0,len(spans)):
    #             if (spans[i].text.casefold() == "breadth".casefold() or spans[i].text.casefold() == "width".casefold()) and not breadth:
                    
    #                 span_counter = 0    
    #                 j = i
    #                 k = i 
    #                 while not breadth and (j > 0 or k < len(spans) - 1):           
                        
    #                     if span_counter:
    #                         span_counter += 1 
    #                         if span_counter > 8:
    #                             breadth = spans[span_index].text
    #                             breadth_index = span_index
    #                             break
                        
    #                     if j > 0:
    #                         j -= 1
    #                     if k < len(spans) - 1:
    #                         k += 1 
    #                     for label in spans[j].labels:    
    #                         if "CD" in label.value:
                                
    #                             if (j != length_index and j != height_index and spans[j].text.isnumeric()):
    #                                 breadth = spans[j].text
    #                                 breadth_index = j
                                
                                
    #                             if span_counter == 0:
    #                                 if (j == length_index or j == height_index) and breadth is None:
    #                                     span_index = j
    #                                     span_counter = 1 

                                    
    #                     if not breadth:
    #                         for label in spans[k].labels:
    #                             if "CD" in label.value:
    #                                 if k != length_index and k != height_index and spans[k].text.isnumeric():
                                     
                                        
    #                                     breadth = spans[k].text 
    #                                     breadth_index = k  

    #                                 if span_counter == 0:
    #                                     if (j == length_index or j == height_index) and breadth is None:
    #                                         span_index = j
    #                                         span_counter = 1 
                
                
    #             if spans[i].text.casefold() == "length".casefold() and not length:
                    
    #                 span_counter = 0    
    #                 j = i
    #                 k = i 
    #                 while not length and (j > 0 or k < len(spans) - 1):           
                        
    #                     if span_counter:
    #                         span_counter += 1 
    #                         if span_counter > 6:
    #                             length = spans[span_index].text
    #                             breadth_index = span_index
    #                             break
                        
    #                     if j > 0:
    #                         j -= 1
    #                     if k < len(spans) - 1:
    #                         k += 1 
    #                     for label in spans[j].labels:    
    #                         if "CD" in label.value:
                             
    #                             if (j != breadth_index and j != height_index and spans[j].text.isnumeric()):
    #                                 length = spans[j].text
    #                                 breadth_index = j
                            
    #                             if span_counter == 0:
    #                                 if (j == breadth_index or j == height_index) and length is None:
                                        
    #                                     span_index = j
    #                                     span_counter = 1 

                                    
    #                     if not length:
    #                         for label in spans[k].labels:
    #                             if "CD" in label.value:
    #                                 if k != breadth_index and k != height_index and spans[k].text.isnumeric():
                               
                                        
    #                                     length = spans[k].text 
    #                                     breadth_index = k  

    #                                 if span_counter == 0:
    #                                     if (j == breadth_index or j == height_index) and length is None:
                                            
    #                                         span_index = j
    #                                         span_counter = 1 

    #             if spans[i].text.casefold() == "height".casefold() and not height:
                    
    #                 span_counter = 0    
    #                 j = i
    #                 k = i 
    #                 while not height and (j > 0 or k < len(spans) - 1):           
                        
    #                     if span_counter:
    #                         span_counter += 1 
             
    #                         if span_counter > 6:
    #                             height = spans[span_index].text
    #                             breadth_index = span_index
    #                             break
                        
    #                     if j > 0:
    #                         j -= 1
    #                     if k < len(spans) - 1:
    #                         k += 1 
    #                     for label in spans[j].labels:    
    #                         if "CD" in label.value:
                               
    #                             if (j != breadth_index and j != length_index and spans[j].text.isnumeric()):
    #                                 height = spans[j].text
    #                                 breadth_index = j
                                
                               
    #                             if span_counter == 0:
    #                                 if (j == breadth_index or j == length_index) and height is None:
                                    
    #                                     span_index = j
    #                                     span_counter = 1 

                                    
    #                     if not height:
    #                         for label in spans[k].labels:
    #                             if "CD" in label.value:
    #                                 if k != breadth_index and k != length_index and spans[k].text.isnumeric():
                               
                                        
    #                                     height = spans[k].text 
    #                                     breadth_index = k  

    #                                 if span_counter == 0:
    #                                     if (j == breadth_index or j == length_index) and height is None:
                                            
    #                                         span_index = j
    #                                         span_counter = 1 
                


    #         # TODO: Only uses the key words location right now needs to be more accurate showing the number it associates with the dimension aswell.. 
                 
    #         l1, l2 = sentence.casefold().find("length"),sentence.casefold().find("length") + 6
    #         b1, b2 = sentence.casefold().find("breadth"),sentence.casefold().find("breadth") + 7
    #         if b1 == -1:
    #             b1, b2 = sentence.casefold().find("width"),sentence.casefold().find("width") + 7
    #         h1, h2 = sentence.casefold().find("height"),sentence.casefold().find("height") + 6

    #         siz_pos = {}

    #         if l1 != -1:
    #             siz_pos["l"] = (l1,l2)

    #         if b1 != -1:
    #             siz_pos["b"] = (b1,b2)
    
    #         if h1 != -1:
    #             siz_pos["h"] = (h1,h2)

    #         return siz_pos,"Length :" + str(length) + " Breadth : " + str(breadth) + " Height : " + str(height)
        
    #     return None, None

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

    rts = []
    rt = ""
    lastword = None
    if any(rocktype.casefold() in sentence.casefold() for rocktype in rocktypes):
        for word in re.sub(r"[,.—;@#?!&$]+\ *", " ", sentence).split(" "):
       
            if word.casefold() in rocktypes:

                if lastword:
                    ex_word = lastword + " " + word if lastword in colours else word
                else:   
                    ex_word = word
                
                if len(rt):
                    rt += ", " + ex_word
                else:
                    rt = ex_word
            
                rts.extend(ex_word.split(" "))

            lastword = word

    if rts:
        return list(dict.fromkeys(rts)), rt
    else:
        return None, None

# This function analyses a sentence to extract the main location mentioned 

# TODO needs more accurate location ! 

def find_location(flair_sentence,match):    
    location = ''    
    locs = []

    # Manual override for first report as the text orientation is consistent
    if False:
        senlen = 0
        for word in match.iterrows():
            if word[1]['left'] < 900:
                if not word[1]['text'].isupper():                    
                    location = word[1]['text']
                    loc_dict[word[1]["text"]] = (senlen,senlen+len(word[1]))
            senlen += len(word[1]['text'])
    
        location = location.split(".—")[0]
    
    if False:
        for j, word in match.iterrows():
            if '.—' in word['text'] and word['text'][0].isupper():
                location = word['text'].split('.—')[0]
                locs.append(word['text'])
                break



    
    for entity in flair_sentence.to_dict(tag_type='ner')['entities']:
        for label in entity["labels"]:
            if "LOC" in label.value:
                
                if not len(location):
                    location = entity["text"] 
                elif entity['text'] not in location:
                    location += " - " + entity["text"]
                    
                locs.extend(entity['text'].split(' '))
        

    if locs:
        return locs, location  
    else:
        return None, None


        
 
