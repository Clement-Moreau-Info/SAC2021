"""Backward-compatible graph exports.

New code should import taxonomy operations, transition models, and rendering
from their dedicated modules.
"""

import warnings

import networkx as nx

from taxonomy_data import HISTORICAL_PERIOD_TAXONOMY, THEME_TAXONOMY
from transition_models import (
    chain_campeur,
    chain_culture,
    chain_fetard,
    chain_jeunes,
)
from visualization import render_graph

datatourisme_hist = HISTORICAL_PERIOD_TAXONOMY.graph
datatourisme_theme = THEME_TAXONOMY.graph


def all_successors(graph, node, accumulator=None):
    """Compatibility wrapper returning a node and all its descendants."""
    warnings.warn(
        "all_successors() is deprecated; use Taxonomy.descendants()",
        DeprecationWarning,
        stacklevel=2,
    )
    result = [node, *nx.descendants(graph, node)]
    if accumulator is not None:
        accumulator.extend(item for item in result if item not in accumulator)
        return accumulator
    return result


def all_predecessors(graph, node):
    """Compatibility wrapper returning a node and all its ancestors."""
    warnings.warn(
        "all_predecessors() is deprecated; use Taxonomy.ancestors()",
        DeprecationWarning,
        stacklevel=2,
    )
    return [node, *nx.ancestors(graph, node)]


def degeneralize(concepts, ontology):
    """Compatibility wrapper retaining only the most specific concepts."""
    warnings.warn(
        "degeneralize() is deprecated; use Taxonomy.retain_most_specific()",
        DeprecationWarning,
        stacklevel=2,
    )
    concepts = set(concepts)
    general = set().union(*(nx.ancestors(ontology, item) for item in concepts))
    return concepts.difference(general)


def display(
    graph,
    filename,
    size_dynamic=True,
    height="750px",
    width="100%",
    notebook=True,
):
    """Compatibility wrapper for the optional PyVis renderer."""
    warnings.warn(
        "display() is deprecated; use visualization.render_graph()",
        DeprecationWarning,
        stacklevel=2,
    )
    render_graph(
        graph,
        filename,
        size_by_descendants=size_dynamic,
        height=height,
        width=width,
    )


__all__ = [
    "all_predecessors",
    "all_successors",
    "chain_campeur",
    "chain_culture",
    "chain_fetard",
    "chain_jeunes",
    "datatourisme_hist",
    "datatourisme_theme",
    "degeneralize",
    "display",
]
