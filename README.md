# IDS project
### Brigitta Rebane, Karl Taal, Laura Katrin Leman

Repository for the team project in the course Introduction to Data Science 2019

Ajapaik is a web and mobile app that contains thousands of old photographs with plenty of metadata ranging from the titles and descriptions to the location and rephotographs of the place depicted in the pictures. (ajapaik.ee)
Our goal is analysing the textual metainformation of photographs in Ajapaik - lemmatise the descriptions, create keywords and use named entities to add location data to the images where it is currently missing.

### Data

The data we used and generated can be found in the following Google Drive link: https://drive.google.com/drive/folders/1LIUqPHGhVgdt7TXbpOhpzcvo04vKenHA?fbclid=IwAR1FJTfejqPHWJbXlvK5nWsg1xfkU4C0Mi-aOY9h0KVJeTQXQHWC5In7KeI
The file data.csv contains the metadata information from all the photographs we scraped from Ajapaik's API.
The file marksonad_nimedega.csv is the result of using Lemmatizer.py on the data, it contains the photo ID, its description, the generated keywords and the proper nouns/names found in the description.
The file koordineeritud6800.csv contains the 6800 instances for which we managed to find geographic coordinates using the geopy library. The file contains the photo ID, the description, the keywords, the names, the name used for location detection, and the latitude and longitude degrees.

### Guide for using Lemmatizer.py and linguistic jargon

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
