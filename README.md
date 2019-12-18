# IDS project
### Brigitta Rebane, Karl Taal, Laura Katrin Leman

Repository for the team project in the course Introduction to Data Science 2019

Ajapaik is a web and mobile app that contains thousands of old photographs with plenty of metadata ranging from the titles and descriptions to the location and rephotographs of the place depicted in the pictures. (ajapaik.ee)
Our goal is analysing the textual metainformation of photographs in Ajapaik - lemmatise the descriptions, create keywords and use named entities to add location data to the images where it is currently missing.

## Process

We scraped the metadata of the images from Ajapaik's API using the code from API_kraapija.py. This resulted in a large csv-file containing all the information available for each photograph, e.g its ID, title, description, location data, whether it has been rephotographed etc. We scraped all the data because we changed project ideas during the process and thought that just in case it is better to have all the data and then we could avoid running again the relatively slow code.        
Next, we used the code from Lemmatizer.py on this csv-file to lemmatise the descriptions, create keywords and find all proper nouns/names from the descriptions. This generated a new csv-file with the added information.     
After that we prepare for the final task by scraping as much estonian location names as possible from the internet. With the help of this csv file we managed to detect some of the location names with 100% certainty that it is a location name and not a person's name.   
Finally, we used coordinatingPhotos.py to go through the newly generated proper noun lists for each photo and find out whether there is a name among the proper nouns that corresponds to an actual geographic location in Estonia. If we found such a place, we added its coordinates and the name of the place to the photo's metadata. We did this for 6800 of the photographs, as the python library we used, geopy, had a limit on the maximum number of requests we could send in short time.

### Data

The data we used and generated can be found in the following Google Drive link:         
https://drive.google.com/drive/folders/1LIUqPHGhVgdt7TXbpOhpzcvo04vKenHA?fbclid=IwAR1FJTfejqPHWJbXlvK5nWsg1xfkU4C0Mi-aOY9h0KVJeTQXQHWC5In7KeI      
The file data.csv contains the metadata information from all the photographs we scraped from Ajapaik's API.
The file marksonad_nimedega.csv is the result of using Lemmatizer.py on the data, it contains the photo ID, its description, the generated keywords and the proper nouns/names found in the description.      
The file Asukohad.csv contains a lot of location names in Estonia.    
The file koordineeritud6800.csv contains the 6800 instances for which we managed to find geographic coordinates using the geopy library. The file contains the photo ID, the description, the keywords, the names, the name used for location detection, and the latitude and longitude degrees. The file does not contain photos where coordinates were already set.

### Program quick descriptions
**Api_Kraapija.py**- scrapes information about all photos from internet.    
**Asukohtade_kraapija.py**- scrapes most of the major location names in Estonia.    
**IamNotebook.ipynb**- with notebook it is better to view datasets.    
**Koordinaator.py**- with this file we tested the geopy opportunities.    
**Lemmatiser.py**- lemmatizes photo descriptions given in Estonian and find nouns and names. Creates corresbonding dataset.   
**coordinatingPhotos.py**- creates the file where we added coordinates if there was not coordinates before. Photos where coordinates were already set does not show up in this dataset.    

### Guide for using scraping programs
**Api_kraapija.py**- you should install libraries requests and pandas. Running the code results with a csv file with inforamation about all the photos. Network connection also required.    
**Asukohtade_kraapija.py**- you should install libraries urrlib, beautifulsoup4 and pandas. Running the code results with a csv file containing major location names in Estonia. Network connection also required.   

### Guide for using coordinatingPhotos.py
Before you try to run this code you should have files marksonad_nimedega.csv and Asukohad.csv. Also you should install libraries pandas. At the beginning of the program you can set the "maht" to some number how many of the instances you would like to look throgh from marksonad_nimedega.py. Network connection also required. The result file will be smaller because some of the picture already have coordinates. Setting this parameter too high would result with a bad results because geopy blocks your IP after some time because of too many requests. But changing your network between two different internet hotspot in every 2-3 minutes you could in theory go through all the dataset but it takes a lot of time. Better solution would be pay for better geocoder and replace it with geopy.   
Running the code gives you constant feedback how much of the dataset is looked through, but compared to whole dataset (~186000 lines). That means if you set the parameter to 10 000 then the work gets done a lot sooner than 100% progress feedback. 
During the program work you can safely change network connections, the programs puts himself in a 10 second paus and then tries again to connect to the network. After 10 failed attempts to connect to the internet, the programs stops and saves current progress. More info in program comments (in Estonian).

