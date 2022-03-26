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


# Formatar números inteiros
def formatNumber(number):
    return format(number,',d').replace(",",".")


# Somar o grau de entrada ou saída de todos os vértices do grafo
def sum_degree(list_of_degrees):
    cont = 0
    for (node, degree) in list_of_degrees:
        cont = cont + degree
    return cont


# Realizar o cálculo das métricas de interesse para o grafo
def graph_metrics(G):
    # Número de vértices 
    nodes = formatNumber(len(G))
    
    # Número de arestas
    edges = formatNumber(G.size())
    
    # Grau médio de entrada
    degree_sum = sum_degree(list(G.degree()))
    degree_average = round(degree_sum/len(G), 2)
    
    graph_metrics_list = [nodes, edges, degree_average]
    
    return graph_metrics_list


def metrics(chosen_area, G):

    columns_list = ['Área', 'Vértices', 'Arestas', 'Grau médio']
    steem_list = steem_areas()
    nodes = graph_nodes(G.nodes(data="area"))
    G_df = pd.DataFrame(columns = columns_list)
    G_without_leaves_df = pd.DataFrame(columns = columns_list)
      
    
    if chosen_area == 'ga':
        # Grafo da genealogia acadêmica 

        if not without_leaves:
            metrics_list = graph_metrics(G)
            metrics_list.insert(0, "Genealogia Acadêmica")
            G_df.loc[len(G_df)] = metrics_list
        
        else:
            G_without_leaves = graph_without_leaves(G)
            metrics_without_leaves_list = graph_metrics(G_without_leaves)
            metrics_without_leaves_list.insert(0, "Genealogia Acadêmica")
            G_without_leaves_df.loc[len(G_without_leaves_df)] = metrics_without_leaves_list


    elif chosen_area == 'steem':
        # Subgrafo induzido pelos vértices das áreas STEEM

        nodes_steem_list = nodes[nodes.area.isin(steem_list)]['id_lattes'].tolist()

        G_steem = G.subgraph(nodes_steem_list)
        if not without_leaves:
            metrics_list = graph_metrics(G_steem)
            metrics_list.insert(0, "STEEM")
            G_df.loc[len(G_df)] = metrics_list

        else:
            G_steem_without_leaves = graph_without_leaves(G_steem)
            metrics_without_leaves_list = graph_metrics(G_steem_without_leaves)
            metrics_without_leaves_list.insert(0, "STEEM")
            G_without_leaves_df.loc[len(G_without_leaves_df)] = metrics_without_leaves_list

    elif chosen_area == 'áreas steem':
        # Subgrafos das áreas STEEM
    
        for area in steem_list:

            nodes_list = nodes[nodes['area'] == area]['id_lattes'].tolist()
            
            G_sub = G.subgraph(nodes_list)
            if not without_leaves:
                metrics_list = graph_metrics(G_sub)
                metrics_list.insert(0, area)
                G_df.loc[len(G_df)] = metrics_list
            
            else:
                G_sub_without_leaves = graph_without_leaves(G_sub)
                metrics_without_leaves_list = graph_metrics(G_sub_without_leaves)
                metrics_without_leaves_list.insert(0, area)
                G_without_leaves_df.loc[len(G_without_leaves_df)] = metrics_without_leaves_list

    else:
        # Subgrafo da área STEEM

        nodes['area'] = nodes['area'].apply(lambda x: str(x).lower())
        nodes_list = nodes[(nodes['area']) == chosen_area]['id_lattes'].tolist()
        
        G_sub = G.subgraph(nodes_list)
        if not without_leaves:
            metrics_list = graph_metrics(G_sub)
            metrics_list.insert(0, chosen_area)
            G_df.loc[len(G_df)] = metrics_list
        
        else:
            G_sub_without_leaves = graph_without_leaves(G_sub)
            metrics_without_leaves_list = graph_metrics(G_sub_without_leaves)
            metrics_without_leaves_list.insert(0, chosen_area)
            G_without_leaves_df.loc[len(G_without_leaves_df)] = metrics_without_leaves_list

    
    return G_df if not without_leaves else G_without_leaves_df   



G_df = metrics(chosen_area, G)

print('\n' + '-'*5 + f'{chosen_area} - métricas (vértices, arestas, grau médio de entrada/saída)' + '-'*5)
print(G_df)


chosen_area = chosen_area.replace(" ", "_")

date = datetime.now().strftime("%d%m%Y_%H%M%S")

if not without_leaves:
    dir_path = f'metrics/with_leaves/{graph}'
else:
    dir_path = f'metrics/without_leaves/{graph}'

if not os.path.isdir(dir_path):
    os.makedirs(dir_path)

filename = unidecode(f'{chosen_area}_{date}_metrics.csv')
G_df.to_csv(os.path.join(dir_path, filename), encoding='utf-8-sig', index=False)
