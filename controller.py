from functools import total_ordering
import json
import pickle
import re
import sys
from os import name

import numpy as np
from numpy.core.fromnumeric import size
import pandas as pd
# Convert from path reutrns a list of PIL images making it very easy to use
from pdf2image import convert_from_path
from PIL import Image
import cv2

import NLP_helper
import OCR_helper as OCR
import SPL_helper as SPL


# This is the main entry point function for the project, it takes a number as an argument and will run a complete boulder data extraction over whatever volume is specified
def review_vol(number):

    patch = False


    # Reports 3 and 4 are a different structure being entries in a journal instead of their own books. 
    if number == "3" or number == "4":
        return print_vol(number)
        
    print("Reviewing volume : " + str(number))
    print("Running OCR and Spellchecker...")


    # Getting the OCR'ed and Spellchecked volume back in a word_string and dataframe 
    word_data, word_string = SPL.get_spellchecked_volume(number)
       

    # Saving this data so we don't need to OCR and Spellcheck every time
    with open('word_data.pickle', 'wb') as f:
        pickle.dump(word_data, f)

    with open('word_string.pickle', 'wb') as f:
        pickle.dump(word_string, f)

    
    # Get boulders using NLP techniques.. Also an entry point for the saved OCR to be analysed 
    df = get_boulders(word_data, word_string)

    print("All done!")

    # Print whole dataframe

    pd.set_option("display.max_rows", None, "display.max_columns", None)

    print(df)

    # Saving output

    if input("Would you like to save this data to a csv file?  ( enter y or n ) : " ) == 'y':
        df.to_csv(input("Please enter filename"))


