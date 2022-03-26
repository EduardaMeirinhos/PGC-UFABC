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


# Calcular a quantidade de pessoas em cada gênero
def graph_gender_distribution(nodes):
    total_nodes_number = len(list(nodes))

    nodes = pd.DataFrame(list(nodes), columns=['id_lattes','gender'])

    gender_distribution_list = []
    genders = ['Feminino', 'Masculino', 'Não identificado']

    for gender in genders:
        num_nodes_gender = nodes[nodes['gender'] == gender].shape[0]
        gender_distribution_list.append(f"{formatNumber(num_nodes_gender)} ({round(num_nodes_gender*100/total_nodes_number, 2)}%)")

    gender_distribution_list.append(f"{formatNumber(total_nodes_number)} ({round(total_nodes_number*100/total_nodes_number, 2)}%)")

    return gender_distribution_list

# Distribuição de gênero
def gender_distribution(chosen_area, G):

    columns_list = ['Área', 'Gênero Feminino', 'Gênero Masculino', 'Não identificado', 'Total']
    steem_list = steem_areas()
    nodes = graph_nodes(G.nodes(data="area"))
    G_df = pd.DataFrame(columns = columns_list)
    G_without_leaves_df = pd.DataFrame(columns = columns_list)
      
    
    if chosen_area == 'ga':
        # Grafo da genealogia acadêmica 

        if not without_leaves:
            gender_distribution_list = graph_gender_distribution(G.nodes(data="gender"))
            gender_distribution_list.insert(0, "Genealogia Acadêmica")
            G_df.loc[len(G_df)] = gender_distribution_list
        
        else:
            G_without_leaves = graph_without_leaves(G)
            gender_distribution_without_leaves_list = graph_gender_distribution(G_without_leaves.nodes(data="gender"))
            gender_distribution_without_leaves_list.insert(0, "Genealogia Acadêmica")
            G_without_leaves_df.loc[len(G_without_leaves_df)] = gender_distribution_without_leaves_list


    elif chosen_area == 'steem':
        # Subgrafo induzido pelos vértices das áreas STEEM

        nodes_steem_list = nodes[nodes.area.isin(steem_list)]['id_lattes'].tolist()

        G_steem = G.subgraph(nodes_steem_list)
        if not without_leaves:
            gender_distribution_list = graph_gender_distribution(G_steem.nodes(data="gender"))
            gender_distribution_list.insert(0, "STEEM")
            G_df.loc[len(G_df)] = gender_distribution_list

        else:
            G_steem_without_leaves = graph_without_leaves(G_steem)
            gender_distribution_without_leaves_list = graph_gender_distribution(G_steem_without_leaves.nodes(data="gender"))
            gender_distribution_without_leaves_list.insert(0, "STEEM")
            G_without_leaves_df.loc[len(G_without_leaves_df)] = gender_distribution_without_leaves_list

    elif chosen_area == 'áreas steem':
        # Subgrafos das áreas STEEM
    
        for area in steem_list:

            nodes_list = nodes[nodes['area'] == area]['id_lattes'].tolist()
            
            G_sub = G.subgraph(nodes_list)
            if not without_leaves:
                gender_distribution_list = graph_gender_distribution(G_sub.nodes(data="gender"))
                gender_distribution_list.insert(0, area)
                G_df.loc[len(G_df)] = gender_distribution_list
            
            else:
                G_sub_without_leaves = graph_without_leaves(G_sub)
                gender_distribution_without_leaves_list = graph_gender_distribution(G_sub_without_leaves.nodes(data="gender"))
                gender_distribution_without_leaves_list.insert(0, area)
                G_without_leaves_df.loc[len(G_without_leaves_df)] = gender_distribution_without_leaves_list

    else:
        # Subgrafo da área STEEM

        nodes['area'] = nodes['area'].apply(lambda x: str(x).lower())
        nodes_list = nodes[(nodes['area']) == chosen_area]['id_lattes'].tolist()
        
        G_sub = G.subgraph(nodes_list)
        if not without_leaves:
            gender_distribution_list = graph_gender_distribution(G_sub.nodes(data="gender"))
            gender_distribution_list.insert(0, chosen_area)
            G_df.loc[len(G_df)] = gender_distribution_list
        
        else:
            G_sub_without_leaves = graph_without_leaves(G_sub)
            gender_distribution_without_leaves_list = graph_gender_distribution(G_sub_without_leaves.nodes(data="gender"))
            gender_distribution_without_leaves_list.insert(0, chosen_area)
            G_without_leaves_df.loc[len(G_without_leaves_df)] = gender_distribution_without_leaves_list

    
    return G_df if not without_leaves else G_without_leaves_df 



G_df = gender_distribution(chosen_area, G)

print('\n' + '-'*5 + f'{chosen_area} - Quantidade de pessoas de cada gênero' + '-'*5)
print(G_df)

chosen_area = chosen_area.replace(" ", "_")

date = datetime.now().strftime("%d%m%Y_%H%M%S")


if not without_leaves:
    dir_path = f'gender_distribution/with_leaves/{graph}'
else:
    dir_path = f'gender_distribution/without_leaves/{graph}'

if not os.path.isdir(dir_path):
    os.makedirs(dir_path)

filename = unidecode(f'{chosen_area}_{date}_gender.csv')
G_df.to_csv(os.path.join(dir_path, filename), encoding='utf-8-sig', index=False)

