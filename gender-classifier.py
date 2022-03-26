import pandas as pd
import numpy as np
from tqdm import tqdm
from unidecode import unidecode
from sklearn.preprocessing import OneHotEncoder
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import cross_val_score


# Elaboração do classificador de gênero (feminino e masculino) para rotulação do gênero dos vértices da Genealogia Acadêmica (GA)

# Importação do dataset do dicionário de nomes

# Ler CSV retirado de "Brasil.io - Gênero dos Nomes" (https://brasil.io/dataset/genero-nomes/nomes/)
raw_names = pd.read_csv('nomes.csv')

# Criar dataset principal contendo "nome" vs o "gênero"  
names = raw_names[['first_name', 'classification']]
names.columns = ['name', 'gender']

# Pré-processamento dos dados do dicionário de nomes
names = names.copy()

# Aplicar caixa baixa em todos os nomes
names['name'] = names['name'].apply(lambda x: x.lower())

# Codificar os gêneros -> M (masculino) é codificado com valor 0, F (feminino) é codificado com valor 1
names['gender'] = names['gender'].apply(lambda x: 0 if x == 'M' else 1)

# Distribuição de nomes classificados com o gênero feminino e masculino
name_f_dict_total = names['gender'].value_counts()[1]
name_m_dict_total = names['gender'].value_counts()[0]
name_total = name_f_dict_total+name_m_dict_total

print(f"Total de nomes femininos no dicionário de nomes: {name_f_dict_total} ({round(name_f_dict_total/name_total*100,2)}%)")
print(f"Total de nomes masculinos no dicionário de nomes: {name_m_dict_total} ({round(name_m_dict_total/name_total*100,2)}%)")
print(f"Total de nomes no dicionário de nomes: {name_total} ({round(name_total/name_total*100,2)}%)")


# Extração de features

# As features são definidas como a seguir:
# última letra do nome (ul)
# duas últimas letra do nome (2ul)
# três últimas letras do nome (3ul)
names['ul'] = names['name'].apply(lambda x: x[-1:])
names['2ul'] = names['name'].apply(lambda x: x[-2:])
names['3ul'] = names['name'].apply(lambda x: x[-3:])


# Divisão do dataset do dicionário de nomes entre features/atributos (X) e label/classe (y)

#features
X_data = np.array(names[['ul', '2ul', '3ul']])

#label
y_data = np.array(names['gender'])


# Codificação dos dados utilizando One-hot encoding

# Aplicar OneHotEncoder para transformar os valores categóricos das features em valores numéricos (cria uma coluna binária para cada valor único)
onehot_encoder = OneHotEncoder(categories = "auto", handle_unknown = "ignore")
X_data = onehot_encoder.fit_transform(X_data).toarray()

print('Número total de features após OneHotEncoder: ' + str(X_data.shape[1]))


#  Redução de dimensionalidade aplicando Linear Discriminant Analysis - LDA

# Aplicar Linear Discriminant Analysis - LDA (extrai uma única feature a partir da codificação do OneHotEncoder)
lda = LinearDiscriminantAnalysis(n_components=1)
lda = lda.fit(X_data, y_data)
X_data = lda.transform(X_data)

print('Número total de features após LDA: ' + str(X_data.shape[1]))
print('Explained variance ratio: ' + str(lda.explained_variance_ratio_))


#  Criação e Validação do modelo utilizando Naive Bayes

# Aplicação de validação cruzada para criação e avaliação do modelo (k-fold)
NB_classifier = GaussianNB()
scores = cross_val_score(NB_classifier, X_data, y_data, cv=30)

print("Naive Bayes: %0.2f acurácia com desvio padrão de %0.2f" % (scores.mean(), scores.std()))


#  Elaboração do classificador de gênero (final) utilizando o dicionário de nomes e o modelo Naive Bayes

NB_classifier = NB_classifier.fit(X_data, y_data)

