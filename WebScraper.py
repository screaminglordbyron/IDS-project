import requests
import pandas as pd
import time

#gives roughly % how much of collecting is done
#takes "pageNR" on what iteration are we
def progress(pageNR):
    pr = round(pageNR / 16822 * 100, 4)
    return "\r" + "Collecting data:  " + str(pr) + " %"


url ="https://opendata.ajapaik.ee/photos/?fbclid=IwAR3Zf_f2bM07WRrJuGijOQNoJmJawYV70hKgdUVAJPkWy5_rtNjKwwVdvpE&page=1"
list_of_pic_dictionaries = []

start_time = time.time()
pageNR = 1
while url is not None:
    response = requests.get(url)

    #in case something goes wrong
    if response.status_code != 200:
        print("Something went wrong, couldn't get the url content!")
        print("Page number: " + str(pageNR))
        print(url)
        break


    nextURl = response.json()["next"]

    pictures = response.json()["results"]

    #Iter over all the pictures on that page.
    for i in range(len(pictures)):
        pic = response.json()["results"][i]
        list_of_pic_dictionaries.append(pic)

        #if there are rephotos, add those too
        for re in pic["rephotos"]:
            list_of_pic_dictionaries.append(re)

    url = nextURl
    print(progress(pageNR), end="")
    pageNR += 1


df = pd.DataFrame(list_of_pic_dictionaries)
df.to_csv("data.csv", sep='\t')
print()
print("DONE!")
print("--- %s minutes ---" % str(round((time.time() - start_time) / 60, 2)))

#Ma ei teadnud, kas pildid, mis on rephotos all oleks niisama ka välja tulnud.
#Lisasin igaksjuhuks need veel eraldi dataframei, kui rephotode all midagi oli.
#Peaks igaksjuhuks kontrollima ega duplikaate nüüd ei ole.

#Output from code run, total page number was wrong in progress() function. Thats why progress is > 100%.
###################################
#Collecting data:  100.0119 %
#DONE!
#--- 174.6 minutes ---
###################################