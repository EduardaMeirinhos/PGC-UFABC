import networkx as nx
import pandas as pd


# Geração do grafo da Genealogia Acadêmica (GA)
def create_graph():

    # Criar um multidígrafo vazio
    G = nx.Graph()

    # Ler os dados dos vértices da genealogia acadêmica
    nodes = pd.read_csv(r"nodes_full_name_gender.csv")

    # Atribuir os vértices e seus respectivos atributos ao grafo
    attrs = {}
    for i, nlrow in nodes.iterrows():
        G.add_node(nlrow['id_lattes'])
        attrs[nlrow['id_lattes']] = nlrow[1:].to_dict()
    nx.set_node_attributes(G, attrs)

    # Ler os dados das arestas da genealogia acadêmica
    edges = pd.read_csv(r"edges_full_name.csv")

    # Atribuir as arestas e seus respectivos atributos ao grafo
    attrs_edge = {}
    for i, elrow in edges.iterrows():
        G.add_edge(elrow[0], elrow[1])
        attrs_edge[(elrow[0], elrow[1])] = elrow[2:].to_dict()
    nx.set_edge_attributes(G, attrs_edge)

    # Gerar o grafo sem os vértices com gênero não identificado
    G_without_unidentified_gender = graph_without_unidentified_gender(G, "Não identificado")

    return G, G_without_unidentified_gender


# Gerar o grafo sem os vértices com gênero não identificado
def graph_without_unidentified_gender(G, gender):
    G_copy = G.copy()

    # Criar uma lista dos vértices com gênero não identificado
    gender_nodes = [node for node in G_copy.nodes(data='gender') if node[1] == gender]

    # Remover vértices que não tiveram o gênero identificado
    G_copy.remove_nodes_from([n[0] for n in gender_nodes])

    return G_copy


# Gerar o grafo sem vértices folha
def graph_without_leaves(G):
    G_copy = G.copy()
    
    # Criar uma lista dos vértices folha do grafo
    #leaf_nodes = [node for node in G_copy.nodes() if G_copy.in_degree(node) != 0 and G_copy.out_degree(node) == 0]
    leaf_nodes = [node for node in G_copy.nodes() if G_copy.degree(node) == 1]

    # Remover vértices folha do grafo
    G_copy.remove_nodes_from(leaf_nodes)
    
    return G_copy


# Gerar o dataframe dos nós do grafo contendo apenas o id_lattes e a área
def graph_nodes(nodes):
    nodes = pd.DataFrame(list(nodes), columns=['id_lattes','area'])
    return nodes


# Áreas STEEM
def steem_areas():
    steem_list = ['Astronomia','Biofísica','Biologia Geral','Bioquímica','Botânica','Ciência Da Computação','Ecologia','Economia','Engenharia Aeroespacial','Engenharia Agrícola','Engenharia Biomédica','Engenharia Civil','Engenharia De Materiais E Metalúrgica','Engenharia De Minas','Engenharia De Produção','Engenharia De Transportes','Engenharia Elétrica','Engenharia Mecânica','Engenharia Naval E Oceânica','Engenharia Nuclear','Engenharia Química','Engenharia Sanitária','Farmacologia','Física','Fisiologia','Genética','Geociências','Imunologia','Matemática','Microbiologia','Morfologia','Oceanografia','Parasitologia','Probabilidade E Estatística','Química','Zoologia']
    return steem_list