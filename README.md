# boulders !

"14/06" 

Added a few components to make the software more sophisticated before attempting to apply NLP techniques.

+ Added helper functions for the OCR package allowing easy analysis of multiple records at a time. The data collected from these functions will export as a pandas.DataFrame which can be used in functions for training purposes (conf - confidence) and for the pygame manual verification software (x,y coords relative to each image for displaying the original scanned texts)

+ I thought I'd start incorporating a simple spellchecker. By scraping wikipedia articles we will be able to build a dictionary of many scottish lochs which would be useful for later down the line when we encounter spelling mistakes from italics. Will work on lower confidence guesses from the OCR.

"15/06"

Started applying NLP techniques and added preprocessing and more regex 

+ Added NLP_helper which is now coded with simple NER to pick out locations and will be used for POS tagging later down the line.

+ Added a function in OCR_helper which pre processes each page before being OCR'ed.. I think this will increase the accuracy of the OCR by alot meaning once the spell checker has ran through there should be little error meaning the OCR may not need trained!  

+ Started using alot of regex to pick out the numbered boulders and their sizes.. More work to be done for looking up sizes however as alot of them are stated in english which will require more NLP. 
