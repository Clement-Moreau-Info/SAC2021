"""Generate synthetic semantic trajectories and compute their CED matrix.

Authors: Alexandre Chanson and Clément Moreau.
"""

import csv
import multiprocessing as mp
from pathlib import Path

import numpy as np
import pandas as pd
from ced import ced
from context_functions import SequenceLengthGaussianMembership
from scipy.spatial.distance import squareform

from dis_and_sim import mval_sim_ignore_null
from profiles import (
    PROFILES,
    TravelerProfile,
    categories_,
)
from taxonomy import Taxonomy
from taxonomy_data import HISTORICAL_PERIOD_TAXONOMY
from transition_models import TransitionModel

# Load data
PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "Data"
INSTANCES_FILE = DATA_DIR / "instances_clean.csv"
SEQ_FILE = DATA_DIR / "seqs.csv"
CED_MATRIX_FILE = DATA_DIR / "dis_matrix_ced.txt"
CED_MEMBERSHIP = SequenceLengthGaussianMembership()


"""## Model Vis"""
# Display code - Markov model
# display(chain, "markov.html", size_dynamic=False, height="600px", width="70%")


"""## Sequence Gen"""
def build_basic_sequence(
    model: TransitionModel[str],
    rng: np.random.Generator,
    *,
    append_end_node: bool = True,
) -> list[str]:
    return model.sample(rng, include_terminal=append_end_node)


def build_instance_sequence(
    base_seq: list[str],
    instance_map: dict[str, list[str]],
    profile: TravelerProfile,
    rng: np.random.Generator,
) -> list[str]:
    """Replace abstract states with instances selected from profile preferences."""
    def sample_instance(category: str) -> str:
        candidates = instance_map.get(category)
        if not candidates:
            raise ValueError(f"no instances are available for category {category!r}")
        return rng.choice(candidates)

    accommodation_category = profile.accommodation.sample(rng)
    hotel = sample_instance(accommodation_category)

    outseq = []
    for state in base_seq:
        if state in {"Start", "Hotel", "Sleep"}:
            outseq.append(hotel)
        else:
            category = profile.sample_category(state, rng)
            outseq.append(sample_instance(category))

    return outseq


def map_to_multival(seq, database):
    sem = []
    for item in seq:
        data = database[database["uri"] == item]
        tags = data["main_tags"].tolist()
        theme = data["event_tags"].tolist()
        archi = data["architecture_tags"].tolist()
        sem_item = (set() if tags == [np.nan] else datatourisme_main.retain_most_specific(set(tags[0].split(';'))),
                    set() if theme == [np.nan] else set(theme[0].split(';')),
                    set() if archi == [np.nan] else set(archi[0].split(';')))
        sem.append(sem_item)
    return sem


# Ontologies
datatourisme_main = Taxonomy.from_gml(DATA_DIR / "graph_main.gml", root="All")
datatourisme_theme = Taxonomy.from_gml(DATA_DIR / "graph_event.gml", root="All")


def sim(x, y):
    return mval_sim_ignore_null(
        x,
        y,
        [datatourisme_main, datatourisme_theme, HISTORICAL_PERIOD_TAXONOMY],
    )


def ced_distance(seq1, seq2):
    """Compute SAC2021 CED with its historical length-relative Gaussian."""
    return ced(seq1, seq2, sim, membership=CED_MEMBERSHIP)


def compute_distance_matrix(sequences, workers=12):
    """Compute the symmetric pairwise CED matrix."""
    pairs = [
        (sequences[i], sequences[j])
        for i in range(len(sequences))
        for j in range(i + 1, len(sequences))
    ]
    if workers == 1:
        condensed = [ced_distance(*pair) for pair in pairs]
    else:
        with mp.Pool(processes=workers) as pool:
            condensed = pool.starmap(ced_distance, pairs)
    return squareform(np.asarray(condensed, dtype=float))


def main():
    rng = np.random.default_rng()
    # Instances
    data_instances = pd.read_csv(INSTANCES_FILE)
    instances = {
        category: list(
            data_instances[data_instances["category"] == category]["uri"]
        )
        for category in categories_
    }

    seqs = []
    types = []
    for profile in PROFILES:
        print("Generating", profile.name)
        for _ in range(50):
            mv = []
            for _ in range(2):
                base = build_basic_sequence(profile.transition_model, rng)
                ids = build_instance_sequence(base, instances, profile, rng)
                mv.extend(map_to_multival(ids, data_instances))
            seqs.append(mv)
            types.append(profile.name)

    print("Writing", len(seqs), "sequences to", SEQ_FILE)
    with SEQ_FILE.open("w", newline="\n", encoding="utf-8") as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        spamwriter.writerow(["type", "seq_id", "item_id", "main_tags", "event_tags", "archi_tags"])

        for seq_id, seq in enumerate(seqs):
            for item_id, item in enumerate(seq):
                line = [types[seq_id], seq_id, item_id, ";".join(item[0]), ";".join(item[1]), ";".join(item[2])]
                spamwriter.writerow(line)
    print("Computing distance matrix - CED")
    ced_matrix = compute_distance_matrix(seqs)
    np.savetxt(CED_MATRIX_FILE, ced_matrix)


if __name__ == "__main__":
    main()
