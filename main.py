"""
    Alexandre Chanson
"""

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
from numpy.random import choice
from scipy.cluster.hierarchy import dendrogram, linkage
import csv

from CED import *
from Context_function import gaussian
from graphs import datatourisme_hist, datatourisme_theme, chain_fetard, all_successors, all_predecessors, degeneralize, display
from dis_and_sim import halkidi, mval_sim, wu_palmer, mval_sim_ignore_null
import concurrent.futures
import multiprocessing as mp



# Load data
ID_PREFIX = "https://data.datatourisme.gouv.fr/"  # Ids (URI) have been striped for memory/ease of use
INSTANCES_FILE = "data/instances_clean.csv"
SEQ_FILE = "data/seqs.csv"


"""## Model Vis"""
# Display code - Markov model
# display(chain, "markov.html", size_dynamic=False, height="600px", width="70%")


"""## Sequence Gen"""
def build_basic_sequence(markov, start_node, end_node, append_end_node=True):
    def white_walker(acc):
        successors = markov.successors(acc[-1])
        probas = []
        items = []
        for next in successors:
            items.append(next)
            probas.append(markov.get_edge_data(acc[-1], next)["weight"])
        # numpy.random.choice
        draw = choice(items, 1, p=probas)[0]

        if draw == end_node:
            if append_end_node:
                acc.append(draw)
            return acc

        acc.append(draw)
        return white_walker(acc)

    return white_walker([start_node])


def build_instance_sequence(base_seq, instance_map, profile, start_node_swap="Hotel"):
    if start_node_swap is not None:
        base_seq[0] = start_node_swap

    # Hotel is drawn once
    # numpy.random.choice
    acc_types, acc_probas = get_types_and_probas(profile["accommodation"])
    acc_type = choice(acc_types, 1, p=acc_probas)[0]
    hotel = choice(instance_map[acc_type], 1)[0]

    outseq = []
    for item in base_seq:
        if item == "Hotel" or item == "Sleep":
            outseq.append(hotel)
        elif item == "Resto":
            res_types, res_probas = get_types_and_probas(profile["food"])
            res_type = choice(res_types, 1, p=res_probas)[0]
            outseq.append(choice(instance_map[res_type], 1)[0])
        elif item == "act_matin" or item == "act_aprem":
            act_types, act_probas = get_types_and_probas(profile["activity"])
            act_type = choice(act_types, 1, p=act_probas)[0]
            outseq.append(choice(instance_map[act_type], 1)[0])
        else:
            act_type = "act"
            outseq.append(choice(instance_map[act_type], 1)[0])

    return outseq


def map_to_multival(seq, database):
    sem = []
    for item in seq:
        data = database[database["uri"] == item]
        tags = data["main_tags"].tolist()
        theme = data["event_tags"].tolist()
        archi = data["architecture_tags"].tolist()
        sem_item = (set() if tags == [np.nan] else degeneralize(set(tags[0].split(';')), datatourisme_main),
                    set() if theme == [np.nan] else set(theme[0].split(';')),
                    set() if archi == [np.nan] else set(archi[0].split(';')))
        sem.append(sem_item)
    return sem


# Ontologies
datatourisme_main = nx.read_gml("./data/graph_main.gml")
datatourisme_theme = nx.read_gml("./data/graph_event.gml")


def sim(x, y):
    return mval_sim_ignore_null(x, y, [datatourisme_main, datatourisme_theme, datatourisme_hist])


if __name__ == '__main__':
    from profiles import *
    # Instances
    data_instances = pd.read_csv(INSTANCES_FILE)
    instances = dict()
    for cat in categories_:
        instances[cat] = list(data_instances[data_instances["category"] == cat]["uri"])

    profiles = [campeur, fetard, gastronomie, culturel, jeunes]
    seqs = []
    types = []
    for profile in profiles:
        print("Generating", profile["name"])
        for i in range(50):
            mv = []
            for day in range(2):
                base = build_basic_sequence(profile["chain"], "Start", "Sleep")
                ids = build_instance_sequence(base, instances, profile)
                mv.extend(map_to_multival(ids, data_instances))
            seqs.append(mv)
            types.append(profile["name"])

    print("Writing", len(seqs), "sequences to", SEQ_FILE)
    with open(SEQ_FILE, 'w', newline='\n') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        spamwriter.writerow(["type", "seq_id", "item_id", "main_tags", "event_tags", "archi_tags"])

        for seq_id, seq in enumerate(seqs):
            for item_id, item in enumerate(seq):
                line = [types[seq_id], seq_id, item_id, ";".join(item[0]), ";".join(item[1]), ";".join(item[2])]
                spamwriter.writerow(line)



    # Convert to numpy data type
    #msize = int((len(seqs) * (len(seqs) - 1)) / 2) # Compute triangular matrix size
    np_seqs = []
    for seq in seqs:
        seqA = np.empty((len(seq),), dtype=object)
        for k in range(len(seq)):
            seqA[k] = seq[k]
        np_seqs.append(seqA)
    del seqs#Free memory

    print("Computing distance matrix - CED")
    pool = mp.Pool(12)
    result = pool.starmap(ced, [(np_seqs[i], np_seqs[j], sim, gaussian, 0.) for i in range(len(np_seqs)) for j in range(i + 1, len(np_seqs))])
    pool.close()

    from scipy.spatial.distance import squareform
    CED_matrix = squareform(np.array(result))
    np.savetxt("data/dis_matrix_ced.txt", CED_matrix)

    print("Computing distance matrix - ED")
    pool = mp.Pool(12)
    result = pool.starmap(ced, [(np_seqs[i], np_seqs[j], sim, gaussian, 1.) for i in range(len(np_seqs)) for j in range(i + 1, len(np_seqs))])
    pool.close()

    from scipy.spatial.distance import squareform
    CED_matrix = squareform(np.array(result))
    np.savetxt("data/dis_matrix_ed.txt", CED_matrix)

    print("Computing distance matrix - Levenshtein")
    def trivial(x, y):
        return 1 if x == y else 0
    pool = mp.Pool(12)
    result = pool.starmap(ced, [(np_seqs[i], np_seqs[j], trivial, gaussian, 1.) for i in range(len(np_seqs)) for j in
                                range(i + 1, len(np_seqs))])
    pool.close()

    from scipy.spatial.distance import squareform

    CED_matrix = squareform(np.array(result))
    np.savetxt("data/dis_matrix_lev.txt", CED_matrix)


