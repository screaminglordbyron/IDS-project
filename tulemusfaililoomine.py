import pandas as pd
import geopy
import ast
from geopy.extra.rate_limiter import RateLimiter
import time
start_time = time.time()

# Lühidalt
# Programm käib läbi kõik märksõnadega piltide read, kus pole juba koordinaate. Märksõnade seast otsitakse eelkõige neid sõnu asulateks,
# mis esinevad ka asulate nimistus. Kui märksõnades seas sellist sõna ei sisaldu, siis käiakse märksõnad ükshaaval. Märksõna kohta küsitakse
# koordinaate. Seejärel kontrollitakse kas koordinaadid sattusid Eestisse ja kui see on tõsi, siis need koordinaadid lisamegi.

# Kuna geopy, millega me koordinaate küsime, omab päringute piirangut ja umbes paari saja päringu järel blokib see su IP ajutiselt ära, siis üritasime luua vastumeetmeid:
# 1) Esiteks kui juba sõna on küsitud geopylt, siis uuesti seda kunagi ei küsita. Hoiame sõnastikus seda vastet ja vajadusel vaatame sinna.
# 2) Geopyle lisasime RateLimiteri, mis siis viivitab natuke päringutega.
# 3) Nii sai kätte umbes 2700 vastet tulemus andmestikus, kuni su IP ajutiselt blokeeriti ja töö lõppes.
# 4) Pigistasime välja 6800 vastet lisades programmile erindite püüdjaid, mis võimaldasid erroreid ohjeldada ja
#    umbes iga 500-1000 kirje leidmise järel vahetasime arvutil interneti ühenduse teise vastu ära, mis lasi programmil jätkata ilma geopyd ülekoormata ühe network IP alt.

# Lahendus probleemile oleks mõne parema GeoCoderi kasutamine, kuid need on tavaliselt tasulised.

# loeme sisse abi andmestiku.
# märksõnades on lemmatiseeria poolt loodud märksõnad.
# df on kogu ajapaiga API, sealt kontrollime kas koordinaadid on juba olemas.
# asukohanimede failis hoiame Eesti asukohtade nimesi. Märksõnadest eelistame koordineerida eelkõige neid sõnu, mis leiavad sellest failist vaste.
marksonad = pd.read_csv("marksonad_nimedega.csv", sep=",", low_memory=False)
df = pd.read_csv("data.csv", sep="\t", low_memory=False)
asukohanimesi = pd.read_csv("Asukohad.csv", sep="\t", low_memory=False)

maht = 5000 #Nii palju kirjeid vaadatakse läbi. Tulemusfailis kirjed vähem kuna osadel on juba koordinaadid olemas. Geopy ei ole suuteline kõike läbi käima.

row_list = [] #tulemus dataframei read salvestame siia, et hiljem mugavalt dataframe luua.

#loome sõnastiku peamistest Eesti asulatest, et kiiresti leida märksõnade seest võimalusel parim sõna.
asukohti = {}
for index, rida in asukohanimesi.iterrows():
    asukohti[str(rida[1]).strip().lower()] = "asukoht"

# siin hakkame hoidma nimesi, mis on geopy'st juba läbi käinud. Siis ei pea korduvalt ühte ja sama sõna geopysse sisestama.
nimede_arhiiv = {}
nimede_arhiiv["Eesti"] = "puudub" #väga palju esines "Eesti" koordinaatide leidmist, välistame selle, lisades arhiivi kohe märke, et sellel koordinaadid puuduvad.

#abi funktsioon progressi väljastamiseks ja töö käigu jälgmiseks.
def progress(pageNR):
    pr = round(pageNR / maht * 100, 4)
    return "\r" + "Protsess:  " + str(pr) + " %"

# dropime kaks esimesest unnamed tulpa
marksonad = marksonad.drop(marksonad.columns[0], axis=1)
marksonad = marksonad.drop(marksonad.columns[0], axis=1)