# Criar dicionário a partir do dataframe (tempo O(1) para varredura do dicionário - verificar se o nome de entrada existe)
dict_names = names[['name', 'gender']].set_index('name').to_dict()
dict_names = dict_names['gender']


# Criar classe para armazenar todas as informações referentes à classificação de gênero de um certo nome de entrada
class PredictedGender():
    def __init__(self):
        self.prob_1st_name = [0,0]
        self.prob_2sd_name = [0,0]
        self.which_method = 'Nenhum'
        self.which_name = 0
        self.gender = 'Não identificado'


# Função auxiliar para aplicar caixa baixa e remover palavras com menos de duas letras para um certo nome de entrada
def valid_name_preprocessing(fullname):
    fullname = fullname.lower()
    fullname = unidecode(fullname)
    fullname_preprocessed = ' '.join([name for name in fullname.split(' ') if len(name) > 2])
    return fullname_preprocessed


# Classificador de gênero utilizando o dicionário de nomes e o modelo Naive Bayes
def predict_gender(fullname):
    predicted_gender = PredictedGender()
    fullname = valid_name_preprocessing(fullname)
    # Ver se o primeiro nome está no dicionário
    try:
        firstname = fullname.split()[0]
    # Caso não tenha primeiro nome, simplesmente considerar gênero não identificado
    except Exception as e:
        return predicted_gender
    
    dict_names_classification = dict_names.get(firstname)
    # Se encontrou o primeiro nome no dicionário
    if not dict_names_classification is None:
        # Se o primeiro nome está no dicionário classificado como FEMININO
        if dict_names_classification == 1:
            predicted_gender.prob_1st_name = [0, 1]
        # Se o primeiro nome está no dicionário classificado como MASCULINO
        else:
            predicted_gender.prob_1st_name = [1, 0]
        predicted_gender.which_name = 1
        predicted_gender.gender = 'Feminino' if dict_names_classification == 1 else 'Masculino'
        predicted_gender.which_method = 'Dicionário'
        return predicted_gender
    
    # Se não encontrou o primeiro nome no dicionário, avaliar probabilidades do primeiro nome pelo modelo Naive Bayes
    # Criando dados de entrada (X) que serão avaliados no modelo
    data = pd.DataFrame([firstname], columns=['name'])
    # Criando as features (ultimo letra, duas ultimas letras e três ultimas letras)
    data['ul'] = data['name'].apply(lambda x: x[-1:])
    data['2ul'] = data['name'].apply(lambda x: x[-2:])
    data['3ul'] = data['name'].apply(lambda x: x[-3:])
    data = np.array(data[['ul', '2ul', '3ul']])
    # Aplicando o OneHotEncoder nas features -> transforma as features em muitas colunas binárias
    data = onehot_encoder.transform(data).toarray()
    # Aplicando o Linear Discriminant Analysis (redução de dimensionalidade) -> comprime a informação em uma só coluna
    data = lda.transform(data)
    # Realizando a predição das probabilidades a partir do modelo Naive Bayes
    predicted_gender.prob_1st_name = NB_classifier.predict_proba(data)[0].tolist()
    # Se a probabilidade da classificação ser 0 (MASCULINO) for maior ou igual a 90%
    if predicted_gender.prob_1st_name[0] >= 0.90:
        predicted_gender.which_name = 1
        predicted_gender.gender = 'Masculino'
        predicted_gender.which_method = 'Naive Bayes'
        return predicted_gender
    # Se a probabilidade da classificação ser 1 (FEMININO) for maior ou igual a 90%
    elif predicted_gender.prob_1st_name[1] >= 0.90:
        predicted_gender.which_name = 1
        predicted_gender.gender = 'Feminino'
        predicted_gender.which_method = 'Naive Bayes'
        return predicted_gender
    
    # Se ambas as probabilidades do primeiro nome foram menores que 90%, ver se o segundo nome está no dicionário
    try:
        secondname = fullname.split()[1]
    # Caso não tenha segundo nome, simplesmente considerar gênero não identificado
    except Exception as e:
        return predicted_gender
        
    dict_names_classification = dict_names.get(secondname)
    # Se encontrou o segundo nome no dicionário
    if not dict_names_classification is None:
        # Se o segundo nome está no dicionário classificado como FEMININO
        if dict_names_classification == 1:
            predicted_gender.prob_2sd_name = [0, 1]
        # Se o segundo nome está no dicionário classificado como MASCULINO
        else:
            predicted_gender.prob_2sd_name = [1, 0]
        predicted_gender.which_name = 2
        predicted_gender.gender = 'Feminino' if dict_names_classification == 1 else 'Masculino'
        predicted_gender.which_method = 'Dicionário'
        return predicted_gender

    # Se não encontrou o segundo nome no dicionário, avaliar probabilidades do segundo nome pelo modelo Naive Bayes
    # Criando dados de entrada (X) que serão avaliados no modelo
    data = pd.DataFrame([secondname], columns=['name'])
    # Criando as features (ultimo letra, duas ultimas letras e três ultimas letras)
    data['ul'] = data['name'].apply(lambda x: x[-1:])
    data['2ul'] = data['name'].apply(lambda x: x[-2:])
    data['3ul'] = data['name'].apply(lambda x: x[-3:])
    data = np.array(data[['ul', '2ul', '3ul']])
    # Aplicando o OneHotEncoder nas features -> transforma as features em muitas colunas binárias
    data = onehot_encoder.transform(data).toarray()
    # Aplicando o Linear Discriminant Analysis (redução de dimensionalidade) -> comprime a informação em uma só coluna
    data = lda.transform(data)
    # Realizando a predição das probabilidades a partir do modelo Naive Bayes
    predicted_gender.prob_2sd_name = NB_classifier.predict_proba(data)[0].tolist()
    # Se a probabilidade da classificação ser 0 (MASCULINO) for maior ou igual a 90%
    if predicted_gender.prob_2sd_name[0] >= 0.90:
        predicted_gender.which_name = 2
        predicted_gender.gender = 'Masculino'
        predicted_gender.which_method = 'Naive Bayes'
        return predicted_gender
    # Se a probabilidade da classificação ser 1 (FEMININO) for maior ou igual a 90%
    elif predicted_gender.prob_2sd_name[1] >= 0.90:
        predicted_gender.which_name = 2
        predicted_gender.gender = 'Feminino'
        predicted_gender.which_method = 'Naive Bayes'
        return predicted_gender    
    
    # Se ambas as probabilidades do segundo nome foram menores que 90%, então o gênero será considerado como não-identificado
    return predicted_gender


