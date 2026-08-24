"""Extract the SAC2021 taxonomy projections from DATAtourisme OWL.

This module intentionally models only the class hierarchy needed by SAC2021.
It is not a general OWL-to-property-graph converter.
"""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
from pathlib import Path

import networkx as nx

from taxonomy import Taxonomy
from visualization import render_graph

PROJECT_DIR = Path(__file__).resolve().parent
DEFAULT_SOURCE = PROJECT_DIR / "Data" / "onto_xml.owl"
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "Data"
DEFAULT_COMPONENT_ANCHOR = "PlaceOfInterest"
DEFAULT_ROOT_CLASS = "PointOfInterest"
DEFAULT_SYNTHETIC_ROOT = "All"
DEFAULT_EVENT_ROOTS = ("Tour", "Product", "EntertainmentAndEvent")


def parse_class_hierarchy(source: str | Path) -> nx.DiGraph:
    """Parse the legacy OWL source into the hierarchy exposed by onto2nx."""
    try:
        from onto2nx import OWLParser
    except ImportError as exc:
        raise RuntimeError(
            "taxonomy extraction currently requires the 'onto2nx' package"
        ) from exc

    parser = OWLParser(file=str(source))
    graph = nx.DiGraph()
    graph.add_nodes_from(parser.nodes())
    graph.add_edges_from((parent, child) for parent, child in parser.edges() if parent != child)
    return graph


def retain_component(graph: nx.DiGraph, anchor: str) -> nx.DiGraph:
    """Return a copy of the weak component containing ``anchor``."""
    if anchor not in graph:
        raise ValueError(f"component anchor {anchor!r} is absent from the hierarchy")
    component = nx.node_connected_component(graph.to_undirected(as_view=True), anchor)
    return graph.subgraph(component).copy()


def normalize_legacy_hierarchy(
    graph: nx.DiGraph,
    *,
    root_class: str = DEFAULT_ROOT_CLASS,
    synthetic_root: str = DEFAULT_SYNTHETIC_ROOT,
) -> nx.DiGraph:
    """Reproduce SAC2021's parent-to-child orientation and root normalization."""
    hierarchy = graph.reverse(copy=True)
    if root_class not in hierarchy:
        raise ValueError(f"root class {root_class!r} is absent from the hierarchy")
    hierarchy = nx.relabel_nodes(hierarchy, {root_class: synthetic_root}, copy=True)

    # Preserve the historical onto2nx normalization. A future RDF-aware parser
    # should replace this topology-based handling with explicit OWL semantics.
    pseudo_roots = [
        node
        for node, degree in hierarchy.in_degree()
        if degree == 0 and node != synthetic_root
    ]
    for source, target in list(hierarchy.out_edges(pseudo_roots)):
        hierarchy.remove_edge(source, target)
        hierarchy.add_edge(target, source)
    return hierarchy


def partition_taxonomy(
    hierarchy: nx.DiGraph,
    partition_roots: Iterable[str],
    *,
    root: str = DEFAULT_SYNTHETIC_ROOT,
) -> tuple[Taxonomy[str], Taxonomy[str]]:
    """Split event-related branches from the main class taxonomy."""
    main_graph = hierarchy.copy()
    event_nodes: set[str] = set()
    roots = tuple(partition_roots)

    for partition_root in roots:
        if not main_graph.has_edge(root, partition_root):
            raise ValueError(
                f"expected taxonomy edge {root!r} -> {partition_root!r} is missing"
            )
        event_nodes.add(partition_root)
        event_nodes.update(nx.descendants(main_graph, partition_root))

    event_graph = main_graph.subgraph(event_nodes).copy()
    event_graph.add_node(root)
    event_graph.add_edges_from((root, partition_root) for partition_root in roots)

    main_graph.remove_nodes_from(event_nodes)
    return Taxonomy(main_graph, root), Taxonomy(event_graph, root)


def build_taxonomies(
    source: str | Path = DEFAULT_SOURCE,
    *,
    component_anchor: str = DEFAULT_COMPONENT_ANCHOR,
    root_class: str = DEFAULT_ROOT_CLASS,
    synthetic_root: str = DEFAULT_SYNTHETIC_ROOT,
    event_roots: Sequence[str] = DEFAULT_EVENT_ROOTS,
) -> tuple[Taxonomy[str], Taxonomy[str]]:
    """Parse, normalize, partition, and validate DATAtourisme taxonomies."""
    parsed = parse_class_hierarchy(source)
    component = retain_component(parsed, component_anchor)
    normalized = normalize_legacy_hierarchy(
        component,
        root_class=root_class,
        synthetic_root=synthetic_root,
    )
    return partition_taxonomy(normalized, event_roots, root=synthetic_root)


def write_taxonomies(
    main_taxonomy: Taxonomy[str],
    event_taxonomy: Taxonomy[str],
    output_dir: str | Path,
    *,
    render_html: bool = False,
) -> None:
    """Write validated derived taxonomy artifacts."""
    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    nx.write_gml(main_taxonomy.graph, destination / "graph_main.gml")
    nx.write_gml(event_taxonomy.graph, destination / "graph_event.gml")

    if render_html:
        render_graph(
            event_taxonomy.graph,
            destination / "graph_event.html",
            height="900px",
        )
        render_graph(
            main_taxonomy.graph,
            destination / "graph_main.html",
            height="900px",
        )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build SAC2021 taxonomy projections from DATAtourisme OWL."
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--render-html", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = build_argument_parser().parse_args(argv)
    main_taxonomy, event_taxonomy = build_taxonomies(arguments.source)
    write_taxonomies(
        main_taxonomy,
        event_taxonomy,
        arguments.output_dir,
        render_html=arguments.render_html,
    )
    print(
        f"Wrote {len(main_taxonomy.graph)} main concepts and "
        f"{len(event_taxonomy.graph)} event concepts to {arguments.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
