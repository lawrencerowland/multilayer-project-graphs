"""Rebuild the railway example from preserved notebook data and audit every change."""
from __future__ import annotations

import ast
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform

ROOT = Path(__file__).resolve().parent
SOURCE_NOTEBOOK = ROOT / "sources/notebooks/stakeholder_objectives.ipynb"
LAYERS = [
    {"id": "objectives", "label": "Objectives", "description": "The notebook's ambitions and proposed choices."},
    {"id": "stakeholders", "label": "Stakeholders", "description": "Organisations with interests in the railway scheme."},
    {"id": "scope", "label": "Scope", "description": "Work and systems that could be delivered."},
]
RELATION_TYPES = [
    {"id": "objective-association", "label": "Objective association", "layers": ["objectives", "objectives"]},
    {"id": "stakeholder-association", "label": "Stakeholder association", "layers": ["stakeholders", "stakeholders"]},
    {"id": "scope-association", "label": "Scope association", "layers": ["scope", "scope"]},
    {"id": "objective-stakeholder", "label": "Objective–stakeholder association", "layers": ["objectives", "stakeholders"]},
    {"id": "scope-objective", "label": "Scope–objective association", "layers": ["scope", "objectives"]},
    {"id": "scope-stakeholder", "label": "Scope–stakeholder association", "layers": ["scope", "stakeholders"]},
]
LABELS = {
    "sustain_carbon": "Carbon sustainability",
    "faster_trains": "Faster trains",
    "new_station": "New station",
    "New_construction_method": "New construction method",
    "Town_council": "Town council",
    "Train_Operator": "Train operator",
    "Safety_Board": "Safety board",
    "Train_manufacturer": "Train manufacturer",
    "civil_works": "Civil works",
    "new_track": "New track",
    "in_cab_signalling": "In-cab signalling",
    "new_trains": "New trains",
    "telecoms": "Telecoms",
}
ALIASES = {"Train_manfacturer": "Train_manufacturer"}
LIST_NAMES = ("objectives", "stakeholders", "scope", "inter_layer_edges")


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def original_rows(notebook: Path = SOURCE_NOTEBOOK) -> dict:
    """Read only literal lists using the AST, without executing notebook code."""
    document = json.loads(notebook.read_text())
    definitions = {}
    for cell_index, cell in enumerate(document["cells"]):
        if cell["cell_type"] != "code":
            continue
        try:
            tree = ast.parse("".join(cell["source"]))
        except SyntaxError:
            continue
        for statement in tree.body:
            if not isinstance(statement, ast.Assign) or len(statement.targets) != 1:
                continue
            target = statement.targets[0]
            if isinstance(target, ast.Name) and target.id in LIST_NAMES:
                if target.id in definitions:
                    raise ValueError(f"Repeated data definition {target.id}")
                definitions[target.id] = (cell_index + 1, ast.literal_eval(statement.value))
    if set(definitions) != set(LIST_NAMES):
        raise ValueError("The four source edge lists must all be present")
    rows = []
    for group in LIST_NAMES:
        cell_number, edges = definitions[group]
        for row_number, row in enumerate(edges, 1):
            source, source_layer, target, target_layer, weight = row
            rows.append({
                "id": f"{group}-{row_number:02d}", "list": group,
                "row": row_number, "cell": cell_number, "source": source,
                "sourceLayer": source_layer, "target": target,
                "targetLayer": target_layer, "weight": weight,
            })
    return {
        "sourceNotebook": "sources/notebooks/stakeholder_objectives.ipynb",
        "sourceCommit": "9bdfca4aa40a5115e8697fbd64e67347dc7a0a9a",
        "originalRuntime": {"directed": True, "parallelEdges": True,
                            "basis": "The 2022 multi_layer_network constructor defaults to directed=True and creates a NetworkX MultiDiGraph."},
        "rows": rows,
    }


