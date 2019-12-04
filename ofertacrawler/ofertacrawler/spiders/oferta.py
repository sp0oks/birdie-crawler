# -*- coding: utf-8 -*-
import scrapy
import w3lib
import re

URL_CASAS_BAHIA = re.compile(r'casasbahia')
URL_MAGAZINE_LUIZA = re.compile(r'magazineluiza')
URL_MERCADO_LIVRE_PROD = re.compile(r'produto\.mercadolivre')
URL_MERCADO_LIVRE = re.compile(r'mercadolivre')


class OfertaSpider(scrapy.Spider):
    name = 'oferta'
    allowed_domains = ['www.casasbahia.com.br', 'produto.mercadolivre.com.br', 'www.mercadolivre.com.br', 'www.magazineluiza.com.br']

    def __init__(self, urlfile=None):
        if urlfile:
            with open(urlfile, 'r') as urls:
                self.start_urls = [url.strip() for url in urls.readlines()]

    def parse(self, response):
        if re.search(URL_CASAS_BAHIA, response.url):
            yield scrapy.Request(response.url, callback=self.parse_casas_bahia)
        elif re.search(URL_MAGAZINE_LUIZA, response.url):
            yield scrapy.Request(response.url, callback=self.parse_magazine_luiza)
        elif re.search(URL_MERCADO_LIVRE_PROD, response.url):
            yield scrapy.Request(response.url, callback=self.parse_produto_mercado_livre)
        elif re.search(URL_MERCADO_LIVRE, response.url):
            yield scrapy.Request(response.url, callback=self.parse_mercado_livre)

    def parse_casas_bahia(self, response):
            if response.css('.page-not-found').get():
                pass
            else:
                dominio = response.url.split('/')[2]
                categoria = response.css('.breadcrumb a span::text').getall()[1]
                titulo = response.css('.produtoNome h1.name b::text').get()
            
                preco_tag = response.css('#ctl00_Conteudo_ctl00_precoPorValue')
                preco = ' '.join([preco_tag.css('::text').get(), preco_tag.css('i::text').get()])
            
                detalhes = response.css('.detalhesProduto')
                descricao = detalhes.xpath('.//div[re:test(@class, "descricao")]/p/text()').get().strip()
                
                tabela_info = detalhes.css('.caracteristicasGerais').xpath('./div/dl')
                caracteristicas = {}
                # Caracteristicas são dispostas em <dl> com chave em <dt> e valores em <dd>
                for div in tabela_info:
                    key = div.xpath('./dt/text()').get().strip()
                    values = div.xpath('./dd/text()').get().strip()
                    caracteristicas[key] = values

                yield { 
                        'dominio': dominio,
                        'categoria': categoria,
                        'titulo': titulo,
                        'preco': preco,
                        'descricao': descricao,
                        'caracteristicas': caracteristicas,
                      }

    def parse_magazine_luiza(self, response):
            resultado = {}
            resultado['dominio'] = response.url.split('/')[2]
            resultado['disponivel'] = response.xpath('//meta[re:test(@content, "OutOfStock")]').get() is None
            resultado['categoria'] = response.css('.breadcrumb__item::text').get().strip()

            if resultado['disponivel']:
                resultado['titulo'] = response.css('.header-product__title::text').get().strip()

                preco_tag = response.css('.price-template-price-block')
                resultado['preco'] = ' '.join([preco_tag.css('.price-template__bold::text').get(), preco_tag.css('.price-template__text::text').get()])

            else:
                resultado['titulo'] = response.css('.header-product__title--unavailable::text').get().strip()
                
            resultado['descricao'] = ' '.join(response.xpath('//div[re:test(@itemprop, "description")]/text()').getall()).strip()
            
            tabela_info = response.xpath('//div').xpath('./table/tr')
            caracteristicas = {}
            # Características são dispostas em <td class=desc_info-left> para chave e outra tabela com <td class=..left/right> para valores, para cada <tr>
            for tr in tabela_info:
                key = tr.css('.description__information-left::text').get().lower()
                values = tr.css('.description__information-right').xpath('./table//td/text()').getall()
                values = '\n'.join([val.strip() for val in values if val.strip() != ''])
                caracteristicas[key] = values
            resultado['caracteristicas'] = caracteristicas

            yield resultado 

    def parse_mercado_livre(self, response):
            dominio = response.url.split('/')[2]
            titulo = response.css('.ui-pdp-title::text').get().strip()
            
            categoria = None
            if response.css('.andes-breadcrumb__item a::text').get():
                categoria = response.css('.andes-breadcrumb__item a::text').get().strip()

            # Quando um produto não está em estoque há uma mensagem de erro
            disponivel = response.css('.ui-pdp-warning-message').get() is None
            preco = None
            if disponivel:
                preco_tag = response.css('.price-tag')
                # Se existe preço, é necessário checar se existe um valor em centavos no preço
                if preco_tag.css('.price-tag-cents').get():
                    preco = ' '.join([preco_tag.css('.price-tag-symbol::text').get(), 
                                      preco_tag.css('.price-tag-fraction::text').get() + ',' + preco_tag.css('.price-tag-cents::text').get()])
                else:
                    preco = ' '.join([preco_tag.css('.price-tag-symbol::text').get(), preco_tag.css('.price-tag-fraction::text').get()])

            # Captura descrição linha a linha, remove excesso de espaçamento e reordena por linha
            descricao = '\n'.join([line.strip() for line in response.css('.ui-pdp-description__content::text').getall()])

            tabela_info = response.css('.ui-pdp-specs')
            caracteristicas = {'principais': {}, 'outras': {}}
            # Características principais são dispostas em <tr> com chave em <th> e valor em um <span>
            for tr in tabela_info.css('.andes-table__row'):
                key = tr.xpath('./th/text()').get()
                value = tr.xpath('./td/span/text()').get()
                caracteristicas['principais'][key] = value
            # Outras características são dispostas em <li> com chave em <span> e valor em <p>
            for li in tabela_info.css('.ui-pdp-list__item'):
                key = li.xpath('./span/text()').get().strip()
                value = li.xpath('./p/text()').get().strip()
                caracteristicas['outras'][key] = value

            yield {
                    'dominio': dominio,
                    'categoria': categoria,
                    'titulo': titulo,
                    'disponivel': disponivel,
                    'preco': preco,
                    'descricao': descricao,
                    'caracteristicas': caracteristicas
                  }

    def parse_produto_mercado_livre(self, response):
            dominio = response.url.split('/')[2]
            categoria = response.css('.vip-navigation-breadcrumb-list a::text').get().strip()
            titulo = response.css('.item-title__primary::text').get().strip()

            preco_tag = response.css('.price-tag')
            # É necessário checar se existe um valor em centavos no preço
            if preco_tag.css('.price-tag-cents').get():
                preco = ' '.join([preco_tag.css('.price-tag-symbol::text').get(), 
                                  preco_tag.css('.price-tag-fraction::text').get() + ',' + preco_tag.css('.price-tag-cents::text').get()])
            else:
                preco = ' '.join([preco_tag.css('.price-tag-symbol::text').get(), preco_tag.css('.price-tag-fraction::text').get()])

            # Captura descrição linha a linha, remove excesso de espaçamento e reordena por linha
            descricao = '\n'.join([line.strip() for line in response.css('.item-description__text p::text').getall()])

            tabela_info = response.css('.specs-wrapper').xpath('./section/ul/li')
            caracteristicas = {}
            # Características são dispostas em <li> com chave em <strong> e valor em <span>
            for li in tabela_info:
                key = li.xpath('./strong/text()').get().strip()
                values = li.xpath('./span/text()').get().strip()
                caracteristicas[key] = values

            yield {
                    'dominio': dominio,
                    'categoria': categoria,
                    'titulo': titulo,
                    'preco': preco,
                    'descricao': descricao,
                    'caracteristicas': caracteristicas
                  }

