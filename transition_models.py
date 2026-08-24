"""Generic, validated Markov models for synthetic sequence generation."""

from __future__ import annotations

from collections.abc import Hashable, Mapping
from math import isclose, isfinite
from typing import Generic, TypeVar

import networkx as nx
import numpy as np

State = TypeVar("State", bound=Hashable)
TransitionSpec = Mapping[State, Mapping[State, float]]


class TransitionModelError(ValueError):
    """Raised when a transition specification is not a valid absorbing model."""


class TransitionModel(Generic[State]):
    """A finite Markov model with configured initial and terminal states."""

    def __init__(
        self,
        spec: Mapping[State, Mapping[State, float]],
        *,
        initial_state: State,
        terminal_state: State,
    ) -> None:
        self.initial_state = initial_state
        self.terminal_state = terminal_state
        graph = self._build_graph(spec)
        self._validate(graph)
        self.graph = nx.freeze(graph)

    def _build_graph(
        self, spec: Mapping[State, Mapping[State, float]]
    ) -> nx.DiGraph:
        graph = nx.DiGraph()
        graph.add_node(self.terminal_state)
        for source, transitions in spec.items():
            if source == self.terminal_state and transitions:
                raise TransitionModelError("the terminal state cannot have transitions")
            total = sum(transitions.values())
            if not isclose(total, 1.0, abs_tol=1e-9):
                raise TransitionModelError(
                    f"outgoing probabilities for {source!r} sum to {total}, not 1"
                )
            for target, probability in transitions.items():
                if not isfinite(probability) or probability < 0:
                    raise TransitionModelError(
                        f"invalid probability {source!r} -> {target!r}: "
                        f"{probability!r}"
                    )
                # Zero-probability edges are not part of the effective Markov chain.
                if probability > 0:
                    graph.add_edge(source, target, weight=float(probability))
        return graph

    def _validate(self, graph: nx.DiGraph) -> None:
        if self.initial_state not in graph:
            raise TransitionModelError(
                f"initial state {self.initial_state!r} is absent"
            )
        reachable = {self.initial_state, *nx.descendants(graph, self.initial_state)}
        unreachable = set(graph).difference(reachable)
        if unreachable:
            raise TransitionModelError(
                f"states unreachable from {self.initial_state!r}: "
                f"{sorted(map(str, unreachable))}"
            )
        for state in reachable.difference({self.terminal_state}):
            if graph.out_degree(state) == 0:
                raise TransitionModelError(f"non-terminal state {state!r} is a dead end")
            if not nx.has_path(graph, state, self.terminal_state):
                raise TransitionModelError(
                    f"terminal state {self.terminal_state!r} is unreachable "
                    f"from {state!r} using positive-probability transitions"
                )

    def sample(
        self,
        rng: np.random.Generator,
        *,
        include_terminal: bool = True,
        max_steps: int = 10_000,
    ) -> list[State]:
        """Sample a state sequence, guarding against exceptionally long walks."""
        if max_steps <= 0:
            raise ValueError("max_steps must be positive")
        sequence = [self.initial_state]
        for _ in range(max_steps):
            current = sequence[-1]
            if current == self.terminal_state:
                return sequence if include_terminal else sequence[:-1]
            transitions = list(self.graph.out_edges(current, data="weight"))
            targets = [target for _, target, _ in transitions]
            probabilities = [probability for _, _, probability in transitions]
            sequence.append(rng.choice(targets, p=probabilities))
        raise RuntimeError(
            f"sample did not reach {self.terminal_state!r} within {max_steps} steps"
        )


PARTY_SPEC = {
    "Start": {"act_matin": 0.05, "Resto": 0.80, "Hotel": 0.15},
    "act_matin": {"act_matin": 0.01, "Resto": 0.48, "act_aprem": 0.01, "Hotel": 0.50},
    "Resto": {"act_aprem": 0.05, "Hotel": 0.65, "Sleep": 0.30},
    "act_aprem": {"act_aprem": 0.05, "Hotel": 0.10, "act_nocturne": 0.85},
    "Hotel": {"Sleep": 0.01, "act_nocturne": 0.99},
    "act_nocturne": {"act_nocturne": 0.40, "Sleep": 0.60},
}

CULTURAL_SPEC = {
    "Start": {"act_matin": 1.00, "Resto": 0.00, "Hotel": 0.00},
    "act_matin": {"act_matin": 0.50, "Resto": 0.40, "act_aprem": 0.10, "Hotel": 0.00},
    "Resto": {"act_aprem": 1.00, "Hotel": 0.00, "Sleep": 0.00},
    "act_aprem": {"act_aprem": 0.60, "Hotel": 0.30, "act_nocturne": 0.10},
    "Hotel": {"Sleep": 0.70, "act_nocturne": 0.30},
    "act_nocturne": {"act_nocturne": 0.05, "Sleep": 0.95},
}

CAMPING_SPEC = {
    "Start": {"act_matin": 0.80, "Resto": 0.10, "Hotel": 0.10},
    "act_matin": {"act_matin": 0.60, "Resto": 0.20, "act_aprem": 0.15, "Hotel": 0.05},
    "Resto": {"act_aprem": 0.78, "Hotel": 0.20, "Sleep": 0.02},
    "act_aprem": {"act_aprem": 0.40, "Hotel": 0.50, "act_nocturne": 0.10},
    "Hotel": {"Sleep": 0.70, "act_nocturne": 0.30},
    "act_nocturne": {"act_nocturne": 0.20, "Sleep": 0.80},
}

YOUTH_SPEC = {
    "Start": {"act_matin": 0.75, "Resto": 0.00, "Hotel": 0.25},
    "act_matin": {"act_matin": 0.50, "Resto": 0.50, "act_aprem": 0.00, "Hotel": 0.00},
    "Resto": {"act_aprem": 0.50, "Hotel": 0.50, "Sleep": 0.00},
    "act_aprem": {"act_aprem": 0.50, "Hotel": 0.50, "act_nocturne": 0.00},
    "Hotel": {"Sleep": 0.20, "act_nocturne": 0.80},
    "act_nocturne": {"act_nocturne": 0.20, "Sleep": 0.80},
}


def tourist_transition_model(
    spec: Mapping[str, Mapping[str, float]],
) -> TransitionModel[str]:
    return TransitionModel(spec, initial_state="Start", terminal_state="Sleep")


party_model = tourist_transition_model(PARTY_SPEC)
cultural_model = tourist_transition_model(CULTURAL_SPEC)
camping_model = tourist_transition_model(CAMPING_SPEC)
youth_model = tourist_transition_model(YOUTH_SPEC)

# Compatibility graph exports used by historical notebooks.
chain_fetard = party_model.graph
chain_culture = cultural_model.graph
chain_campeur = camping_model.graph
chain_jeunes = youth_model.graph

__all__ = [
    "TransitionModel",
    "TransitionModelError",
    "camping_model",
    "chain_campeur",
    "chain_culture",
    "chain_fetard",
    "chain_jeunes",
    "cultural_model",
    "party_model",
    "tourist_transition_model",
    "youth_model",
]
