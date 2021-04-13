#!/usr/bin/env python
# coding: utf-8

# Carrega as bibliotecas necessárias
import requests
import json
from bs4 import BeautifulSoup
import dataset
import time
import pandas as pd
from pathlib import Path
from datetime import datetime

# Define a URL inicial que será consultada para busca dos comentários
commentsUrl = 'https://www.instagram.com/graphql/query/?query_hash={}&variables={}'

# ### Obtendo variáveis de acesso
# 
# Duas variáveis são fundamentais para que consiga o acesso aos comentários do Instagram via XHR:
# 
# 1. **query_hash:** parâmetro para efetivar a requisição que busca os comentários;
# 2. **cookie:** guarda os dados de sessão/autenticação.
# 
# O valores das duas variáveis podem ser obtidos seguindo as seguintes instruções: https://github.com/andrejose/exporting-instagram-comments/blob/master/getting-variables.md
# 
# Após seguir as instruções acima, altere os valores das variáveis abaixo:
query_hash = ''
cookie = ''

# Inicia uma nova sessão (simula um acesso a uma página do Instagram)
session = requests.Session()
session.headers.update({
    'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' + ' (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36',
    'cookie' : cookie
})

# Função para pegar o total de comentários
def get_total_comments(self):
    try:
        return self['edge_media_to_parent_comment']['count']
    except KeyError:
        return self['edge_media_to_comment']['count']

# Função para pegar se há uma próxima página
def get_has_next_page(self):
    try:
        return self['edge_media_to_parent_comment']['page_info']['has_next_page']
    except KeyError:
        return self['edge_media_to_comment']['page_info']['has_next_page']

# Função para pegar o marcador final
def get_end_cursor(self):
    try:
        return self['edge_media_to_parent_comment']['page_info']['end_cursor']
    except KeyError:
        return self['edge_media_to_comment']['page_info']['end_cursor']

# Função para pegar os nós dos comentários
def get_edges(self):
    try:
        return self['edge_media_to_parent_comment']['edges']
    except KeyError:
        return self['edge_media_to_comment']['edges']

# Função que analisa o código retornado do servidor, coletando os dados dos comentários
def parse_comments(reply):
    # Cria variáveis globais para serem acessadas de fora da função
    global total_comments, has_next_page, end_cursor, postID
    # Cria uma lista vazia para inserir os comentários da página
    comments = []

    # Converte o conteúdo retornado para um objeto JSON
    jsonObj = json.loads(reply)

    # Identifica dentro do objeto JSON, dados necessários para a navegação e exploração das páginas posteriores
    # Total de comentários
    totalComments = get_total_comments(jsonObj['data']['shortcode_media'])
    # Se possui uma próxima página a ser explorada
    hasNextPage = get_has_next_page(jsonObj['data']['shortcode_media'])
    # Marcador que indicar o início da próxima página
    endCursor = get_end_cursor(jsonObj['data']['shortcode_media'])
    # Nós que correspondem aos comentários da página atual
    edges = get_edges(jsonObj['data']['shortcode_media'])

    # Atualizando as variáveis globais
    total_comments = totalComments 
    has_next_page = hasNextPage
    end_cursor = endCursor
    
    # Repetição para percorrer os comentários da página
    for i in edges:
        # Identifica os dados a serem coletados do comentário 
        commentId = i['node']['id']
        commentText = i['node']['text']
        commentDate = i['node']['created_at']
        userId = i['node']['owner']['id']
        userPic = i['node']['owner']['profile_pic_url']
        userUsername = i['node']['owner']['username']
        
        # Na lista de comentários, adiciona um novo registro referente ao comentário atual
        comments.append({'commentId': commentId,
            'commentText': commentText,
            'commentDate': commentDate,
            'userId': userId,
            'userPic': userPic,
            'userUsername': userUsername,
            'postId': postID})

    # Após percorrer todos os comentários da página, retorna a lista com o conteúdo extraído
    return comments

# Função que busca os comentários de uma determinada página
def get_comments(post_id, after = '', qh = query_hash):
    # Dados enviados pela requisição
    data = {
        'shortcode':post_id,
        'after':after,
        'first':100
    }
    # Converte os dados para uma variável literal que será enviada pela URL
    dataString = json.dumps(data)
    # Formata a URL final com os dados
    finalUrl = commentsUrl.format(qh, dataString)
    
    # Realiza a requisição
    r = session.get(finalUrl)
    # Identifica os comentários, enviando a resposta da requisição à função parse_comments()
    comments = parse_comments(r.text)
    # Retorna os comentários formatados
    return comments

# Lê o arquivo CSV que contém os posts cujos comentários serão exportados salvando os dados em um data frame
posts_df = pd.read_csv("./posts.csv", sep=";")

# Exibe as cinco primeiras linhas do data frame
posts_df.head()

# Repetição para percorrer todas os posts contidos no data frame
for i in range(len(posts_df)):
    # Identifica a ID do post cujos comentários serão exportados
    postID = posts_df['URL'][i].split("/")[-2]
    # Faz uma requisição, simulando um acesso à página do post
    session.get('https://www.instagram.com/p/{}/'.format(postID))    
    
    # Imprime na tela uma mensagem que o post está sendo "raspado"
    print('=========================================')
    print('Scraping post: ', postID)
    
    # Identifica a qual marca o post pertence
    marca = posts_df['Marca'][i]
    # Define a variável global do total de comentários como zero
    total_comments = 0
    # Define que há uma nova página a ser explorada
    has_next_page = True
    # Define como vazio o marcador de próxima página
    end_cursor = ''
    # Define a página atual como 1    
    page = 1
    # Cria uma lista vazia que conterá todos os comentários do post
    all_comments = []
    
    # Enquando a variável has_next_page for verdadeira, o bloco de ação é executado
    while has_next_page:
        # Imprime na tela qual página está sendo explorada
        print('=========================================')
        print('Page', page, ' - End cursor: ', end_cursor)
        print('=========================================')
        
        # Cria uma variável com os comentários, utilizando a funçao get_comments()
        comments = get_comments(postID, end_cursor)
        
        # Se não há comentários, encerra a repetição
        if not comments:
            break

        # Imprime a quantidade de comentários na página
        print('Comments in page:', len(comments))

        # Verifica se já existe comentários na lista all_comments
        if (len(all_comments)):
            # Se sim, apenas adiciona os novos comentários à lista
            all_comments = all_comments + comments
        else:
            # Caso contrário, a lista é igual aos comentários extraídos
            all_comments = comments
            
        # Incrementa a variável página
        page += 1
        # Pausa o programa por três segundos, para evitar um acesso massivo ao servidor
        time.sleep(3)
    
    # Converte a lista com todos os comentários de um post para um data frame 
    commentsDf = pd.DataFrame(all_comments, columns=['commentId', 'commentText', 'commentDate', 'userId', 'userPic', 'userUsername', 'postId'])
    # Cria uma nova coluna com a data formatada dos comentários
    commentsDf['commentDateFormatted'] = pd.to_datetime(commentsDf['commentDate'], unit='s')
    
    # Caso não exista, cria um novo diretório com a marca para salvar os arquivos que serão exportados
    Path('./exports/'+marca).mkdir(parents=True, exist_ok=True)
    
    # Exporta o data frame com todos os comentários para um planilha Excel
    commentsDf.to_excel('./exports/'+marca+'/comments-post-'+postID+'.xlsx')  

    # Pausa o programa por três segundos, para evitar um acesso massivo ao servidor
    time.sleep(3)