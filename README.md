# Boulders! 

The project was a collaboration between the National Museums Scotland and the School of GeoSciences at The University of Edinburgh. The main objective of this project was to develop a 21st century database from 9 volumes of historical reports published by the Royal Society of Edinburgh “Boulder committee” between 1871 and 1884. This database would be used to assess glacial reconstructions by focusing on boulders of a rock-type differing from the rock-type where they are found (ie. their situ). 

Over the 6-week project I made two pieces of software to help build the database. The first was a script to analyse the reports and extract the boulders and the second was an application for verifying the boulders extracted. 

---

To use the verification app first ensure that you have [python3](https://www.python.org/downloads/) installed.

Then install the dependancies in requirements.txt as shown:

> pip install -r requirements.txt

Also make sure you have your boulder data in a nearby folder for easy navigation within the app - all the boulder data is compressed within [**Archive.zip**](https://uoe-my.sharepoint.com/:f:/g/personal/s1842899_ed_ac_uk/ElLh5BTCSBBKqaK212n02OsBuBGHEy9q-fRegr-5r-CoZA?e=3zW0zB) as it is big in file size. 

Running the app after this is simple:

>python flag.py

--- 

Controller.py is the entry point for the analysis script the usage is as follows :

To analyse all 10 reports - 
> python controller.py -a 

To anayse a single report - 

>python controller.py 
(Will be prompted for report number)

or

> python controller.py x 
(Where x is the report number)

The analysis script uses OCR and spellchecking to read the reports, this usually takes a while which is why the reports word data is automatically stored after the OCR and spellcheck are complete. To analyse a word data file use the -l flag as shown below :

> python controller.py -l ./path_to_file/word_data_x.pickle
(Where path_to_file is the path to the pickle file and x is the report number) 

On completion of any of the above commands a report_x_boulders.pickle file will be generated along with a csv file with the boulders found. This pickle file is formatted to work in the app. This script is specific to these reports and will need work done to be useful on other bodies of work, note also that to run this script you must have [tesseract](https://github.com/tesseract-ocr) installed and also have the neccesary dependancies installed (NB. there are seperate requirements.txt files if you just want to use the app).  

--- 

any problems don't hesitate to contact me at andrewscollin@hotmail.co.uk 
