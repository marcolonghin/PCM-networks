import pandas as pd
import networkx as nx
from pyvis.network import Network
import itertools as it
import numpy as np
import sys

def visualize_graph(g, name, save=False):
    nt = Network(   directed=True,   
                    cdn_resources = "remote",
                    select_menu = True,
                    filter_menu = True,
                    )

    nt.toggle_physics(False)
    nt.show_buttons(filter_=['physics'])
    nt.from_nx(g)

    nt.show(f'{name}.html', notebook=False)
    return nt

def color_graph(G, pos=None):
    leaf_nodes_color = "red" # es: "#79651f" -> dark brown                   
    root_nodes_color = "green" # es: "#5a4c1a" -> yellow                     
    other_nodes_color= "blue" # es: "#8f8877" -> clear gray                  
                                                                            
    for node in G.nodes():
        if pos is not None:
            G.nodes[node]["x"] =  pos[node][0]
            G.nodes[node]["y"] = -pos[node][1]

        if G.out_degree(node)==0:
            G.nodes[node]["color"] = leaf_nodes_color                        
        elif G.in_degree(node)==0:
            G.nodes[node]["color"] = root_nodes_color
        else:
            G.nodes[node]["color"] = other_nodes_color

def graph_preprocessing(df):
    labels = df["Label"]
    G = nx.MultiDiGraph()
    G.add_nodes_from(labels)

    implications = df["Implicational Condition(s)"]
    for node, imp in zip(labels, implications):
        if not pd.notna(imp):
            continue

        imp = imp.translate({ord(k):" " for k in "()+-¬,−"})
        imp = imp.replace("or", " ")
        imp = imp.split()
        for n in imp:
            G.add_edge(n, node)

    return G


def process_implicational_graph(df, G):
    G.remove_nodes_from(list(nx.isolates(G)))
    
    pos = nx.spring_layout(G, scale=500)
    color_graph(G, pos=pos)

    return G

def process_language_graph(df, lang, G):
    features = df[lang]
    labels   = df["Label"]

    renaming_dict = { k:k+str(v) for k,v in zip(labels, features) }
    G = nx.relabel_nodes(G, renaming_dict)

    for node in G.nodes():
        if "+" in node:
            G.nodes[node]["color"] = "green" 
        elif "-" in node:
            G.nodes[node]["color"] = "blue"
        else:
            G.nodes[node]["color"] = "red"

    edges_to_remove = [(u, v) for u, v in G.edges() if "0" in u and ("+" in v or "-" in v or "0" in v)]
    G.remove_edges_from(edges_to_remove)

    pos = nx.spring_layout(G, scale=500)
    color_graph(G, pos=pos)

    return G

if __name__ == "__main__":
    
    if len(sys.argv) > 2:
        raise SystemExit("Usage: python visualizer.py <language>")

    df = pd.read_excel("TableA_94_2025.xlsx")
    possible_languages = [c.lower() for c in df.columns[3:]]
    df.rename(columns={ c1 : c2 for c1,c2 in zip(df.columns[3:], possible_languages) }, 
              inplace=True)

    print(f"Languages contained in the current datafile: {possible_languages}")

    G = graph_preprocessing(df)

    if len(sys.argv) == 2:
        name = sys.argv[1].lower()
        assert name in possible_languages, f"ERROR: language {name} selected language does not exist in current data file"

        G = process_language_graph(df, name, G)

    else:
        name = "Implications"
        G = process_implicational_graph(df, G)

    nt = visualize_graph(G, name)
