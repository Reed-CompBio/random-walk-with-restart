# Read the list of sources
from pathlib import Path
import networkx as nx
import pandas as pd


edges_file = Path("./input/edges1.txt")
source_file = Path("./input/source_nodes1.txt")
target_file = Path("./input/target_nodes1.txt")
output_file = Path("./output/output_file1.txt")
alpha = 0.05

def generate_nodes_and_edges(edges_file: Path) -> tuple:
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
            edges.append((endpoints[0], endpoints[1], endpoints[2]))
    return nodes, edges

def generate_nodes(nodes_file: Path) -> list:
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
            nodes.append((endpoints[0], endpoints[1]))
    return nodes

def generate_edges(edges_file: Path) -> list:
    edges = []
    with edges_file.open() as edges_f:
        for line in edges_f:
            line = line.strip()
            endpoints = line.split(" ")
            if len(endpoints) != 3:
                raise ValueError(f"Edge {line} does not contain 2 nodes separated by ' ' and a weight")
            edges.append((endpoints[0], endpoints[1], endpoints[2]))
    return edges


def generate_graph(nodes, edges) -> nx.DiGraph:
    G = nx.DiGraph()
    G.add_nodes_from(nodes)
    G.add_weighted_edges_from(edges)
    return G

def generate_personalization_vector(nodes : list) -> dict:
    personalization_vector = {}
    # assigning value 1 to the source and target nodes to pass it to the random walk function
    for i in nodes:
        personalization_vector[i[0]] = i[1] 
    
    print(personalization_vector)
    return personalization_vector

nodes, edges = generate_nodes_and_edges(edges_file)
G = generate_graph(nodes, edges)
source_node = generate_nodes(source_file)
pr = nx.pagerank(G, alpha=0.85, personalization=generate_personalization_vector(source_node))

R = G.reverse()
target_node = generate_nodes(target_file)
r_pr = nx.pagerank(R, alpha=0.85, personalization=generate_personalization_vector(target_node))

final_pr = {}
for i in pr:
    final_pr[i] = min(pr[i], r_pr[i])

print(f'Final pr, {final_pr}')    
# for each node : node, pr, r_pr, final_pr


# def construct_pathway_nodes(G: nx.DiGraph, final_pr: dict, source_node: list, target_node: list):
#     nodes = set()
#     for source in source_node:
#         nodes.add(source[0])
#     for target in target_node:
#         nodes.add(target[0])
#     for key in final_pr:
#         if final_pr[key] > alpha:
#             nodes.add(key)
#     print(nodes)
#     P = G.subgraph(nodes)
#     for source in source_node:
#         for target in target_node:
#             if nx.has_path(P, source[0], target[0]) != True:
#                 print(f'No path from {source[0]} to {target[0]}')
#                 return None
#     print("Constructing pathway nodes by using nodes with high linking scores")
#     return P

# def scoreLinkers(heats1, sorted1, heats2, sorted2, sourceSet, targetSet, cutoff, size):
#     """
#         Get linkers greater than this cutoff according to reverse-sorted list.

#         Inputs:
#             source and target sets, diffused heats for each and the heat-sorted
#             order for each.
        
#       The linker cutoff chosen.
#     """

#     print(f'cuttoff, {cutoff}')
#     # find the genes in the first set that fall above this cutoff
#     filtered_h1 = {}
#     for l in sorted1:
#         s = heats1[l]
#         if s < cutoff:
#             break

#         filtered_h1[l] = s
#     print(f'Filtered h1, {filtered_h1}')

#     # genes in second set above this cutoff
#     filtered_h2 = {}
#     for l in sorted2:
#         s = heats2[l]
#         if s < cutoff:
#             break

#         filtered_h2[l] = s
#     print(f'Filtered h2, {filtered_h2}')

#     # make sets of both 'relevance neighborhoods' R_s and R_t
#     f1 = set(filtered_h1)
#     f2 = set(filtered_h2)

