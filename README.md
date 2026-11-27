# What do project layers reveal?

**Foray 342 · Graphs and representations · Essai 01 · 21 November 2026**

An independent enquiry by Lawrence Rowland into what a project model gains when stakeholders, objectives and delivery scope remain distinct but connected.

[Open the foray](https://experimentsin.ai/multilayer-project-graphs/) · [Try the first essai](https://experimentsin.ai/multilayer-project-graphs/essai-01/) · [Read the foray prompt](FORAY_PROMPT.md)

The first essai revisits Lawrence's hand-entered 2022 railway example with the latest stable Py3Plex available on 21 November 2026. It preserves selected original notebook code, commentary and data; makes corrections explicit; executes a typed multilayer model; and publishes an interactive reading of the actual results. The scenario remains deliberately simple. Later essais may introduce genuine disagreement, alternatives, time, uncertainty and evidence when those additions test a useful claim.

This repository has a new history and is not a fork of Py3Plex. Py3Plex is installed as a pinned dependency, not copied here. The original library code, caches and full fork history are excluded.

## Repeat Essai 01

Use Python 3.12. The exact tested package versions and run evidence are supplied with the analysis.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python project_graph.py
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python build_site.py
python3 -m http.server 8768 --directory _site
```

The deployment workflow repeats the model, checks and explicit static-site build. Only `_site/` is published; no Python service or user-data collection is needed for the reader.

## Source and interpretation

`sources/notebooks/` contains the three personal notebooks, with code and Markdown retained and saved outputs/execution metadata removed. Their original revision and hashes are recorded in `sources/provenance.json`. The two historical drawings already published in the main website's Library remain unchanged there. Source rows and commentary are retained separately from the curated dataset and results. The source notebooks are historical readings; their old Colab badges and tutorial dependencies have not been rewritten. `project_graph.py` is the current, tested reproduction route.

This maintained project supersedes the old fork for this personal work. This is the new maintained project, not a backup of the fork. Numerical weights in the old example have no common documented scale; the essai does not treat them as probabilities, causal effects, costs or distances. See the model method and correction ledger for the precise interpretation used in this run.

## Layout

- `FORAY_PROMPT.md`: enduring End, Ways and Means, with a bounded first essai.
- `sources/`: selected original personal material and attribution.
- `data/`: explicit layer, node and relationship grammar.
- `outputs/`: computed network, results and execution evidence.
- `METHOD-AND-RESULTS.md`: what the first run establishes and leaves open.
- `web/`: interactive reader template and local assets.
- `project_graph.py`, `tests/`: reproducible analysis and substantive checks.
- `build_site.py`: explicit public reading-copy assembly.

Py3Plex attribution and its original licence are in `sources/LICENSE-py3plex-2022.txt`. The dependency is maintained at [SkBlaz/py3plex](https://github.com/SkBlaz/py3plex).
