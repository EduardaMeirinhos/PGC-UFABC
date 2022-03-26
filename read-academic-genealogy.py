import pandas as pd


# Importação do dataset referente às arestas e vértices da Genealogia Acadêmica (GA)

# Separação dos dados referente às arestas da GA

# Ler dados das arestas contendo o nome completo dos vértices de saíde e entrada
edges_full_name = pd.read_csv('full-name-v2-2020-08.csv', nrows=1404109)

# Selecionar colunas de interesse
edges_full_name = pd.DataFrame(edges_full_name, columns =['origem_id_lattes','destino_id_lattes', 'origem_nome','destino_nome','titulacao','ano_inicio','ano_conclusao','curso','instituicao','tese','grande_area','area'])

# Renomear as colunas
edges_full_name.columns = ['source_id_lattes','target_id_lattes','source_name','target_name','academic_degree','start_year','conclusion_year','course','institution','thesis','major_area','area']

# Exportar CSV das arestas contendo o nome completo dos vértices de saíde e entrada
edges_full_name.to_csv("edges_full_name.csv", index=False, encoding='utf-8-sig')


# Separação dos dados referente aos vértices da GA

# Ler dados dos vértices contendo o nome completo
nodes_full_name = pd.read_csv('full-name-v2-2020-08.csv', skiprows=1404110, nrows=1272590)

# Selecionar colunas de interesse
nodes_full_name = pd.DataFrame(nodes_full_name, columns =['id_lattes','nome','primeira_grande_area','primeira_area','dp','fcp','ftp','cp','gp','rp','gi'])

# Renomear as colunas
nodes_full_name.columns = ['id_lattes','name','major_area','area','descendants','fecundity','fertility','cousins','generations','relationships','genealogical_index']

# Exportar CSV dos vértices contendo seus respectivos nomes completos
nodes_full_name.to_csv("nodes_full_name.csv", index=False, encoding='utf-8-sig')