def curate(original: dict) -> dict:
    """Correct an alias and exact repeat while retaining direction and conflicts."""
    nodes = {}
    grouped = defaultdict(list)
    for row in original["rows"]:
        ends = []
        for side in ("source", "target"):
            source_name = row[side]
            node_id = ALIASES.get(source_name, source_name)
            layer = row[side + "Layer"]
            node = nodes.setdefault(node_id, {
                "id": node_id, "label": LABELS[node_id], "layer": layer,
                "type": {"objectives": "objective", "stakeholders": "stakeholder", "scope": "scope"}[layer],
                "sourceName": node_id, "originalNames": [],
                "summary": f"{LABELS[node_id]} in the notebook’s {layer} layer.",
            })
            if node["layer"] != layer:
                raise ValueError(f"Node {node_id} appears in multiple layers")
            if source_name not in node["originalNames"]:
                node["originalNames"].append(source_name)
            ends.append(node_id)
        grouped[tuple(ends)].append(row)
    relation_lookup = {tuple(item["layers"]): item for item in RELATION_TYPES}
    edges = []
    for number, ((source, target), rows) in enumerate(sorted(grouped.items()), 1):
        weights = sorted(set(row["weight"] for row in rows))
        relation = relation_lookup[(nodes[source]["layer"], nodes[target]["layer"])]
        edges.append({
            "id": f"edge-{number:02d}", "source": source, "target": target,
            "relation": relation["id"], "label": relation["label"],
            "directed": True, "weight": weights[0] if len(weights) == 1 else None,
            "sourceWeights": weights,
            "weightStatus": "conflicting" if len(weights) > 1 else "unvalidated",
            "sourceRows": [row["id"] for row in rows],
            "provenance": "Original notebook edge lists",
            "interpretation": "Recorded direction is preserved; its project meaning is undocumented. The relation label classifies the endpoint layers.",
        })
    edge_records = []
    for edge in edges:
        for weight in edge["sourceWeights"]:
            rows = [row for row in original["rows"] if row["id"] in edge["sourceRows"] and row["weight"] == weight]
            edge_records.append({"id": f"record-{len(edge_records) + 1:02d}", "edgeId": edge["id"],
                                 "source": edge["source"], "target": edge["target"],
                                 "relation": edge["relation"], "weight": weight, "directed": True,
                                 "sourceRows": [row["id"] for row in rows]})
    data = {
        "meta": {
            "title": "A railway project through three layers",
            "subtitle": "Trace how objectives, stakeholders and scope connect.",
            "sourceDate": "2022-10-17", "editionDate": "2026-11-21",
            "networkType": "multilayer", "directed": True,
            "nodeIdentity": "Each entity belongs to exactly one layer. Explicit edges connect different entities across layers.",
            "weightPolicy": "Every distinct original weight is retained. Their units and scale were not defined. The conflicting parallel records remain separate in the runtime graph. Topological metrics ignore their weights.",
            "pathPolicy": "Directed routes follow the recorded orientation. Connected-neighbour views explicitly ignore orientation. Neither establishes causation, delivery sequence or responsibility. Source weights are never treated as distances or probabilities.",
            "scopeNote": "This is a small hand-entered teaching example. The notebook groups aspirations and proposed choices together in the objectives layer.",
            "directionPolicy": "The original code created directed parallel edges. Both the original reconstruction and corrected runtime preserve that orientation. Arrowheads mean recorded direction; their project meaning remains undocumented.",
        },
        "layers": deepcopy(LAYERS), "nodes": list(nodes.values()), "edges": edges, "edgeRecords": edge_records,
        "relationTypes": deepcopy(RELATION_TYPES),
        "corrections": [
            {"id": "manufacturer-alias", "title": "One manufacturer", "detail": "Train_manfacturer is treated as a spelling variant of Train_manufacturer. Both names remain in the original extract.", "sourceRows": ["inter_layer_edges-11"]},
            {"id": "repeated-trains-objective", "title": "One repeated association", "detail": "The identical new_trains → faster_trains row with weight 0.9 occurs twice. It counts as one association.", "sourceRows": ["inter_layer_edges-05", "inter_layer_edges-09"]},
            {"id": "conflicting-trains-safety", "title": "An unresolved weight", "detail": "New trains → safety board occurs with weights 0.7 and 0.9. Both values are retained and neither is selected as authoritative.", "sourceRows": ["inter_layer_edges-10", "inter_layer_edges-15"]},
            {"id": "recorded-direction", "title": "Recorded direction preserved", "detail": "The runtime retains directed parallel records. The display bundles records with the same endpoints and exposes each value in the inspector. An undirected projection is used only for explicitly labelled connected-neighbour exploration."},
        ],
        "sources": [
            {"id": "notebook", "title": "Original personal notebook", "path": "sources/notebooks/stakeholder_objectives.ipynb"},
            {"id": "rows", "title": "All 27 original edge records", "path": "data/original-extract.json"},
            {"id": "commentary", "title": "Original comments and Markdown", "path": "sources/commentary.md"},
            {"id": "provenance", "title": "Source hashes and publication edits", "path": "sources/provenance.json"},
        ],
    }
    validate(data)
    return data


