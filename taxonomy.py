"""Validated class-taxonomy operations built on directed acyclic graphs.

Edges are oriented from a general concept to a more specific concept.
"""

from __future__ import annotations

from collections.abc import Collection, Hashable
from pathlib import Path
from types import MappingProxyType
from typing import Generic, Literal, TypeVar

import networkx as nx

Concept = TypeVar("Concept", bound=Hashable)
UnknownConceptPolicy = Literal["error", "preserve", "ignore"]


class TaxonomyError(ValueError):
    """Base exception for invalid taxonomy structure or operations."""


class UnknownConceptError(TaxonomyError):
    """Raised when an operation receives a concept outside the taxonomy."""


class Taxonomy(Generic[Concept]):
    """A validated, immutable parent-to-child class hierarchy."""

    def __init__(self, graph: nx.DiGraph, root: Concept) -> None:
        owned_graph = nx.DiGraph(graph)
        self._validate(owned_graph, root)
        self._graph = nx.freeze(owned_graph)
        self.root = root
        self._depths = MappingProxyType(
            dict(nx.single_source_shortest_path_length(self._graph, root))
        )
        self._similarity_cache: dict[tuple[Concept, Concept], float] = {}

    @classmethod
    def from_gml(cls, path: str | Path, root: Concept) -> "Taxonomy[Concept]":
        """Load and validate a taxonomy stored in NetworkX GML format."""
        return cls(nx.read_gml(Path(path)), root)

    @staticmethod
    def _validate(graph: nx.DiGraph, root: Concept) -> None:
        if not graph.is_directed():
            raise TaxonomyError("a taxonomy graph must be directed")
        if root not in graph:
            raise TaxonomyError(f"taxonomy root {root!r} is missing")
        if not nx.is_directed_acyclic_graph(graph):
            raise TaxonomyError("a taxonomy graph must be acyclic")

        unreachable = set(graph).difference({root}, nx.descendants(graph, root))
        if unreachable:
            sample = sorted(map(str, unreachable))[:5]
            raise TaxonomyError(
                f"{len(unreachable)} concepts are unreachable from {root!r}: {sample}"
            )

    @property
    def graph(self) -> nx.DiGraph:
        """Return the frozen NetworkX projection for graph algorithms."""
        return self._graph

    def __contains__(self, concept: object) -> bool:
        return concept in self._graph

    def _require(self, concept: Concept) -> None:
        if concept not in self:
            raise UnknownConceptError(f"unknown taxonomy concept: {concept!r}")

    def ancestors(
        self, concept: Concept, *, inclusive: bool = False
    ) -> frozenset[Concept]:
        self._require(concept)
        result = set(nx.ancestors(self._graph, concept))
        if inclusive:
            result.add(concept)
        return frozenset(result)

    def descendants(
        self, concept: Concept, *, inclusive: bool = False
    ) -> frozenset[Concept]:
        self._require(concept)
        result = set(nx.descendants(self._graph, concept))
        if inclusive:
            result.add(concept)
        return frozenset(result)

    def retain_most_specific(
        self,
        concepts: Collection[Concept],
        *,
        unknown: UnknownConceptPolicy = "error",
    ) -> frozenset[Concept]:
        """Remove concepts that are ancestors of another supplied concept."""
        if unknown not in {"error", "preserve", "ignore"}:
            raise ValueError("unknown policy must be 'error', 'preserve', or 'ignore'")

        known = {concept for concept in concepts if concept in self}
        unknown_concepts = set(concepts).difference(known)
        if unknown_concepts and unknown == "error":
            raise UnknownConceptError(
                f"unknown taxonomy concepts: {sorted(map(str, unknown_concepts))}"
            )

        general = set().union(*(self.ancestors(c) for c in known)) if known else set()
        result = known.difference(general)
        if unknown == "preserve":
            result.update(unknown_concepts)
        return frozenset(result)

    def wu_palmer(self, left: Concept, right: Concept) -> float:
        """Return Wu–Palmer similarity using the deepest common ancestor."""
        self._require(left)
        self._require(right)
        key = (left, right)
        reverse_key = (right, left)
        if key in self._similarity_cache:
            return self._similarity_cache[key]
        if reverse_key in self._similarity_cache:
            return self._similarity_cache[reverse_key]

        common = self.ancestors(left, inclusive=True).intersection(
            self.ancestors(right, inclusive=True)
        )
        ancestor = max(common, key=self._depths.__getitem__)
        left_depth = self._depths[left]
        right_depth = self._depths[right]
        denominator = left_depth + right_depth
        similarity = (
            1.0 if denominator == 0 else 2.0 * self._depths[ancestor] / denominator
        )
        self._similarity_cache[key] = similarity
        return similarity


__all__ = ["Taxonomy", "TaxonomyError", "UnknownConceptError"]
