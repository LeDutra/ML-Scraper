#!/usr/local/bin/python
# coding: latin-1
import csv
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import random

def get_price(node):
    # Função para obter o preço do nó da página
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

        # Verificar se o título e descrição já foram vistos
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

# Valores padrão do WooCommerce
published_default = '1'  # Publicado, 0 para Não Publicado
is_featured_default = '0'  # Não é destaque
visibility_default = 'visible'  # Visível no catálogo
short_description_default = ''  # Descrição curta em branco
date_sale_price_starts_default = ''  # Data de início da promoção em branco
date_sale_price_ends_default = ''  # Data de término da promoção em branco
tax_status_default = 'none'  # Não Tributável
tax_class_default = ''  # Classe de imposto em branco
in_stock_default = '1'  # Em estoque
stock_default = ''  # Quantidade em estoque em branco
low_stock_amount_default = ''  # Quantidade baixa em estoque em branco
backorders_allowed_default = 'no'  # Backorders não permitidos
sold_individually_default = 'yes'  # Vendido individualmente
weight_default = ''  # Peso em branco
length_default = ''  # Comprimento em branco
width_default = ''  # Largura em branco
height_default = ''  # Altura em branco
allow_customer_reviews_default = 'no'  # Avaliações de clientes não permitidas
purchase_note_default = ''  # Nota de compra em branco
shipping_class_default = ''  # Classe de envio em branco
download_limit_default = ''  # Limite de download em branco
download_expiry_days_default = ''  # Dias de expiração do download em branco
parent_default = ''  # Produto pai em branco
grouped_products_default = ''  # Produtos agrupados em branco
upsells_default = ''  # Upsells em branco
cross_sells_default = ''  # Cross-sells em branco
external_url_default = ''  # URL externa em branco
button_text_default = ''  # Texto do botão em branco
position_default = ''  # Posição em branco
attribute_name_default = ''  # Nome do atributo em branco
attribute_value_default = ''  # Valor do atributo em branco
attribute_visible_default = ''  # Visibilidade do atributo em branco
attribute_global_default = ''  # Global do atributo em branco
attribute_default_default = ''  # Valor padrão do atributo em branco

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
