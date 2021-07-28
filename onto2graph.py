from onto2nx import OWLParser, parse_owl
import networkx as nx
import pickle

parser = OWLParser(file="./data/onto_xml.owl")
print("Parsed OWL file")

outgraph = nx.DiGraph()

for n in parser.nodes():
    outgraph.add_node(n)
for u, v in parser.edges():
    if u != v:
        outgraph.add_edge(u, v)

components = nx.weakly_connected_components(outgraph)
to_keep = set()

for comp in components:
    if "PlaceOfInterest" in comp:
        to_keep.update(comp)
to_del = set(outgraph.nodes()).difference(to_keep)

outgraph.remove_nodes_from(to_del)
outgraph = outgraph.reverse()
outgraph = nx.relabel_nodes(outgraph, {"PointOfInterest": "All"})

# Flip equivalent edges
pseudo_roots = []
for node in outgraph:
    if len(nx.ancestors(outgraph, node)) == 0 and node != "All":
        pseudo_roots.append(node)

for u, v in [(e[0], e[1]) for e in nx.edges(outgraph, pseudo_roots)]:
    print("Flipped", u, "->", v)
    outgraph.remove_edge(u, v)
    outgraph.add_edge(v, u)

from graphs import all_successors
event = nx.DiGraph()
event_roots = ["Tour", "Product", "EntertainmentAndEvent"]
event_nodes = set()
for er in event_roots:
    outgraph.remove_edge("All", er)
    event_nodes.update(all_successors(outgraph, er, []))

for u, v in outgraph.edges:
    if u in event_nodes or v in event_nodes:
        event.add_edge(u, v)

for u, v in event.edges:
    outgraph.remove_edge(u, v)

for n in event_nodes:
    outgraph.remove_node(n)

for n in event_roots:
    event.add_edge("All", n)

nx.write_gml(outgraph, "./data/graph_main.gml")
nx.write_gml(event, "./data/graph_event.gml")

from graphs import display
display(event, "./data/graph_event.html", height="900px", width="100%")
display(outgraph, "./data/graph_main.html", height="900px", width="100%")