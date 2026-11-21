# Original notebook commentary

The following comments and Markdown are transcribed from the selected personal notebooks. Code and Markdown remain intact in the accompanying notebooks. Saved outputs, execution counts and incidental notebook metadata were cleared for this publication. The original saved-output counts are recorded in provenance.json.

## stakeholder_objectives

### Cell 1

```text
<a href="https://colab.research.google.com/github/lawrencerowland/py3plex/blob/master/stakeholder_objectives.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
```

### Cell 2

```text
# Edges  added as lists: [n1,l1,n2,l2,w]
```

### Cell 3

```text
# specify that input is list
```

### Cell 5

```text
# quick summary
```

### Cell 7

```text
# or later, we use name networks[0]
```

### Cell 8

```text
# or networks[0]
```

### Cell 9

```text
# or networks[0]
```

### Cell 10

```text
# show the layers 
```

### Cell 11

```text
#even simpler A.visualize_network()
# You can also access individual graphical elements separately
# eg if edge_type == "refers_to":
```

### Cell 12

```text
#can do for edges
```

### Cell 13

```text
# tensor-based operations examples
# random node is accessed as follows
```

## LR test the visualisations

### Cell 1

```text
<a href="https://colab.research.google.com/github/lawrencerowland/py3plex/blob/master/LR%20test%20the%20visualisations.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
```

### Cell 4

```text
## visualization of a simple heterogeneous network
## you can try the default visualization options --- this is the simplest option/
## multilayer
## check core imports
## a simple hairball plot
```

### Cell 5

```text
# visualization of a simple heterogeneous network
```

### Cell 6

```text
# visualization from a simple file
#multilayer_network.split_to_layers()
#separate_layers = multilayer_network.separate_layers
```

### Cell 7

```text
# visualization from a simple file
```

### Cell 8

```text
# Warm up - hairball plots
# Construct a heterogeneous information network object
# going full py3plex (default 100 iterations)
# Show some basic statistics
```

### Cell 9

```text
# multilayer
# check core imports
# a simple hairball plot
```

### Cell 10

```text
# multilayer -----------------------------------
# check core imports
# multilayer_network.visualize_network() ## visualize
# plt.show()
# You can also access individual graphical elements separately!
# get layers for visualizat# ion
#    network_list,multi_edge_tuple,input_type="nodes",linepoints="-.",alphachannel=0.3,linecolor="black",curve_height=1,style="curve2_bezier",linewidth=1,invert=False,linmod="both",resolution=0.1
```

### Cell 11

```text
# monotone coloring
```

### Cell 12

```text
# basic string layout ----------------------------------
```

### Cell 13

```text
#NOT WORKING CURRENTLY
```

### Cell 14

```text
#NOT TESTED
# network and group objects must be present within the .mat object
# check core imports
# select top n communities by size
# assign node colors
# visualize the network's communities!
```

### Cell 15

```text
#NOT FULLY TESTED
# string layout for larger network -----------------------------------
# embedding-based layout (custom coordinates) -----------------------------------
# call a specific n2v compiled binary
# preprocess and check embedding
# custom layouts are part of the custom coordinate option
# assign parameters
```

## Working through the easy examples

### Cell 1

```text
<a href="https://colab.research.google.com/github/lawrencerowland/py3plex/blob/master/Working%20through%20the%20easy%20examples" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>
```

### Cell 7

```text
# visualization of a simple heterogeneous network
```

### Cell 8

```text
# You can also access individual graphical elements separately!
# get layers for visualizat# ion
#    network_list,multi_edge_tuple,input_type="nodes",linepoints="-.",alphachannel=0.3,linecolor="black",curve_height=1,style="curve2_bezier",linewidth=1,invert=False,linmod="both",resolution=0.1
```

### Cell 9

```text
# entanglement: By. Benjamin Renoust and Blaz Skrlj, 2019
# load an example multilayer network
# visualization from a simple file
```

### Cell 10

```text
# A simple example for extracting different layers based on subgraphs.
# print some basic statistics of each network
```

### Cell 11

```text
#this example demonstrates how a network can be manipulated
# dealing with multiplex networks
# subset the network by layers
# coupled edges
# non-coupled edges
# visualize this toy example
# B.visualize_network(show=True,resolution=0.01)
# nodes can also be removed easily
```

### Cell 12

```text
# this is nicer printing.
# looping through edges:
# what about nodes?
```

### Cell 13

```text
#from py3plex.algorithms import *
## import status
# check core imports
# results frame
# construct a single dataframe
```

### Cell 14

```text
# quick summary
```

### Cell 15

```text
# An example how nx functions can be used.
# compute node centralities --- this will be applied to the network object
# get top nodes by centrality
```

### Cell 16

```text
# An example general multilayer network
# Edges can also be added as lists: [n1,l1,n2,l2,w]
# specify that input is list, all else is recognized by Py3plex!
# other ad hoc options:
# def visualize_network(self,style="diagonal",parameters_layers=None,parameters_multiedges=None,show=False,compute_layouts="force",layouts_parameters=None,verbose=True,orientation="upper",resolution=0.01, axis = None, fig = None, no_labels = False, linewidth = 1.7, alphachannel = 0.3, linepoints = "-."):
# if it's not present in networkx, you cannot use it as part of py3plex!
```

### Cell 17

```text
# tensor-based operations examples
# initiate an instance of a random graph
# some simple visualization
# random node is accessed as follows
# and random edge as
```

### Cell 18

```text
## a simple visualization of a twitter network
## Load the relevan layer names for later
## Loade the network first!
## Let's customize it a bit.
```