def validate(data: dict) -> None:
    """Reject layer leakage, invalid relation pairs and silently duplicated edges."""
    layers = {layer["id"] for layer in data["layers"]}
    node_ids = [node["id"] for node in data["nodes"]]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError("Node IDs must be unique and belong to one layer")
    nodes = {node["id"]: node for node in data["nodes"]}
    if any(node["layer"] not in layers for node in nodes.values()):
        raise ValueError("Unknown node layer")
    relations = {relation["id"]: relation for relation in data["relationTypes"]}
    seen = set()
    for edge in data["edges"]:
        if edge["source"] not in nodes or edge["target"] not in nodes:
            raise ValueError("Edge endpoint is absent")
        pair = (edge["source"], edge["target"])
        if pair in seen or pair[0] == pair[1]:
            raise ValueError("Canonical associations must be distinct and connect two different nodes")
        seen.add(pair)
        relation = relations.get(edge["relation"])
        endpoint_layers = [nodes[end]["layer"] for end in (edge["source"], edge["target"])]
        if relation is None or relation["layers"] != endpoint_layers:
            raise ValueError("Relation is invalid for these endpoint layers")
        if not edge["directed"]:
            raise ValueError("This edition preserves recorded direction")
        if not edge["sourceRows"]:
            raise ValueError("Every edge needs source rows")
        if edge["weightStatus"] == "conflicting" and edge["weight"] is not None:
            raise ValueError("A conflicting source weight must remain unresolved")
    edge_index = {edge["id"]: edge for edge in data["edges"]}
    seen_records = set()
    for record in data["edgeRecords"]:
        edge = edge_index.get(record["edgeId"])
        signature = (record["source"], record["target"], record["weight"])
        if edge is None or signature in seen_records:
            raise ValueError("Edge records must be unique and belong to a display edge")
        seen_records.add(signature)
        if any(record[key] != edge[key] for key in ("source", "target", "relation", "directed")):
            raise ValueError("Edge record disagrees with its display edge")
        if record["weight"] not in edge["sourceWeights"]:
            raise ValueError("Edge record weight is absent from its source")


def build_network(data: dict):
    from py3plex.core import multinet

    validate(data)
    network = multinet.multi_layer_network(network_type="multilayer", directed=True, verbose=False)
    nodes = {node["id"]: node for node in data["nodes"]}
    network.add_nodes([{"source": node["id"], "type": node["layer"], "label": node["label"]}
                       for node in data["nodes"]], input_type="dict")
    for edge in data["edgeRecords"]:
        network.add_edges([{
            "source": edge["source"], "target": edge["target"],
            "source_type": nodes[edge["source"]]["layer"],
            "target_type": nodes[edge["target"]]["layer"],
            "type": edge["relation"], "weight": edge["weight"], "edge_id": edge["id"],
        }], input_type="dict")
    expected_nodes = {(node["id"], node["layer"]) for node in data["nodes"]}
    actual_nodes = set(network.core_network.nodes)
    expected_edges = {((edge["source"], nodes[edge["source"]]["layer"]),
                      (edge["target"], nodes[edge["target"]]["layer"]))
                      for edge in data["edges"]}
    actual_edges = set(network.core_network.edges())
    if actual_nodes != expected_nodes or actual_edges != expected_edges:
        raise ValueError("The runtime graph changed the declared node or edge set")
    if network.core_network.number_of_edges() != len(data["edgeRecords"]):
        raise ValueError("Unexpected parallel or automatically generated edges")
    return network


