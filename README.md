# Boulders! 

The project was a collaboration between the National Museums Scotland and the School of GeoSciences at The University of Edinburgh. The main objective of this project was to develop a 21st century database from 9 volumes of historical reports published by the Royal Society of Edinburgh “Boulder committee” between 1871 and 1884. This database would be used to assess glacial reconstructions by focusing on boulders of a rock-type differing from the rock-type where they are found (ie. their situ). 

Over the 6-week project I made two pieces of software to help build the database. The first was a script to analyse the reports and extract the boulders and the second, was an application for verifying the boulders extracted. 

--- 

Controller.py is the entry point for the analysis script the usage is as follows :

To analyse all 10 reports - 
>> python controller.py -a 

To anayse a single report - 

>>python controller.py 
(Will be prompted for report number)

or

>> python controller.py x 
(Where x is the report number)

The analysis script uses OCR and spellchecking to read the reports, this usually takes a while which is why the reports word data is automatically stored after the OCR and spellcheck are complete. To analyse a word data file use the -l flag as shown below :

>>python controller.py -l ./path_to_file/word_data_x.pickle
(Where path_to_file is the path to the pickle file and x is the report number) 

On completion of any of the above commands a report_x_boulders.pickle file will be generated along with a csv file with the boulders found. This pickle file is formatted to work in the app.

---

To use the verification app first ensure you have the dependancies installed, I suggest you use the [virtualenv](
https://uoe-my.sharepoint.com/:f:/g/personal/s1842899_ed_ac_uk/ElLh5BTCSBBKqaK212n02OsBuBGHEy9q-fRegr-5r-CoZA?e=p24Ewv) linked, however you can still manually install the dependancies in requirements.txt as shown:

>> pip install -r requirements.txt

To use the virtualenv first select your operating system by choosing to download either MacVerf (for UNIX based systems) or WindowsVerf (for Microsoft Windows) 

# MacVerf

To begin open terminal. This can be done by hitting Command(⌘) + Spacebar and searching for "terminal"

Navigate to the MacVerf folder you downloaded using :

>>cd /path/to/MacVerf

Then change the source by entering this command :

>>source ./verf_env/bin/activate

Then just run the flag.py file :

>>python flag.py

# WindowVerf

To begin open the command prompt. This can be done by hitting Win + R and typing in "cmd" and pressing enter. 

Navigate to the WindowsVerf folder you downloaded using :

>>cd C:\path\to\WindowsVerf

Then change the source by entering this command :

>>\env\Scripts\activate

Then just run the flag.py file :

>>python flag.py


--- 

The program itself has instructions on usage. If you run into any problems whilst using the virtualenv's install [python3](https://www.python.org/downloads/) and the requirements as shown above and try again; any other problems don't hesitate to contact me at andrewscollin@hotmail.co.uk
