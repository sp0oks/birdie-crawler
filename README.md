# birdie-crawler
Desenvolvendo um sistema ETL com foco em performance em escalabilidade para coletar dados de sites populares de venda online.

## Introdução
A arquitetura deste sistema é relativamente simples:
- Os dados são coletados por um ou vários crawlers, dependendo da configuração do Docker do `crawler`, que trabalharão em paralelo coletando o conteúdo das 40.000 urls dadas em `offers.csv`.
- Os dados coletados e organizados em formato JSON são armazenados no banco de dados do sistema, um MongoDB (visto que os dados não são estruturados).
- Finalmente, tendo os dados armazenados no banco, poderemos então servir uma API de consulta e pesquisa por categoria, preço e nome de produtos.

## Estrutura
Apesar dos dados não serem exatamente estruturados, foi usado um esqueleto de Item para a coleta dos mesmos, que consiste de:
- URL da oferta
- Categoria do produto 
- Título da oferta
- Disponibilidade da oferta
- Moeda em que está sendo anunciada a oferta
- Preço da oferta
- Descrição do produto
- Características do produto

## Instalação
Não é necessário instalar nada além do `docker-compose` para executar o sistema, todo o resto da configuração é feito pelo Docker.

## Configuração
É opcional, mas as configurações do Flask e Scrapy podem ser alteradas em `flask-api/config.py` e `ofertascrawler/ofertascrawler/settings.py`, respectivamente.

## Execução
O sistema pode ser executado por completo com `docker-compose up`, ou apenas alguns serviços com `docker-compose up <serviço>`.
Para consultar a API, utilize os endpoints dados em `/`.

## Benchmark
Com a configuração default (1 processo e 8 spiders), foi possível coletar ~23.000 itens em média (de 40.000 urls) no período de 5 horas.