# TODO: Entry point for analysing the OCR'ed data.. Will need to be expanded to include multiple page spanning analysis and more search terms, not just boulder. 
def get_boulders(word_data, word_string):

    numbers = []

    locations = []

    sizes = []
 
    rocktypes = []

    page_numbers = []

    full_boundings = []

    loc_boundings = []
    
    siz_boundings = []

    rt_boundings = []

    par_nums = []

    number = 0

    page_number = int(input("What page number did the scan start at? : "))

    print_page = True if input("Would you like to print each page? ( enter y or n ) : ") == 'y' else False 
    
    print("Running NLP...")
    
    WINDOW_NAME = "Page : "

    if print_page:
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.startWindowThread()

    # For each dataframe in word_data ie each page :

    for i in range(0,len(word_data)):

        print("Analysing page : " + str(page_number))

        img = cv2.cvtColor(np.array(word_data[i][1]), cv2.COLOR_RGB2BGR)

        

        # For each word in the page : 

        for j, row in word_data[i][0].iterrows():
            
            # if the word is a boulder related search term, look for the boulders features! 

            if ("boulder" in row['text']):

                # for whole boulder phrase bounding box

                least_x = 1000000
                least_y = 1000000 
                greatest_x_w = -1
                greatest_y_h = -1


                loc_bound = []
                siz_bound = []
                rt_bound = []
             
                # Use paragraph where boulder search term was found for analysis
                
                loc_pos, siz_pos, rt_pos, location, size, rocktype = NLP_helper.find_boulder_from_paragraph(word_data[i][0].loc[word_data[i][0]['par_num'] == row['par_num']])

                # Highlight each word related to the boudlers features .. 
                loc_char_count = 0
                siz_char_count = 0
                rt_char_count = 0 

                

                for k, word in word_data[i][0].loc[word_data[i][0]['par_num'] == row['par_num']].iterrows():
    
                    if word['left'] < least_x:
                            least_x = word['left']      

                    if word['left'] + word['width'] > greatest_x_w:
                            greatest_x_w = word['left'] + word['width']    
                            
                    if word['top'] < least_y:
                        least_y = word['top']  

                    if word['top'] + word['height'] > greatest_y_h:
                        greatest_y_h = word['top'] + word['height']
                    
                    if loc_pos:
                        if loc_char_count >= loc_pos[0] and loc_char_count <= loc_pos[1]:
                            (x, y, w, h) = (word['left'], word['top'], word['width'], word['height'])
                            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 5)

                            loc_bound.append((x,y,x+w,y+h))
                    

                        loc_char_count += len(word['text']) + 1
                    
                    if siz_pos:
                        # Size_pos has multiple dimensions.. 
                        for dim in siz_pos:
                            if (siz_char_count >= siz_pos[dim][0] and siz_char_count <= siz_pos[dim][1]): 
                                (x, y, w, h) = (word['left'], word['top'], word['width'], word['height'])
                                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 5)
                                siz_bound.append((x,y,x+w,y+h))
                                
                               
                        siz_char_count += len(word['text']) + 1

                    if rt_pos:
                        if rt_char_count >= rt_pos[0] and rt_char_count <= rt_pos[1]:       
                            (x, y, w, h) = (word['left'], word['top'], word['width'], word['height'])
                                
                            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 5)
                            rt_bound.append((x,y,x+w,y+h))

                        rt_char_count += len(word['text']) + 1


                # If we have a location and rocktype it qualifies as a boulder ! 
                if location and rocktype:

                    numbers.append(number)
                    locations.append(location)
                    sizes.append(size)
                    rocktypes.append(rocktype)
                    page_numbers.append(page_number)
                    loc_boundings.append(loc_bound)
                    siz_boundings.append(siz_bound)
                    rt_boundings.append(rt_bound)
                    full_boundings.append((least_x,least_y,greatest_x_w,greatest_y_h))
                    par_nums.append(row['par_num'])
                    cv2.rectangle(img, (least_x, least_y), (greatest_x_w, greatest_y_h), (255, 0, 255), 8)
                    print(least_x)
                    print(least_y)
                    number += 1
            
           
        
        if print_page:
            cv2.imshow("Page : " + str(page_number), img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            cv2.waitKey(1)

        page_number += 1
 

    d = {'Number': numbers, 'Location': locations, 'Size' : sizes, 'Rocktype' : rocktypes, 'Page_Number' : page_numbers, 'FullBB' : full_boundings, 'LBB' : loc_boundings, 'SBB' : siz_boundings, 'RBB' : rt_boundings, 'par_num' : par_nums}
     
    return pd.DataFrame(data=d)
    


# For volumes 3 and 4 just to print the data and not fully analyse it.. 

def print_vol(number):

    print("Reviewing volume : " + str(number))
    print("Running OCR and Spellchecker...")

    word_data, word_string = SPL.get_spellchecked_volume_for_printing(number)
       
    # This regex splits paragraphs over "X. ..." meaning any paragraph mentioning a numbered boulder will be assessed, this will need extra 
    # consideration for the later volumes where they change the labeling standarads 

    matches = re.findall("([\d]+\. )(.*?)(?=([\d]+\.)|($))",word_string)

    numbers = []

    locations = []

    sizes = []
 
    rocktypes = []

    print("Running NLP...")

    # Ie for boulder paragraph in report..

    for match in matches:
        
        if len(match[1]) > 5:

            number, location, size, rocktype = NLP_helper.find_boulder_from_numbered_regex(match)
            numbers.append(number)
            locations.append(location)
            sizes.append(size)
            rocktypes.append(rocktype)

    d = {'Boulder Number': numbers, 'Boulder Location': locations, 'Boulder Size' : sizes, 'Boulder Rocktype' : rocktypes}
    
    df = pd.DataFrame(data=d)

    print(df)

    return df
    


# Basic functions I wrote for testing the OCR .. 

def print_all_volumes():
    for i in range(3,8):
        images = convert_from_path("./bouldercopies/" + str(i) + "_Report.pdf", 500)    
        for image in images:
            OCR.print_from_image(image)

def print_one_volume(number):
    images = convert_from_path("./bouldercopies/" + str(number) + "_Report.pdf", 500)    
    for image in images:
        OCR.print_from_image(image)


# two optional arguments, either no arguments then you will be prompted for a number, enter a number, or enter the path to the word_data and word_string !  

if len(sys.argv) == 2:

    review_vol(sys.argv[1])

elif len(sys.argv) == 3:
    
    with open(sys.argv[1], 'rb') as f:
        word_data = pickle.load(f)
    
    with open(sys.argv[2], 'rb') as f:
        word_string = pickle.load(f)
    
    df = get_boulders(word_data,word_string)

    print("All done!")

    # TODO doesn't really work :/ 
    # ||
    # \/

    df.drop_duplicates(keep='first',inplace=True)

    pd.set_option("display.max_rows", None, "display.max_columns", None)

    print(df)

    if input("Would you like to save this data to a csv file?  ( enter y or n ) : " ) == 'y':
        df.to_csv(input("Please enter filename"))

else:

    review_vol(input("Please input number of report to review : "))