#     print(f'f1, {f1}, f2, {f2}')
#     # the union are all the genes in the relevance neighborhoods of each set R_s U R_t
#     union = f1.union(f2)
#     intersection = f1.intersection(f2)
#     # connecting genes are linkers not in the source or target.
#     # intutively, this is the heat that flows to the same
#     print(f'Union, {union}; Intersection, {intersection}')
#     print(f'Source set, {sourceSet}; Target set, {targetSet}')
#     print(f'intersection.difference(sourceSet), {intersection.difference(sourceSet)}')
#     connecting = intersection.difference(sourceSet).difference(targetSet)
#     print(f'Connecting, {connecting}')
#     # the score is the number of connecting 'linker' genes over the size of the entire
#     # relevance neighborhoods
#     score = len(connecting)/float(len(union))
#     print(f'Score, {score}')
#     # the relative size of the connecting genes, compared to the input set sizes
#     size_frac = (len(connecting)/float(len(sourceSet.union(targetSet))))/float(size)
#     print(f'Size frac, {size_frac}')
#     return (score, size_frac)

# def filterLinkers(up_heats_diffused, down_heats_diffused, cutoff):
#     """
#     Use the min(diffused1, diffused2) function to return a list of genes
#     that fall above that cutoff.
#     Input:
#         diffused heats for each set, and the numeric cutoff value

#     Returns:
#         a list of genes above the cutoff, a hash of minimum heat values
#     """
#     linkers = {}
#     filtered = []
#     if down_heats_diffused is None:
#         # trivially: if this is a single list of diffused values, just return it
#         return (up_heats_diffused.keys(), up_heats_diffused)

#     for node in up_heats_diffused:
#         if node not in down_heats_diffused:
#             # it doesn't make the cut if it's not in both sets
#             continue
#         min_heat = min(up_heats_diffused[node], down_heats_diffused[node])
#         linkers[node] = min_heat
#         if min_heat > cutoff:
#             filtered.append(node)

#     return (filtered, linkers)

# def findLinkerCutOffMulti(source_node, target_node, pr, r_pr, final_pr, size):
#     if size == 0:
#         return (1000000, 0)
#     source_set = set([i[0] for i in source_node])
#     target_set = set([i[0] for i in target_node])
#     EPSILON = 0.0001
#     for cutoff in [h-EPSILON for h in sorted(final_pr.values(), reverse=True)]:
#         print(f'cutoff, {cutoff}')
#         score, size_frac = scoreLinkers(pr, sorted(pr, key=pr.get, reverse=True), r_pr, sorted(r_pr, key=r_pr.get, reverse=True), source_set, target_set, cutoff, size)
#         if size_frac > 1:
#             return (cutoff, score)

def pathway_construction(G : nx.DiGraph, final_pr : dict, alpha : float, source_node : list, target_node : list):
    """
    Return a subnetwork of G where for each edge of it, both ends are in the subset of interest.
    
    """
 
     
    linker_nodes = set()
    filtered_nodes = set()
    for key in final_pr:
        if final_pr[key] > alpha:
            print(f'Adding {key} to filtered nodes')
            linker_nodes.add(key)
    
    source_set = set([i[0] for i in source_node])
    target_set = set([i[0] for i in target_node])
    filtered_nodes = set(source_set).union(set(target_set)).union(set(linker_nodes))
    print(filtered_nodes)
 
    edgelist = set()
 
    for u in G.edges().keys():
        print(f'Checking edge {u}')
        print(f'Checking edge {u[0]} and {u[1]}')
        if u[0] in filtered_nodes and u[1] in filtered_nodes:
            print(f'Adding edge {u}')
            edgelist.add(u)
     
    P = nx.DiGraph()
    P.add_edges_from(list(edgelist))
 
    validated_edges = set()
    for component in nx.weakly_connected_components(P):
        validated_nodes = component
        for edge in edgelist:
            if edge[0] in validated_nodes and edge[1] in validated_nodes:
                validated_edges.add(edge)

    return validated_edges
 