def reconstruct_original(original: dict):
    """Reconstruct all original rows with their direction and parallel records."""
    from py3plex.core import multinet

    network = multinet.multi_layer_network(network_type="multilayer", directed=True, verbose=False)
    rows = [[row["source"], row["sourceLayer"], row["target"], row["targetLayer"], row["weight"]]
            for row in original["rows"]]
    network.add_edges(rows, input_type="list")
    expected = Counter((row[0], row[1], row[2], row[3], row[4]) for row in rows)
    actual = Counter((source[0], source[1], target[0], target[1], attrs["weight"])
                     for source, target, attrs in network.core_network.edges(data=True))
    if actual != expected:
        raise ValueError("Original reconstruction changed row multiplicity, orientation or weight")
    return network


def analyze(data: dict, network) -> dict:
    import networkx as nx

    directed_graph = nx.DiGraph(network.core_network)
    graph = nx.Graph(directed_graph)
    result = deepcopy(data)
    for node in result["nodes"]:
        key = (node["id"], node["layer"])
        neighbours = list(graph.neighbors(key))
        node["degree"] = len(neighbours)
        node["inDegree"] = directed_graph.in_degree(key)
        node["outDegree"] = directed_graph.out_degree(key)
        node["crossLayerDegree"] = sum(layer != node["layer"] for _, layer in neighbours)
        node["bridgedLayers"] = sorted({layer for _, layer in neighbours if layer != node["layer"]})
        node["neighbours"] = sorted(name for name, _ in neighbours)
    layer_counts = []
    for layer in LAYERS:
        ids = {(node["id"], node["layer"]) for node in data["nodes"] if node["layer"] == layer["id"]}
        subgraph = graph.subgraph(ids)
        layer_counts.append({"id": layer["id"], "label": layer["label"], "nodes": len(ids),
                             "intralayerEdges": subgraph.number_of_edges(),
                             "density": nx.density(subgraph),
                             "densityProjection": "simple-undirected",
                             "directedDensity": nx.density(directed_graph.subgraph(ids))})
    relation_counts = Counter(edge["relation"] for edge in data["edges"])
    cross_edges = sum(source[1] != target[1] for source, target in graph.edges)
    result["metrics"] = {
        "nodeCount": graph.number_of_nodes(), "edgeCount": network.core_network.number_of_edges(),
        "associationCount": directed_graph.number_of_edges(),
        "layerCount": len(LAYERS), "componentCount": nx.number_connected_components(graph),
        "crossLayerEdges": cross_edges, "intralayerEdges": graph.number_of_edges() - cross_edges,
        "isolatedNodeCount": len(list(nx.isolates(graph))), "density": nx.density(graph),
        "densityProjection": "simple-undirected", "directedDensity": nx.density(directed_graph),
        "originalNodeCount": 14, "originalEdgeRecords": 27,
        "conflictingWeightEdges": sum(edge["weightStatus"] == "conflicting" for edge in data["edges"]),
        "layerCounts": layer_counts, "relationCounts": dict(relation_counts),
        "degreeRanking": [{"id": node["id"], "label": node["label"], "degree": node["degree"],
                           "crossLayerDegree": node["crossLayerDegree"]}
                          for node in sorted(result["nodes"], key=lambda node: (-node["degree"], node["id"]))],
        "analysisPolicy": "Runtime edge count includes distinct parallel records. Degree, cross-layer counts and density use distinct endpoint pairs. Connected degree uses an explicit undirected projection; in/out degree uses recorded direction. All metrics exclude source weights.",
        "metricDefinitions": {
            "edgeCount": "Directed MultiDiGraph records, including the two conflicting safety weights.",
            "associationCount": "Simple directed graph: distinct ordered endpoint pairs; parallel records collapsed.",
            "componentCount": "Connected components of the simple undirected projection (weak components of the directed graph).",
            "crossLayerEdges": "Simple undirected projection: distinct endpoint pairs in different layers.",
            "intralayerEdges": "Simple undirected projection: distinct endpoint pairs in the same layer.",
            "isolatedNodeCount": "Simple undirected projection: nodes with no incident edges.",
            "density": "Simple undirected projection: m / (n * (n - 1) / 2), ignoring weights and parallel records.",
            "directedDensity": "Simple directed graph: m / (n * (n - 1)), ignoring weights and parallel records.",
            "degreeRanking": "Simple undirected projection: number of distinct adjacent entities, regardless of orientation.",
            "layerCounts": "Each layer's induced simple undirected subgraph; directedDensity uses its simple directed counterpart.",
            "relationCounts": "Simple directed graph: display pairs grouped by their endpoint-layer relation.",
            "node.inDegree": "Distinct predecessors in the simple directed graph.",
            "node.outDegree": "Distinct successors in the simple directed graph.",
            "node.degree": "Distinct neighbours in the simple undirected projection.",
            "node.crossLayerDegree": "Distinct neighbours in other layers in the simple undirected projection.",
        },
    }
    return result


