import re
import json

# Scraper bot to get names from a wikipedia markup of a list, uses regex to check within list and save 
# in JSON formatting to be used as a dictionary in the spell check and perhaps OCR 

def scrape(filename):
    scrapedwords = {}
    f = open(filename, "r")
    for line in f:
        reg = re.findall(r"(?<=\[\[).+?(?=\]\])", line)
        for phrase in reg:
            for word in phrase.split():
                if word.isalpha():
                    scrapedwords[word] = 1
    return scrapedwords
        

filename = input("Please enter the filename of the Wiki list markup to rip names from.. make sure it's .txt! :")
json.dump(scrape(filename), open(filename[:-4]+".json", 'w'))

