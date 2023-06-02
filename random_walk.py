import networkx as nx

"""
Local neighborhood pathway reconstruction algorithm.
The algorithm takes a network and a list of nodes as input.
It outputs all edges in the network that have a node from the list as an endpoint.
"""

import argparse
from pathlib import Path

'''
--edges_file 
format:
Node1 Node2 Weight
A B 0.5
B C 0.6
D E 0.7
E A 0.8
...

--sources_file 
format:
node prize
A 1
B 1
C 1
...

--targets_file (same format as sources_file) 
--relevance_function(default: random_walk) (options: random_walk, HotNet)
--selection_function(default: min)
# --alpha(default: 0.01)

--output_nodes
format:
node pr r_pr final pr
A 1 1 1
B 2 2 2
...

--output_edges
format:
node1 node2 weight
A B 0.5
B C 0.6
...
'''

'''
Test:
cd \random-walk-with-restart
1. python random_walk.py --edges_file ./input/edges.txt --sources_file ./input/source_nodes.txt --targets_file ./input/target_nodes.txt --output_nodes ./output/output_nodes.txt --output_edges ./output/output_edges.txt
2. python random_walk.py --edges_file ./input/edges1.txt --sources_file ./input/source_nodes1.txt --targets_file ./input/target_nodes1.txt --output_nodes ./output/output_nodes1.txt --output_edges ./output/output_edges1.txt
3. python random_walk.py --edges_file ./input/edges2.txt --sources_file ./input/source_nodes2.txt --targets_file ./input/target_nodes2.txt --output_nodes ./output/output_nodes2.txt --output_edges ./output/output_edges2.txt
4. python random_walk.py --edges_file ./input/edges3.txt --sources_file ./input/source_nodes3.txt --targets_file ./input/target_nodes3.txt --output_nodes ./output/output_nodes3.txt --output_edges ./output/output_edges3.txt
5. python random_walk.py --edges_file ./input/edges4.txt --sources_file ./input/source_nodes4.txt --targets_file ./input/target_nodes4.txt --output_nodes ./output/output_nodes4.txt --output_edges ./output/output_edges4.txt
'''

def parse_arguments():
    """
    Process command line arguments.
    @return arguments
    """
    parser = argparse.ArgumentParser(
        description="Random Walk path reconstruction"
    )
    parser.add_argument("--edges_file", type=Path, required=True, help="Path to the edges file")
    parser.add_argument("--sources_file", type=Path, required=True, help="Path to the source node file")
    parser.add_argument("--targets_file", type=Path, required=True, help="Path to the target node file")
    # parser.add_argument("--relevance_function(default: pagerank)", type=str, required= True, default='r' ,help="Select a relevance function to use (r for random walk/h for HotNet)")
    # parser.add_argument("--selection_function", type=str, required= True, default= 'min', help="Select a function to use (min for minimum/sum for sum)")
    # parser.add_argument("--alpha", type=float, required= True, default= 0.01, help="Select the alpha value for the random walk")
    parser.add_argument("--output_nodes", type=Path, required=True, help="Path to the output file for nodes")
    parser.add_argument("--output_edges", type=Path, required=True, help="Path to the output file for edges")

    return parser.parse_args()

# Utility functions
def generate_nodes_and_edges(edges_file: Path) -> tuple:
    """
    This function is for extracting the nodes and edges from the path to the edges file
    """
    nodes = set()
    edges = []
    with edges_file.open() as edges_f:
        for i, line in enumerate(edges_f):
            # if the first line is the title, skip it
            if i == 0:
                continue
            line = line.strip()
            endpoints = line.split(" ")
            if len(endpoints) != 3:
                raise ValueError(f"Edge {line} does not contain 2 nodes separated by ' ' and a weight")
            nodes.add(endpoints[0])
            nodes.add(endpoints[1])
            # add the edge to the list of edges
            # (node1, node2, weight)
            edges.append((endpoints[0], endpoints[1], endpoints[2]))
    return nodes, edges

