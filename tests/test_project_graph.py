"""Regression checks for the modelling choices that affect this example."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
import os
import unittest

import project_graph as model

os.environ.setdefault("MPLCONFIGDIR", str(model.ROOT / ".cache/matplotlib"))


class ProjectGraphTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = model.original_rows()
        cls.data = model.curate(cls.original)
        cls.network = model.build_network(cls.data)

    def test_original_reconstruction_retains_parallel_records_and_direction(self):
        network = model.reconstruct_original(self.original)
        self.assertTrue(network.core_network.is_directed())
        self.assertEqual(network.core_network.number_of_nodes(), 14)
        self.assertEqual(network.core_network.number_of_edges(), 27)
        pair = network.core_network.get_edge_data(("new_trains", "scope"), ("Safety_Board", "stakeholders"))
        self.assertEqual(sorted(item["weight"] for item in pair.values()), [0.7, 0.9])

    def test_corrections_preserve_all_source_rows_and_conflicting_weights(self):
        self.assertEqual(len(self.data["nodes"]), 13)
        self.assertEqual(len(self.data["edgeRecords"]), 26)
        self.assertEqual(len(self.data["edges"]), 25)
        references = [row for record in self.data["edgeRecords"] for row in record["sourceRows"]]
        self.assertEqual(Counter(references), Counter(row["id"] for row in self.original["rows"]))
        conflict = next(edge for edge in self.data["edges"] if edge["weightStatus"] == "conflicting")
        self.assertIsNone(conflict["weight"])
        self.assertEqual(conflict["sourceWeights"], [0.7, 0.9])
        pair = self.network.core_network.get_edge_data(("new_trains", "scope"), ("Safety_Board", "stakeholders"))
        self.assertEqual(sorted(item["weight"] for item in pair.values()), [0.7, 0.9])

    def test_disjoint_layers_have_only_explicit_cross_layer_links(self):
        graph = self.network.core_network
        self.assertEqual(graph.number_of_nodes(), 13)
        self.assertEqual(graph.number_of_edges(), 26)
        self.assertEqual(len({node_id for node_id, _ in graph}), 13)
        self.assertFalse(any(source[0] == target[0] for source, target in graph.edges()))
        self.assertFalse(any(attrs.get("type") == "coupling" for _, _, attrs in graph.edges(data=True)))

    def test_schema_rejects_wrong_layer_relation_and_direction(self):
        wrong_relation = deepcopy(self.data)
        wrong_relation["edges"][0]["relation"] = "scope-stakeholder"
        with self.assertRaisesRegex(ValueError, "Relation is invalid"):
            model.validate(wrong_relation)
        wrong_layer = deepcopy(self.data)
        wrong_layer["nodes"][0]["layer"] = "unrecognised"
        with self.assertRaisesRegex(ValueError, "Unknown node layer"):
            model.validate(wrong_layer)
        reversed_record = deepcopy(self.data)
        record = reversed_record["edgeRecords"][0]
        record["source"], record["target"] = record["target"], record["source"]
        with self.assertRaisesRegex(ValueError, "disagrees"):
            model.validate(reversed_record)

    def test_topological_metrics_ignore_source_weight_values(self):
        baseline = model.analyze(self.data, self.network)["metrics"]
        graph = self.network.core_network
        saved = [attributes["weight"] for _, _, attributes in graph.edges(data=True)]
        for _, _, attributes in graph.edges(data=True):
            attributes["weight"] = 9999
        self.assertEqual(model.analyze(self.data, self.network)["metrics"], baseline)
        for (_, _, attributes), weight in zip(graph.edges(data=True), saved):
            attributes["weight"] = weight

    def test_queries_distinguish_recorded_routes_and_undirected_neighbours(self):
        findings = model.compute_findings(self.original, self.data, self.network)
        station, route, safety = [query["result"] for query in findings["queries"]]
        self.assertEqual(station["incoming"], ["civil_works", "faster_trains", "sustain_carbon"])
        self.assertEqual(station["outgoing"], [])
        self.assertEqual(station["undirectedNeighbours"], station["incoming"])
        self.assertEqual(route["directedPath"], ["new_track", "sustain_carbon", "Town_council"])
        self.assertEqual(route["directedDistance"], 2)
        self.assertFalse(route["reverseDirectedReachable"])
        self.assertEqual(route["reverseUndirectedDistance"], 2)
        self.assertEqual(safety["weights"], [0.7, 0.9])
        self.assertEqual(safety["runtimeRecordCount"], 2)
        self.assertIsNone(safety["resolvedWeight"])
        metrics = model.analyze(self.data, self.network)["metrics"]
        self.assertAlmostEqual(metrics["directedDensity"], 25 / (13 * 12))
        self.assertAlmostEqual(metrics["density"], 25 / (13 * 12 / 2))

    def test_source_notebooks_retain_authored_cells_after_output_cleanup(self):
        provenance = json.loads((model.ROOT / "sources/provenance.json").read_text())
        for record in provenance["files"]:
            path = model.ROOT / record["path"]
            if path.suffix != ".ipynb" or record.get("retained") is False:
                continue
            document = json.loads(path.read_text())
            cells = [[cell["cell_type"], "".join(cell.get("source", []))] for cell in document["cells"]]
            digest = hashlib.sha256(json.dumps(cells, ensure_ascii=False).encode()).hexdigest()
            self.assertEqual(digest, record["sourceCellsSha256"])
            self.assertFalse(any(cell.get("outputs") for cell in document["cells"]))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["publishedSha256"])


if __name__ == "__main__":
    unittest.main()