# def construct_pathway_edges(G: nx.DiGraph, edges : dict, source_node : list, target_node : list, nodes : list):
#     P = nx.DiGraph()
#     P.add_nodes_from(nodes)
#     for edge in edges:
#         P.add_weighted_edges_from([(edge[0][0], edge[0][1], G[edge[0][0]][edge[0][1]]['weight'])])
#         # stop when every node in the source node list is connected to every node in the target node list
#         index = 0
#         for source in source_node:
#             for target in target_node:
#                 if nx.has_path(P, source[0], target[0]) != True:
#                     break
#                 else:
#                     index += 1
#         if index == len(source_node) * len(target_node):
#             return P
                      
#     print("Constructing pathway edges by using edges with high flux")
#     return P


def generate_output_edges(G: nx.DiGraph, pr : dict, output_prefix: Path):
    
    edge_sum = {}
    for node in G.nodes():
        temp = 0
        for i in G.out_edges(node):
            temp += float(G[node][i[1]]['weight'])
        edge_sum[node] = temp
        
    print(edge_sum)


    edge_flux = {}
    #calculate the edge flux
    for edge in G.edges():
        print(edge)
        edge_flux[edge] = pr[edge[0]] * float(G[edge[0]][edge[1]]['weight']) / edge_sum[edge[0]]

    sorted_edge_flux = sorted(edge_flux.items(), key=lambda x: x[1], reverse=True)
    print(f'edge_flux : {sorted_edge_flux}')
    
    sorted_final_pr = sorted(final_pr.items(), key=lambda x: x[1], reverse=True)
    print(f'final_pr : {sorted_final_pr}')
    
    edgelist = pathway_construction(G, final_pr, alpha, source_node, target_node)
    
    with output_prefix.open('w') as output_file_f:
        output_file_f.write("Node1\tNode2\tWeight\tPlaceholder\tType\n")
        for i in sorted_edge_flux:
            output_file_f.write(f"{i[0][0]}\t{i[0][1]}\t{i[1]}\t\t1\n")
        for i in sorted_final_pr:
            output_file_f.write(f"{i[0]}\t{pr[i[0]]}\t{r_pr[i[0]]}\t{i[1]}\t2\n")
        for edge in edgelist:
            output_file_f.write(f"{edge[0]}\t{edge[1]}\t{G[edge[0]][edge[1]]['weight']}\t\t3\n")
        
generate_output_edges(G,final_pr, output_file)
# get a list of edges 
'''
using edge flux
'''


'''
docker run -w /data --mount type=bind,source=/${PWD},target=/data erikliu24/random-walk

'''

df = pd.read_csv(output_file, sep="\t")
print(df)

# get all rows where type is 1
df_edge = df.loc[df["Type"] == 1]

# get rid of the placeholder column and output it to a file
df_edge = df_edge.drop(columns=['Placeholder'])
df_edge = df_edge.drop(columns=['Type'])
df_edge.to_csv('./output/edge_file.txt', sep=" ", index=False, header=True)
print(df_edge)

# locate the first place where placeholder is not Nan
df_node = df.loc[df['Type'] == 2]
# rename the header to Node, Pr, R_Pr, Final_Pr
df_node = df_node.drop(columns=['Type'])
df_node = df_node.rename(columns={'Node1': 'Node', 'Node2': 'Pr', 'Weight': 'R_Pr', 'Placeholder': 'Final_Pr'})
df_node.to_csv('./output/node_file.txt', sep=" ", index=False, header=True)
print(df_node)

df_pathway = df.loc[df['Type'] == 3]
df_pathway = df_pathway.drop(columns=['Placeholder'])
df_pathway = df_pathway.drop(columns=['Type'])
df_pathway.to_csv('./output/pathway_file.txt', sep=" ", index=False, header=True)
print(df_pathway)