def generate_nodes(nodes_file: Path) -> list:
    """
    This function is for generating the nodes from the path to the source/target file
    """
    nodes = []
    with nodes_file.open() as nodes_f:
        for i, line in enumerate(nodes_f):
            # if the first line is the title, skip it
            if i == 0:
                continue
            line = line.strip()
            endpoints = line.split(" ")
            if len(endpoints) != 2:
                raise ValueError(f"Node {line} does not contain 1 node and a prize")
            # (node, prize)
            nodes.append((endpoints[0], endpoints[1]))
    return nodes


def generate_graph(nodes, edges) -> nx.DiGraph:
    """
    This function is for generating the graph from the input files (edges/sources/targets)
    """
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edges)
    return G

def generate_personalization_vector(nodes : list) -> dict:
    """
    This function is for generating the personalization vector from the source/target file
    """
    personalization_vector = {}
    # assigning value 1 to the source and target nodes to pass it to the random walk function
    for i in nodes:
        personalization_vector[i[0]] = float(i[1]) 
    
    return personalization_vector

def generate_output_edges(G: nx.DiGraph, pr : dict, output_edges_file: Path) -> None:
    """
    This function is for calculating the edge flux and writing it to the output file
    """
    edge_sum = {}
    # Get out_edges for every node and get their sum (sum of neighbors of all nodes = O(2m), so the for loop takes O(m) time.)
    for node in G.nodes():
        temp = 0
        for i in G.out_edges(node):
            temp += float(G[node][i[1]]['weight'])
        edge_sum[node] = temp
        
    edge_flux = {}
    #calculate the edge flux
    for edge in G.edges():
        # edge_sum[edge[0]] can never be 0 because we are only considering the nodes that have out_edges
        edge_flux[edge] = pr[edge[0]] * float(G[edge[0]][edge[1]]['weight']) / edge_sum[edge[0]]

    with output_edges_file.open("w") as output_edges_f:
        output_edges_f.write("Node1 Node2 Weight\n")
        for i in edge_flux:
            output_edges_f.write(f"{i[0]} {i[1]} {edge_flux[i]}\n")
        
    print("Output edges file generated")

# main algorithm
def random_walk(edges_file: Path, sources_file: Path, targets_file: Path, output_nodes_file: Path, output_edges_file: Path):
    """
    This function is the main algorithm for random walk path reconstruction.
    """
    if not edges_file.exists():
        raise OSError(f"Edges file {str(edges_file)} does not exist")
    if not sources_file.exists():
        raise OSError(f"Sources file {str(sources_file)} does not exist")
    if not targets_file.exists():
        raise OSError(f"Targets file {str(targets_file)} does not exist")
    
    if output_nodes_file.exists():
        print(f"Output files {str(output_nodes_file)} (nodes) will be overwritten")
    if output_edges_file.exists():
        print(f"Output files {str(output_edges_file)} (edges) will be overwritten")

    # Create the parent directories for the output file if needed
    output_nodes_file.parent.mkdir(parents=True, exist_ok=True)
    output_edges_file.parent.mkdir(parents=True, exist_ok=True)

    # Read the list of sources
    G = generate_graph(generate_nodes_and_edges(edges_file)[0], generate_nodes_and_edges(edges_file)[1])
    source_node = generate_nodes(sources_file)
    pr = nx.pagerank(G, alpha=0.85, personalization=generate_personalization_vector(source_node))
    
    R = G.reverse()
    target_node = generate_nodes(targets_file)
    r_pr = nx.pagerank(R, alpha=0.85, personalization=generate_personalization_vector(target_node))

    final_pr = {}
    for i in pr:
        final_pr[i] = min(pr[i], r_pr[i])
    
    with output_nodes_file.open("w") as output_nodes_f:
        output_nodes_f.write("node pr r_pr final_pr\n")
        for i in final_pr:
            output_nodes_f.write(f"{i} {pr[i]} {r_pr[i]} {final_pr[i]}\n")
    print(f"Output nodes written to {str(output_nodes_file)}")
    
    # Get the edge flux    
    generate_output_edges(G, final_pr, output_edges_file)
    
def main():
    """
    Parse arguments and run pathway reconstruction
    """
    args = parse_arguments()
    random_walk(args.edges_file, args.sources_file, args.targets_file, args.output_nodes, args.output_edges)

if __name__ == "__main__":
    main()

