# birdie-crawler
Desenvolvendo um sistema ETL com alta performance e foco em escalabilidade para coletar dados de sites populares de venda online

## Instalação
> WIP

## Introdução
A arquitetura deste sistema é relativamente simples.
- Os dados são coletados por um ou vários crawlers, dependendo da configuração do Docker do `scrapy-crawler`, que trabalharão paralelamente coletando o conteúdo das 40.000 urls dadas em `offers.csv`.
- Os dados coletados e organizados em formato JSON são armazenados no banco de dados do sistema, um MongoDB(visto que os dados não são necessariamente iguais em estrutura), também rodando em Docker.
- Finalmente, tendo os dados armazenados no banco, poderemos então servir uma API de consulta e pesquisa por categoria, preço e nome de produtos.