### Guide for using Lemmatiser.py and linguistic jargon

Using this Python file requires the installation of 4 Python libraries: numpy, pandas, estNLTK and langdetect.
The documentation for langdetect is available at https://pypi.org/project/langdetect/ and it can be installed with a simple pip command. We used this to detect whether a given description and title were in Estonian or not. We found that out of the few titles that were non-empty, the ones that langdetect classified as Estonian were actually Finnish, so we did not use titles in our analysis. 
The documentation for estNLTK is available here https://github.com/estnltk/estnltk. We used version 1.4.1, which requires a Python version no higher than 3.5. It can be installed with the command 'conda install -c estnltk -c conda-forge estnltk'.

EstNLTK's most important feature is the Text class. It creates a Text object from any given string and offers a variety of operations, for example tokenization, part-of-speech tagging, temporal entity recognition etc. We made use of two primary features: lemmatisation and part-of-speech tagging (POS-tagging). 

**Lemmatisation** is the process of finding the base form of a word, i.e the form you'd find in a dictionary. In Estonian, this means the singular nominative (ainsuse nimetav) case for nouns (words like koertesse, koera, koertega, koerale are all lemmatised as koer) and the ma-infinitive for verbs (words like tegin, tehti, tehakse etc are all classified as tegema). 
Sometimes, a word can have several possible lemmas, for example the word 'tee' in Estonian can be both a noun (tea or road) or the imperative of the verb 'tegema'. In such cases, estNLTK performs what is known as disambiguation, i.e it chooses only one lemma from the several possible ones. 
Sometimes, estNLTK is unable to offer a single lemma corresponding to a given word, for example, if the word is Kadrioru, estNLTK will return both Kadriorg and Kadrioru as the lemmas, because it has no way of knowing which version is correct, both are perfectly valid names and only by having some sort of semantic knowledge of the context could one make an informed decision. 

**POS-tagging** is the process of giving every token in a text a tag denoting its role in speech, these are usually nouns, proper nouns, verbs, adjectives, adverbs, pronouns, conjugations, punctuation etc. In our case, we are most interested in the words tagged as proper nouns (also known as names), which are tagged with  'H', and in nouns, which are tagged with 'S'. We use both nouns and names to create keywords, as these types of words usually carry the most important information about photographs, and we use the names to look up location data later.
You can read more about estNLTK and the Text class here: https://estnltk.github.io/estnltk/1.4.1/tutorials/text.html

Our goal was to create keywords for photos which don't currently have any. We use nouns and proper nouns to create the keywords, as these tend to be the most informative types of words in descriptions. EstNLTK also has a named entity recognition (NER) function, but its accuracy is not as high as the POS-tagging's name detection, and NER also returns entities in a form which was not well suited for our location search. For example, it returns 'Veriora raudteejaam' (Veriora train station) as a single named entity, which is technically correct, but our way of looking up location data was more suited for using simply 'Veriora', as adding the train station descriptor would have yielded no results. 

Lemmatizer.py has a function exploring_data to look through selected subsets of the data and see how well lemmatisation works and if there are any special cases, stopwords etc that we need to be aware of. 
The most important function is lemmatise_and_locate, which goes through all the non-empty descriptions in the dataset, checks that they are Estonian with langdetect, then makes a text object out of the description and takes the lemmas. In case the disambiguation hasn't worked properly, we simply select the first possible lemma, because we don't have the capacity to determine which one is actually correct. Next we get the POS-tags of the description. We look at nouns and names, and add both of them to the keyword column of the picture, and also add the names to a separate column, which we will later use for location detection. 
Later, we also remove duplicates from the keywords and names, and finally write the results into a csv-file.
