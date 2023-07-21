<!-- Generate README to describe the RandomWalk Algorithm -->

# Random Walk with Restart (RWR) Algorithm

The algorithm generates a random walk, considering the probability of each node being visited based on its importance in the graph. The RWR algorithm incorporates a restart probability and a teleport probability, which affect the traversal behavior. This algorithm will calculate the edge flux of each edge in the graph based on the results from RWR algorithm as well to represent the importance of each edge in the graph.

## Background

The RWR algorithm draws inspiration from the TieDIE algorithm developed by Evan O. Paull and others. The TieDIE algorithm aims to discover causal pathways that link genomic events to transcriptional states using a method called Tied Diffusion Through Interacting Events. You can find more information about the TieDIE algorithm in the research paper titled "Discovering causal pathways linking genomic events to transcriptional states using Tied Diffusion Through Interacting Events (TieDIE)" published in the Bioinformatics journal, Volume 29, Issue 21, November 2013.

The RWR algorithm modifies the TieDIE algorithm to generate random walks in a graph/network while considering the importance of each node. The main idea for RWR is to firstly run pagerank algorithm on the graph based on the given source set, edge weights, and node prizes. Then, the RWR will perform a pagerank algorithm on the reversed graph starting from the target set. The RWR algorithm will then combine the two pagerank results to generate a final result. With the calculation of the edge flux based on the final result for each node, we are able to identify the importance of each node and each edge in the graph. Moreover, the algorithm allows the user to define a threshold. It generates a pathway that includes nodes with visitation possibility exceeding the threshold and includes all edges connecting any two nodes from the extracted set of nodes.

## How to use

```
$ python random_walk.py -h
usage: random_walk.py [-h] --edges_file EDGES_FILE --prizes_file PRIZES_FILE
                      [--single_source SINGLE_SOURCE]
                      [--damping_factor DAMPING_FACTOR]
                      [--selection_function SELECTION_FUNCTION] [--w W]
                      [--threshold THRESHOLD] --output_file OUTPUT_FILE

Random-Walk-with-Restart Path Reconstruction

optional arguments:
  -h, --help            show this help message and exit
  --edges_file EDGES_FILE
                        Path to the edges file
  --prizes_file PRIZES_FILE
                        Path to the prizes file
  --single_source SINGLE_SOURCE
                        1 for single-sourced RWR and 0 for source-target RWR
                        (default: 1)
  --damping_factor DAMPING_FACTOR
                        Select a damping factor between 0 and 1 for the
                        random walk with restart (default: 0.85)
  --selection_function SELECTION_FUNCTION
                        Select a function to use (min for minimum/sum for
                        sum/avg for average/max for maximum)
  --w W                 Select a lower bound between 0 and 1 for the edge
                        weight (default: 0.01)
  --threshold THRESHOLD
                        Select a threshold value between 0 and 1 for the
                        construction reference (default: 0.001)
  --output_file OUTPUT_FILE
                        Path to the output files
```

## Example behavior

Command Line:

```
$ python random_walk.py --edges_file input/edges1.txt --sources_file input/source_nodes1.txt --single_source 0 --targets_file input/target_nodes1.txt --damping_factor 0.85 --selection_function min --w 0.4 --threshold 0.05 --output_file output/output1.txt
```

edge_file:

```
Node1	Node2	Weight
A	E	1
B	E	1
B	F	1
C	G	1
D	G	1
E	F	1
E	G	1
E	I	1
E	H	1
F	G	1
G	I	1
G	L	1
G	M	1
G	N	1
H	I	1
H	J	1
I	K	1
K	G	1

```

prizes_file:

```
NODEID	prizes	Node type
A	1	source
B	1	source
C	1	source
D	1	source
I	1	target
K	1	target
L	1	target
M	1	target
```

output_file file:

```
Node1	Node2	Edge Flux	Weight	InNetwork	Type
I	K	0.07916510453081935	1	True	1
C	G	0.07200586937326067	1	True	1
D	G	0.07200586937326067	1	True	1
A	E	0.07200586937326067	1	True	1
K	G	0.0672888662304317	1	True	1
G	I	0.06042745132956512	1	True	1
G	L	0.06042745132956512	1	True	1
G	M	0.06042745132956512	1	True	1
G	N	0.06042745132956512	1	False	1
F	G	0.050111911667253775	1	False	1
B	E	0.036002934686630336	1	True	1
B	F	0.036002934686630336	1	False	1
E	G	0.022951807559145002	1	True	1
E	I	0.022951807559145002	1	True	1
E	F	0.022951807559145002	1	False	1
E	H	0.022951807559145002	1	False	1
H	I	0.009754750794196887	1	False	1
H	J	0.009754750794196887	1	False	1
G	0.24170980531826047	0.17803669481783677	0.17803669481783677	True	2
E	0.09180723023658001	0.1310577086963235	0.09180723023658001	True	2
I	0.07916510453081935	0.16774725400523366	0.07916510453081935	True	2
B	0.07200586937326067	0.06856124377392274	0.06856124377392274	True	2
K	0.0672888662304317	0.10703439954263362	0.0672888662304317	True	2
A	0.07200586937326067	0.05569854165677538	0.05569854165677538	True	2
M	0.0513642499963964	0.07676796360341454	0.0513642499963964	True	2
L	0.0513642499963964	0.07676796360341454	0.0513642499963964	True	2
F	0.050111911667253775	0.030266435939219082	0.030266435939219082	False	2
C	0.07200586937326067	0.030266435939219082	0.030266435939219082	True	2
D	0.07200586937326067	0.030266435939219082	0.030266435939219082	True	2
H	0.019509501588393773	0.04752892248278801	0.019509501588393773	False	2
N	0.0513642499963964	0.0	0.0	False	2
J	0.00829135294602917	0.0	0.0	False	2
B	E	1		3
I	K	1		3
E	G	1		3
C	G	1		3
G	M	1		3
G	I	1		3
G	L	1		3
K	G	1		3
D	G	1		3
A	E	1		3
E	I	1		3

```

## References

- Evan O. Paull and others, Discovering causal pathways linking genomic events to transcriptional states using Tied Diffusion Through Interacting Events (TieDIE), *Bioinformatics*, Volume 29, Issue 21, November 2013, Pages 2757–2764, [doi.org/10.1093/bioinformatics/btt471](https://academic.oup.com/bioinformatics/article/29/21/2757/195824)
