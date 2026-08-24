"""Optional PyVis rendering for taxonomies and transition models."""

from pathlib import Path

import networkx as nx


def render_graph(
    graph: nx.DiGraph,
    output: str | Path,
    *,
    size_by_descendants: bool = True,
    height: str = "750px",
    width: str = "100%",
) -> None:
    """Render a directed graph to an interactive HTML document."""
    try:
        from pyvis.network import Network
    except ImportError as exc:
        raise RuntimeError(
            "graph rendering requires the optional 'pyvis' dependency"
        ) from exc

    output_path = Path(output)
    network = Network(
        height=height,
        width=width,
        directed=True,
        heading=output_path.stem,
    )

    for node in graph:
        size = 80 * (len(nx.descendants(graph, node)) + 1) if size_by_descendants else 80
        color = "Green" if node == "Start" else "Red" if node == "Sleep" else None
        options = {"value": size, "label": str(node)}
        if color is not None:
            options["color"] = color
        network.add_node(node, **options)

    for source, target, attributes in graph.edges(data=True):
        label = attributes.get("weight")
        if label is None:
            network.add_edge(source, target)
        else:
            network.add_edge(source, target, label=str(label))

    network.show_buttons(filter_=["physics"])
    network.write_html(str(output_path), notebook=False, open_browser=False)


__all__ = ["render_graph"]
