import json
import os
from pprint import pprint
import csv
import networkx as nx
import seaborn as sns
from matplotlib import pyplot as plt

DATA_PATH = "./data/"
HEADER = ["uri", 'label', "category", "main_tags", "event_tags", "architecture_tags"]
CAT = [("Accommodation", "Hotel"), ("Restaurant", "Resto")]

main = nx.read_gml("./data/graph_main.gml")
event = nx.read_gml("./data/graph_event.gml")


def to_keep(tag):
    if tag == "PointOfInterest":
        return False
    if tag.startswith("schema:"):
        return False
    if tag.startswith("olo:"):
        return False
    return True


if __name__ == '__main__':
    archi_domain = []

    with open(DATA_PATH + "index.json", encoding='UTF-8') as idx:
        index = json.load(idx)

    # Parse each file, one entry per file
    entries = []
    for item in index:
        with open(DATA_PATH + "objects/" + item["file"], encoding='UTF-8') as file:
            data = json.load(file)

        # Separate into distinct categories
        type = "act"
        for tag in data["@type"]:
            if tag == "Hotel":
                type = "Hotel"
                break
            if tag == "BistroOrWineBar":
                type = "bar"
                break
            if tag == "FastFoodRestaurant":
                type = "fast_food"
            if tag == "Restaurant":
                type = "Resto"
                break
            if tag == "Church":
                type = "church"
                break
            if tag == "Camping" or tag == "CamperVanArea":
                type = "camping"
                break
            if tag == "Museum":
                type = "museum"
                break
            if tag == "NaturalHeritage":
                type = "nature"
            if tag == "Tasting":
                type = "tasting"
                break
            if tag == "Castle":
                type = "castle"
                break
            if tag == "ParkAndGarden":
                type = "park"
                break
            if tag == "RentalAccommodation":
                type = "gite"
                break
            if tag.startswith("Sports"):
                type = "sport"
                break

        themes = []
        archi = []
        try:
            for theme in data["hasTheme"]:

                #print(theme["@type"])
                if 'ArchitecturalStyle' in theme["@type"]:
                    archi.extend(theme["rdfs:label"]["fr"])
                    t = theme["@type"]
                    t.remove('ArchitecturalStyle')
                    themes.extend(t)
                else:
                    themes.extend(theme["@type"])
        except KeyError:
            pass
        archi_domain.extend(archi)

        #Cleanup
        tag_data = list(filter(to_keep, data["@type"]))

        # Isolate event tags
        event_tags = []
        for t in tag_data:
            if t in event.nodes:
                event_tags.append(t)
        for t in event_tags:
            tag_data.remove(t)

        #Build entry
        entry = [data["@id"][len("https://data.datatourisme.gouv.fr/"):], item['label'], type, ";".join(tag_data), ";".join(event_tags), ";".join(archi)]
        entries.append(entry)

    print("Total instances", len(entries))
    too_empty = []
    for entry in entries:
        s = len(entry[3])*1 + len(entry[3])*1 + len(entry[3])*1
        if s < 2:
            too_empty.append(entry)

    entries = list(filter(lambda e: e not in too_empty, entries))
    print("Dubious instances", len(too_empty))


    with open(DATA_PATH + 'output.csv', 'w', newline='\n', encoding='UTF-8') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',',  quotechar='"', quoting=csv.QUOTE_ALL)
        spamwriter.writerow(HEADER)
        for line in entries:
            spamwriter.writerow(line)

    print("Active domain for architecture")
    print(set(archi_domain))

    sns.displot(list(map(lambda x: x[2][:3], entries)))
    plt.show()
