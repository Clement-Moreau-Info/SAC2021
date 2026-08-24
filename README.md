SAC2021
=======

From the paper : 

* Clustering Sequences of Multi-dimensional Sets of Semantic Elements,
> C Moreau, A Chanson, V Peralta, T Devogele and C de Runz, ACM SAC (2021)

Coding colaboration with [AlexChanson](https://github.com/AlexChanson)


# Files description

## Contextual Edit Distance
------
* `dis_and_sim.py`

CED is provided by the external
[`contextual-edit-distance`](https://github.com/Clement-Moreau-Info/CED)
package. Install it directly from GitHub before running the experiments:

```bash
python -m pip install \
  "contextual-edit-distance @ git+https://github.com/Clement-Moreau-Info/CED.git"
```

The SAC2021 pipeline uses `SequenceLengthGaussianMembership`, corresponding
to the historical Gaussian context with `alpha = 0`.

## [DATAtourisme](https://framagit.org/datatourisme/ontology/) extraction

* `extract.py`
* `onto2graph.py`
* `taxonomy.py`
* `taxonomy_data.py`
* `visualization.py`

and several files in /Data folder. 

SAC2021 consumes a taxonomy projection of DATAtourisme: a validated directed
acyclic graph containing only parent-to-subclass relations. The OWL source
remains richer than this derived projection. Run `python onto2graph.py --help`
to rebuild the GML artifacts; HTML visualization is optional.

## Artificial touristic profile generation

* `profiles.py`
* `transition_models.py`
* `profiles_setting.xlsx`

`.xlsx` file details all weight and probabilities for sequences generation according to the psychological profiles created. 

`transition_models.py` defines validated Markov routines (when abstract
activities occur). `profiles.py` defines validated traveler preferences (which
category is selected for each kind of activity). A transition model can be
shared by several profiles, as the cultural and gastronomic profiles do.
