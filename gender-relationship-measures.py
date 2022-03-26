import os
import sys
import pickle
import pandas as pd
from graph import *
from datetime import datetime
from unidecode import unidecode

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


# Combinações possíveis de gênero entre relacionamentos de vértices
def edge_gender_relationship(g1,g2):
    if g1 == 'Feminino' and g2 == 'Feminino':
        return 'Feminino-Feminino'
    if g1 == 'Masculino' and g2 == 'Masculino':
        return 'Masculino-Masculino'
    if (g1 == 'Feminino' and g2 == 'Masculino') or (g1 == 'Masculino' and g2 == 'Feminino'):
        return 'Feminino-Masculino'
    if (g1 == 'Feminino' and g2 == 'Não identificado') or (g1 == 'Não identificado' and g2 == 'Feminino'):
        return 'Feminino-Não identificado'
    if (g1 == 'Masculino' and g2 == 'Não identificado') or (g1 == 'Não identificado' and g2 == 'Masculino'):
        return 'Masculino-Não identificado'
    if g1 == 'Não identificado' and g2 == 'Não identificado':
        return 'Não identificado-Não identificado'


# Quantidade de arestas para cada combinação de gênero   
def graph_gender_relationship_measures(G):

    total_edges_number = len(list(G.edges))

    columns_list = ['Node1', 'Node2']
    #columns_list = ['Node1', 'Node2', 'Key']
   
    # Criar dataframe com as arestas (id_lattes, id_lattes)
    edges_df = pd.DataFrame(list(G.edges), columns=columns_list)

    # Criar dicionário de id_lattes e seu respectivo gênero
    nodes_gender_dict = dict(G.nodes(data='gender'))

    # Criar colunas auxiliares para calcular o relacionamento dos gêneros
    edges_df['Gender1'] = edges_df['Node1'].apply(lambda x: nodes_gender_dict.get(x))
    edges_df['Gender2'] = edges_df['Node2'].apply(lambda x: nodes_gender_dict.get(x))
    edges_df['Relação'] = edges_df.apply(lambda x: edge_gender_relationship(x['Gender1'],x['Gender2']), axis=1)

    # Combinações possíveis de relações
    relationship_list = ['Feminino-Feminino', 'Feminino-Masculino', 'Feminino-Não identificado', 'Masculino-Masculino', 'Masculino-Não identificado', 'Não identificado-Não identificado']

    # Verificar a quantidade de arestas para cada combinação
    gender_relationship_dict = edges_df.groupby(['Relação']).size().to_dict()

    # Inicializar valores com 0
    gender_relationship_measures_list = []
    for relationship in relationship_list:
        gender_relationship_measures_list.append((relationship, f"{0} (0.0%)"))
    gender_relationship_measures_dict = dict(gender_relationship_measures_list)

    # Atribuir valores
    for key in gender_relationship_dict:
        gender_relationship_measures_dict[key] = f"{formatNumber(gender_relationship_dict.get(key))} ({round(gender_relationship_dict.get(key)*100/total_edges_number, 2)}%)"

    gender_relationship_measures_dict['Total'] = f"{formatNumber(total_edges_number)} ({round(total_edges_number*100/total_edges_number, 2)}%)"

    return list(gender_relationship_measures_dict.values())


