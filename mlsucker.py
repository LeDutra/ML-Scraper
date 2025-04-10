import csv
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random

def get_price(node):

    price_node = node.find('span', class_='andes-money-amount__fraction')
    cents_node = node.find('span', class_='andes-money-amount__cents')
    
    if price_node is not None:
        price = price_node.text.strip()
        if cents_node is not None:
            price = price + ',' + cents_node.text.strip()
        return price
    return None

def remove_duplicates(products):
    unique_products = []
    duplicate_products = []

    seen_titles = set()
    seen_descriptions = set()

    for product in products:
        title = product[3]
        description = product[8]
        value = product[26]

        if (title, description) in seen_titles and (title, value) in seen_descriptions:
            duplicate_products.append(product)
        else:
            seen_titles.add((title, description))
            seen_descriptions.add((title, value))
            unique_products.append(product)

    return unique_products, duplicate_products

i = 1

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:25.0) Gecko/20100101 Firefox/25.0'}
termo_busca = input("Digite o termo de busca: ")

base_url = f"https://lista.mercadolivre.com.br/{termo_busca}"

# Caminho e nome do arquivo CSV
nome_arquivo = f"dados_produtos_ml_{termo_busca[:10]}.csv"
caminho_arquivo = os.path.abspath(nome_arquivo)

# Listas para armazenar produtos e duplicatas
products = []

with open(nome_arquivo, mode='w', newline='', encoding='utf-8') as arquivo_csv:
    writer = csv.writer(arquivo_csv, delimiter=',')
    writer.writerow([
        'Ordem', 'Titulo', 'Preco' #, 'Frete Grátis', 'URL', 'Descrição'
    ])

    while True:
        try:
            page = requests.get(base_url, headers=headers)
            soup = BeautifulSoup(page.text, "html.parser")

            for div in soup.find_all('div', class_='ui-search-result__wrapper'):
                produto = div.find('a', class_='poly-component__title')
                link = produto.get('href')
                titulo = produto.next_element
                preco = get_price(div)
                frete_gratis = bool(div.find("p", class_="ui-search-item__shipping ui-search-item__shipping--free"))

                if link is not None:
                    response_produto = requests.get(link, headers=headers)
                else:
                    continue

                site_produto = BeautifulSoup(response_produto.text, 'html.parser')
                descricao = site_produto.find('p', class_='ui-pdp-description__content')

                if descricao != None:
                    descricao_text = '<h1>' + produto.next_element + '</h1>\n\n' + descricao.text.strip()
                else:
                    descricao_text = "Vendedor não inseriu descrição."
                    
         #       if site_produto.find('symbol', id_='full_icon') != None:
         #           envio_full = 'Não'
         #       else:
         #           envio_full = 'Sim'

                writer.writerow([
                    i, titulo, preco #, frete_gratis, link, descricao_text
                ])

                products.append([
                    i, titulo, preco #, frete_gratis, link, descricao_text
                ])

                print('Codigo: ' + str(i) + ', Produto: ' + titulo + ', Valor: ' + str(preco))
                print("==========================")

                i += 1

            next_link = soup.select_one("a.andes-pagination__link:-soup-contains(Seguinte)")

            if not next_link:
                break
            
            next_url = next_link.get('href')
            base_url = next_url

            # Aguardar um tempo aleatório entre 0.5 e 2.5 segundos entre as solicitações para evitar o bloqueio por sobrecarga no servidor
            time.sleep(random.uniform(0.5, 2.5))

        except ConnectionError as e:
            print("Ocorreu um erro de conexão:", e)

            print("Arquivo CSV salvo com sucesso:")
            print(caminho_arquivo)

            break

print("Arquivo CSV salvo com sucesso:")
print(caminho_arquivo)