def compute_findings(original: dict, data: dict, network) -> dict:
    """Compute queries in the runtime graph, then check against literal source rows."""
    import networkx as nx

    graph = nx.relabel_nodes(nx.DiGraph(network.core_network), {key: key[0] for key in network.core_network})
    undirected = nx.Graph(graph)
    source_pairs = defaultdict(list)
    for row in original["rows"]:
        pair = tuple(ALIASES.get(row[end], row[end]) for end in ("source", "target"))
        source_pairs[pair].append(row)
    # Independent source-list adjacency establishes that the library queries did
    # not reverse directions, introduce coupling, or drop a source connection.
    expected_pairs = set(source_pairs)
    if set(graph.edges) != expected_pairs:
        raise ValueError("Query graph disagrees with original source-list orientation")

    def neighbourhood(node_id):
        incoming = sorted(graph.predecessors(node_id))
        outgoing = sorted(graph.successors(node_id))
        adjacent = sorted(undirected.neighbors(node_id))
        if incoming != sorted(a for a, b in expected_pairs if b == node_id):
            raise ValueError("Incoming query differs from source rows")
        if outgoing != sorted(b for a, b in expected_pairs if a == node_id):
            raise ValueError("Outgoing query differs from source rows")
        if adjacent != sorted(set(incoming + outgoing)):
            raise ValueError("Undirected neighbourhood differs from source rows")
        return {"incoming": incoming, "outgoing": outgoing, "undirectedNeighbours": adjacent}

    station = neighbourhood("new_station")
    station["sourceRows"] = sorted(row["id"] for pair, rows in source_pairs.items()
                                  if "new_station" in pair for row in rows)
    path = ["new_track", "sustain_carbon", "Town_council"]
    steps = [{"source": a, "target": b,
              "sourceRows": [row["id"] for row in source_pairs[(a, b)]]}
             for a, b in zip(path, path[1:])]
    if not all(graph.has_edge(step["source"], step["target"]) and step["sourceRows"] for step in steps):
        raise ValueError("The two-step route is not supported by source rows")
    directed_distance = nx.shortest_path_length(graph, path[0], path[-1])
    reverse_reachable = nx.has_path(graph, path[-1], path[0])
    reverse_undirected_distance = nx.shortest_path_length(undirected, path[-1], path[0])
    # Independent set expansion checks the two-hop claim without using a second
    # library traversal of the same graph.
    first_step = {b for a, b in expected_pairs if a == path[0]}
    second_step = {b for a, b in expected_pairs if a in first_step}
    if path[-1] not in second_step or path[-1] in first_step or directed_distance != 2:
        raise ValueError("Two-hop result disagrees with source-list expansion")
    reverse_seen, frontier = {path[-1]}, {path[-1]}
    while frontier:
        frontier = {b for a, b in expected_pairs if a in frontier} - reverse_seen
        reverse_seen |= frontier
    if reverse_reachable != (path[0] in reverse_seen):
        raise ValueError("Reverse reachability disagrees with source-list expansion")

    safety_rows = source_pairs[("new_trains", "Safety_Board")]
    runtime_safety = network.core_network.get_edge_data(("new_trains", "scope"), ("Safety_Board", "stakeholders"))
    values = sorted(attrs["weight"] for attrs in runtime_safety.values())
    if values != sorted(row["weight"] for row in safety_rows):
        raise ValueError("Safety query discarded a conflicting record")
    return {
        "title": "Three queries that distinguish the model from its picture",
        "verifiedDate": "2026-11-21", "independentlyCheckedAgainstSourceRows": True,
        "weightPolicy": "Queries are unweighted. A hop counts one recorded connection; it is not a cost, probability, time or causal effect.",
        "queries": [
            {"id": "station-direction", "title": "What connects to the new station?", "node": "new_station",
             "result": station,
             "finding": "The new station has three incoming connections and no outgoing connection. Ignoring direction reveals its three neighbours, but does not create three supported outward routes."},
            {"id": "track-carbon-council", "title": "Can the recorded arrows connect new track to the town council?",
             "result": {"directedPath": path, "steps": steps, "directedDistance": directed_distance,
                        "reverseDirectedReachable": reverse_reachable,
                        "reverseUndirectedDistance": reverse_undirected_distance},
             "finding": "A two-hop recorded route passes from new track through carbon sustainability to the town council. No directed return route exists. The undirected projection allows the return in two hops; that is a change in the question, not new project evidence."},
            {"id": "safety-parallel-records", "title": "How many records connect new trains to the safety board?",
             "result": {"source": "new_trains", "target": "Safety_Board", "runtimeRecordCount": len(runtime_safety),
                        "displayConnectionCount": 1, "weights": values,
                        "sourceRows": [row["id"] for row in safety_rows], "resolvedWeight": None},
             "finding": "Two directed records carry conflicting weights, 0.7 and 0.9. The display draws one connection and retains both records in its inspector. A simple graph on its own loses their multiplicity."},
        ],
        "representations": [
            {"id": "runtime", "label": "Directed multilayer runtime", "nodes": network.core_network.number_of_nodes(),
             "records": network.core_network.number_of_edges(), "layersRetained": True,
             "directionRetained": True, "parallelRecordsRetained": True},
            {"id": "flat-display", "label": "Flat drawing", "nodes": len(data["nodes"]), "records": len(data["edgeRecords"]),
             "drawnConnections": len(data["edges"]), "layersRetained": True,
             "directionRetained": True, "parallelRecordsRetained": True,
             "change": "Only node positions and layer grouping on screen change; the same data, arrows and inspector remain."},
            {"id": "simple-directed", "label": "Simple directed analysis", "nodes": graph.number_of_nodes(),
             "connections": graph.number_of_edges(), "directionRetained": True, "parallelRecordsRetained": False,
             "change": "Parallel records collapse to one ordered pair; source weights are excluded from analysis."},
            {"id": "simple-undirected", "label": "Undirected neighbourhood projection", "nodes": undirected.number_of_nodes(),
             "connections": undirected.number_of_edges(), "directionRetained": False, "parallelRecordsRetained": False,
             "change": "Directions and parallel multiplicity are discarded; node layer labels remain available."},
        ],
    }