def gender_relationship_measures(chosen_area, G):
    
    columns_list = ['Área', 'Feminino-Feminino', 'Feminino-Masculino', 'Feminino-Não identificado', 'Masculino-Masculino', 'Masculino-Não identificado', 'Não identificado-Não identificado', 'Total']
    steem_list = steem_areas()
    nodes = graph_nodes(G.nodes(data="area"))
    G_df = pd.DataFrame(columns = columns_list)
    G_without_leaves_df = pd.DataFrame(columns = columns_list)
      
    
    if chosen_area == 'ga':
        # Grafo da genealogia acadêmica 

        if not without_leaves:

            gender_relationship_measures_list = graph_gender_relationship_measures(G)
            gender_relationship_measures_list.insert(0, "Genealogia Acadêmica")
            G_df.loc[len(G_df)] = gender_relationship_measures_list

        else:
        
            G_without_leaves = graph_without_leaves(G)
            gender_relationship_measures_without_leaves_list = graph_gender_relationship_measures(G_without_leaves)
            gender_relationship_measures_without_leaves_list.insert(0, "Genealogia Acadêmica")
            G_without_leaves_df.loc[len(G_without_leaves_df)] = gender_relationship_measures_without_leaves_list


    elif chosen_area == 'steem':
        # Subgrafo induzido pelos vértices das áreas STEEM

        nodes_steem_list = nodes[nodes.area.isin(steem_list)]['id_lattes'].tolist()

        G_steem = G.subgraph(nodes_steem_list)
        if not without_leaves:
            gender_relationship_measures_list = graph_gender_relationship_measures(G_steem)
            gender_relationship_measures_list.insert(0, "STEEM")
            G_df.loc[len(G_df)] = gender_relationship_measures_list

        else:
            G_steem_without_leaves = graph_without_leaves(G_steem)
            gender_relationship_measures_without_leaves_list = graph_gender_relationship_measures(G_steem_without_leaves)
            gender_relationship_measures_without_leaves_list.insert(0, "STEEM")
            G_without_leaves_df.loc[len(G_without_leaves_df)] = gender_relationship_measures_without_leaves_list

    elif chosen_area == 'áreas steem':
        # Subgrafos das áreas STEEM
    
        for area in steem_list:

            nodes_list = nodes[nodes['area'] == area]['id_lattes'].tolist()
            
            G_sub = G.subgraph(nodes_list)
            if not without_leaves:
                gender_relationship_measures_list = graph_gender_relationship_measures(G_sub)
                gender_relationship_measures_list.insert(0, area)
                G_df.loc[len(G_df)] = gender_relationship_measures_list
            
            else:
                G_sub_without_leaves = graph_without_leaves(G_sub)
                gender_relationship_measures_without_leaves_list = graph_gender_relationship_measures(G_sub_without_leaves)
                gender_relationship_measures_without_leaves_list.insert(0, area)
                G_without_leaves_df.loc[len(G_without_leaves_df)] = gender_relationship_measures_without_leaves_list

    else:
        # Subgrafo da área STEEM

        nodes['area'] = nodes['area'].apply(lambda x: str(x).lower())
        nodes_list = nodes[(nodes['area']) == chosen_area]['id_lattes'].tolist()
        
        G_sub = G.subgraph(nodes_list)
        if not without_leaves:
            gender_relationship_measures_list = graph_gender_relationship_measures(G_sub)
            gender_relationship_measures_list.insert(0, chosen_area)
            G_df.loc[len(G_df)] = gender_relationship_measures_list
        
        else:
            G_sub_without_leaves = graph_without_leaves(G_sub)
            gender_relationship_measures_without_leaves_list = graph_gender_relationship_measures(G_sub_without_leaves)
            gender_relationship_measures_without_leaves_list.insert(0, chosen_area)
            G_without_leaves_df.loc[len(G_without_leaves_df)] = gender_relationship_measures_without_leaves_list

    
    return G_df if not without_leaves else G_without_leaves_df  


G_df = gender_relationship_measures(chosen_area, G)

print('\n' + '-'*5 + f'{chosen_area} - relacionamentos por combinação de gênero' + '-'*5)
print(G_df)

chosen_area = chosen_area.replace(" ", "_")

date = datetime.now().strftime("%d%m%Y_%H%M%S")

if not without_leaves:
    dir_path = f'gender_relationship_measures/with_leaves/{graph}'
else:
    dir_path = f'gender_relationship_measures/without_leaves/{graph}'

if not os.path.isdir(dir_path):
    os.makedirs(dir_path)

filename = unidecode(f'{chosen_area}_{date}_gender_relationship.csv')

G_df.to_csv(os.path.join(dir_path, filename), encoding='utf-8-sig', index=False)