# Realização da classificação dos gêneros dos vértices da GA

#  Importação do dataset de vértices da GA

# Ler os dados dos vértices da genealogia acadêmica (GA) contendo o nome completo dos acadêmicos
nodes_full_name = pd.read_csv('nodes_full_name.csv')

# Armazenar todos os nomes dos vértices em uma lista
nodes_names = nodes_full_name['name'].tolist()


#  Rotulação dos gêneros dos vértices da GA

# Aplicar função para realizar a classificação de gênero
predicted_genders = [predict_gender(x) for x in tqdm(nodes_names, desc="TQDM")]

# Criar lista do resultado da classificação de gênero dos vértices 
predicted_genders_list = []
for x in predicted_genders:        
    predicted_genders_list.append([round(x.prob_1st_name[0], 2),round(x.prob_1st_name[1], 2),round(x.prob_2sd_name[0], 2),round(x.prob_2sd_name[1], 2),x.which_name,x.which_method,x.gender])


# Criar dataframe para armazenar os resultados da classicação de gênero dos vértices
predicted_genders_df = pd.DataFrame(predicted_genders_list, columns = ['prob_1st_name_m', 'prob_1st_name_f', 'prob_2sd_name_m','prob_2sd_name_f','which_name','which_method','gender'])


# Concatenar os dados dos vértices com o dados de classificação de gênero 
nodes_gender = pd.concat([nodes_full_name, predicted_genders_df], axis=1, join="inner")


