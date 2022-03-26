import os
import sys
import networkx as nx
import pandas as pd
from prone import *
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

def graph_prone_measures(G):

    #attribute_dict = {'gender': ['Feminino','Masculino','Não identificado']}
    attribute_dict = {'gender': ['Feminino','Masculino']}
    att = 'gender'
    att2 = 'gender'
    
    res = get_all(G, attribute_dict, att, att2, print_mixing = False, normalized= False ) 
     
    prone_mesures = [round(res['Q'], 2), round(res['r'], 2), round(res['ProNe_l'], 2), round(res['ProNe_2'], 2), round(res['ProNe_3'], 2)]
    
    return prone_mesures


def prone_measures(chosen_area, G):

    columns_list = ['Área', 'Q', 'r', 'ProNe_l', 'ProNe_2', 'ProNe_3']
    steem_list = steem_areas()
    nodes = graph_nodes(G.nodes(data="area"))
    G_df = pd.DataFrame(columns = columns_list)
    G_without_leaves_df = pd.DataFrame(columns = columns_list)
      
    
    if chosen_area == 'ga':
        # Grafo da genealogia acadêmica 

        if not without_leaves:
            prone_list = graph_prone_measures(G)
            prone_list.insert(0, "Genealogia Acadêmica")
            G_df.loc[len(G_df)] = prone_list
        
        else:
            G_without_leaves = graph_without_leaves(G)
            prone_without_leaves_list = graph_prone_measures(G_without_leaves)
            prone_without_leaves_list.insert(0, "Genealogia Acadêmica")
            G_without_leaves_df.loc[len(G_without_leaves_df)] = prone_without_leaves_list


    elif chosen_area == 'steem':
        # Subgrafo induzido pelos vértices das áreas STEEM

        nodes_steem_list = nodes[nodes.area.isin(steem_list)]['id_lattes'].tolist()

        G_steem = G.subgraph(nodes_steem_list)
        if not without_leaves:
            prone_list = graph_prone_measures(G_steem)
            prone_list.insert(0, "STEEM")
            G_df.loc[len(G_df)] = prone_list

        else:
            G_steem_without_leaves = graph_without_leaves(G_steem)
            prone_without_leaves_list = graph_prone_measures(G_steem_without_leaves)
            prone_without_leaves_list.insert(0, "STEEM")
            G_without_leaves_df.loc[len(G_without_leaves_df)] = prone_without_leaves_list

    elif chosen_area == 'áreas steem':
        # Subgrafos das áreas STEEM
    
        for area in steem_list:

            nodes_list = nodes[nodes['area'] == area]['id_lattes'].tolist()
            
            G_sub = G.subgraph(nodes_list)
            if not without_leaves:
                prone_list = graph_prone_measures(G_sub)
                prone_list.insert(0, area)
                G_df.loc[len(G_df)] = prone_list
            
            else:
                G_sub_without_leaves = graph_without_leaves(G_sub)
                prone_without_leaves_list = graph_prone_measures(G_sub_without_leaves)
                prone_without_leaves_list.insert(0, area)
                G_without_leaves_df.loc[len(G_without_leaves_df)] = prone_without_leaves_list

    else:
        # Subgrafo da área STEEM

        nodes['area'] = nodes['area'].apply(lambda x: str(x).lower())
        nodes_list = nodes[(nodes['area']) == chosen_area]['id_lattes'].tolist()
        
        G_sub = G.subgraph(nodes_list)
        if not without_leaves:
            prone_list = graph_prone_measures(G_sub)
            prone_list.insert(0, chosen_area)
            G_df.loc[len(G_df)] = prone_list
        
        else:
            G_sub_without_leaves = graph_without_leaves(G_sub)
            prone_without_leaves_list = graph_prone_measures(G_sub_without_leaves)
            prone_without_leaves_list.insert(0, chosen_area)
            G_without_leaves_df.loc[len(G_without_leaves_df)] = prone_without_leaves_list

    
    return G_df if not without_leaves else G_without_leaves_df 



G_df = prone_measures(chosen_area, G)

print('\n' + '-'*5 + f'{chosen_area} - medidas do PRONE' + '-'*5)
print(G_df)

chosen_area = chosen_area.replace(" ", "_")

date = datetime.now().strftime("%d%m%Y_%H%M%S")

if not without_leaves:
    dir_path = f'prone_measures/with_leaves/{graph}'
else:
    dir_path = f'prone_measures/without_leaves/{graph}'

if not os.path.isdir(dir_path):
    os.makedirs(dir_path)

filename = unidecode(f'{chosen_area}_{date}_prone.csv')
G_df.to_csv(os.path.join(dir_path, filename), encoding='utf-8-sig', index=False)


