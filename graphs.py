import networkx as nx
from pyvis.network import Network

datatourisme_theme = nx.DiGraph()
datatourisme_theme.add_node("SpatialEnvironmentTheme")
datatourisme_theme.add_edges_from([("All", "CulturalTheme"), ("All", "ParkAndGardenTheme"), ("All", "HealthTheme"),
                                   ("All", "FoodEstablishementTheme"), ("All", "FoodProduct"),
                                   ("All", "SpatialEnvironmentTheme"), ("All", "SportsTheme"),
                                   ("All", "EntertainmentAndEventTheme"), ("All", "CuisineCategory"),
                                   ("All", "RouteTheme"), ("RouteTheme", "CycleRouteTheme"),
                                   ("RouteTheme", "MTBRouteTheme"), ("All", "CommonAmenity")])
datatourisme_hist = nx.DiGraph()
datatourisme_hist.add_edges_from(
    [("All", "AD"), ("All", "BC"), ("AD", "Médiéval"), ("Médiéval", "Gothique"), ("Médiéval", "Roman"),
     ("AD", "Renaissance"),
     ("BC", "Antiquité"), ("Antiquité", "Gallo-romain"), ("AD", "XVII/XVIII"), ("XVII/XVIII", "Classique"),
     ("XVII/XVIII", "Néo-Classique"), ("AD", "Moderne"), ("Moderne", "Contemporain"), ("Moderne", "Xixe siècle"),
     ("Moderne", "Xxe siècle")])

"""# Generator models"""

r = "Resto";
m = "act_matin";
a = "act_aprem";
h = "Hotel";
s = "Sleep";
n = "act_nocturne";
st = "Start"

chain_fetard = nx.DiGraph()
# Start
chain_fetard.add_edge(st, m, weight=0.05)
chain_fetard.add_edge(st, r, weight=0.80)
chain_fetard.add_edge(st, h, weight=0.15)
# Activité matin
chain_fetard.add_edge(m, m, weight=0.01)  # autre act
chain_fetard.add_edge(m, r, weight=0.48)  # resto
chain_fetard.add_edge(m, a, weight=0.01)  # act matiné
chain_fetard.add_edge(m, h, weight=0.5)  # hotel
# Resto
chain_fetard.add_edge(r, a, weight=0.05)
chain_fetard.add_edge(r, h, weight=0.65)
chain_fetard.add_edge(r, s, weight=0.30)
# Activité Aprem
chain_fetard.add_edge(a, a, weight=0.05)
chain_fetard.add_edge(a, h, weight=0.1)
chain_fetard.add_edge(a, n, weight=0.85)
# Hotel (Soir)
chain_fetard.add_edge(h, s, weight=0.01)
chain_fetard.add_edge(h, n, weight=0.99)
# Activité Nocturne
chain_fetard.add_edge(n, n, weight=0.4)
chain_fetard.add_edge(n, s, weight=0.6)

chain_culture = nx.DiGraph()
# Start
chain_culture.add_edge(st, m, weight=1.)
chain_culture.add_edge(st, r, weight=0.)
chain_culture.add_edge(st, h, weight=0.)
# Activité matin
chain_culture.add_edge(m, m, weight=0.5)
chain_culture.add_edge(m, r, weight=0.4)
chain_culture.add_edge(m, a, weight=0.1)
chain_culture.add_edge(m, h, weight=0.)
# Resto
chain_culture.add_edge(r, a, weight=1.)
chain_culture.add_edge(r, h, weight=0.)
chain_culture.add_edge(r, s, weight=0.)
# Activité Aprem
chain_culture.add_edge(a, a, weight=0.6)
chain_culture.add_edge(a, h, weight=0.3)
chain_culture.add_edge(a, n, weight=0.1)
# Hotel (Soir)
chain_culture.add_edge(h, s, weight=0.7)
chain_culture.add_edge(h, n, weight=0.3)
# Activité Nocturne
chain_culture.add_edge(n, n, weight=0.05)
chain_culture.add_edge(n, s, weight=0.95)

