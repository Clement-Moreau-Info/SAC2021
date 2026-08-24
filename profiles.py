"""Validated traveler preferences coupled to reusable transition models."""

from __future__ import annotations

from collections.abc import Hashable, Iterable, Sequence
from dataclasses import dataclass
from math import isclose, isfinite
from typing import Generic, TypeVar

import numpy as np

from transition_models import (
    TransitionModel,
    camping_model,
    cultural_model,
    party_model,
    youth_model,
)

Choice = TypeVar("Choice", bound=Hashable)


@dataclass(frozen=True)
class WeightedDistribution(Generic[Choice]):
    """A finite categorical probability distribution."""

    values: tuple[Choice, ...]
    probabilities: tuple[float, ...]

    def __post_init__(self) -> None:
        if not self.values:
            raise ValueError("a weighted distribution cannot be empty")
        if len(self.values) != len(self.probabilities):
            raise ValueError("values and probabilities must have equal lengths")
        if len(set(self.values)) != len(self.values):
            raise ValueError("distribution values must be unique")
        if any(not isfinite(p) or p < 0 for p in self.probabilities):
            raise ValueError("probabilities must be finite and non-negative")
        total = sum(self.probabilities)
        if not isclose(total, 1.0, abs_tol=1e-9):
            raise ValueError(f"probabilities sum to {total}, not 1")

    @classmethod
    def from_pairs(
        cls, pairs: Iterable[tuple[Choice, float]]
    ) -> "WeightedDistribution[Choice]":
        materialized = tuple(pairs)
        return cls(
            tuple(value for value, _ in materialized),
            tuple(float(probability) for _, probability in materialized),
        )

    def sample(self, rng: np.random.Generator) -> Choice:
        return rng.choice(self.values, p=self.probabilities)


@dataclass(frozen=True)
class TravelerProfile:
    """Traveler preferences independent from the daily transition routine."""

    name: str
    transition_model: TransitionModel[str]
    accommodation: WeightedDistribution[str]
    food: WeightedDistribution[str]
    activity: WeightedDistribution[str]
    nighttime: WeightedDistribution[str]

    def distribution_for_state(self, state: str) -> WeightedDistribution[str] | None:
        if state in {"Hotel", "Sleep", "Start"}:
            return self.accommodation
        if state == "Resto":
            return self.food
        if state in {"act_matin", "act_aprem"}:
            return self.activity
        if state == "act_nocturne":
            return self.nighttime
        return None

    def sample_category(self, state: str, rng: np.random.Generator) -> str:
        distribution = self.distribution_for_state(state)
        return "act" if distribution is None else distribution.sample(rng)


def distribution(*pairs: tuple[str, float]) -> WeightedDistribution[str]:
    return WeightedDistribution.from_pairs(pairs)


fetard = TravelerProfile(
    name="fetard",
    transition_model=party_model,
    accommodation=distribution(("Hotel", 0.15), ("camping", 0.85), ("gite", 0.0)),
    food=distribution(("fast_food", 0.9), ("Resto", 0.05), ("park", 0.05)),
    activity=distribution(
        ("church", 0.05), ("museum", 0.05), ("nature", 0.1),
        ("tasting", 0.05), ("castle", 0.05), ("park", 0.1),
        ("sport", 0.1), ("bar", 0.5),
    ),
    nighttime=distribution(("act", 0.1), ("bar", 0.9)),
)

culturel = TravelerProfile(
    name="culturel",
    transition_model=cultural_model,
    accommodation=distribution(("Hotel", 0.5), ("camping", 0.0), ("gite", 0.5)),
    food=distribution(("fast_food", 0.0), ("Resto", 0.7), ("park", 0.3)),
    activity=distribution(
        ("church", 0.2), ("museum", 0.3), ("nature", 0.05),
        ("tasting", 0.05), ("castle", 0.25), ("park", 0.05),
        ("sport", 0.05), ("act", 0.05),
    ),
    nighttime=distribution(("act", 0.9), ("bar", 0.1)),
)

campeur = TravelerProfile(
    name="campeur",
    transition_model=camping_model,
    accommodation=distribution(("Hotel", 0.0), ("camping", 1.0), ("gite", 0.0)),
    food=distribution(("fast_food", 0.0), ("Resto", 0.2), ("park", 0.8)),
    activity=distribution(
        ("church", 0.05), ("museum", 0.125), ("nature", 0.125),
        ("tasting", 0.05), ("castle", 0.2), ("park", 0.2),
        ("sport", 0.125), ("act", 0.125),
    ),
    nighttime=distribution(("act", 0.1), ("bar", 0.9)),
)

jeunes = TravelerProfile(
    name="jeunes",
    transition_model=youth_model,
    accommodation=distribution(("Hotel", 0.1), ("camping", 0.1), ("gite", 0.8)),
    food=distribution(("fast_food", 0.0), ("Resto", 0.5), ("park", 0.5)),
    activity=distribution(
        ("church", 0.05), ("museum", 0.125), ("nature", 0.2),
        ("tasting", 0.05), ("castle", 0.125), ("park", 0.2),
        ("sport", 0.125), ("act", 0.125),
    ),
    nighttime=distribution(("act", 0.1), ("bar", 0.9)),
)

gastronomie = TravelerProfile(
    name="gastronomie",
    transition_model=cultural_model,
    accommodation=distribution(("Hotel", 1.0), ("camping", 0.0), ("gite", 0.0)),
    food=distribution(("fast_food", 0.0), ("Resto", 1.0), ("park", 0.0)),
    activity=distribution(
        ("church", 0.1), ("museum", 0.15), ("nature", 0.1),
        ("tasting", 0.3), ("castle", 0.15), ("park", 0.05),
        ("sport", 0.05), ("act", 0.1),
    ),
    nighttime=distribution(("act", 0.1), ("bar", 0.9)),
)

PROFILES: tuple[TravelerProfile, ...] = (
    campeur,
    fetard,
    gastronomie,
    culturel,
    jeunes,
)

categories_ = [
    "act", "Hotel", "fast_food", "Resto", "church", "camping", "museum",
    "nature", "tasting", "castle", "park", "gite", "sport", "bar",
]


def get_types_and_probas(
    values: WeightedDistribution[str] | Sequence[tuple[str, float]],
) -> tuple[list[str], list[float]]:
    """Compatibility helper retained for historical notebooks."""
    if isinstance(values, WeightedDistribution):
        return list(values.values), list(values.probabilities)
    return [item[0] for item in values], [item[1] for item in values]


__all__ = [
    "PROFILES",
    "TravelerProfile",
    "WeightedDistribution",
    "campeur",
    "categories_",
    "culturel",
    "fetard",
    "gastronomie",
    "get_types_and_probas",
    "jeunes",
]
