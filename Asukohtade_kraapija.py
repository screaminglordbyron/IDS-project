import urllib.request
import bs4
import pandas as pd

#Program creates dataframe of major location names in Estonia and puts the in csv file.

url = "https://www.riigiteataja.ee/akt/74442"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
leht = urllib.request.urlopen(req).read()
soup = bs4.BeautifulSoup(leht, 'html.parser')

#Lets add cities manually.
tulemus = ["Tallinn", "Tartu", "Narva", "Pärnu", "Kohtla-Järve",
           "Viljandi", "Maardu", "Rakvere", "Sillamäe", "Võru",
           "Kuressaare", "Valga", "Jõhvi", "Haapsalu", "Keila",
           "Paide", "Türi", "Tapa", "Põlva", "Kiviõli", "Elva",
           "Saue", "Jõgeva", "Rapla", "Põltsamaa", "Paldiski",
           "Sindi", "Kunda", "Kärdla", "Kehra", "Loksa", "Räpina",
           "Tõrva", "Narva-Jõesuu", "Tamsalu", "Otepää", "Kilingi-Nõmme",
           "Karksi-Nuia", "Lihula", "Mustvee", "Võhma", "Antsla",
           "Abja-Paluoja", "Püssi", "Suure-Jaani", "Kallaste", "Mõisaküla"]

#Lets collect major location names.
for br in soup.findAll('br'):
    next_s = br.nextSibling
    if not (next_s and isinstance(next_s,bs4.NavigableString)):
        continue
    next2_s = next_s.nextSibling
    if next2_s and isinstance(next2_s,bs4.Tag) and next2_s.name == 'br':
        text = str(next_s).strip()
        if text:
            tulemus.append(next_s.strip())

df = pd.DataFrame(tulemus, columns=["Asukoht"])
df.to_csv("Asukohad.csv", sep='\t')