#  Exportação dos vértices da GA com seus respectivos gêneros rotulados

# Exportar os vértices com suas respectivas classificações de gênero
nodes_gender.to_csv("nodes_full_name_gender.csv", index=False, encoding='utf-8-sig')


#  Números a respeito da classificação dos gêneros dos vértices da GA

# Total de vértices rotulados
total_nodes = len(nodes_gender)
print(f'Total de vértices: {total_nodes}')


# Total de classificações realizadas através do primeiro nome, segundo nome e classificações inviáveis
first_name_total = nodes_gender['which_name'].value_counts()[1]
second_name_total = nodes_gender['which_name'].value_counts()[2]
none_name_total = nodes_gender['which_name'].value_counts()[0]

print(f"Total de classificações pelo 1º nome: {first_name_total} ({round(first_name_total/total_nodes*100,2)}%)")
print(f"Total de classificações pelo 2º nome: {second_name_total} ({round(second_name_total/total_nodes*100,2)}%)")
print(f"Total de classificações inviáveis (gênero não identificado): {none_name_total} ({round(none_name_total/total_nodes*100,2)}%)")


#  Total de pessoas classificadas com o gênero masculino, feminino e sem o gênero identificado
masculine_gender_total = nodes_gender['gender'].value_counts()['Masculino']
feminine_gender_total = nodes_gender['gender'].value_counts()['Feminino']
unidentified_gender_total = nodes_gender['gender'].value_counts()['Não identificado']

print(f"Total de pessoas classificadas como gênero masculino: {masculine_gender_total} ({round(masculine_gender_total/total_nodes*100,2)}%)")
print(f"Total de pessoas classificadas como gênero feminino: {feminine_gender_total} ({round(feminine_gender_total/total_nodes*100,2)}%)")
print(f"Total de pessoas classificadas como gênero não identificado: {unidentified_gender_total} ({round(unidentified_gender_total/total_nodes*100,2)}%)")


# Análise da quantidade de classificações de gênero realizadas utilizando somente o dicionário de nomes
prob_1st_name_m_dict_total = nodes_gender[(nodes_gender['gender'] == 'Masculino') & (nodes_gender['which_name'] == 1) & (nodes_gender['which_method'] == 'Dicionário')].shape[0]
prob_1st_name_f_dict_total = nodes_gender[(nodes_gender['gender'] == 'Feminino') & (nodes_gender['which_name'] == 1) & (nodes_gender['which_method'] == 'Dicionário')].shape[0]
prob_2sd_name_m_dict_total = nodes_gender[(nodes_gender['gender'] == 'Masculino') & (nodes_gender['which_name'] == 2) & (nodes_gender['which_method'] == 'Dicionário')].shape[0]
prob_2sd_name_f_dict_total = nodes_gender[(nodes_gender['gender'] == 'Feminino') & (nodes_gender['which_name'] == 2) & (nodes_gender['which_method'] == 'Dicionário')].shape[0]

print(f"Total de pessoas classificadas pelo 1º nome como gênero masculino a partir do dicionário de nomes: {prob_1st_name_m_dict_total} ({round(prob_1st_name_m_dict_total/total_nodes*100,2)}%)")
print(f"Total de pessoas classificadas pelo 1º nome como gênero feminino a partir do dicionário de nomes: {prob_1st_name_f_dict_total} ({round(prob_1st_name_f_dict_total/total_nodes*100,2)}%)")
print(f"Total de pessoas classificadas pelo 2º nome como gênero masculino a partir do dicionário de nomes: {prob_2sd_name_m_dict_total} ({round(prob_2sd_name_m_dict_total/total_nodes*100,2)}%)")
print(f"Total de pessoas classificadas pelo 2º nome como gênero feminino a partir do dicionário de nomes: {prob_2sd_name_f_dict_total} ({round(prob_2sd_name_f_dict_total/total_nodes*100,2)}%)")

print('\n')