# nüüd tulbad: 0-id, 1-description, 2-keywords, 3-names
i = 1
arhiivi_kasutusi = 0
pöördumisi = 0
terminator = False
puhkamisi = 0
for index, rida in marksonad.iterrows(): #läbime andmestiku iga rea.

    #Kirjutame iga 500 leitud tulemusrea järel tulemuse csv faili igaksjuhuks. Programm võib lõppeda geopy piirangute pärast töötamast ja siis katkestades on meil tulemusfail alles.
    if i % 500 == 0:
        try:
            tulemus = pd.DataFrame(row_list)
            tulemus.to_csv("koordineeritud.csv", sep='\t')
        except:
            print()
            print("Program stopped! Bad data to csv")
            break

    #Paneme programmi pausile korraks interneti vahetamise ajal või muul erindi juhul.
    if terminator:
        if puhkamisi == 10:
            print()
            print("Program stopped!")
            break
        else:
            time.sleep(15)
            try:
                tulemus = pd.DataFrame(row_list)
                tulemus.to_csv("koordineeritud.csv", sep='\t')
            except:
                print()
                print("Program stopped! Bad data to csv")
                break
            terminator = False

    if type(rida[3]) is not float and len(
            ast.literal_eval(rida[3])) is not 0:  # kui nimede väli pole ei none ega suurusega 0
        pildi_ID = rida[0]
        alg_data_vaste = df.loc[df['id'] == pildi_ID]
        if pd.isna(alg_data_vaste["lat"].iloc[0]):  # kontroll kas alg andmestikus pole koordinaate
            kas_leiti = False
            kas_käi_kõik_läbi = True

            #Siia jõudes on olemas meil andmestiku rida, millel pole koordinaate.

            #Käime läbi kõik märksõnad otsides vastet nii asukoha andmestikust kui arhiivist, kas oleme juba sõna vaadelnud.
            for nimi in ast.literal_eval(rida[3]):
                placeOrig = str(nimi).strip()
                place = str(nimi).strip().lower()
                if place in asukohti and placeOrig in nimede_arhiiv and nimede_arhiiv[placeOrig] != "puudub":
                    arhiivi_kasutusi += 1
                    cor = nimede_arhiiv[placeOrig]
                    lattt = cor[0]
                    longgg = cor[1]
                    row = [rida[0], rida[1], rida[2], rida[3], placeOrig, lattt, longgg]
                    row_list.append(row)
                    kas_leiti = True
                    kas_käi_kõik_läbi = False
                    break
                if place in asukohti:
                    try:
                        locator = geopy.Nominatim(user_agent="myGeocoder", timeout=3)
                        geocode = RateLimiter(locator.geocode, min_delay_seconds=20, max_retries=50, error_wait_seconds=25)
                        pöördumisi += 1
                        location = locator.geocode(place)
                        ##ainult riik
                        jupid = location.raw["display_name"].split(",")
                        riik = (jupid[len(jupid) - 1].strip())
                        if riik == "Eesti":
                            nimede_arhiiv[placeOrig] = [location.latitude, location.longitude]
                            row = [rida[0], rida[1], rida[2], rida[3], placeOrig, location.latitude, location.longitude]
                            row_list.append(row)
                            kas_leiti = True
                            kas_käi_kõik_läbi = False
                            break
                        else:
                            nimede_arhiiv[place] = "puudub"
                            nimede_arhiiv[placeOrig] = "puudub"

                    except:
                        kas_käi_kõik_läbi = False
                        terminator = True
                        puhkamisi += 1
                        break


            # Siia siseneme juhul kui asukohtade andmestikust ei leitud ühtegi vastet ja arhiivis ka vasteid ei olnud.
            # Küsime iga märksõna kohta koordinaate ja kontrollime, kas on Eestis.
            if kas_käi_kõik_läbi:
                for nimi in ast.literal_eval(rida[3]):
                    place = str(nimi).strip()
                    try:
                        if place not in nimede_arhiiv:
                            locator = geopy.Nominatim(user_agent="myGeocoder", timeout=3)
                            geocode = RateLimiter(locator.geocode, min_delay_seconds=20, max_retries=50, error_wait_seconds=25)
                            try:
                                pöördumisi += 1
                                location = locator.geocode(place)
                                puhkamisi = 0
                            except:
                                terminator = True
                                puhkamisi += 1
                                break
                            ##ainult riik
                            jupid = location.raw["display_name"].split(",")
                            riik = (jupid[len(jupid) - 1].strip())
                            if riik == "Eesti":
                                nimede_arhiiv[place] = [location.latitude, location.longitude]
                                row = [rida[0], rida[1], rida[2], rida[3], place, location.latitude, location.longitude]
                                row_list.append(row)
                                kas_leiti = True
                                break
                            else:
                                nimede_arhiiv[place] = "puudub"
                        else:
                            if nimede_arhiiv[place] != "puudub":
                                arhiivi_kasutusi += 1
                                cor = nimede_arhiiv[place]
                                lattt = cor[0]
                                longgg = cor[1]
                                row = [rida[0], rida[1], rida[2], rida[3], place, lattt, longgg]
                                row_list.append(row)
                                kas_leiti = True
                                break
                    except:
                        pass

            # Kui mitte ühelegi märksõnale vastet kuidagi ei leitud, siis kirjelduses asukohta polnud märgitud.
            if not kas_leiti:  # kui ei leitud koha vastet eestis
                row = [rida[0], rida[1], rida[2], rida[3], None, None, None]
                row_list.append(row)

    if i == maht:
        break

    # Väljastame progressi.
    print(progress(i), end="")
    i += 1


print()
tulemus = pd.DataFrame(row_list)
print(tulemus)
print("Pöördumisi geopy poole: " + str(pöördumisi))
print("Vaste arhiivis olemas: " + str(arhiivi_kasutusi))
tulemus.to_csv("koordineeritud.csv", sep='\t')
print("--- %s minutes ---" % str(round((time.time() - start_time) / 60, 2)))
