import pandas as pd
import numpy as np
from estnltk import Text
from langdetect import detect

# Please refer to the readme file for more information about the necessary Python libraries and linguistics-related terminology

# Read in the data, appropriately named 
data =  pd.read_csv("data.csv", sep='\t', low_memory=False)

# Make a copy of the data  
andmed = data.copy(deep=True)

# Looking at how many titles have values (10611)
titles = data.loc[data['title'].notna() == True]['title']
print("There are",len(titles),"non-empty titles in the dataset")

# How many values under title_et (Estonian titles) have real values (10607)

e_titles = data.loc[data['title'].notna() == True]['title']
print("There are",len(e_titles),"non-empty titles in the dataset")

# How many of those are actually Estonian?
counter = 0
undetectable = 0
for t in e_titles: # also ran the same thing for regular titles and got similar results
    try:
        if type(t) == str:
            if detect(t) == 'et':
                counter+=1
				#print(t)
    except:
        undetectable+=1
    
print('Estonian descriptions:',counter) # 138 in total (141 in regular titles)
print('Undetectable values',undetectable) # 0 in total

# Since our language detection program only identified 138 instances as Estonian, and as I looked manually through them, it appeared they were all actually Finnish (street names like Mariankatu etc), I decided not to use the titles for language processing, since there did not appear to be any Estonian data in them 


# Used this to look at subsets of the data manually to explore what the texts look like and how lemmatising and POS-tagging works: if there are stopwords we should exclude, disambiguation we should perform etc. I chose many random subsets from across the entire dataset, generally between 20-100 instances in size, and went through the output manually
def exploring_data(data,start,end):
	subset = data[start:end]['description']
	for el in subset:
    if type(el) == str: # check to make sure the description contains textual data and is not empty
        if detect(el) == 'et': # check for the Estonian language
            tekst = Text(el) # create an EstNLTK Text object
            lemmad = tekst.lemmas # get the lemmas
            #ner = zip(tekst.named_entities,tekst.named_entity_labels) # Ilooked at named entity recognition as well, but it is less accurate than lemmatising for Estonian and also does not return the exact type/format of location data we're looking for
            for j in range(len(lemmad)):
                if '|' in lemmad[j]:
                    lemmad[j] = lemmad[j][:lemmad[j].index('|')] # disambiguation
            sonaliigid = tekst.postags
            for i  in range(len(sonaliigid)):
                if sonaliigid[i] =='S':
                    if lemmad[i] not in stopwords:
                        print(lemmad[i])
                if sonaliigid[i] == 'H':
                    print(lemmad[i], 'lemmatised name') # for comparing NER and lemmatised names
            for el in ner:
                print(el,'NER') # for comparing NER and lemmatised names
    print("\n")
        


# Drop the columns that aren't necessary for our analysis, only keep the ID columns and the description columns
kirjeldused_ja_marksonad = andmed.drop(['rephotos', 'similar_photos', 'geotags', 'image',
       'image_unscaled', 'image_no_watermark', 'height', 'width',
       'aspect_ratio', 'flip', 'invert', 'stereo', 'rotated', 'date',
       'date_text', 'title', 'title_et', 'title_en', 'title_ru', 'title_fi',
       'title_sv', 'title_nl', 'title_de', 'title_no', 
       'description_et', 'description_en', 'description_ru', 'description_fi',
       'description_sv', 'description_nl', 'description_de', 'description_no',
       'author', 'uploader_is_author', 'types', 'level',
       'guess_level', 'lat', 'lon', 'geography', 'bounding_circle_radius',
       'address', 'azimuth', 'confidence', 'azimuth_confidence', 'source_key',
       'external_id', 'external_sub_id', 'source_url', 'first_rephoto',
       'latest_rephoto', 'fb_object_id', 'comment_count', 'first_comment',
       'latest_comment', 'view_count', 'first_view', 'latest_view',
       'like_count', 'first_like', 'latest_like', 'geotag_count',
       'first_geotag', 'latest_geotag', 'dating_count', 'first_dating',
       'latest_dating', 'created', 'modified', 'gps_accuracy', 'gps_fix_age',
       'cam_scale_factor', 'cam_yaw', 'cam_pitch', 'cam_roll',
       'video_timestamp', 'face_detection_attempted_at', 'perceptual_hash',
       'hasSimilar', 'licence', 'user', 'source', 'device', 'area',
       'rephoto_of', 'video'],axis=1)


