import networkx as nx
import argparse
from pathlib import Path

def parse_arguments():
    """
    Process command line arguments.
    @return arguments
    """
    parser = argparse.ArgumentParser(
        description="Random-walk-with-restart Path Reconstruction"
    )
    
    # add arguments
    parser.add_argument("--edges_file", type=Path, required=True, help="Path to the edges file")
    parser.add_argument("--sources_file", type=Path, required=True, help="Path to the source node file")
    parser.add_argument("--targets_file", type=Path, required=True, help="Path to the target node file")
    parser.add_argument("--damping_factor", type=float, required= False, default= 0.85, help="Select a damping factor between 0 and 1 for the random walk with restart (default: 0.85)")
    parser.add_argument("--selection_function", type=str, required= False, default= 'min', help="Select a function to use (min for minimum/sum for sum/avg for average/max for maximum)")
    parser.add_argument("--threshold", type=float, required= False, default= 0.0001, help="Select a threshold value between 0 and 1 for the construction reference (default: 0.001)")
    parser.add_argument("--single_source", type=bool, required = True, default= False, help="Select True if you want to use a single source node (default: False)")
    parser.add_argument("--output_file", type=Path, required=True, help="Path to the output files")

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


def generate_graph(nodes : set, edges : list) -> nx.DiGraph:
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


def pathway_construction(G : nx.DiGraph, final_pr : dict, alpha : float, source_node : list, target_node : list):
    """
    Return a subnetwork of G where for each edge of it, both ends are in the subset of interest.
    
    """
 
    linker_nodes = set()
    filtered_nodes = set()
    for key in final_pr:
        if final_pr[key] > alpha:
            print(f'Adding {key} (Final PR = {final_pr[key]}) to filtered nodes.')
            linker_nodes.add(key)
    
    source_set = set([i[0] for i in source_node])
    target_set = set([i[0] for i in target_node])
    filtered_nodes = set(source_set).union(set(target_set)).union(set(linker_nodes))
    print(f'Filtered nodes: {filtered_nodes}')
 
    edgelist = set()
 
    for u in G.edges().keys():
        if u[0] in filtered_nodes and u[1] in filtered_nodes:
            print(f'Adding edge {u}')
            edgelist.add(u)

    return edgelist

def generate_output(G : nx.DiGraph, final_pr : dict, threshold : float, source_node : list, target_node : list, output_file : Path, pr : dict, r_pr : dict):
    """
    This function is for calculating the edge flux and writing the results to the output file.
    """
    edge_sum = {}
    for node in G.nodes():
        temp = 0
        for i in G.out_edges(node):
            temp += float(G[node][i[1]]['weight'])
        edge_sum[node] = temp
        
    edge_flux = {}
    #calculate the edge flux
    for edge in G.edges():
        edge_flux[edge] = pr[edge[0]] * float(G[edge[0]][edge[1]]['weight']) / edge_sum[edge[0]]

    sorted_edge_flux = sorted(edge_flux.items(), key=lambda x: x[1], reverse=True)
    
    sorted_final_pr = sorted(final_pr.items(), key=lambda x: x[1], reverse=True)
    
    edgelist = pathway_construction(G, final_pr, threshold, source_node, target_node)
    with output_file.open('w') as output_file_f:
        output_file_f.write("Node1\tNode2\tWeight\tPlaceholder\tType\n")
        for i in sorted_edge_flux:
            output_file_f.write(f"{i[0][0]}\t{i[0][1]}\t{i[1]}\t\t1\n")
        for i in sorted_final_pr:
            output_file_f.write(f"{i[0]}\t{pr[i[0]]}\t{r_pr[i[0]]}\t{i[1]}\t2\n")
        for edge in edgelist:
            output_file_f.write(f"{edge[0]}\t{edge[1]}\t{G[edge[0]][edge[1]]['weight']}\t\t3\n")
        
    print("Output file generated")

# main algorithm
def random_walk(edges_file: Path, sources_file: Path, targets_file: Path, output_file: Path, damping_factor : float = 0.85, selection_function : str = 'min', threshold : float = 0.001, single_source : bool = False):
    """
    This function is the main algorithm for random-walk-with-restart path reconstruction.
    """
    if not edges_file.exists():
        raise OSError(f"Edges file {str(edges_file)} does not exist")
    if not sources_file.exists():
        raise OSError(f"Sources file {str(sources_file)} does not exist")
    if not targets_file.exists():
        raise OSError(f"Targets file {str(targets_file)} does not exist")
    
    if output_file.exists():
        print(f"Output files {str(output_file)} (nodes) will be overwritten")

    # Create the parent directories for the output file if needed
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # check if the damping factor is between 0 and 1
    if damping_factor < 0 or damping_factor > 1:
        raise ValueError(f"Damping factor should be between 0 and 1")
    else:
        print(f"Damping factor is {damping_factor}")
    
    # check if the selection function is either min, max, sum or avg
    if selection_function != 'min' and selection_function != 'sum' and selection_function != 'max' and selection_function != 'avg':
        raise ValueError(f"Selection function should be either min, max, sum or avg")
    else:
        print(f"Selection function is {selection_function}")
        
    # check if the threshold is between 0 and 1
    if threshold < 0 or threshold > 1:
        raise ValueError(f"Threshold should be between 0 and 1")
    else:
        print(f"Threshold is {threshold}")
    
    # Read the list of sources
    nodes, edges = generate_nodes_and_edges(edges_file)
    G = generate_graph(nodes, edges)
    source_node = generate_nodes(sources_file)
    pr = nx.pagerank(G, alpha=damping_factor, personalization=generate_personalization_vector(source_node))
    
    # Create the reverse graph
    R = G.reverse()
    target_node = generate_nodes(targets_file)
    # Running pagerank on the reverse graph with T as the personalization vector
    r_pr = nx.pagerank(R, alpha=damping_factor, personalization=generate_personalization_vector(target_node))

    final_pr = {}
    
    if not single_source:
        # Combine the two pageranks with the selection function
        if selection_function == 'min':
            for i in pr:
                'Let user decide how to combine the two pageranks'
                final_pr[i] = min(pr[i], r_pr[i])
        elif selection_function == 'sum':
            for i in pr:
                final_pr[i] = pr[i] + r_pr[i]
        elif selection_function == 'avg':
            for i in pr:
                final_pr[i] = (pr[i] + r_pr[i])/2
        elif selection_function == 'max':
            for i in pr:
                final_pr[i] = max(pr[i], r_pr[i])
    else:
        final_pr = pr
    # Output the results
    generate_output(G, final_pr, threshold, source_node, target_node, output_file, pr, r_pr)
    
def main():
    """
    Parse arguments and run pathway reconstruction
    """
    args = parse_arguments()
    random_walk(args.edges_file, args.sources_file, args.targets_file,args.output_file, args.damping_factor, args.selection_function, args.threshold, args.single_source)

if __name__ == "__main__":
    main()
    
'''
test:
python random_walk.py --edges_file input/edges1.txt --sources_file input/source_nodes1.txt --targets_file input/target_nodes1.txt --damping_factor 0.85 --selection_function min --threshold 0.1 --single_source False --output_file output/output1.txt
'''

