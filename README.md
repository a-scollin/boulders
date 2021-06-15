# boulders !

- 14/06 

Added a few components to make the software more sophisticated before attempting to apply NLP techniques.

+ Added helper functions for the OCR package allowing easy analysis of multiple records at a time. The data collected from these functions will export as a pandas.DataFrame which can be used in functions for training purposes (conf - confidence) and for the pygame manual verification software (x,y coords relative to each image for displaying the original scanned texts)

+ I thought I'd start incorporating a simple spellchecker. By scraping wikipedia articles we will be able to build a dictionary of many scottish lochs which would be useful for later down the line when we encounter spelling mistakes from italics. Will work on lower confidence guesses from the OCR.