chain_campeur = nx.DiGraph()
# Start
chain_campeur.add_edge(st, m, weight=0.8)
chain_campeur.add_edge(st, r, weight=0.1)
chain_campeur.add_edge(st, h, weight=0.1)
# Activité matin
chain_campeur.add_edge(m, m, weight=0.6)  # autre act
chain_campeur.add_edge(m, r, weight=0.2)  # resto
chain_campeur.add_edge(m, a, weight=0.15)  # act aprem
chain_campeur.add_edge(m, h, weight=0.05)  # hotel
# Resto
chain_campeur.add_edge(r, a, weight=0.78)
chain_campeur.add_edge(r, h, weight=0.2)
chain_campeur.add_edge(r, s, weight=0.02)
# Activité Aprem
chain_campeur.add_edge(a, a, weight=0.4)
chain_campeur.add_edge(a, h, weight=0.5)
chain_campeur.add_edge(a, n, weight=0.1)
# Hotel (Soir)
chain_campeur.add_edge(h, s, weight=0.70)
chain_campeur.add_edge(h, n, weight=0.3)
# Activité Nocturne
chain_campeur.add_edge(n, n, weight=0.2)
chain_campeur.add_edge(n, s, weight=0.8)

chain_jeunes = nx.DiGraph()
# Start
chain_jeunes.add_edge(st, m, weight=0.75)
chain_jeunes.add_edge(st, r, weight=0.)
chain_jeunes.add_edge(st, h, weight=0.25)
# Activité matin
chain_jeunes.add_edge(m, m, weight=0.5)  # autre act
chain_jeunes.add_edge(m, r, weight=0.5)  # resto
chain_jeunes.add_edge(m, a, weight=0.)  # act aprem
chain_jeunes.add_edge(m, h, weight=0.)  # hotel
# Resto
chain_jeunes.add_edge(r, a, weight=0.5)
chain_jeunes.add_edge(r, h, weight=0.5)
chain_jeunes.add_edge(r, s, weight=0.)
# Activité Aprem
chain_jeunes.add_edge(a, a, weight=0.5)
chain_jeunes.add_edge(a, h, weight=0.5)
chain_jeunes.add_edge(a, n, weight=0.)
# Hotel (Soir)
chain_jeunes.add_edge(h, s, weight=0.2)
chain_jeunes.add_edge(h, n, weight=0.8)
# Activité Nocturne
chain_jeunes.add_edge(n, n, weight=0.2)
chain_jeunes.add_edge(n, s, weight=0.8)


def all_successors(G, n, all_succ):
    all_succ += [n]
    for _n in G.successors(n):
        if _n not in all_succ:
            all_successors(G, _n, all_succ)
    return all_succ


def all_predecessors(Graph, node):
    def internal(G, n, acc):
        acc += [n]
        for _n in G.predecessors(n):
            if _n not in acc:
                internal(G, _n, acc)
        return acc

    return internal(Graph, node, [])


def degeneralize(concepts, ontology):
    more_general = set()

    for concept in concepts:
        to_rem = all_predecessors(ontology, concept)
        to_rem.remove(concept)

        more_general.update(to_rem)

    return concepts.difference(more_general)


def display(G, filename, size_dynamic=True, height='750px', width="100%", notebook=True):
    # pyvis.Network
    g = Network(height=height, width=width, directed=True, heading=filename.rstrip(".html"))

    if size_dynamic:
        size = lambda Graph, node: 80 * len(all_successors(Graph, node, []))
    else:
        size = lambda Graph, node: 80

    for n in G:
        if n == "Start":
            g.add_node(n, value=size(G, n), label=n, color="Green")
        elif n == "Sleep":
            g.add_node(n, value=size(G, n), label=n, color="Red")
        else:
            g.add_node(n, value=size(G, n), label=n, )
    for edge in G.edges:
        try:
            g.add_edge(edge[0], edge[1], label=G.get_edge_data(edge[0], edge[1])["weight"])
        except KeyError:
            g.add_edge(edge[0], edge[1])

    g.show_buttons(filter_=['physics'])
    g.show(filename)


if __name__ == '__main__':
    from profiles import culturel, fetard

    profs = [fetard, culturel]
    for pr in profs:
        print('---', pr["name"], "---")
        print('Départ,Arrivée,Proba')
        chain_campeur = pr['chain']
        for u, v in chain_campeur.edges:
            print(u, v, chain_campeur.get_edge_data(u, v)["weight"], sep=',')