print(f"Total de pessoas classificadas pelo 1º nome através do dicionário de nomes: {prob_1st_name_m_dict_total+prob_1st_name_f_dict_total} ({round((prob_1st_name_m_dict_total+prob_1st_name_f_dict_total)/total_nodes*100,2)}%)")
print(f"Total de pessoas classificadas pelo 2º nome através do dicionário de nomes: {prob_2sd_name_m_dict_total+prob_2sd_name_f_dict_total} ({round((prob_2sd_name_m_dict_total+prob_2sd_name_f_dict_total)/total_nodes*100,2)}%)")

print('\n')

gender_classified_by_dict_names = prob_1st_name_m_dict_total+prob_1st_name_f_dict_total+prob_2sd_name_m_dict_total+prob_2sd_name_f_dict_total

print(f"Total de classificações realizadas a partir do dicionário de nomes: {gender_classified_by_dict_names} ({round(gender_classified_by_dict_names/total_nodes*100,2)}%) - acurácia aproximada da classificação de gênero utilizando o dicionário de nomes e naive bayes")


# Análise da quantidade de classificações de gênero realizadas utilizando o modelo Naive Bayes
prob_1st_name_m_nb_total = nodes_gender[(nodes_gender['gender'] == 'Masculino') & (nodes_gender['which_name'] == 1) & (nodes_gender['which_method'] == 'Naive Bayes')].shape[0]
prob_1st_name_f_nb_total = nodes_gender[(nodes_gender['gender'] == 'Feminino') & (nodes_gender['which_name'] == 1) & (nodes_gender['which_method'] == 'Naive Bayes')].shape[0]
prob_2sd_name_m_nb_total = nodes_gender[(nodes_gender['gender'] == 'Masculino') & (nodes_gender['which_name'] == 2) & (nodes_gender['which_method'] == 'Naive Bayes')].shape[0]
prob_2sd_name_f_nb_total = nodes_gender[(nodes_gender['gender'] == 'Feminino') & (nodes_gender['which_name'] == 2) & (nodes_gender['which_method'] == 'Naive Bayes')].shape[0]

print(f"Total de pessoas classificadas pelo 1º nome como gênero masculino a partir do modelo Naive Bayes: {prob_1st_name_m_nb_total} ({round(prob_1st_name_m_nb_total/total_nodes*100,2)}%)")
print(f"Total de pessoas classificadas pelo 1º nome como gênero feminino a partir do modelo Naive Bayes: {prob_1st_name_f_nb_total} ({round(prob_1st_name_f_nb_total/total_nodes*100,2)}%)")
print(f"Total de pessoas classificadas pelo 2º nome como gênero masculino a partir do modelo Naive Bayes: {prob_2sd_name_m_nb_total} ({round(prob_2sd_name_m_nb_total/total_nodes*100,2)}%)")
print(f"Total de pessoas classificadas pelo 2º nome como gênero feminino a partir do modelo Naive Bayes: {prob_2sd_name_f_nb_total} ({round(prob_2sd_name_f_nb_total/total_nodes*100,2)}%)")

print('\n')

print(f"Total de pessoas classificadas pelo 1º nome através do modelo Naive Bayes: {prob_1st_name_m_nb_total+prob_1st_name_f_nb_total} ({round((prob_1st_name_m_nb_total+prob_1st_name_f_nb_total)/total_nodes*100,2)}%)")
print(f"Total de pessoas classificadas pelo 2º nome através do modelo Naive Bayes: {prob_2sd_name_m_nb_total+prob_2sd_name_f_nb_total} ({round((prob_2sd_name_m_nb_total+prob_2sd_name_f_nb_total)/total_nodes*100,2)}%)")

print('\n')

gender_classified_by_nb = prob_1st_name_m_nb_total+prob_1st_name_f_nb_total+prob_2sd_name_m_nb_total+prob_2sd_name_f_nb_total

print(f"Total de classificações realizadas a partir do modelo naive bayes: {gender_classified_by_nb} ({round(gender_classified_by_nb/total_nodes*100,2)}%)")

