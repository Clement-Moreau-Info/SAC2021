import unittest
from pathlib import Path

import networkx as nx

from taxonomy import Taxonomy, TaxonomyError, UnknownConceptError
from onto2graph import DEFAULT_EVENT_ROOTS, partition_taxonomy


class TaxonomyTests(unittest.TestCase):
    def setUp(self):
        self.taxonomy = Taxonomy(
            nx.DiGraph(
                [
                    ("All", "Place"),
                    ("Place", "Museum"),
                    ("Place", "Park"),
                    ("Museum", "ArtMuseum"),
                ]
            ),
            root="All",
        )

    def test_traversal_can_include_the_concept(self):
        self.assertEqual(
            self.taxonomy.ancestors("Museum", inclusive=True),
            frozenset({"All", "Place", "Museum"}),
        )
        self.assertEqual(
            self.taxonomy.descendants("Museum", inclusive=True),
            frozenset({"Museum", "ArtMuseum"}),
        )

    def test_retain_most_specific(self):
        result = self.taxonomy.retain_most_specific(
            {"All", "Place", "Museum", "ArtMuseum", "Park"}
        )
        self.assertEqual(result, frozenset({"ArtMuseum", "Park"}))

    def test_unknown_concept_policies(self):
        with self.assertRaises(UnknownConceptError):
            self.taxonomy.retain_most_specific({"Museum", "Missing"})
        self.assertEqual(
            self.taxonomy.retain_most_specific(
                {"Museum", "Missing"}, unknown="preserve"
            ),
            frozenset({"Museum", "Missing"}),
        )

    def test_wu_palmer(self):
        self.assertEqual(self.taxonomy.wu_palmer("All", "All"), 1.0)
        self.assertEqual(self.taxonomy.wu_palmer("Museum", "Museum"), 1.0)
        self.assertAlmostEqual(self.taxonomy.wu_palmer("Museum", "Park"), 0.5)

    def test_rejects_cycles_and_unreachable_nodes(self):
        with self.assertRaises(TaxonomyError):
            Taxonomy(nx.DiGraph([("All", "A"), ("A", "All")]), "All")
        graph = nx.DiGraph([("All", "A")])
        graph.add_node("Detached")
        with self.assertRaises(TaxonomyError):
            Taxonomy(graph, "All")

    def test_existing_artifacts_are_valid_taxonomies(self):
        data_dir = Path(__file__).resolve().parent / "Data"
        for filename in ("graph_main.gml", "graph_event.gml"):
            taxonomy = Taxonomy.from_gml(data_dir / filename, root="All")
            self.assertIn("All", taxonomy)

    def test_existing_partition_can_be_reconstructed(self):
        data_dir = Path(__file__).resolve().parent / "Data"
        expected_main = nx.read_gml(data_dir / "graph_main.gml")
        expected_event = nx.read_gml(data_dir / "graph_event.gml")

        combined = nx.compose(
            expected_main,
            expected_event.subgraph(set(expected_event).difference({"All"})),
        )
        combined.add_edges_from(("All", root) for root in DEFAULT_EVENT_ROOTS)
        actual_main, actual_event = partition_taxonomy(
            combined, DEFAULT_EVENT_ROOTS
        )

        self.assertEqual(set(actual_main.graph), set(expected_main))
        self.assertEqual(set(actual_main.graph.edges), set(expected_main.edges))
        self.assertEqual(set(actual_event.graph), set(expected_event))
        self.assertEqual(set(actual_event.graph.edges), set(expected_event.edges))


if __name__ == "__main__":
    unittest.main()
