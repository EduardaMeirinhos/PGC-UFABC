import os
import sys
import networkx as nx
import pandas as pd
from datetime import datetime
from graph import *
from unidecode import unidecode
import pickle 


chosen_area = (sys.argv[1]).lower()
print("\nÁrea escolhida: ", (sys.argv[1]))

graph = (sys.argv[2]).lower()
print("\nGrafo escolhido: ", (sys.argv[2]))

without_leaves = 'sem folhas' in sys.argv 

# Ler o grafo da GA
with open(f'{graph}.pickle', 'rb') as f:
    G = pickle.load(f)


# Exportar o grafo
def export_graph(G, graph_name):

    graph_name = graph_name.replace(" ", "_")

    date = datetime.now().strftime("%d%m%Y_%H%M%S")

    filename = unidecode(f'{graph_name}_{date}_export.gml')

    if not without_leaves:
        dir_path = f'exported_graphs/with_leaves/{graph}'
    else:
        dir_path = f'exported_graphs/without_leaves/{graph}'

    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)

    nx.write_gml(G, os.path.join(dir_path, filename))


def export(chosen_area, G):

    steem_list = steem_areas()
    nodes = graph_nodes(G.nodes(data="area"))

    if chosen_area == 'ga':
        # Grafo da genealogia acadêmica 

        if not without_leaves:
            export_graph(G, chosen_area)
        
        else:
            G_without_leaves = graph_without_leaves(G)
            export_graph(G_without_leaves, chosen_area)


    elif chosen_area == 'steem':
        # Subgrafo induzido pelos vértices das áreas STEEM

        nodes_steem_list = nodes[nodes.area.isin(steem_list)]['id_lattes'].tolist()

        G_steem = G.subgraph(nodes_steem_list)
        if not without_leaves:
            export_graph(G_steem, chosen_area)

        else:
            G_steem_without_leaves = graph_without_leaves(G_steem)
            export_graph(G_steem_without_leaves, chosen_area)


    elif chosen_area == 'áreas steem':
        # Subgrafos das áreas STEEM
    
        for area in steem_list:

            nodes_list = nodes[nodes['area'] == area]['id_lattes'].tolist()
            
            G_sub = G.subgraph(nodes_list)
            if not without_leaves:
                export_graph(G_sub, area)
            
            else:
                G_sub_without_leaves = graph_without_leaves(G_sub)
                export_graph(G_sub_without_leaves, area)


    else:
        # Subgrafo da área STEEM

        nodes['area'] = nodes['area'].apply(lambda x: str(x).lower())
        nodes_list = nodes[(nodes['area']) == chosen_area]['id_lattes'].tolist()
        
        G_sub = G.subgraph(nodes_list)
        if not without_leaves:
            export_graph(G_sub, chosen_area)
        
        else:
            G_sub_without_leaves = graph_without_leaves(G_sub)
            export_graph(G_sub_without_leaves, chosen_area)



export(chosen_area, G)

