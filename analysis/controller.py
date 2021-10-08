from functools import total_ordering
import json
import pickle
import re
import sys
from os import name

import numpy as np
from numpy.core.fromnumeric import size
from numpy.lib.utils import byte_bounds
import pandas as pd
# Convert from path reutrns a list of PIL images making it very easy to use
from pdf2image import convert_from_path
from PIL import Image
import cv2

import NLP_helper
import OCR_helper as OCR
import SPL_helper as SPL


# This is the main entry point function for the project, it takes a number as an argument and will run a complete boulder data extraction over whatever volume is specified
def review_vol(number, page_number=None, print_page=None):

    patch = False

    if page_number is None:
        page_number = int(input("Please enter starting page number : "))

    # Reports 3 and 4 are a different structure being entries in a journal and have 4 pages to an image. 
    # if number == "3" or number == "4":
    #     return print_vol(number)
        
    print("Reviewing volume : " + str(number))
    print("Running OCR and Spellchecker...")


    # Getting the OCR'ed and Spellchecked volume back in a word_string and dataframe 
    word_data, word_string = SPL.get_spellchecked_volume(number)
       

    # Saving this data so we don't need to OCR and Spellcheck every time
    with open('word_data_' + str(number) + '.pickle', 'wb') as f:
        pickle.dump((word_data, page_number, number), f)

    # Get boulders using NLP techniques.. Also an entry point for the saved OCR to be analysed 
    df, df_for_saving = get_boulders(word_data,number,page_number,print_page)

    print("All done!")

    # Print whole dataframe

    pd.set_option("display.max_rows", None, "display.max_columns", None)

    print(df)

    # Saving output

    with open('report_'+ str(number) + '_boulders.pickle', 'wb') as f:
        pickle.dump((word_data, df, page_number, number), f)

    df_for_saving.to_csv("boulder_data" + str(number) + '.csv')



