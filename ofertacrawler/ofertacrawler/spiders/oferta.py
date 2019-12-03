# -*- coding: utf-8 -*-
import scrapy
import w3lib
import re

URL_CASAS_BAHIA = re.compile(r'casasbahia')
URL_MAGAZINE_LUIZA = re.compile(r'magazineluiza')
URL_MERCADO_LIVRE_PROD = re.compile(r'produto\.mercadolivre')
URL_MERCADO_LIVRE = re.compile(r'mercadolivre')


class OfertaSpider(scrapy.Spider):
    name = 'Oferta'

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
                caracteristicas = detalhes.css('.Caracteristicas-Gerais').xpath('./dd/text()').get().strip()
                garantia = detalhes.css('.Garantia').xpath('./dd/text()').get().strip()
                cor = detalhes.css('.Cor').xpath('./dd/text()').get().strip()

                yield { 
                        'dominio': dominio,
                        'categoria': categoria,
                        'titulo': titulo,
                        'preco': preco,
                        'descricao': descricao,
                        'caracteristicas': {
                                             'texto': caracteristicas,
                                             'cor': cor.lower(),
                                             'garantia': garantia,
                                           }
                      }

    def parse_magazine_luiza(self, response):
            dominio = response.url.split('/')[2]
            disponivel = response.xpath('//meta[re:test(@content, "OutOfStock")]').get() is None
            categoria = response.css('.breadcrumb__item::text').get().strip()
            
            if disponivel:
                titulo = response.css('.header-product__title::text').get().strip()

                preco_tag = response.css('.price-template-price-block')
                preco = ' '.join([preco_tag.css('.price-template__bold::text').get(), preco_tag.css('.price-template__text::text').get()])
                
                descricao = ' '.join(response.xpath('//div[re:test(@itemprop, "description")]/text()').getall()).strip()

                tabela_info = response.css('.description__box--wildSand .description__box')
                caracteristicas = {}
                for box in tabela_info:
                    box_info = w3lib.html.replace_tags(box.get().strip(), token='|').split('|')
                    box_info = [item for item in box_info if item.strip() != '']
                    print(box_info)
                #    key = box.css('.description__information-left::text').get().lower()
                #    value = box.css('.description__information-right::text').get().lower()
                #    caracteristicas[key] = value
                yield {
                        'dominio': dominio,
                        'disponivel': disponivel,
                        'categoria': categoria,
                        'titulo': titulo,
                        'preco': preco,
                        'descricao': descricao,
                        'caracteristicas': caracteristicas, 
                      }
            else:
                titulo = response.css('.header-product__title--unavailable::text').get().strip()
                yield {
                        'dominio': dominio,
                        'disponivel': disponivel,
                        'categoria': categoria,
                        'titulo': titulo,
                      }
            
    def parse_mercado_livre(self, response):
            dominio = response.url.split('/')[2]

            yield {
                    'dominio': dominio,
                  }

    def parse_produto_mercado_livre(self, response):
            dominio = response.url.split('/')[2]

            yield {
                    'dominio': dominio,
                  }