def write_findings_markdown(findings: dict, metrics: dict) -> None:
    station, route, safety = [item["result"] for item in findings["queries"]]
    text = f"""# What changed when we ran the railway model?

The original lists were reconstructed in py3plex 2.0.93 as **14 entities and 27 directed records**. Correcting one manufacturer spelling and one exactly repeated row gives **13 entities and 26 directed records**, shown as **25 connections**. All 27 source rows remain traceable. The two different new-trains/safety-board weights remain separate.

## Three computed observations

1. **The new station is an endpoint, not a starting point.** Its incoming neighbours are civil works, carbon sustainability and faster trains. It has **{len(station['outgoing'])} outgoing connections**. An undirected neighbourhood query returns all three, but those are not supported outward routes. Source rows: {', '.join('`' + value + '`' for value in station['sourceRows'])}.
2. **A recorded route crosses all three layers.** New track → carbon sustainability → town council is an unweighted **{route['directedDistance']}-hop route**. There is no directed return route. Ignoring direction makes the return possible in {route['reverseUndirectedDistance']} hops. This difference is produced by the projection; it supplies no extra evidence about authority, causation or delivery. Source rows: {', '.join('`' + row + '`' for step in route['steps'] for row in step['sourceRows'])}.
3. **One line can stand for two unresolved records.** New trains → safety board has **{safety['runtimeRecordCount']} records**, carrying **0.7 and 0.9**. The picture bundles them as one connection, while the inspector and runtime retain both. Selecting or averaging a weight would add an unsupported judgement. Source rows: {', '.join('`' + value + '`' for value in safety['sourceRows'])}.

These queries were computed from the running graph and checked independently against adjacency sets and row values extracted from the notebook. The two-hop result was also checked by direct expansion of those source lists. See the complete [machine-readable findings](outputs/findings.json) and [27 original rows](data/original-extract.json).

## What “flat” does and does not mean

The interactive **flat drawing changes placement only**. It keeps the same entities, layer labels, arrows, original rows and inspector. It is a comparison of visual organisation, not a different network and not evidence that layering changes an algorithm's answer.

The **simple directed analysis** really is a projection: parallel records become one ordered endpoint pair, reducing 26 records to 25 connections. The **undirected neighbourhood projection** additionally forgets orientation. It retains 25 connections here because this example has no reciprocal pair, but its permitted routes differ, as the new-station and town-council queries show. Neither projection uses the source weights.

## Method and limits

This is a heterogeneous multilayer network: each stakeholder, objective or scope item belongs to exactly one layer. It is not a multiplex containing replicas of the same entity in every layer. No automatic identity-coupling edges are added. A schema checks each relation's source and target layers and preserves the recorded orientation. Relation names classify the endpoint layers; the notebook does not establish their business meaning.

The original 2022 constructor defaulted to a directed graph with parallel edges. The fresh reconstruction explicitly requests that behaviour and checks every endpoint, layer, orientation, weight and repeated row. The corrected graph makes only the declared alias and exact-repeat changes. The original authored notebook code and commentary remain in [sources](sources/commentary.md); historical outputs and incidental metadata were removed before publication. The old exploratory notebooks are source material, not a claim that every cell now runs.

There are **{metrics['crossLayerEdges']} cross-layer pairs**, **{metrics['intralayerEdges']} within-layer pairs**, and **{metrics['componentCount']} weakly connected component**. The simple directed density is **{metrics['directedDensity']:.4f}** (25 of 156 possible ordered pairs). The simple undirected density is **{metrics['density']:.4f}** (25 of 78 possible unordered pairs). These are different denominators, not a change in the evidence. Each [metric](outputs/metrics.json) names its projection.

The weights have no established common unit: objective rows include 5, 7 and 10, while other rows use values between 0.1 and 1. They are preserved as source data, never treated as distances, probabilities or comparable strengths. No weighted path, benefit ranking, responsibility allocation or causal conclusion is justified by this run. The result is a reproducible small example for asking which relationships need clarification.

## Reproduce

Use Python 3.12 in a new virtual environment, install `requirements-lock.txt`, then run `python project_graph.py` and `python -m unittest discover -s tests -v`. The verified environment was Python 3.12.14, py3plex 2.0.93, NetworkX 3.7 and Matplotlib 3.11.2. The [runtime receipt](outputs/runtime-receipt.json) records the successful graph checks and package versions. Release verification and source hashes are in [provenance](sources/provenance.json).
"""
    (ROOT / "METHOD-AND-RESULTS.md").write_text(text)