# Add a new column, "names", where we'll put the words estNLTK classified as proper nouns (names)
kirjeldused_ja_marksonad['names'] = np.nan

# Change the type of the column, as it will by default be float64
kirjeldused_ja_marksonad['names'] = kirjeldused_ja_marksonad['names'].astype(object)

# As I went manually through many, many of instances of the data and tried lemmatising them to see what the results would be, it seemed there were some words that wouldn't be useful as keywords, e.g 'rida' in the context of describing where a person is located in a group photo ('1. rida vasakult teine'), 'pääle' as a variant of the word 'peale', which is not a noun, but an adposition, and 'orig' as shorthand for 'original'. This list could always be updated, we simply did not have the capacity to go through thousands of pictures and determine whether a word found in the description is actually useful and descriptive as a keyword
stopwords = ['rida','pääle','orig']


# Function for lemmatising the descriptions and gathering the words tagged as proper nouns (names)
def lemmatise_and_locate(data,stopwords):
    error_counter = 0
    for index, row in data.iterrows():
        description = row['description'] # take the description column
        if (type(row['keywords']) != str) and (type(description) == str): # if the picture doesn't already have a set of keywords, but has a valid description, we'll use that description to create new keywords for it
            try:
                if detect(description) == 'et':# if the language of the description is Estonian (because EstNLTK only works for Estonian)
                    keywords_list = []
                    name_list = []
                    text_object = Text(description) # Create an EstNLTK Text object from the description
                    lemmas = text_object.lemmas # get the lemmas from the Text object
                    for i in range(len(lemmas)):
                        if '|' in lemmas[i]: # sometimes the lemmatiser cannot be sure what form of the word is correct, e.g it will output "Kadriorg|Kadrioru" for the word "Kadriorg", these forms are always separated by |
                            lemmas[i] = lemmas[i][:lemmas[i].index('|')] # if the lemmatiser failed to disambiguate, we will simply choose the first lemma, as we don't have the capacity to manually check which form of the lemma is correct
                    parts_of_speech_tags = text_object.postags # get the part-of-speech tags of the description
                    for j in range(len(parts_of_speech_tags)):
                        if parts_of_speech_tags[j] == 'S': # if the word is a noun
                            if lemmas[j] not in stopwords: # if the word is not something we want to exclude from keywords
                                keywords_list.append(lemmas[j]) 
                        if parts_of_speech_tags[j] == 'H': # if the word is a proper noun (name)
                            name_list.append(lemmas[j])
                            keywords_list.append(lemmas[j]) # we will add it both to the list of keywords, as we want proper nouns to be amongst the keywords, and to the name tab, which we will later use to try and find the location of the picture
                  #  print(keywords_list)
                 #   print(name_list)
                    data.at[index,'keywords'] = keywords_list
                    data.at[index,'names'] = name_list
            except:
                error_counter+=1
                print("There was an error detecting the language of the description. This row will not be lemmatised.") # Sometimes langdetect fails to determine the language, e.g if the description only had numbers in it
    print("Lemmatisation and location detection finished.")
    print("There were",error_counter," rows where the language could not be detected and analysis was not performed.")
    return data
	
# Using the function on the data
lemmatise_and_locate(kirjeldused_ja_marksonad,stopwords)

# Another copy just in case
marksonad_ja_kirjeldused = kirjeldused_ja_marksonad.copy(deep=True)


# Removing duplicates from keywords, as I forgot to do so in the original function and did not want to rerun it due to the massive amount of running time
for i,r in marksonad_ja_kirjeldused.iterrows():
    if type(r['keywords']) == list:
        no_duplicates = list(set(r['keywords']))
        marksonad_ja_kirjeldused.at[i,'keywords'] = no_duplicates
        


# Same, but for the names column
for i,r in marksonad_ja_kirjeldused.iterrows():
    if type(r['names']) == list:
        no_duplicates = list(set(r['names']))
        marksonad_ja_kirjeldused.at[i,'names'] = no_duplicates

# Writing the data into a csv-file
marksonad_ja_kirjeldused.to_csv('marksonad_nimedega.csv')
