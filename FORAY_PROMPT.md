# Foray 342 — What do project layers reveal?

Established: 21 November 2026  
Status: first essai published and checked. The wider End remains open.  
PW-ID: `PW-342`  
Foray-ID: `FORAY-342-PROJECT-LAYERS`  
Primary level: Level 1 — improving what practitioners can inspect, question and choose about a project through its connected representations.

## End

Discover what a typed, multilayer representation lets a practitioner understand or do that is difficult, misleading or unavailable when a project is flattened into one network, list or diagram. Develop representations and operations that keep meaningful distinctions between entities, relationships and views while making their connections inspectable.

The aim is not to draw every project as a multilayer graph. When do layers expose a consequential dependency, missing explanation, conflicting interpretation or choice? When does separating them hide something important? What must survive a change of view for an answer to remain warranted? A useful result may be a new operation, a counterexample, a disciplined way to connect views, or evidence that a simpler representation is sufficient.

## Rationale

Lawrence's 2022 rail notebook connects objectives, stakeholders and scope using py3plex. It asks a durable practical question: how can these different kinds of project information stay distinct while their relationships remain visible? Its handwritten links and commentary are a starting point for enquiry, not validated evidence about a real railway.

The example also exposes choices that a picture alone can conceal: the identity of an entity, the meaning and direction of an edge, repeated records, weights with different scales, and the information removed by a restricted view. Making those choices explicit can turn an appealing diagram into an account that someone can question and compare.

## Relationship to other forays

341 preserves work on higher-dimensional graphs; 360 concerns alternate perspectives. 365 asks how representational form affects reasoning and judgement. 355 asks when a model is adequate for a declared purpose, while 245 investigates useful abstraction layers. The Functors collection explores relationships between mathematical descriptions of projects.

342 has its own question: what becomes inspectable or actionable when distinct project relations are connected through explicit layers, and what is lost when they are collapsed or filtered? It can draw on those enquiries without taking over their Ends. A correct graph query is not evidence that a picture improves human judgement; a useful cross-layer path is not automatically a causal explanation or a construction plan.

## Ways — make the distinctions and their consequences inspectable

Choose and combine methods that test the End. Begin with an explicit grammar: what counts as an entity, which layer it occupies, what each relationship means, whether it is directed, and how repeated or uncertain assertions are represented. Separate an entity's identity from a label and distinguish a layer of entity types from multiple relations among the same entities. Do not call every layered picture a multiplex without checking that its structure fits that term.

Audit the source before improving it. Preserve an inspectable route from original commentary and data to a declared interpretation, then to each computed answer. When correcting a spelling or collapsing a repeated record, say exactly what changed and why. Retaining a number is not the same as establishing its units, comparability or evidential meaning.

Compare representations through questions that could distinguish them: a typed path across layers, the relationships retained by a restricted view, or an answer that changes after direction, parallel records or types are discarded. Use small, explicit examples and independently checked computations where those give a clearer test than a large demonstration. Distinguish a lossy projection from a display that keeps all the information but makes it harder to see.

Later essais may introduce richer rail situations, other project settings, changes over time, evidence and disagreement, stakeholder choices, or alternative layer grammars. Add realism when it tests a claim or enables a previously missing operation. The first dataset and software library do not determine the limits of the enquiry. Comparisons with simpler tools or other formalisms remain open.

## First essai — a project in connected layers

Use a pinned py3plex 2.0.93 environment to execute a contemporary analysis of the rail notebook's original material. Retain its 14 distinct names and 27 directed edge records as the historical account. Keep its code and Markdown commentary unchanged in the preserved notebook source; identify the removal of saved execution outputs explicitly. The two original rail pictures remain available in the existing Library guide.

The first checked run makes a separate, declared analytical interpretation: reconcile the misspelled train-manufacturer identity and remove one exactly repeated row. This gives 13 entities and 26 directed records, displayed as 25 distinct ordered endpoint pairs. All 27 original source rows remain traceable. The two different new-trains-to-safety-board weights remain separate records within one displayed connection. Keep those records and weights available for inspection; explain what any simple-graph projection retains and discards. The original weights have no documented common scale and must not become probabilities, a stakeholder-priority score or an investment ranking by assumption.

An interactive public reading copy should let a reader inspect the layers, follow named connections, change the view, and see the corresponding result or omission. Explain the original data, interpretation choices, computed findings and limits in ordinary project language. The accompanying source and reproduction route should let another reader check those findings. This is the first bounded attempt, not completion of the End.

## Means and explanatory route

The independent repository is [multilayer-project-graphs](https://github.com/lawrencerowland/multilayer-project-graphs); its public entrance is [the foray](https://experimentsin.ai/multilayer-project-graphs/) with [Essai 01](https://experimentsin.ai/multilayer-project-graphs/essai-01/). Publication status is established by the deployment and ordinary-reader checks, separately from source preparation.

Use Lawrence's original notebook data and commentary, the retained [Library guide](https://experimentsin.ai/library/models/rail-stakeholders-objectives-scope.html), and the current [py3plex source and documentation](https://github.com/SkBlaz/py3plex). Read the relevant implementations and primary methods when relying on an algorithm. Attribute the upstream tool separately from Lawrence's example and our new interpretation; preserve applicable notices.

Keep a source → concept → construction → limitation route on the normal entrance. Show what each view preserves and loses, and distinguish borrowed methods, new constructions, bounded computational checks and remaining uncertainty. Native tables and clear text remain useful companions to the graph. An attractive interface or successful library call alone is not the research result.

## Progress and working practice

Progress changes what we can derive, distinguish, explain or choose relative to the End. Record null results and limitations as well as useful constructions. A new essai should identify what the previous attempts leave unresolved and what its own result changes.

Keep the broad enquiry in this prompt, individual attempts in their own folders, and publication receipts separate from research claims. Preserve the original source account while allowing explicit alternative interpretations. New scenarios and methods remain available when they pursue the End; do not turn the first essai's scope into a permanent boundary.
