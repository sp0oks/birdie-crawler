# -*- coding: utf-8 -*-
import scrapy
import re

from ofertascrawler.items import Oferta

URL_CASAS_BAHIA = re.compile(r'casasbahia')
URL_MAGAZINE_LUIZA = re.compile(r'magazineluiza')
URL_MERCADO_LIVRE_PROD = re.compile(r'produto\.mercadolivre')
URL_MERCADO_LIVRE = re.compile(r'mercadolivre')


class OfertasSpider(scrapy.Spider):
    name = 'ofertas'
    allowed_domains = ['www.casasbahia.com.br', 'produto.mercadolivre.com.br', 'www.mercadolivre.com.br', 'www.magazineluiza.com.br']

    def __init__(self, urlfile=None, user_agent=None):
        if isinstance(urlfile, str):
            with open(urlfile, 'r') as urls:
                self.start_urls = [url.strip() for url in urls.readlines()]
        elif isinstance(urlfile, list):
            self.start_urls = urlfile

        if user_agent:
            self.user_agent = user_agent

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
            item = Oferta()

            item['dominio'] = response.url.split('/')[2]
            item['url'] = response.url
            item['categoria'] = response.css('.breadcrumb a span::text').getall()[1]
            item['titulo'] = response.css('.produtoNome h1.name b::text').get()

            if response.css('#ctl00_Conteudo_ctl40_spanProdutoTempIndisponivel').get():
                item['disponivel'] = False
            else:
                item['disponivel'] = True
                preco_tag = response.css('#ctl00_Conteudo_ctl00_precoPorValue')
                item['moeda'] = preco_tag.css('::text').get()
                try:
                    item['preco'] = preco_tag.css('i::text').get().replace('.', '').replace(',', '.')
                except AttributeError:
                    pass
            detalhes = response.css('.detalhesProduto')
            try:
                item['descricao'] = detalhes.xpath('.//div[re:test(@class, "descricao")]/p/text()').get().strip()
            except AttributeError:
                item['descricao'] = None
                
            tabela_info = detalhes.css('.caracteristicasGerais').xpath('./div/dl')
            item['caracteristicas'] = {}
            # Caracteristicas são dispostas em <dl> com chave em <dt> e valores em <dd>
            for div in tabela_info:
                key = div.xpath('./dt/text()').get().strip()
                values = div.xpath('./dd/text()').get().strip()
                item['caracteristicas'][key] = values

        yield item

    def parse_magazine_luiza(self, response):
        item = Oferta()

        item['dominio'] = response.url.split('/')[2]
        item['url'] = response.url
        item['disponivel'] = response.xpath('//meta[re:test(@content, "OutOfStock")]').get() is None

        item['categoria'] = None
        if response.css('.breadcrumb__item').get():
            item['categoria'] = response.css('.breadcrumb__item::text').get().strip()

        if item['disponivel']:
            try:
                item['titulo'] = response.css('.header-product__title::text').get().strip()
            except AttributeError:
                item['titulo'] = None

            preco_tag = response.css('.price-template-price-block')
            item['moeda'] = preco_tag.css('.price-template__bold::text').get()
            try:
                item['preco'] = preco_tag.css('.price-template__text::text').get().replace('.', '').replace(',', '.')
            except AttributeError:
                pass
        else:
            item['titulo'] = response.css('.header-product__title--unavailable::text').get().strip()
                
        item['descricao'] = ' '.join(response.xpath('//div[re:test(@itemprop, "description")]/text()').getall()).strip()
            
        tabela_info = response.xpath('//div').xpath('./table/tr')
        item['caracteristicas'] = {}
        # Características são dispostas em <td class=desc_info-left> para chave e outra tabela com <td class=..left/right> para valores, para cada <tr>
        for tr in tabela_info:
            key = tr.css('.description__information-left::text').get().lower()
            values = tr.css('.description__information-right').xpath('./table//td/text()').getall()
            values = '\n'.join([val.strip() for val in values if val.strip() != ''])
            item['caracteristicas'][key] = values

        yield item 

    def parse_mercado_livre(self, response):
        item = Oferta()

        item['dominio'] = response.url.split('/')[2]
        item['url'] = response.url

        try:
            item['titulo'] = response.css('.ui-pdp-title::text').get().strip()
        except AttributeError:
            pass
            
        try:
            item['categoria'] = response.css('.andes-breadcrumb__item a::text').get().strip()
        except AttributeError:
            item['categoria'] = None

        # Quando um produto não está em estoque há uma mensagem de erro
        item['disponivel'] = response.css('.ui-pdp-warning-message').get() is None
        item['preco'] = None
        if item['disponivel']:
            preco_tag = response.css('.price-tag')
            item['moeda'] = preco_tag.css('.price-tag-symbol::text').get()
            try:
                # Se existe preço, é necessário checar se existe um valor em centavos no preço
                if preco_tag.css('.price-tag-cents').get():
                    item['preco'] = preco_tag.css('.price-tag-fraction::text').get().replace('.', '') + '.' + preco_tag.css('.price-tag-cents::text').get()
                else:
                    item['preco'] = preco_tag.css('.price-tag-fraction::text').get().replace('.', '')
            except AttributeError:
                pass
        # Captura descrição linha a linha, remove excesso de espaçamento e reordena por linha
        item['descricao'] = '\n'.join([line.strip() for line in response.css('.ui-pdp-description__content::text').getall()])

        tabela_info = response.css('.ui-pdp-specs')
        item['caracteristicas'] = {'principais': {}, 'outras': {}}
        # Características principais são dispostas em <tr> com chave em <th> e valor em um <span>
        for tr in tabela_info.css('.andes-table__row'):
            key = tr.xpath('./th/text()').get()
            value = tr.xpath('./td/span/text()').get()
            item['caracteristicas']['principais'][key] = value
        # Outras características são dispostas em <li> com chave em <span> e valor em <p>
        for li in tabela_info.css('.ui-pdp-list__item'):
            key = li.xpath('./span/text()').get().strip()
            value = li.xpath('./p/text()').get().strip()
            item['caracteristicas']['outras'][key] = value

        yield item

    def parse_produto_mercado_livre(self, response):
        item = Oferta()

        item['dominio'] = response.url.split('/')[2]
        item['url'] = response.url
        item['disponivel'] = True

        try:
            item['categoria'] = response.css('.vip-navigation-breadcrumb-list a::text').get().strip()
        except AttributeError:
            item['categoria'] = None
        item['titulo'] = response.css('.item-title__primary::text').get().strip()

        preco_tag = response.css('.price-tag')
        item['moeda'] = preco_tag.css('.price-tag-symbol::text').get()
        try:
            # É necessário checar se existe um valor em centavos no preço
            if preco_tag.css('.price-tag-cents').get():
                item['preco'] = preco_tag.css('.price-tag-fraction::text').get().replace('.', '') + '.' + preco_tag.css('.price-tag-cents::text').get()
            else:
                item['preco'] = preco_tag.css('.price-tag-fraction::text').get().replace('.', '')
        except AttributeError:
            pass
        # Captura descrição linha a linha, remove excesso de espaçamento e reordena por linha
        item['descricao'] = '\n'.join([line.strip() for line in response.css('.item-description__text p::text').getall()])

        tabela_info = response.css('.specs-wrapper').xpath('./section/ul/li')
        item['caracteristicas'] = {}
        # Características são dispostas em <li> com chave em <strong> e valor em <span>
        for li in tabela_info:
            key = li.xpath('./strong/text()').get().strip()
            values = li.xpath('./span/text()').get().strip()
            item['caracteristicas'][key] = values

        yield item
