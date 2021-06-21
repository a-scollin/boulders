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

"16-18/06"

+ Fixed the spellchecker and started adding some interesting terms to increase the accuracy, the custom dictionary and spellchecker works seemingly quite well just from inspecting the corrections the system makes.

+ I cleaned up the code a bit, it could definitly use some comments though, so I'll probably do that over the weekend. 

+ Researched the flair NLP library and NLP in general, I think right now a better idea than making a generalised unsupervised model that magically does everything, is to start making training data for the named entity recognition that would be able to recognise **different boulders** mentioned in the same body of text. https://medium.com/thecyphy/training-custom-ner-model-using-flair-df1f9ea9c762 I'm still not sure if I can introduce new tags into the NER labeling and it's quite hard to wrap my head around but I think with more research it will work well. This will be very important for the boulders that aren't numbered as the current system wouldn't even consider them. It is also useful for ambiguity in numbered boulders when other smaller boulders are mentioned.

+ I had a few ideas about how to retrieve more accurate size, location and rocktype data as well:

Size
=
After looking at the records more I notice that the sizes are usually mentioned either in the first sentence or in a sentence of their own, this means I can just look for key words like height, length, width or breadth and flag the sentence to be considered for a special size analysis within the find_size function. This should be simple enough to do from the way I've laid out each function and class. 

20/06

I've added more to find_size so that it now will return the size for sentences that mention length and breadth which works in quite a few cases, also implemented a "span" variable that helps when looking at ambiguous or old timey speech, basically it creates a window around the mention of breadth length or height and looks for a p-o-s CD tag indicating a number, if the tag that it finds is already used it won't use it straight away rather only until its searched 8 words behind and in front of the mention. This works really well however I'll need to add a few more words to recognise such as "width", "high" and a few others.

Location
=
Although I've improved the accuracy of the location selection from the named entity recognition, some locations are far too broad.. for example they just describe the area of one of the boulders as Ayrshire which is massive. To remedy this I was thinking of doing the same thing for compass directions as above, where I would flag up sentences mentioning NW N .viz and such. This is a simple solution and hopefully should be easy to implement, however there is another challenge with contextual locations, 3/13 boulders mentioned in the 3rd report have locations referenced from other paragaphs, ie they mention "along the same path" or "this place" which is quite hard to determine, I think these will have to be self validated in the end unless I get a really good idea. 

20/06

I've looked into the location tagging more and there isn't really an elagant solution to get accurate locations outside of the cases where we would have compass directions and units of measurement. I've looked over the reports and the county should be simple enough to pull out as it's a placename that is in uppercase lettering however when talking about more specific areas it might be benfificial to just make a nice piece of verification software that would have the original text snippet and the general area meaning I could then just go through to manually do it. I'm currently just trying to get a simple python package that would let me do this as Pygame isn't working on my machine atm :/

Rocktype
=
The hardest part with getting accurate rock types is when multiple boulders or landscapes are mentioned in the same sentence, usually choosing the first mentioned rock type will get the boulder in questions rock type however this isn't always the case, especially when talking about a boulder on some clay terrain where the 1800's way of speaking even confuses me. I was thinking of making a rating system based on word frequencies in which - down the line - after multiple volumes have been scanned, the script from each can be filtered by rock type and word apperences (frequencies) to get the most common boulder types, then any collisions in rating can just be manually decided.    

These ideas won't take too long to implement but they will take a while to perfect, and as these are the three main features of the boulder they are very important to classify accurately. 


