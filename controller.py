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

    if number == "3" or number == "4":
        return print_vol(number)
        
    print("Reviewing volume : " + str(number))
    print("Running OCR and Spellchecker...")

    word_data, word_string = SPL.get_spellchecked_volume(number)
       
    with open('word_data.pickle', 'wb') as f:
        pickle.dump(word_data, f)

    with open('word_string.pickle', 'wb') as f:
        pickle.dump(word_string, f)

    df = get_boulders(word_data, word_string)

    print("All done!")

    pd.set_option("display.max_rows", None, "display.max_columns", None)


    print(df)

    if input("Would you like to save this data to a csv file?  ( enter y or n ) : " ) == 'y':
        df.to_csv(input("Please enter filename"))


def get_boulders(word_data, word_string):
    
    
    # This regex splits paragraphs over "X. ..." meaning any paragraph mentioning a numbered boulder will be assessed, this will need extra 
    # consideration for the later volumes where they change the labeling standarads 

    # start = False

    # matches = {}

    # title = None
    # paragraph = None

    # df_indexes = []

    # for i in range(0,len(word_data)):
        
    #     if not start:
    #         df_indexes.append(i)
        
    #     for word in word_data[i][0].text:
    #         if not start and word.isupper() and len(word) > 5:
    #             if title and paragraph:

    #                 matches[title] = (paragraph, [word_data[j] for j in df_indexes])

    #                 df_indexes = []
                    
    #             title = ""
    #             paragraph = ""

    #             start = True
    #         if start and word.isupper():
    #             title += word + " " 
    #         if start and not word.isupper():
    #             paragraph += word + " "
    #             start = False

    numbers = []

    locations = []

    sizes = []
 
    rocktypes = []

    page_numbers = []

    number = 0

    page_number = int(input("What page number did the scan start at? : "))
    
    start_page_number = int(page_number)
    
    WINDOW_NAME = "Page : "

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.startWindowThread()

    for i in range(0,len(word_data)):

        print("Analysing page : " + str(page_number))

        img = cv2.cvtColor(np.array(word_data[i][1]), cv2.COLOR_RGB2BGR)

        for j, row in word_data[i][0].iterrows():
            
            if ("boulder" in row['text']):
                
                loc_pos, siz_pos, rt_pos, location, size, rocktype = NLP_helper.find_boulder_from_paragraph(word_data[i][0].loc[word_data[i][0]['par_num'] == row['par_num']])

                if loc_pos:
                    char_count = 0
                    for k, word in word_data[i][0].loc[word_data[i][0]['par_num'] == row['par_num']].iterrows():
    
                        if char_count >= loc_pos[0] and char_count <= loc_pos[1]:
                            # This word variable has the area for highlighting the passage in the pdf and verification app..
                            # word
                            (x, y, w, h) = (word['left'], word['top'], word['width'], word['height'])
                            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)
                        
                        char_count += len(word['text']) + 1
                
                if siz_pos:
                    char_count = 0
                    for k, word in word_data[i][0].loc[word_data[i][0]['par_num'] == row['par_num']].iterrows():
    

                        for dim in siz_pos:
                            if (char_count >= siz_pos[dim][0] and char_count <= siz_pos[dim][1]):
                                # This word variable has the area for highlighting the passage in the pdf and verification app..
                                # word
                                (x, y, w, h) = (word['left'], word['top'], word['width'], word['height'])
                                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
                        
                        char_count += len(word['text']) + 1

                if rt_pos:
                    char_count = 0
                    for k, word in word_data[i][0].loc[word_data[i][0]['par_num'] == row['par_num']].iterrows():
    
                        if char_count >= rt_pos[0] and char_count <= rt_pos[1]:
                            # This word variable has the area for highlighting the passage in the pdf and verification app..
                            # word
                            print("ROCKTYPE :" + str(word['text']))
                            (x, y, w, h) = (word['left'], word['top'], word['width'], word['height'])
                            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 5)
                        
                        char_count += len(word['text']) + 1

        

                if location and rocktype:
                    numbers.append(number)
                    locations.append(location)
                    sizes.append(size)
                    rocktypes.append(rocktype)
                    page_numbers.append(page_number)
                    number += 1
            
           
            

        cv2.imshow("Page : " + str(page_number), img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        cv2.waitKey(1)

        
        

        page_number += 1
    # img_index = []
    # loc_pos = []
    # siz_pos = []
    # rt_pos = []

    print("Running NLP...")

    # # Ie for boulder paragraph in report..

    # for match in matches:
    #     if len(match[1]) > 5:

    #         loc_pos, siz_pos, rt_pos, location, size, rocktype = NLP_helper.find_boulder_from_paragraph(match[1])
            
    #         numbers.append(match[0])
    #         locations.append(location)
    #         sizes.append(size)
    #         rocktypes.append(rocktype)
            


    d = {'Boulder Number': numbers, 'Boulder Location': locations, 'Boulder Size' : sizes, 'Boulder Rocktype' : rocktypes, 'Page Number' : page_numbers }
    
    


    return pd.DataFrame(data=d)
    # print(word_data)



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


if len(sys.argv) == 2:

    review_vol(sys.argv[1])

elif len(sys.argv) == 3:
    
    with open(sys.argv[1], 'rb') as f:
        word_data = pickle.load(f)
    
    with open(sys.argv[2], 'rb') as f:
        word_string = pickle.load(f)
    
    df = get_boulders(word_data,word_string)

    print("All done!")

    df.drop_duplicates(keep='first',inplace=True)

    pd.set_option("display.max_rows", None, "display.max_columns", None)

    print(df)

    if input("Would you like to save this data to a csv file?  ( enter y or n ) : " ) == 'y':
        df.to_csv(input("Please enter filename"))

else:

    review_vol(input("Please input number of report to review : "))
