# Earlier checkpoint

The earlier checkpoint has the same four graph-data lists as stakeholder_objectives.ipynb. Its broader tutorial cells recur in Working through the easy examples.ipynb. The complete duplicate checkpoint is omitted. This early exploratory cell is retained verbatim as the useful difference, including its original comments. The original saved execution raised a TypeError in this cell.

```python
# specify that input is list
A.add_edges(objectives, input_type="list")
A.add_edges(stakeholders, input_type="list")
A.add_edges(inter_layer_edges, input_type="list")
print(list(A.get_edges()))

multilayer_network = A
multilayer_network.visualize_network(style="diagonal",
                                     resolution=0.001,
                                     linepoints="-",
                                     linewidth=3)
plt.show()
plt.clf()
multilayer_network.visualize_network(style="hairball",
                                     resolution=10,
                                     linepoints="-",
                                     linewidth=1.5)
plt.show()

# other ad hoc options:
# def visualize_network(self,style="diagonal",parameters_layers=None,parameters_multiedges=None,show=False,compute_layouts="force",layouts_parameters=None,verbose=True,orientation="upper",resolution=0.01, axis = None, fig = None, no_labels = False, linewidth = 1.7, alphachannel = 0.3, linepoints = "-."):

A.basic_stats()

centralities = A.monoplex_nx_wrapper("degree_centrality")
A.monitor(centralities)

# if it's not present in networkx, you cannot use it as part of py3plex!
G = nx.cycle_graph(4)
sim = nx.simrank_similarity(G)
lol = [[sim[u][v] for v in sorted(sim[u])] for u in sorted(sim)]

print("Similarity", lol)
```