# TODO: Entry point for analysing the OCR'ed data.. Will need to be expanded to include multiple page spanning analysis and more search terms, not just boulder. 
def get_boulders(word_data, number, page_number=None, print_page=None):


    numbers = []

    locations = []

    sizes = []
 
    rocktypes = []

    authors = []

    extras = []

    compass_directions = []

    distances = []

    volumes = []

    weights = []

    hasls = []

    array_numberofboulders = []

    page_numbers = []

    full_boundings = []

    loc_boundings = []
    
    siz_boundings = []

    rt_boundings = []

    b_boundings = []

    aut_boundings = []

    compass_boundings = []

    par_nums = []

    extra_boundings = []

    number = 0

    if page_number is None:

        page_number = int(input("What page number did the scan start at? : "))

    if print_page is None:

        print_page = True if input("Would you like to print each page? ( enter y or n ) : ") == 'y' else False 
    
    print("Running NLP...")
    
    WINDOW_NAME = "Page : "

    if print_page:
        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.startWindowThread()

    general_location = ""

    # For each dataframe in word_data ie each page :
    for i in range(0,len(word_data)):

        print("Analysing page : " + str(page_number))

        img = cv2.cvtColor(np.array(word_data[i][1]), cv2.COLOR_RGB2BGR)

        # Trying to remedy the paragraph mismatching from tesseract, This will set any par_num that is recognised as the first par_num to the last 

        for k, word in word_data[i][0].iterrows():
            if word['par_num'] > 1:
                break

        if len(word_data[i][0]['par_num']):
            word_data[i][0].loc[(word_data[i][0].par_num == 1) & (word_data[i][0].index > k), 'par_num'] = max(word_data[i][0]['par_num'])

        # Used for discarding multiple mention of same boulder on same page

        last_rocktype = ""
        last_size = ""
        last_location = ""

        # Loop through each page

        for j, row in word_data[i][0].iterrows():
            
            # For each word check if there is a new general location being mentioned and extract the placename from line and paragraph match

            if number == 5 or number == 6 or number == 1 or number == 10:

                if '.—' in row['text']:
                    words = word_data[i][0][(word_data[i][0]['line_num'] == row['line_num']) & (word_data[i][0]['par_num'] == row['par_num']) & (word_data[i][0]['word_num'] <= row['word_num'])]['text'].tolist()
                    general_location = ''
                    for word in words:
                        if len(general_location):
                            general_location += " " + word 
                        else:
                            general_location = word
                    
                    general_location = general_location.split('.—')[0]


            # if the word is a boulder related search term, look for the boulders features! 
            if ("boulder" in row['text'] or "Boulder" in row['text'] or "Block" in row['text'] or "block" in row['text']):
 
                # for whole boulder phrase bounding box

                least_x = 1000000
                least_y = 1000000 
                greatest_x_w = -1
                greatest_y_h = -1

                loc_bound = []
                siz_bound = []
                rt_bound = []
                aut_bound = []
                extra_bound = []
                compass_bound = []
                
                siz_char_count = 0

                # Use paragraph where boulder search term was found for analysis
                
                loc_pos, siz_pos, rt_pos, aut_pos, location, size, rocktype, author, numberofboulders, numbox, extra_pos, extra, dim_dict, volume, weight, hasl, distance, comp_dict, compass_direction = NLP_helper.find_boulder_from_paragraph(word_data[i][0].loc[word_data[i][0]['par_num'] == row['par_num']], number)

                
                if len(general_location) and location:
                    location = general_location + ' - ' + location 

                
                # Boulder and boulder number tagging

                if numbox:
                    (x,y,w,h) = numbox
                    cv2.rectangle(img, (x, y), (x + w, y + h), (40, 100, 200), 5)

                (x, y, w, h) = (row['left'], row['top'], row['width'], row['height'])
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 5)
                
                b_bound = (x,y,x+w,y+h)

                # Size tagging and paragraph tagging

                for k, word in word_data[i][0].loc[word_data[i][0]['par_num'] == row['par_num']].iterrows():
    
                    if word['left'] < least_x:
                        least_x = word['left']     

                    if word['left'] + word['width'] > greatest_x_w:
                        greatest_x_w = word['left'] + word['width']    
                            
                    if word['top'] < least_y:
                        least_y = word['top']  

                    if word['top'] + word['height'] > greatest_y_h:
                        greatest_y_h = word['top'] + word['height']
                    
                    if siz_pos:
                        for dim in siz_pos:
                            if (siz_char_count >= siz_pos[dim][0] and siz_char_count <= siz_pos[dim][1]): 
                                (x, y, w, h) = (word['left'], word['top'], word['width'], word['height'])
                                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 5)
                                siz_bound.append((x,y,x+w,y+h))
                                
                               
                        siz_char_count += len(word['text']) + 1


                if dim_dict:
                    for dim in dim_dict:
                        for (x,y,w,h) in dim_dict[dim]:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 5)
                            siz_bound.append((x,y,x+w,y+h))

                # Primary and Secondary rocktype tagging 

                if rt_pos:
                    for dim in rt_pos:
                        for (x,y,w,h) in rt_pos[dim]:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 5)
                            rt_bound.append((x,y,x+w,y+h))

                if extra_pos:
                        for dim in extra_pos:
                            for (x,y,w,h) in extra_pos[dim]:
                                cv2.rectangle(img, (x, y), (x + w, y + h), (147,20,255), 5)
                                extra_bound.append((x,y,x+w,y+h))

                # Tagging of Authors (People mentioned or excerpt references)

                if aut_pos:
                    for dim in aut_pos:
                        for (x,y,w,h) in aut_pos[dim]:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 255), 5)
                            aut_bound.append((x,y,x+w,y+h))

                # Tagging locations and compass directions

                if loc_pos:
                    for dim in loc_pos:
                        for (x,y,w,h) in loc_pos[dim]:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 5)
                            loc_bound.append((x,y,x+w,y+h))
                        
                if comp_dict:
                    for dim in comp_dict:
                        for (x,y,w,h) in comp_dict[dim]:
                            cv2.rectangle(img, (x, y), (x + w, y + h), (200, 70, 10), 5)
                            compass_bound.append((x,y,x+w,y+h))

                
                # If no location is found try setting the location to the last boulder on same pages location if not 
                # just use the general location

                if not location and len(locations) and page_number == page_numbers[len(page_numbers) - 1]:
                    location = locations[len(locations) - 1]
                    loc_pos = loc_boundings[len(loc_boundings) - 1]
                elif not location and len(general_location):
                    location = general_location 
              
                # For last_x matching

                if not location:
                    location = ""                    

                if not size:
                    size = ""                    
                
                if not rocktype:
                    rocktype = ""                    
        
                if not (location == last_location and size == last_size and rocktype == last_rocktype):
            
                    last_rocktype = rocktype
                    last_size = size
                    last_location = location
                
                    # Increase the paragraph bounding box for easy viewing and highlight on page

                    least_y -= 100
                    least_x -= 100
                    greatest_y_h += 100
                    greatest_x_w += 100

                    cv2.rectangle(img, (least_x, least_y), (greatest_x_w, greatest_y_h), (255, 0, 255), 8)

                    # Fill data into arrays

                    numbers.append(number)

                    number += 1

                    locations.append(location)
                    sizes.append(size)
                    rocktypes.append(rocktype)
                    authors.append(author)
                    extras.append(extra)
                    array_numberofboulders.append(numberofboulders)
                    
                    compass_directions.append(compass_direction)
                    distances.append(distance)

                    volumes.append(volume)
                    weights.append(weight)
                    hasls.append(hasl)
                    aut_boundings.append(aut_bound)
                    page_numbers.append(page_number)
                    loc_boundings.append(loc_bound)
                    siz_boundings.append(siz_bound)
                    rt_boundings.append(rt_bound)
                    b_boundings.append(b_bound)
                    compass_boundings.append(compass_bound)

                    extra_boundings.append(extra_bound)
                    full_boundings.append((least_x,least_y,greatest_x_w,greatest_y_h))
                    par_nums.append(row['par_num'])

        if print_page:
            print(word_data[i][0])
            d = {'Numbers' : numbers, 'Location': locations, 'Size' : sizes, 'Rocktype' : rocktypes, 'Volume' : volumes, 'Weight' : weights, 'HASL' : hasls, 'Compass' : compass_directions, 'Distance' : distances, 'Page_Number' : page_numbers, 'BNum' : array_numberofboulders, 'Extra' : extras, 'EBB' : extra_boundings, 'Author' : authors, 'ABB' : aut_boundings, 'FullBB' : full_boundings, 'BBB' : b_boundings, 'LBB' : loc_boundings, 'SBB' : siz_boundings, 'RBB' : rt_boundings, 'CBB' : compass_boundings, 'par_num' : par_nums}
            print(d)
            cv2.imshow("Page : " + str(page_number), img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            cv2.waitKey(1)

        page_number += 1
 
    # Formatted for CSV
    
    d_for_saving = {'Numbers' : numbers, 'Location': locations, 'Size' : sizes, 'Rocktype' : rocktypes, 'Volume' : volumes, 'Weight' : weights, 'Height above sea level' : hasls, 'Compass' : compass_directions, 'Distance' : distances, 'Number of Boulders mentioned' : array_numberofboulders, 'Extra' : extras, 'Author' : authors, 'Paragraph' : par_nums, 'Page' : page_numbers}
    
    df_for_saving = pd.DataFrame(data=d_for_saving)
    
    d = {'Numbers' : numbers, 'Location': locations, 'Size' : sizes, 'Rocktype' : rocktypes, 'Volume' : volumes, 'Weight' : weights, 'HASL' : hasls, 'Compass' : compass_directions, 'Distance' : distances, 'Page_Number' : page_numbers, 'BNum' : array_numberofboulders, 'Extra' : extras, 'EBB' : extra_boundings, 'Author' : authors, 'ABB' : aut_boundings, 'FullBB' : full_boundings, 'BBB' : b_boundings, 'LBB' : loc_boundings, 'SBB' : siz_boundings, 'RBB' : rt_boundings, 'CBB' : compass_boundings, 'par_num' : par_nums}     
    
    
    df = pd.DataFrame(data=d)

    return df, df_for_saving




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


def analyse_everything():
    report_nums = [(1,21),(3,0),(4,0),(5,3),(6,3),(7,3),(8,3),(9,193),(10,769)]

    for report, page_num in report_nums:
        review_vol(report,page_num,False)


# two optional arguments, either no arguments then you will be prompted for a number, enter a number, or enter the path to the word_data and word_string !  

if len(sys.argv) == 2:

    if sys.argv[1] == '-a':
        analyse_everything()
    else:
        review_vol(sys.argv[1])

    

elif len(sys.argv) == 3:
    
    if sys.argv[1] != '-l':
        print("use -l to use preloaded data")
        raise

    with open(sys.argv[2], 'rb') as f:
        loaded_data = pickle.load(f)

    if len(loaded_data) == 4:
        # Checking if it's a boulder file or a word_data file 
        word_data, boulders, page_number, report_number = loaded_data
    elif len(loaded_data) == 3:
        word_data, page_number, report_number = loaded_data
    else:
        print(loaded_data)
        raise("Incorrect pickle")


    df, df_for_saving = get_boulders(word_data,report_number,page_number)

    print("All done!")

    pd.set_option("display.max_rows", None, "display.max_columns", None)

    print(df)

    with open('report_'+ str(report_number) + '_boulders.pickle', 'wb') as f:
        pickle.dump((word_data, df, page_number, report_number), f)

    df_for_saving.to_csv("report_" + str(report_number) + ".csv")

else:

    review_vol(input("Please input number of report to review : "))