def plot_network(data: dict, destination: Path) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch

    colors = {"objectives": "#28705e", "stakeholders": "#966043", "scope": "#4d6395"}
    positions = {}
    fig, ax = plt.subplots(figsize=(12, 7.5))
    fig.patch.set_facecolor("#f7f5ef")
    ax.set_facecolor("#f7f5ef")
    for index, layer in enumerate(LAYERS):
        nodes = [node for node in data["nodes"] if node["layer"] == layer["id"]]
        x = index * 2.4
        ax.axvspan(x - 0.82, x + 0.82, color=colors[layer["id"]], alpha=0.055)
        ax.text(x, 5.9, layer["label"], ha="center", fontsize=16, color=colors[layer["id"]], weight="bold")
        for row, node in enumerate(nodes):
            positions[node["id"]] = (x, 5.15 - row * 1.03)
    for edge in data["edges"]:
        start, end = positions[edge["source"]], positions[edge["target"]]
        same_layer = start[0] == end[0]
        curve = 0.24 if same_layer else 0
        style = "--" if edge["weightStatus"] == "conflicting" else "-"
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=10, shrinkA=8, shrinkB=8, connectionstyle=f"arc3,rad={curve}",
                                     linewidth=1.1, color="#83908b", alpha=0.55, linestyle=style, zorder=1))
    for node in data["nodes"]:
        x, y = positions[node["id"]]
        ax.scatter([x], [y], s=180, color=colors[node["layer"]], edgecolors="white", linewidths=1.6, zorder=3)
        ax.text(x, y - 0.26, node["label"], ha="center", va="top", fontsize=10, zorder=4,
                bbox={"facecolor": "#f7f5ef", "edgecolor": "none", "pad": 1.5, "alpha": 0.95})
    ax.set_title("A railway project through three layers", loc="left", fontsize=22, color="#173b33", pad=28)
    fig.text(0.055, 0.055, "13 entities · 26 records shown as 25 connections · Arrowheads retain recorded direction", fontsize=10, color="#44564f")
    fig.text(0.055, 0.028, "Project meaning and weight scales remain unvalidated. Dashed connection has parallel weights 0.7 and 0.9.", fontsize=9, color="#44564f")
    ax.set_xlim(-1.1, 5.9)
    ax.set_ylim(0.3, 6.1)
    ax.axis("off")
    fig.subplots_adjust(left=0.055, right=0.98, top=0.84, bottom=0.13)
    fig.savefig(destination / "railway-three-layers.svg", facecolor=fig.get_facecolor())
    fig.savefig(destination / "railway-three-layers.png", dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> None:
    os.environ.setdefault("MPLCONFIGDIR", str(ROOT / ".cache/matplotlib"))
    original = original_rows()
    data = curate(original)
    write_json(ROOT / "data/original-extract.json", original)
    write_json(ROOT / "data/railway-project.json", data)
    original_network = reconstruct_original(original)
    network = build_network(data)
    result = analyze(data, network)
    write_json(ROOT / "outputs/network.json", result)
    write_json(ROOT / "outputs/metrics.json", result["metrics"])
    findings = compute_findings(original, data, network)
    write_json(ROOT / "outputs/findings.json", findings)
    write_findings_markdown(findings, result["metrics"])
    plot_network(result, ROOT / "outputs")
    packages = {name: importlib.metadata.version(name) for name in ("py3plex", "networkx", "matplotlib", "numpy", "scipy")}
    receipt = {
        "verifiedDate": "2026-11-21", "python": platform.python_version(), "packages": packages,
        "source": "https://pypi.org/project/py3plex/2.0.93/", "networkType": network.network_type,
        "runtimeGraphClass": type(network.core_network).__name__, "directed": network.core_network.is_directed(),
        "nodeCount": network.core_network.number_of_nodes(), "edgeCount": network.core_network.number_of_edges(),
        "displayConnectionCount": len(data["edges"]),
        "originalReconstruction": {"nodeCount": original_network.core_network.number_of_nodes(),
                                   "edgeCount": original_network.core_network.number_of_edges(),
                                   "directed": original_network.core_network.is_directed(),
                                   "allRowsWeightsAndDirectionsVerified": True},
        "automaticCouplingEdges": 0, "sourceNodeAndEdgeSetsVerified": True,
        "sourceCheckedQueryCount": len(findings["queries"]),
        "datasetSha256": hashlib.sha256((ROOT / "data/railway-project.json").read_bytes()).hexdigest(),
    }
    write_json(ROOT / "outputs/runtime-receipt.json", receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
